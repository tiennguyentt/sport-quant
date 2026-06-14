"""sport-quant — a governed sports-prediction terminal (de-crypto'd SIRE rebuild).

The Terminal is the front door (the interaction layer): live scores, pick a match, ask,
and the engine answers with a Kelly-sized recommendation — but every answer is routed
through a deterministic gate. Models advise, code governs.
"""
from __future__ import annotations

import streamlit as st

import theme
from data import LIVE_SCORES, REASONINGS, fixtures, recorded_run
from engine import Candidate, PortfolioState, edge, fractional_kelly, gate_check
import scoring

BRAND = "sport-quant"

st.set_page_config(page_title="sport-quant terminal", layout="wide", initial_sidebar_state="expanded")
theme.inject_css()

RUN = recorded_run()
FIX = fixtures()
STATE = PortfolioState()

# ---- nav (left rail, de-crypto'd version of the aLink sidebar) -------------
with st.sidebar:
    st.markdown(theme.rail(BRAND, "100,000.00"), unsafe_allow_html=True)
    page = st.radio("nav", ["Terminal", "Performance", "Calibration"], label_visibility="collapsed")
    st.markdown('<div class="dk-foot">▢ Documentation<br>⚙ Settings<br>'
                '<span class="on">● engine connected</span></div>', unsafe_allow_html=True)

# live score ticker (top, like the reference terminal)
st.markdown(theme.ticker(LIVE_SCORES), unsafe_allow_html=True)


def _decide(f: dict) -> dict:
    c = Candidate(f["event"], f["category"], f["selection"], f["model_p"], f["market_p"],
                  f["odds"], f["confidence"], f["ci_width"], f["sources"])
    passed, reasons = gate_check(c, STATE)
    stake = fractional_kelly(c.model_p, c.odds, STATE.bankroll)
    return {"f": f, "passed": passed, "reasons": reasons, "stake": stake,
            "edge": edge(c.model_p, c.odds)}


def _response_html(d: dict) -> str:
    f = d["f"]
    reasoning = REASONINGS.get(f["event"], "")
    if d["passed"]:
        verdict = '<span class="dk-verdict ok">APPROVED · GATE PASSED</span>'
        rec = (f'<div class="rec"><b>{f["selection"]}</b> · stake '
               f'<b class="pos">{theme.money(d["stake"])}</b> · edge '
               f'<b class="pos">+{d["edge"]*100:.1f}%</b> · odds {f["odds"]:.2f} · '
               f'conf {f["confidence"]*100:.0f}% · sources {", ".join(f["sources"])}</div>')
        extra = ""
    else:
        verdict = '<span class="dk-verdict no">REJECTED · GATE BLOCKED</span>'
        rec = '<div class="rec">No bet surfaced — the model proposed, the policy refused.</div>'
        codes = "".join(f'<span class="dk-code">{r}</span>' for r in d["reasons"])
        extra = f'<div style="margin-top:9px">{codes}</div>'
    return f'{reasoning}{rec}<div style="margin-top:6px">{verdict}</div>{extra}'


def _ask(event_name: str) -> None:
    d = next((_decide(f) for f in FIX if f["event"] == event_name), None)
    if d is None:
        return
    thread = st.session_state.setdefault("thread", [])
    thread.append(("u", f'What should I do on {event_name}?'))
    thread.append(("a", _response_html(d)))


