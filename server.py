"""Hybrid backend: serves the pixel-faithful HTML frontend (clone/index.html) and
runs the REAL engine — live World Cup 2026 data + a streaming OpenRouter LLM whose
output is governed by the deterministic gate. Pure stdlib (no FastAPI dependency).

The LLM advises (streamed); engine.gate_check + fractional_kelly decide. The API key
stays server-side (read from env or .streamlit/secrets.toml), never sent to the browser.

Run:   OPENROUTER_API_KEY=... python server.py      → http://localhost:8512
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import data
import llm
from engine import Candidate, PortfolioState, edge, fractional_kelly, gate_check

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = PortfolioState()
VSEP = "<<<VERDICT>>>"


def _load_key() -> None:
    if os.getenv("OPENROUTER_API_KEY"):
        return
    sec = os.path.join(HERE, ".streamlit", "secrets.toml")
    if os.path.exists(sec):
        with open(sec) as fh:
            for line in fh:
                if "OPENROUTER_API_KEY" in line and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        os.environ["OPENROUTER_API_KEY"] = val


_load_key()


def _fixtures() -> list[dict]:
    return (data.live_fixtures() or data.fixtures())[:9]


def _scores() -> list[dict]:
    return data.live_scores() or data.LIVE_SCORES


def _decide(f: dict):
    c = Candidate(f["event"], f["category"], f["selection"], f["model_p"], f["market_p"],
                  f["odds"], f["confidence"], f["ci_width"], f["sources"])
    passed, reasons = gate_check(c, STATE)
    stake = fractional_kelly(c.model_p, c.odds, STATE.bankroll)
    return passed, reasons, stake, edge(c.model_p, c.odds)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _head(self, code=200, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(os.path.join(HERE, "clone", "index.html"), "rb") as fh:
                self._head(200, "text/html; charset=utf-8")
                self.wfile.write(fh.read())
        elif path == "/api/board":
            self._head()
            self.wfile.write(json.dumps({"fixtures": _fixtures(), "scores": _scores(),
                                         "live": bool(data.live_fixtures())}).encode())
        else:
            self._head(404, "text/plain")
            self.wfile.write(b"not found")

    def do_POST(self):
        if urlparse(self.path).path != "/api/chat":
            self._head(404, "text/plain")
            self.wfile.write(b"not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(length) or "{}")
        fx = _fixtures()
        f = next((x for x in fx if x["event"] == req.get("event")), None) or (fx[0] if fx else None)
        if not f:
            self._head(404, "text/plain")
            self.wfile.write(b"no fixture")
            return
        passed, reasons, stake, e = _decide(f)
        fb = data.REASONINGS.get(f["event"]) or (
            f'Model puts {f["selection"]} at {f["model_p"]*100:.1f}% vs '
            f'{f["market_p"]*100:.1f}% implied — a {(f["model_p"]-f["market_p"])*100:+.1f}pt edge.')
        self._head(200, "text/plain; charset=utf-8")
        try:
            for chunk in llm.stream_analysis(f, e * 100, fb):
                self.wfile.write(chunk.encode())
                self.wfile.flush()
        except Exception:
            self.wfile.write(fb.encode())
        verdict = {"passed": passed, "reasons": reasons, "stake": stake, "edge": e,
                   "selection": f["selection"], "odds": f["odds"],
                   "confidence": f["confidence"], "sources": f["sources"]}
        self.wfile.write((VSEP + json.dumps(verdict)).encode())
        self.wfile.flush()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8512"))
    print(f"sport-quant hybrid on http://localhost:{port}  (LLM key: "
          f"{'set' if os.getenv('OPENROUTER_API_KEY') else 'MISSING'})")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
