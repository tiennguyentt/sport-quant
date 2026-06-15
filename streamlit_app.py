"""sport-quant — a governed sports-prediction terminal (prediction-market terminal).

The Terminal is the front door (the interaction layer): live scores, pick a match, ask, and
the engine answers with a Kelly-sized recommendation — every answer routed through a
deterministic gate. Models advise, code governs.
"""
from __future__ import annotations

import os
from datetime import datetime

import streamlit as st
from PIL import Image, ImageDraw

import theme
from data import (LIVE_SCORES, REASONINGS, fixtures, recorded_run,
                  live_fixtures, live_scores)
from engine import Candidate, PortfolioState, edge, fractional_kelly, gate_check
import scoring
import llm

BRAND = "Sport Quant"


def _favicon() -> Image.Image:
    """Branded favicon: dark panel + brand-green border + lime ◆ with soft glow.
    Matches the dk-mark component in the design system exactly.
    Passed as a PIL Image so Streamlit embeds it in <head> — overrides any body-level link."""
    S = 64
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # outer dark background
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=14, fill=(6, 6, 7, 255))
    # inner panel with brand-green border (mirrors dk-mark: #0d120b bg, #2c3a22 border)
    d.rounded_rectangle([3, 3, S - 4, S - 4], radius=10,
                        fill=(13, 18, 11, 255), outline=(44, 58, 34, 255), width=2)
    # lime ◆ diamond (#92CE53)
    cx, pad = S // 2, 10
    d.polygon([(cx, pad), (S - pad, cx), (cx, S - pad), (pad, cx)],
              fill=(146, 206, 83, 255))
    # inner highlight stroke for depth
    d.polygon([(cx, pad + 6), (S - pad - 6, cx), (cx, S - pad - 6), (pad + 6, cx)],
              outline=(184, 232, 122, 100), width=1)
    return img


st.set_page_config(page_title="Sport Quant terminal", page_icon=_favicon(), layout="wide",
                   initial_sidebar_state="collapsed")
theme.inject_css()

# Make the OpenRouter key visible to llm.py via env: prefer a local .env, then
# Streamlit secrets (for Streamlit Cloud, set OPENROUTER_API_KEY in app secrets).
_envf = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_envf):
    for _line in open(_envf):
        _line = _line.strip()
        if _line.startswith("OPENROUTER_API_KEY") and "=" in _line:
            os.environ.setdefault("OPENROUTER_API_KEY",
                                  _line.split("=", 1)[1].strip().strip('"').strip("'"))
try:
    _k = st.secrets.get("OPENROUTER_API_KEY")
    if _k:
        os.environ.setdefault("OPENROUTER_API_KEY", _k)
except Exception:
    pass

RUN = recorded_run()
STATE = PortfolioState()


@st.cache_data(ttl=300, show_spinner=False)
def _get_fixtures():
    """Real World Cup 2026 fixtures (TheSportsDB), synthetic fallback if offline."""
    if os.getenv("SPORTQUANT_OFFLINE"):
        return fixtures()
    return live_fixtures() or fixtures()


@st.cache_data(ttl=120, show_spinner=False)
def _get_scores():
    return live_scores() or LIVE_SCORES


FIX = _get_fixtures()
LIVE = _get_scores()
DATA_IS_LIVE = FIX and FIX[0].get("category") == "World Cup 2026"


def _decide(f: dict) -> dict:
    c = Candidate(f["event"], f["category"], f["selection"], f["model_p"], f["market_p"],
                  f["odds"], f["confidence"], f["ci_width"], f["sources"])
    passed, reasons = gate_check(c, STATE)
    stake = fractional_kelly(c.model_p, c.odds, STATE.bankroll)
    return {"f": f, "passed": passed, "reasons": reasons, "stake": stake,
            "edge": edge(c.model_p, c.odds)}


def _fallback_reasoning(f: dict) -> str:
    return (REASONINGS.get(f["event"]) or
            f'Model puts {f["selection"]} at {f["model_p"]*100:.1f}% vs {f["market_p"]*100:.1f}% '
            f'implied — a {(f["model_p"]-f["market_p"])*100:+.1f}pt model edge across '
            f'{", ".join(f["sources"])} (live World Cup 2026 fixture; model probability illustrative).')


