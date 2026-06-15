"""Real LLM analysis via OpenRouter (streaming).

The LLM ADVISES — it explains the edge in plain language. It deliberately does NOT
make the final bet decision; engine.gate_check + fractional_kelly GOVERN that. This
is the anti-prompt-gaming design: the model reasons, the code decides. Falls back to
a provided recorded line when no API key is configured.
"""
from __future__ import annotations

import json
import os
import urllib.request

MODEL = os.getenv("SPORTQUANT_MODEL", "deepseek/deepseek-chat-v3-0324")
_URL = "https://openrouter.ai/api/v1/chat/completions"
_SYS = (
    "You are a sports quantitative analyst on a risk desk. Given a fixture and the model's "
    "probability versus the market's implied probability, explain the edge in 2-3 tight "
    "sentences, citing the actual numbers. Do NOT give a final yes/no bet decision or a stake "
    "size — a separate deterministic risk gate decides that. Keep it under 70 words, no preamble."
)


def have_key() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY"))


def _prompt(f: dict, edge_pct: float) -> str:
    return (
        f'Fixture: {f["event"]} ({f["category"]}). Candidate selection: {f["selection"]}. '
        f'Model probability {f["model_p"]*100:.1f}%, market implied {f["market_p"]*100:.1f}%, '
        f'decimal odds {f["odds"]:.2f}, model edge {edge_pct:+.1f} points, '
        f'confidence {f["confidence"]*100:.0f}%, signal sources: {", ".join(f["sources"])}. '
        "Explain whether there is a real edge and where it comes from."
    )


def stream_analysis(f: dict, edge_pct: float, fallback: str = "", model: str | None = None):
    """Yield analysis text chunk-by-chunk. Streams from OpenRouter when a key is set."""
    key = os.getenv("OPENROUTER_API_KEY")
    if os.getenv("SPORTQUANT_OFFLINE") or not key:
        yield fallback or "Live model not configured on this deployment; showing the gate verdict only."
        return
    body = {
        "model": model or MODEL, "stream": True, "max_tokens": 240, "temperature": 0.4,
        "messages": [{"role": "system", "content": _SYS},
                     {"role": "user", "content": _prompt(f, edge_pct)}],
    }
    req = urllib.request.Request(
        _URL, data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://sport-quant.streamlit.app", "X-Title": "sport-quant"},
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            for raw in r:
                line = raw.decode("utf-8", "ignore").strip()
                if not line.startswith("data: "):
                    continue
                chunk = line[6:]
                if chunk == "[DONE]":
                    break
                try:
                    delta = json.loads(chunk)["choices"][0]["delta"].get("content", "")
                except Exception:
                    continue
                if delta:
                    yield delta
    except Exception as exc:
        yield (fallback + f"  \n\n_(live model unavailable: {exc})_") if fallback else \
              f"_(live model unavailable: {exc})_"