# ===========================================================================
if page == "Terminal":
    st.markdown('<div class="dk-hero">Introducing the <span class="g">terminal</span>. '
                'It\'s all about Positive EV.<br>Ask for a prediction — the gate decides what you see.</div>',
                unsafe_allow_html=True)
    st.markdown('<p class="dk-sub">The model proposes a sized bet; a deterministic policy approves or '
                'refuses it. No free-form prompt-gaming.</p>', unsafe_allow_html=True)

    # +EV scanner — DKING-style match cards you can ask about
    cards = FIX[:8]
    for row_start in range(0, len(cards), 4):
        cols = st.columns(4, gap="small")
        for col, f in zip(cols, cards[row_start:row_start + 4]):
            with col:
                e = max(0.0, edge(f["model_p"], f["odds"])) * 100
                st.markdown(theme.match_card(f, e), unsafe_allow_html=True)
                if st.button("Ask DKING", key=f'ask_{f["event"]}', use_container_width=True):
                    _ask(f["event"])
                    st.rerun()

    # chat thread inside the green-cornered panel
    thread = st.session_state.get("thread", [])
    if thread:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        bubbles = "".join(
            theme.user_msg(body) if role == "u" else theme.engine_msg(body)
            for role, body in thread
        )
        st.markdown(f'<div class="dk-chat">{bubbles}</div>', unsafe_allow_html=True)

    prompt = st.chat_input("Ask about a match, e.g. “best edge tonight?” or “Bayern vs Werder Bremen”")
    if prompt:
        # route free text to the closest fixture; else answer with the top edge
        match = next((f for f in FIX if f["event"].lower() in prompt.lower()
                      or prompt.lower() in f["event"].lower()), None)
        if match is None:
            ranked = sorted(FIX, key=lambda f: edge(f["model_p"], f["odds"]), reverse=True)
            match = ranked[0]
        _ask(match["event"])
        st.rerun()

# ===========================================================================
elif page == "Performance":
    k = RUN["kpis"]
    st.markdown('<div class="sq-kick">engine performance · paper portfolio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sq-h">Performance</div>', unsafe_allow_html=True)

    left, right = st.columns([0.34, 0.66], gap="medium")
    with left:
        st.markdown(
            '<div class="sq-card"><div class="cap">Your paper book</div>'
            + theme.kpi_grid([
                theme.kpi("Open P&amp;L", f'<span class="pos">+$280</span>'),
                theme.kpi("Positions", '6'),
                theme.kpi("Bankroll", '$100,000'),
            ], cols=3)
            + '</div>', unsafe_allow_html=True)
        # live signal card (telegram-style), de-crypto'd
        sig = next(f for f in FIX if f["event"].startswith("Dota2"))
        st.markdown(
            f'<div class="sq-sig" style="margin-top:14px"><div class="hd">▚ SIGNAL DETECTED</div>'
            f'<div class="sub">GATE PASSED // SURFACED</div>'
            f'<div class="row"><span class="k">Sport</span><span class="v">{sig["category"]}</span></div>'
            f'<div class="row"><span class="k">Event</span><span class="v">Xtreme Gaming vs MOUZ</span></div>'
            f'<div class="row"><span class="k">Bet</span><span class="v">{sig["selection"]}</span></div>'
            f'<div class="row"><span class="k">Odds</span><span class="v">{sig["odds"]:.2f}</span></div>'
            f'<div class="row"><span class="k">Confidence</span><span class="v">{sig["confidence"]*100:.0f}%</span></div>'
            f'</div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="sq-card"><div class="cap">Engine performance</div>'
            + theme.kpi_grid([
                theme.kpi("Net P&amp;L", f'<span class="{theme.cls(k["pnl"])}">{theme.money(k["pnl"], sign=True)}</span>'),
                theme.kpi("Total Gains", f'<span class="pos">{theme.money(k["total_gains"], sign=True)}</span>'),
                theme.kpi("Total Losses", f'<span class="neg">{theme.money(k["total_losses"])}</span>'),
                theme.kpi("Win Rate", f'{k["win_rate"]:.1f}%'),
            ], cols=4)
            + '<div style="height:10px"></div>'
            + theme.kpi_grid([
                theme.kpi("Deployed", theme.money(k["deployed"])),
                theme.kpi("Pending", theme.money(k["pending"])),
                theme.kpi("Settled Bets", str(k["n_bets"])),
            ], cols=3)
            + '</div>', unsafe_allow_html=True)

        rows = ""
        for s in RUN["settled"][:9]:
            pnl = s["realized_pnl"]
            w = min(60, abs(pnl) / 60)
            bar = (f'<span class="sq-bar" style="width:{w}px;background:'
                   f'{theme.POS if pnl>0 else theme.NEG}"></span>')
            rows += (f'<tr><td class="sq-ev">{s["event"]}</td>'
                     f'<td><span class="sq-cat">{s["category"]}</span></td>'
                     f'<td>{s["stake"]:,.2f}</td>'
                     f'<td class="{theme.cls(pnl)}">{theme.money(pnl, sign=True)}{bar}</td></tr>')
        st.markdown(
            '<div class="sq-card" style="margin-top:14px"><div class="cap">Settled trades</div>'
            '<table class="sq-tbl"><thead><tr><th>Event</th><th>League</th><th>Stake ($)</th>'
            f'<th>Realized P&amp;L ($)</th></tr></thead><tbody>{rows}</tbody></table></div>',
            unsafe_allow_html=True)