def _verdict_html(d: dict) -> str:
    """The deterministic gate's verdict — appended AFTER the LLM's streamed reasoning."""
    f = d["f"]
    if d["passed"]:
        verdict = '<span class="dk-verdict ok">APPROVED · GATE PASSED</span>'
        rec = (f'<div class="rec"><b>{f["selection"]}</b> · stake '
               f'<b class="pos">{theme.money(d["stake"])}</b> · edge '
               f'<b class="pos">+{d["edge"]*100:.1f}%</b> · odds {f["odds"]:.2f} · '
               f'conf {f["confidence"]*100:.0f}% · sources {", ".join(f["sources"])}</div>')
        extra = ""
    else:
        verdict = '<span class="dk-verdict no">REJECTED · GATE BLOCKED</span>'
        rec = '<div class="rec">No bet surfaced — the model proposed, the risk desk refused.</div>'
        codes = "".join(f'<span class="dk-code">{r}</span>' for r in d["reasons"])
        extra = f'<div style="margin-top:9px">{codes}</div>'
    return f'{rec}<div style="margin-top:6px">{verdict}</div>{extra}'


def _ask(event_name: str, user_text: str | None = None) -> None:
    # queue the question; the chat view streams the LLM reply, then the gate decides.
    # user_text = exactly what the human typed (echoed in the chat); None for card clicks.
    st.session_state["pending"] = {"event": event_name, "text": user_text}


_CHAT_ONLY = {"hi", "hello", "hey", "yo", "sup", "hola", "test", "ok", "okay",
              "thanks", "thank", "thx", "bye", "good", "great", "nice", "cool"}


def _ask_box(key: str) -> None:
    """Chat composer — one centered rounded box (styled in theme CSS): the input on top,
    decorative attach/mic icons + a green send pill on the bottom row. Matches the reference."""
    with st.form(key, clear_on_submit=True, border=False):
        q = st.text_input("ask", placeholder="Ask the model about a match, or a team name",
                          label_visibility="collapsed")
        c1, c2 = st.columns([0.7, 0.3], gap="small", vertical_alignment="center")
        c1.markdown(":material/attach_file: :material/mic:")
        go = c2.form_submit_button("Ask  :material/send:", use_container_width=True)
    if go and q.strip():
        words = set(q.lower().split())
        # conversational / non-match input — reply directly, skip match analysis
        if words <= _CHAT_ONLY or len(q.strip()) <= 4:
            thread = st.session_state.setdefault("thread", [])
            thread.append(("u", q.strip()))
            thread.append(("a", "I'm the Sport Quant engine — ask me about a specific match "
                           "or team name and I'll run the model, surface the edge, and let the "
                           "gate decide. Try: <em>South Korea vs Czech Republic</em> or "
                           "<em>USA</em>."))
            st.rerun()
            return
        m = next((f for f in FIX if any(w in f["event"].lower() for w in q.lower().split())), None) \
            or max(FIX, key=lambda f: edge(f["model_p"], f["odds"]))
        _ask(m["event"], q.strip())
        st.rerun()


# deepseek-v4 is the default engine; deepseek-chat is the optional lighter pick.
MODEL_MAP = {"deepseek-v3": "deepseek/deepseek-chat-v3-0324", "deepseek-chat": "deepseek/deepseek-chat"}


def _go_home() -> None:
    """Return to the default Terminal landing and start a fresh session.

    Runs as a widget callback (before the next rerun), so it may safely reset the
    nav radio's keyed state — the fix for 'can't get back to the default screen'.
    """
    st.session_state["nav_page"] = "Terminal"
    st.session_state.pop("thread", None)
    st.session_state.pop("pending", None)


# ---- top header strip (brand · hamburger menu) ----------------------------
# The brand IS the home button; nav + model + status collapse into a single
# hamburger popover — keeps the header to one compact row on every screen size.
hc1, hc2 = st.columns([0.82, 0.18], gap="small", vertical_alignment="center")
with hc1:
    st.button(f":green[◆]  {BRAND}", key="home_brand", on_click=_go_home,
              help="Back to the terminal home")
with hc2:
    with st.popover("☰", use_container_width=True):
        st.markdown('<div class="menu-sec">Navigate</div>', unsafe_allow_html=True)
        page = st.radio("nav", ["Terminal", "Performance", "Calibration", "About"],
                        key="nav_page", label_visibility="collapsed")
        st.markdown('<div class="menu-sec t">Engine model</div>', unsafe_allow_html=True)
        st.selectbox("model", list(MODEL_MAP), key="model_choice", label_visibility="collapsed")
        st.markdown('<div class="menu-status">engine&nbsp;<span class="on">●</span>&nbsp;'
                    'online · gate governed</div>', unsafe_allow_html=True)

SEL_MODEL = MODEL_MAP.get(st.session_state.get("model_choice", "deepseek-v3"))

st.markdown(theme.ticker(LIVE), unsafe_allow_html=True)

# a card's "Ask" button is a ?ask=<event> link — route it into the chat, then clean the URL.
_ask_param = st.query_params.get("ask")
if _ask_param:
    st.query_params.clear()
    _ask(_ask_param)

thread = st.session_state.get("thread", [])
pending = st.session_state.get("pending")
in_chat = page == "Terminal" and bool(thread or pending)

if page == "Terminal" and not in_chat:
    # ===== LANDING (Grok-style): faint centered watermark fills the calm void,
    # the card slide is pinned just above the bottom-fixed composer. The whole
    # screen is locked to the viewport — no page scroll here. ==================
    strip = "".join(theme.card(f, max(0.0, edge(f["model_p"], f["odds"])) * 100) for f in FIX[:12])
    st.markdown(
        f'<div class="sq-landing">{theme.landing_hero()}{theme.card_strip(strip)}</div>',
        unsafe_allow_html=True,
    )
    _ask_box("ask_landing")

elif in_chat:
    # ===== CHAT (matches 19.11.51): rail | chat panel ========================
    rail_col, main = st.columns([0.23, 0.77], gap="medium")
    with rail_col:
        st.markdown(theme.rail(BRAND, "100,000.00"), unsafe_allow_html=True)
        st.button("← Home  ·  new session", key="home_rail", on_click=_go_home, use_container_width=True)
    with main:
        if thread:
            bubbles = ""
            for role, body in thread:
                ts = "4:41 PM" if role == "u" else "4:42 PM"
                bubbles += theme.user_msg(body, ts) if role == "u" else theme.engine_msg(body, ts)
            st.markdown(theme.chat_panel(bubbles), unsafe_allow_html=True)
        if pending:
            f = next((x for x in FIX if x["event"] == pending["event"]), None)
            if not f:
                # the queued match is no longer in the fixture list (live data refreshed) —
                # drop it instead of trapping the user in an empty chat view.
                st.session_state.pop("pending", None)
                st.rerun()
            if f:
                d = _decide(f)
                # echo the human's actual words; fall back to a default for card clicks
                q = pending.get("text") or f"Give me the details on {pending['event']}."
                st.markdown(theme.user_msg(q, "4:41 PM"), unsafe_allow_html=True)

                # Show thinking indicator while waiting for the first LLM token.
                # Cleared the moment the stream yields its first chunk.
                _think = st.empty()
                _think.markdown(
                    '<div class="dk-msg"><div class="dk-av a">◆</div>'
                    '<div class="dk-txt"><span class="sq-thinking">'
                    '<span class="sq-tl">ANALYZING EDGE</span>'
                    '<span class="dk-dots"><i></i><i></i><i></i></span>'
                    '</span></div></div>',
                    unsafe_allow_html=True,
                )

                def _stream_clear_thinking(gen, slot):
                    first = True
                    for chunk in gen:
                        if first:
                            slot.empty()
                            first = False
                        yield chunk
                    slot.empty()  # also clear if stream returned nothing

                st.markdown('<div class="dk-msg"><div class="dk-av a">◆</div>'
                            '<div class="dk-txt" style="padding-top:2px">', unsafe_allow_html=True)
                streamed = st.write_stream(
                    _stream_clear_thinking(
                        llm.stream_analysis(f, d["edge"] * 100, _fallback_reasoning(f), model=SEL_MODEL),
                        _think,
                    )
                )
                st.markdown("</div></div>", unsafe_allow_html=True)
                thread = st.session_state.setdefault("thread", [])
                thread.append(("u", q))
                thread.append(("a", f"{streamed}{_verdict_html(d)}"))
                st.session_state.pop("pending", None)
                st.rerun()
        if not pending:
            st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
            _ask_box("ask_chat")

elif page == "Performance":
    if True:
        k = RUN["kpis"]
        st.markdown('<div class="sq-kick">engine performance · paper portfolio</div>', unsafe_allow_html=True)
        st.markdown('<div class="sq-h">Performance</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sq-card" style="margin-top:8px"><div class="cap">Engine performance</div>'
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
            ], cols=3) + '</div>', unsafe_allow_html=True)

        rows = ""
        for s in RUN["settled"][:10]:
            pnl = s["realized_pnl"]
            w = min(60, abs(pnl) / 60)
            bar = (f'<span class="sq-bar" style="width:{w}px;background:'
                   f'{theme.POS if pnl>0 else theme.NEG}"></span>')
            rows += (f'<tr><td>{s["event"]}</td><td><span class="sq-cat">{s["category"]}</span></td>'
                     f'<td>{s["stake"]:,.2f}</td>'
                     f'<td class="{theme.cls(pnl)}">{theme.money(pnl, sign=True)}{bar}</td></tr>')
        st.markdown(
            '<div class="sq-card" style="margin-top:14px"><div class="cap">Settled trades</div>'
            '<table class="sq-tbl"><thead><tr><th>Event</th><th>League</th><th>Stake ($)</th>'
            f'<th>Realized P&amp;L ($)</th></tr></thead><tbody>{rows}</tbody></table></div>',
            unsafe_allow_html=True)