# ===========================================================================
elif page == "Calibration":
    import numpy as np
    settled = RUN["settled"]
    p = np.array([s["model_p"] for s in settled])
    o = np.array([s["outcome"] for s in settled])
    pnls = np.array([s["pnl"] for s in settled])
    stakes = np.array([s["stake"] for s in settled])
    clvs = np.array([scoring.clv(s["odds"], s["odds_close"]) for s in settled])

    bs = scoring.brier(p, o)
    bs_base = scoring.brier(np.full_like(p, o.mean()), o)
    ll = scoring.log_loss(p, o)
    ece_v = scoring.ece(p, o, bins=6)
    roi = scoring.roi_with_ci(pnls, stakes)
    vd = scoring.verdict(bs, bs_base, float(clvs.mean()), roi["lo"])

    st.markdown('<div class="sq-kick">calibration lab · is the model actually accurate?</div>', unsafe_allow_html=True)
    st.markdown('<div class="sq-h">Calibration & edge</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);font-size:14px;margin:2px 0 16px">Win rate alone is the '
                'wrong lens. We measure calibration (Brier/ECE), market edge (CLV), and significant ROI.</p>',
                unsafe_allow_html=True)

    st.markdown(theme.kpi_grid([
        theme.kpi("Brier", f'{bs:.3f}<span style="font-size:12px;color:var(--dim)"> / base {bs_base:.3f}</span>'),
        theme.kpi("Log loss", f'{ll:.3f}'),
        theme.kpi("ECE", f'{ece_v:.3f}'),
        theme.kpi("Mean CLV", f'<span class="{theme.cls(clvs.mean())}">{clvs.mean()*100:+.1f}%</span>'),
    ], cols=4), unsafe_allow_html=True)

    st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
    roi_lo = roi["lo"] * 100
    chips = []
    for label, ok in [("calibrated", vd["calibrated"]), ("beats market (CLV)", vd["beats_market"]),
                      ("profitable (ROI>0)", vd["profitable"])]:
        c = theme.POS if ok else theme.NEG
        chips.append(f'<span class="sq-cat" style="border-color:{c};color:{c}">'
                     f'{"✓" if ok else "✗"} {label}</span>')
    final = "EDGE IS REAL" if vd["edge_is_real"] else "EDGE NOT YET PROVEN"
    fcls = "ok" if vd["edge_is_real"] else "no"
    st.markdown(
        f'<div class="sq-card"><div class="cap">Verdict — measured, not asserted</div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">{"".join(chips)}</div>'
        f'<span class="sq-verdict {fcls}">{final}</span>'
        f'<div class="sq-foot" style="margin-top:10px">ROI {roi["roi"]*100:+.1f}% '
        f'(95% CI {roi_lo:+.1f}% … {roi["hi"]*100:+.1f}%) · n={len(settled)} bets · '
        f'method: Brier/log-loss/ECE + CLV + normal-approx ROI CI</div></div>',
        unsafe_allow_html=True)

    # reliability bins
    rb = scoring.reliability_bins(p, o, bins=6)
    bars = ""
    for conf, acc, n in rb:
        bars += (f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0;font-family:IBM Plex Mono;font-size:12px">'
                 f'<span style="width:64px;color:var(--muted)">p≈{conf:.2f}</span>'
                 f'<div style="flex:1;background:#1A1E23;border-radius:4px;height:14px;position:relative">'
                 f'<div style="width:{acc*100:.0f}%;height:100%;background:var(--accent);border-radius:4px;opacity:.85"></div></div>'
                 f'<span style="width:88px;text-align:right">obs {acc*100:.0f}% · n={n}</span></div>')
    st.markdown(f'<div class="sq-card" style="margin-top:14px"><div class="cap">Reliability — '
                f'predicted vs observed</div>{bars}</div>', unsafe_allow_html=True)