elif page == "Calibration":
    if True:
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
        st.markdown('<div class="sq-h">Calibration &amp; edge</div>', unsafe_allow_html=True)
        st.markdown(theme.kpi_grid([
            theme.kpi("Brier", f'{bs:.3f}<span style="font-size:12px;color:var(--dim)"> / base {bs_base:.3f}</span>'),
            theme.kpi("Log loss", f'{ll:.3f}'),
            theme.kpi("ECE", f'{ece_v:.3f}'),
            theme.kpi("Mean CLV", f'<span class="{theme.cls(clvs.mean())}">{clvs.mean()*100:+.1f}%</span>'),
        ], cols=4), unsafe_allow_html=True)

        chips = []
        for label, ok in [("calibrated", vd["calibrated"]), ("beats market (CLV)", vd["beats_market"]),
                          ("profitable (ROI>0)", vd["profitable"])]:
            c = theme.POS if ok else theme.NEG
            chips.append(f'<span class="sq-cat" style="border-color:{c};color:{c}">'
                         f'{"✓" if ok else "✗"} {label}</span>')
        final = "EDGE IS REAL" if vd["edge_is_real"] else "EDGE NOT YET PROVEN"
        fcls = "ok" if vd["edge_is_real"] else "no"
        st.markdown(
            f'<div class="sq-card" style="margin-top:12px"><div class="cap">Verdict — measured, not asserted</div>'
            f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">{"".join(chips)}</div>'
            f'<span class="sq-verdict {fcls}">{final}</span>'
            f'<div class="sq-foot" style="margin-top:10px">ROI {roi["roi"]*100:+.1f}% '
            f'(95% CI {roi["lo"]*100:+.1f}% … {roi["hi"]*100:+.1f}%) · n={len(settled)} bets</div></div>',
            unsafe_allow_html=True)

        rb = scoring.reliability_bins(p, o, bins=6)
        bars = ""
        for conf, acc, n in rb:
            bars += (f'<div style="display:flex;align-items:center;gap:10px;margin:6px 0;font-family:IBM Plex Mono;font-size:12px">'
                     f'<span style="width:64px;color:var(--muted)">p≈{conf:.2f}</span>'
                     f'<div style="flex:1;background:#181d14;border-radius:4px;height:14px">'
                     f'<div style="width:{acc*100:.0f}%;height:100%;background:var(--lime);border-radius:4px;opacity:.85"></div></div>'
                     f'<span style="width:88px;text-align:right">obs {acc*100:.0f}% · n={n}</span></div>')
        st.markdown(f'<div class="sq-card" style="margin-top:14px"><div class="cap">Reliability — '
                    f'predicted vs observed</div>{bars}</div>', unsafe_allow_html=True)

elif page == "About":
    st.markdown('<div class="sq-kick">about · how it works</div>', unsafe_allow_html=True)
    st.markdown('<div class="sq-h">Quant scoring for prediction markets</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--muted);font-size:14px;margin:4px 0 18px;max-width:680px">'
                'Sport Quant scores live markets (built for Polymarket &amp; Kalshi), finds +EV '
                'mispricings, and sizes bets with fractional Kelly — governed by a deterministic '
                'gate. The pipeline:</p>', unsafe_allow_html=True)
    st.markdown(theme.flow(), unsafe_allow_html=True)

    def _stage(num, title, note):
        st.markdown(f'<div class="sq-kick" style="margin-top:18px">{num} · {title}</div>'
                    f'<p style="color:var(--muted);font-size:13px;margin:2px 0 6px">{note}</p>',
                    unsafe_allow_html=True)

    _stage("00", "SIGNALS — Computer Vision Player Tracking",
           "Raw video frames enter a YOLO detection pass that produces bounding boxes for every "
           "player on the pitch. A Kalman-filter tracker (SORT / ByteTrack-style) assigns stable "
           "IDs and estimates velocity across frames. The resulting position + velocity packets "
           "feed the scoring ensemble as real-time signal inputs. "
           "The same pipeline architecture (Score Vision, Bittensor SN44) processed "
           "4 million packets in production — this is not a backtest toy.")
    st.markdown('<p style="color:var(--dim);font-size:12px;margin:6px 0 2px">'
                'Constant-velocity model (simplest baseline):</p>', unsafe_allow_html=True)
    st.latex(
        r"c_{x,\text{pred}} = c_x + v_x\,\Delta t \qquad c_{y,\text{pred}} = c_y + v_y\,\Delta t"
        r"\qquad (\Delta t \approx 0.033\,\text{s at 30 fps})"
    )
    st.markdown('<p style="color:var(--dim);font-size:12px;margin:10px 0 2px">'
                'Kalman Filter — prediction step (what production trackers actually run):</p>',
                unsafe_allow_html=True)
    st.latex(
        r"\mathbf{x} = \begin{bmatrix} c_x \\ c_y \\ v_x \\ v_y \end{bmatrix}, \qquad"
        r"\hat{\mathbf{x}}_{t+1} = F\,\hat{\mathbf{x}}_t, \qquad"
        r"F = \begin{pmatrix} 1 & 0 & \Delta t & 0 \\ 0 & 1 & 0 & \Delta t \\"
        r"0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}"
    )
    st.latex(r"P_{\text{pred}} = F\,P\,F^\top + Q")
    st.markdown(
        '<p style="color:var(--dim);font-size:12px;margin:4px 0 6px">'
        r'\(P\) = current position/velocity uncertainty · '
        r'\(Q\) = process noise (accounts for sudden acceleration) · '
        r'\(F^\top\) = transpose of the state-transition matrix. '
        'After prediction, detections are matched to tracks by IoU; '
        'the Kalman update step corrects the state estimate.</p>',
        unsafe_allow_html=True
    )

    _stage("01", "SCORE — Elo + Dixon-Coles ensemble",
           "Two base models produce a probability; a meta-ensemble blends them. No LLM here.")
    st.latex(r"\textbf{Elo: } \quad P_{\text{elo}}(\text{home}) = \frac{1}{1 + 10^{(R_{away}-R_{home})/400}}")
    st.latex(r"\textbf{Dixon-Coles: }\quad \lambda_{home}=\gamma\,\alpha_{home}\,\beta_{away},\;\; "
             r"\mu_{away}=\alpha_{away}\,\beta_{home}")
    st.latex(r"P(x,y)=\tau_{\lambda,\mu,\rho}(x,y)\,\frac{\lambda^{x}e^{-\lambda}}{x!}\,"
             r"\frac{\mu^{y}e^{-\mu}}{y!}\;\Rightarrow\; P_{dc}(\text{home})=\!\!\sum_{x>y}P(x,y)")
    st.latex(r"\textbf{Ensemble: }\quad p = w_{dc}\,P_{dc} + w_{elo}\,P_{elo}\quad(w_{dc}=0.6,\;w_{elo}=0.4)")

    _stage("02", "EDGE — model probability vs the de-vigged market", "")
    st.latex(r"\text{edge} = p - q,\qquad q = \tfrac{1}{\text{odds}}\;\;(\text{implied probability})")

    _stage("03", "SIZE — fractional Kelly with hard caps (1% per position)", "")
    st.latex(r"f^{*}=\frac{b\,p-(1-p)}{b},\quad b=\text{odds}-1;\qquad "
             r"\text{stake}=\min\!\big(\tfrac14 f^{*}B,\;0.01\,B\big)")

    _stage("04", "GATE — deterministic, code-enforced (the model cannot override)",
           "edge ≥ 2.8% · confidence ≥ 52% · |p−q| ≥ 2.2% · CI width ≤ 0.19 · "
           "≥ 2 sources · total deployed ≤ 12% · no event concentration.")

    _stage("05", "PROVE — is the model actually accurate? (not just win rate)", "")
    st.latex(r"\text{Brier}=\tfrac1n\!\sum (p_i-o_i)^2,\quad "
             r"\text{ECE}=\sum_b \tfrac{n_b}{n}\,\lvert \text{acc}_b-\text{conf}_b\rvert,\quad "
             r"\text{CLV}=\tfrac{O_{bet}}{O_{close}}-1")
    st.markdown('<p style="color:var(--dim);font-size:12px;margin-top:14px">The LLM (selectable above) '
                'reads these numbers and writes the plain-language rationale. It is advisory — it '
                'never sets the probability, the size, or the gate decision.</p>', unsafe_allow_html=True)
