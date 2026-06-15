"""Design system for sport-quant — a pixel-faithful rebuild of the SIRE / DKING terminal.

Reference: the DKING terminal screenshots — near-black starfield canvas, lime-green accent,
heavy Archivo display type, a live-score ticker, a left rail with a green folded-corner
balance card, a chat panel with avatar bubbles, DKING-style match cards, and a green input.
De-crypto'd: wallet/staking labels become session/paper-bankroll, same exact visual slots.
"""
from __future__ import annotations

import streamlit as st

import fonts_data  # SIRE fonts (Kensmark + PP Neue Montreal) embedded as data URIs

# ---- palette (DKING) -------------------------------------------------------
BG      = "#060607"
PANEL   = "#11150F"
PANEL2  = "#161B12"
LINE    = "#222A1C"
INK     = "#F2F4EF"
MUTED   = "#8A938A"
DIM     = "#5A6356"
LIME    = "#92CE53"   # the DKING green
POS     = "#92CE53"
NEG     = "#FF5B6B"
ACCENT  = "#92CE53"


def inject_css() -> None:
    html = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#060607; --panel:#11150F; --panel2:#161B12; --line:#222A1C;
  --ink:#F2F4EF; --muted:#8A938A; --dim:#5A6356; --lime:#92CE53; --pos:#92CE53; --neg:#FF5B6B; --accent:#92CE53;
}
html,body,[class*="css"]{ font-family:'ppNeueMontreal','kensmark',sans-serif; }
.stApp{
  background:#060607;
  background-image:
    radial-gradient(900px 520px at 50% 4%, rgba(146,206,83,.07), transparent 60%),
    radial-gradient(1.5px 1.5px at 12% 22%, rgba(146,206,83,.55), transparent),
    radial-gradient(1.5px 1.5px at 78% 18%, rgba(146,206,83,.30), transparent),
    radial-gradient(1px 1px at 34% 64%, rgba(146,206,83,.45), transparent),
    radial-gradient(1px 1px at 62% 78%, rgba(255,255,255,.20), transparent),
    radial-gradient(1.5px 1.5px at 88% 52%, rgba(146,206,83,.40), transparent),
    radial-gradient(1px 1px at 8% 76%, rgba(146,206,83,.30), transparent),
    radial-gradient(2px 2px at 46% 36%, rgba(146,206,83,.30), transparent),
    radial-gradient(1px 1px at 24% 88%, rgba(146,206,83,.35), transparent),
    radial-gradient(1px 1px at 92% 82%, rgba(146,206,83,.28), transparent),
    radial-gradient(1px 1px at 54% 14%, rgba(255,255,255,.16), transparent),
    radial-gradient(1.5px 1.5px at 70% 40%, rgba(146,206,83,.30), transparent);
  background-attachment:fixed;
  color:var(--ink);
}
#MainMenu,header[data-testid="stHeader"],footer{ display:none!important; }
[data-testid="stAppViewContainer"]>.main .block-container{ padding:.35rem 1.4rem 5rem; max-width:1240px; }
.num{ font-family:'IBM Plex Mono',monospace; font-variant-numeric:tabular-nums; }
.pos{ color:var(--pos); } .neg{ color:var(--neg); }
/* sidebar = DKING left rail */
[data-testid="stSidebar"]{ background:transparent; border-right:none; padding-top:6px; }
[data-testid="stSidebar"]>div{ padding-top:10px; }
[data-testid="stSidebar"] *{ color:var(--ink); }
.dk-rail{ background:rgba(17,21,15,.82); border:1px solid var(--line); border-radius:18px; padding:16px 15px; backdrop-filter:blur(3px); }
.dk-brand{ display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.dk-mark{ width:34px;height:34px;border-radius:9px;border:1px solid #2c3a22;background:#0d120b;display:grid;place-items:center;color:var(--lime);font-size:15px; }
.dk-brand b{ font-family:'kensmark';font-weight:800;font-size:17px;letter-spacing:-.01em; display:block;line-height:1; }
.dk-brand span{ font-family:'IBM Plex Mono';font-size:10px;color:var(--dim);letter-spacing:.12em; }
.dk-row{ display:flex;justify-content:space-between;align-items:center;font-size:12px;margin:12px 2px 8px; }
.dk-row .k{ color:var(--muted);font-weight:600; } .dk-row .v{ font-family:'IBM Plex Mono';color:var(--muted);font-size:11px; }
.dk-bal{ position:relative; overflow:hidden; background:#0e130b; border:1px solid #2c3a22; border-radius:13px; padding:13px 14px; }
.dk-bal::after{ content:""; position:absolute; top:0; right:0; border-width:0 30px 30px 0; border-style:solid; border-color:transparent var(--lime) transparent transparent; }
.dk-bal .l{ font-size:11px;color:var(--muted);font-weight:600;letter-spacing:.02em; }
.dk-bal .v{ font-family:'kensmark';font-weight:800;font-size:24px;color:var(--lime);letter-spacing:-.01em;margin-top:3px; }
.dk-foot{ font-size:12px;color:var(--dim);line-height:2.1;margin-top:14px; }
.dk-foot .on{ color:var(--lime); }
/* top live-score ticker */
.dk-tick{ display:flex; align-items:center; gap:16px; background:rgba(10,13,10,.7); border:1px solid var(--line); border-radius:12px; padding:8px 14px; overflow:hidden; margin-bottom:16px; }
.dk-tick .lab{ font-family:'IBM Plex Mono';font-size:11px;font-weight:600;color:var(--lime);letter-spacing:.08em;white-space:nowrap;flex:none;display:flex;align-items:center;gap:6px; }
.dk-tick .lab::before{ content:"";width:7px;height:7px;border-radius:50%;background:var(--lime);box-shadow:0 0 8px var(--lime); }
.dk-twrap{ flex:1; min-width:0; overflow:hidden; }
.dk-track{ display:flex; gap:34px; white-space:nowrap; animation:dktk 40s linear infinite; width:max-content; }
.dk-mi{ display:flex; align-items:center; gap:9px; }
.dk-cir{ width:22px;height:22px;border-radius:50%;background:#1a2113;border:1px solid #2c3a22;flex:none;display:grid;place-items:center;font-family:'kensmark';font-weight:700;font-size:10px;color:#7c8a66; }
.dk-mi .nm{ font-family:'kensmark';font-weight:700;font-size:13px;color:var(--ink);text-transform:uppercase;letter-spacing:.01em; }
.dk-mi .sc{ font-family:'kensmark';font-weight:800;font-size:14px;color:var(--lime); }
.dk-mi .mn{ font-family:'IBM Plex Mono';font-size:10px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:1px 7px; }
@keyframes dktk{ from{transform:translateX(0);} to{transform:translateX(-50%);} }
/* hero line */
.dk-hero{ font-family:'ppNeueMontreal',sans-serif;font-weight:700;font-size:30px;line-height:1.15;letter-spacing:-.02em;max-width:620px;margin:6px 0 4px; }
.dk-hero .g{ color:var(--lime); }
.dk-sub{ color:var(--muted);font-size:14px;margin:0 0 16px;max-width:660px; }
/* animated pipeline diagram (explains the flow visually) */
.dk-flow{ display:flex;align-items:stretch;gap:0;margin:8px 0 0;flex-wrap:nowrap; }
.fl-node{ flex:1;min-width:0;background:rgba(17,21,15,.7);border:1px solid var(--line);border-radius:12px;
          padding:14px 8px 12px;text-align:center;opacity:0;animation:flin .55s ease forwards; }
.fl-node.sc{ border-color:#3a521f;box-shadow:0 0 18px rgba(146,206,83,.14); }
.fl-ic{ font-family:'kensmark';font-size:21px;color:var(--lime);line-height:1;text-shadow:0 0 12px rgba(146,206,83,.5); }
.fl-t{ font-family:'kensmark';font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:.04em;margin-top:7px; }
.fl-s{ font-family:'IBM Plex Mono';font-size:9px;color:var(--dim);margin-top:3px;letter-spacing:.02em; }
.fl-link{ flex:0 0 30px;align-self:center;height:2px;background:var(--line);position:relative; }
.fl-link i{ position:absolute;top:-2px;width:6px;height:6px;border-radius:50%;background:var(--lime);box-shadow:0 0 9px var(--lime);animation:fldot 1.9s linear infinite; }
@keyframes fldot{ 0%{left:-3px;opacity:0;} 12%{opacity:1;} 88%{opacity:1;} 100%{left:calc(100% - 3px);opacity:0;} }
@keyframes flin{ from{opacity:0;transform:translateY(9px);} to{opacity:1;transform:none;} }
.dk-flowllm{ display:flex;align-items:center;gap:0;margin:0 0 20px;padding-left:calc(16.66% - 10px); }
.fl-branch{ width:1px;height:18px;border-left:1px dashed #3a521f; }
.fl-chip{ font-family:'IBM Plex Mono';font-size:10.5px;color:var(--muted);border:1px solid var(--line);border-left:none;border-radius:0 8px 8px 0;padding:5px 11px;margin-top:18px;background:rgba(13,16,11,.6); }
.dk-thesis{ display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:13px;overflow:hidden;margin:4px 0 20px; }
.dk-th{ background:rgba(17,21,15,.7);padding:15px 16px; }
.dk-th .k{ font-family:'IBM Plex Mono';font-size:10.5px;letter-spacing:.14em;color:var(--lime);margin-bottom:8px; }
.dk-th .b{ font-family:'ppNeueMontreal',sans-serif;font-size:12.5px;line-height:1.55;color:var(--muted); }
.dk-th .b b{ color:var(--ink);font-weight:600; }
/* DKING match card */
.dk-card{ position:relative; overflow:hidden; background:rgba(17,21,15,.7); border:1px solid var(--line); border-radius:15px; padding:16px 16px 14px; height:100%; backdrop-filter:blur(2px); }
.dk-card::after{ content:""; position:absolute; top:0; right:0; border-width:0 30px 30px 0; border-style:solid; border-color:transparent var(--lime) transparent transparent; }
.dk-card .lg{ font-family:'IBM Plex Mono';font-size:10px;color:var(--dim);letter-spacing:.12em;text-transform:uppercase; }
.dk-teamrow{ display:flex;justify-content:space-between;align-items:center;margin:11px 0; }
.dk-tm{ display:flex;align-items:center;gap:11px; }
.dk-ph{ width:32px;height:32px;border-radius:8px;background:#222a18;border:1px solid #394a28;flex:none;display:grid;place-items:center;font-family:'kensmark';font-weight:800;font-size:14px;color:#9aab73; }
img.dk-ph{ object-fit:contain; padding:3px; background:#0e130b; }
img.dk-cir{ object-fit:contain; background:#0e130b; padding:1px; }
.dk-teamrow .t{ font-family:'kensmark';font-weight:800;font-size:16px;letter-spacing:-.01em;text-transform:uppercase; }
.dk-teamrow .s{ font-family:'kensmark';font-weight:800;font-size:34px;color:var(--lime);line-height:1; }
.dk-prog{ height:3px;background:#1a2113;border-radius:2px;overflow:hidden;margin:6px 0 12px; }
.dk-prog>i{ display:block;height:100%;background:var(--lime); }
.dk-meta{ display:flex;justify-content:space-between;align-items:flex-end; }
.dk-meta .m{ font-family:'IBM Plex Mono';font-size:10px;color:var(--muted);line-height:1.9;letter-spacing:.02em; }
.dk-meta .m b{ color:var(--dim);font-weight:500; }
.dk-meta .m .dot{ display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--lime);margin-right:7px;vertical-align:middle; }
.dk-edge{ color:var(--lime);font-weight:700;font-family:'kensmark'; }
/* chat panel */
.dk-chat{ position:relative; overflow:hidden; background:rgba(13,16,11,.55); border:1px solid var(--line); border-radius:18px; padding:20px 22px; min-height:120px; }
.dk-chat::after{ content:""; position:absolute; top:0; right:0; border-width:0 40px 40px 0; border-style:solid; border-color:transparent var(--lime) transparent transparent; opacity:.85; }
.dk-arr{ position:absolute; top:50%; transform:translateY(-50%); width:30px;height:30px;border-radius:50%;background:#0d120b;border:1px solid var(--line);display:grid;place-items:center;color:var(--muted);font-size:17px;z-index:2; }
.dk-arr.l{ left:-14px; } .dk-arr.r{ right:-14px; }
.dk-msg{ display:flex; gap:13px; margin:18px 0; align-items:flex-start; }
.dk-av{ width:34px;height:34px;border-radius:10px;flex:none;display:grid;place-items:center;font-size:15px;font-family:'kensmark';font-weight:800; }
.dk-av.a{ background:#0d120b;border:1px solid #2c3a22;color:var(--lime); }
.dk-av.u{ background:linear-gradient(135deg,#92CE53,#5f8f1f);color:#060607; }
.dk-txt{ font-family:'ppNeueMontreal',sans-serif;font-weight:400;font-size:15px;line-height:1.6;color:#E8EBE4;max-width:680px;padding-top:5px; }
.dk-msg.u{ flex-direction:row-reverse; }
.dk-bub{ font-family:'ppNeueMontreal',sans-serif;font-weight:400;font-size:15px;line-height:1.55;color:#0c1208;background:var(--lime);border-radius:14px 14px 4px 14px;padding:11px 15px;max-width:70%; }
.dk-time.u{ text-align:right;margin:3px 50px 0 0; }
.dk-txt .rec{ font-family:'IBM Plex Mono';font-size:12.5px;margin-top:11px;color:var(--muted); }
.dk-txt .rec b{ color:var(--ink); } .dk-txt .rec .pos{ color:var(--lime); }
.dk-time{ font-family:'IBM Plex Mono';font-size:10.5px;color:var(--dim);margin:2px 0 0 47px; }
.dk-verdict{ font-family:'kensmark';font-weight:900;font-size:13px;letter-spacing:.06em;padding:6px 13px;border-radius:8px;display:inline-block;margin-top:11px; }
.dk-verdict.ok{ background:rgba(146,206,83,.12);color:var(--lime);border:1px solid #3a521f; }
.dk-verdict.no{ background:rgba(255,91,107,.1);color:var(--neg);border:1px solid #4a1d24; }
.dk-code{ font-family:'IBM Plex Mono';font-size:11px;color:#FF8A95;border:1px solid #4a1d24;border-radius:6px;padding:2px 8px;margin:0 4px 4px 0;display:inline-block; }
/* generic cards / kpis (Performance + Calibration) */
.sq-card{ background:rgba(17,21,15,.7); border:1px solid var(--line); border-radius:15px; padding:18px; backdrop-filter:blur(2px); }
.sq-card .cap{ font-size:13px;color:var(--muted);font-weight:600;margin-bottom:14px; }
.sq-h{ font-family:'kensmark';font-weight:800;font-size:28px;letter-spacing:-.02em;margin:2px 0; }
.sq-kick{ font-family:'IBM Plex Mono';font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--dim); }
.sq-kgrid{ display:grid; gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.sq-kgrid.c4{ grid-template-columns:repeat(4,1fr); } .sq-kgrid.c3{ grid-template-columns:repeat(3,1fr); }
.sq-k{ background:var(--panel); padding:14px 15px; }
.sq-k .l{ font-size:11px;color:var(--muted);margin-bottom:7px; }
.sq-k .v{ font-family:'IBM Plex Mono';font-weight:600;font-size:21px; }
.sq-tbl{ width:100%; border-collapse:collapse; font-size:13px; }
.sq-tbl th{ text-align:right;font-weight:600;font-size:11px;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--line); }
.sq-tbl th:first-child,.sq-tbl td:first-child{ text-align:left; }
.sq-tbl td{ padding:13px 12px;border-bottom:1px solid #181d14;font-family:'IBM Plex Mono';text-align:right; }
.sq-cat{ font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);border:1px solid var(--line);border-radius:6px;padding:2px 8px; }
.sq-bar{ display:inline-block;height:4px;border-radius:2px;vertical-align:middle;margin-left:8px; }
.sq-sig{ position:relative;overflow:hidden;background:#0e130b; border:1px solid #2c3a22; border-radius:13px; padding:15px 16px; }
.sq-sig::after{ content:"";position:absolute;top:0;right:0;border-width:0 26px 26px 0;border-style:solid;border-color:transparent var(--lime) transparent transparent; }
.sq-sig .hd{ font-family:'kensmark';font-weight:800;font-size:13px;color:var(--lime); }
.sq-sig .sub{ font-family:'IBM Plex Mono';font-size:10px;color:var(--dim);letter-spacing:.1em;margin-bottom:10px; }
.sq-sig .row{ display:flex;justify-content:space-between;font-size:13px;padding:3px 0; }
.sq-sig .row .k{ color:var(--muted); } .sq-sig .row .v{ font-family:'IBM Plex Mono'; }
.sq-verdict{ font-family:'kensmark';font-weight:900;font-size:14px;letter-spacing:.05em;padding:7px 14px;border-radius:8px;display:inline-block; }
.sq-verdict.ok{ background:rgba(146,206,83,.12);color:var(--lime);border:1px solid #3a521f; }
.sq-verdict.no{ background:rgba(255,91,107,.1);color:var(--neg);border:1px solid #4a1d24; }
.sq-foot{ font-size:11px;color:var(--dim);margin-top:8px; }
/* Streamlit widget restyle: green Ask buttons + chat input */
.stButton>button{ background:var(--lime); color:#060607; border:none; border-radius:9px; font-family:'kensmark'; font-weight:700; font-size:12px; padding:8px 0; letter-spacing:.02em; transition:.15s; }
.stButton>button:hover{ background:#B7F564; color:#060607; transform:translateY(-1px); }
.stButton>button:focus{ box-shadow:none;color:#060607; }
/* bottom chat input — clean, blends into the dark canvas (kill Streamlit's blue bar) */
[data-testid="stBottom"], [data-testid="stBottomBlockContainer"], [data-testid="stChatInput"] > div{ background:transparent!important; }
[data-testid="stChatInput"]{ background:rgba(17,21,15,.92); border:1px solid var(--line); border-radius:13px; }
[data-testid="stChatInput"]:focus-within{ border-color:#3a521f; }
[data-testid="stChatInput"] textarea{ font-family:'ppNeueMontreal',sans-serif; color:var(--ink); }
[data-testid="stChatInput"] textarea::placeholder{ color:var(--dim); font-family:'ppNeueMontreal',sans-serif; }
[data-testid="stChatInput"] button{ background:var(--lime)!important; color:#060607!important; border-radius:9px; box-shadow:0 0 14px rgba(146,206,83,.3); }
[data-testid="stSidebar"] .stRadio label{ font-size:13px; }
/* landing top header */
.dk-head{ display:flex; align-items:center; gap:11px; padding:2px 0 2px; }
.dk-head b{ font-family:'kensmark';font-weight:800;font-size:17px;letter-spacing:-.01em; }
.dk-hmark{ width:28px;height:28px;border-radius:7px;border:1px solid #2c3a22;background:#0d120b;display:grid;place-items:center;color:var(--lime);font-size:13px; }
.dk-clock{ font-family:'IBM Plex Mono';font-size:13px;color:var(--muted);margin-left:2px; }
.dk-dots{ display:inline-flex;gap:5px;margin-left:4px; }
.dk-dots i{ width:7px;height:7px;border-radius:50%;background:var(--lime);display:inline-block;animation:dkb 1.2s infinite; }
.dk-dots i:nth-child(2){ animation-delay:.2s; } .dk-dots i:nth-child(3){ animation-delay:.4s; }
@keyframes dkb{ 0%,100%{opacity:.3;} 50%{opacity:1;} }
.dk-status{ text-align:right;font-family:'IBM Plex Mono';font-size:12px;color:var(--muted);padding-top:7px; }
.dk-status .on{ color:var(--lime); }
.dk-filter{ font-family:'IBM Plex Mono';font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:9px;padding:8px 13px;float:right;margin-top:14px; }
/* terminal status footer (replaces the scrubber) */
.dk-footer{ display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;
            border-top:1px solid var(--line);margin:26px 0 4px;padding:14px 2px 2px; }
.ft-brand{ display:flex;align-items:center;gap:10px;font-family:'IBM Plex Mono';font-size:12px;color:var(--muted); }
.ft-brand b{ font-family:'kensmark';font-weight:800;font-size:13px;letter-spacing:.02em;color:var(--ink); }
.ft-tag{ color:var(--dim);letter-spacing:.13em;text-transform:uppercase;font-size:10px; }
.ft-dot{ width:7px;height:7px;border-radius:50%;background:var(--lime);box-shadow:0 0 9px var(--lime);animation:dkb 1.7s infinite; }
.ft-right{ display:flex;gap:7px;flex-wrap:wrap; }
.ft-chip{ font-family:'IBM Plex Mono';font-size:10.5px;color:var(--muted);border:1px solid var(--line);border-radius:7px;padding:4px 9px;transition:border-color .15s; }
.ft-chip:hover{ border-color:#3a521f; } .ft-chip b{ color:var(--lime);font-weight:500;letter-spacing:.04em; }
div[role="radiogroup"]{ gap:2px; justify-content:center; }
div[role="radiogroup"] label{ padding:5px 14px;border-radius:8px;font-size:13px;color:var(--muted); }
div[role="radiogroup"] label:hover{ background:#161b12;color:var(--ink); }
div[role="radiogroup"] label>div:first-child{ display:none; }
/* neon glow + motion to match the reference's lit feel */
.stButton>button{ box-shadow:0 0 16px rgba(146,206,83,.30); }
.stButton>button:hover{ box-shadow:0 0 22px rgba(146,206,83,.5); }
.dk-card::after,.dk-match::after,.dk-bal::after,.dk-chat::after{ filter:drop-shadow(-3px 3px 5px rgba(146,206,83,.45)); }
.dk-verdict.ok{ box-shadow:0 0 16px rgba(146,206,83,.22); }
.dk-hero .g{ text-shadow:0 0 22px rgba(146,206,83,.45); }
.dk-card{ transition:border-color .15s, transform .15s; }
.dk-card:hover{ border-color:#3a521f; transform:translateY(-2px); }
.dk-av.a{ box-shadow:0 0 12px rgba(146,206,83,.18); }
.stApp{ animation:drift 60s ease-in-out infinite alternate; }
@keyframes drift{ from{background-position:0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0,0 0;} to{background-position:0 0,8px 12px,-10px 8px,6px -8px,-8px 10px,10px 6px,-6px -10px,4px 8px,-8px -6px,12px 4px,-4px 10px,8px -8px;} }
hr{ border-color:var(--line); }
</style>
"""
    # Streamlit/markdown ends an HTML block at the first blank line — which would dump
    # the rest of the CSS as visible text. Strip blank lines so the <style> stays intact.
    html = "\n".join(line for line in html.splitlines() if line.strip())
    # embed the real SIRE fonts (Kensmark + PP Neue Montreal) right after <style>
    html = html.replace("<style>", "<style>" + fonts_data.FONT_CSS, 1)
    st.markdown(html, unsafe_allow_html=True)


def money(v: float, *, sign: bool = False, dollar: bool = True) -> str:
    return f"{'+' if sign and v > 0 else ''}{'-' if v < 0 else ''}{'$' if dollar else ''}{abs(v):,.0f}"


def cls(v: float) -> str:
    return "pos" if v > 0 else ("neg" if v < 0 else "")


# ---- sidebar (DKING left rail) --------------------------------------------
def rail(brand: str, bankroll: str) -> str:
    return (
        f'<div class="dk-rail">'
        f'<div class="dk-brand"><div class="dk-mark">◆</div>'
        f'<div><b>{brand}</b><span>V0.1 · GOVERNED</span></div></div>'
        f'<div class="dk-row"><span class="k">Session</span><span class="v">0xQUANT…paper</span></div>'
        f'<div class="dk-bal"><div class="l">Paper Bankroll</div><div class="v">{bankroll}</div></div>'
        f'</div>'
    )


# ---- live ticker -----------------------------------------------------------
def ticker(scores: list[dict]) -> str:
    def badge(s, side):
        url, nm = s.get(f"{side}_badge"), s["home" if side == "home" else "away"]
        return f'<img class="dk-cir" src="{url}" alt="">' if url else f'<span class="dk-cir">{nm[:1]}</span>'

    def item(s):
        mn = s["min"] if str(s["min"]) in ("FT", "HT") else f'{s["min"]}\''
        return (f'<span class="dk-mi">{badge(s, "home")}'
                f'<span class="nm">{s["home"]}</span><span class="sc">{s["hs"]}</span>'
                f'<span style="color:#5A6356">/</span><span class="sc">{s["as_"]}</span>'
                f'<span class="nm">{s["away"]}</span>{badge(s, "away")}'
                f'<span class="mn">{mn}</span></span>')
    items = "".join(item(s) for s in scores)
    return (f'<div class="dk-tick"><span class="lab">LIVE SCORE TRACKER</span>'
            f'<div class="dk-twrap"><div class="dk-track">{items}{items}</div></div></div>')


# ---- match card (logo + team + big score, stacked meta) --------------------
_PALETTE = ["#E0524B", "#4B7BE0", "#E0B24B", "#3FD68C", "#9B6BE0", "#E0744B",
            "#46C7E0", "#C45BE0", "#E04B92", "#7CC44B"]


def _team_color(name: str) -> str:
    return _PALETTE[sum(ord(ch) for ch in name) % len(_PALETTE)]


def _badge(name: str, url: str | None = None) -> str:
    if url:
        return f'<img class="dk-ph" src="{url}" alt="">'
    c = _team_color(name)
    return (f'<span class="dk-ph" style="background:{c}22;border-color:{c}66;color:{c}">'
            f'{name[:1].upper()}</span>')


def match_card(f: dict, edge_pct: float) -> str:
    home, _, away = f["event"].partition(" vs ")
    fill = min(100, max(8, edge_pct * 9))
    return (
        f'<div class="dk-card"><div class="lg">{f["category"]}</div>'
        f'<div class="dk-teamrow"><span class="dk-tm">{_badge(home, f.get("home_badge"))}'
        f'<span class="t">{home}</span></span>'
        f'<span class="s">{f["model_p"]*100:.0f}</span></div>'
        f'<div class="dk-teamrow"><span class="dk-tm">{_badge(away, f.get("away_badge"))}'
        f'<span class="t">{away}</span></span>'
        f'<span class="s">{(1-f["model_p"])*100:.0f}</span></div>'
        f'<div class="dk-prog"><i style="width:{fill:.0f}%"></i></div>'
        f'<div class="dk-meta"><div class="m"><span class="dot"></span><b>START:</b> {f["start"]}<br>'
        f'<b>VENUE:</b> {f["venue"]}<br><b>MODEL:</b> {f["confidence"]*100:.0f}% conf</div>'
        f'<div class="dk-edge">+{edge_pct:.1f}% EV</div></div></div>'
    )


# ---- chat bubbles ----------------------------------------------------------
def user_msg(text: str, ts: str = "") -> str:
    t = f'<div class="dk-time u">{ts} ⧉</div>' if ts else ""
    return (f'<div class="dk-msg u"><div class="dk-bub">{text}</div>'
            f'<div class="dk-av u">◧</div></div>{t}')


def engine_msg(body_html: str, ts: str = "") -> str:
    t = f'<div class="dk-time">⧉ {ts}</div>' if ts else ""
    return (f'<div class="dk-msg"><div class="dk-av a">◆</div>'
            f'<div class="dk-txt">{body_html}</div></div>{t}')


def chat_panel(bubbles: str) -> str:
    return f'<div class="dk-chat">{bubbles}</div>'


def flow() -> str:
    """Animated pipeline diagram — explains the system visually, not in prose.
    signals → score → edge → kelly → gate → bet, with the LLM as a side branch."""
    nodes = [
        ("◈", "signals", "ratings·xG·form"),
        ("∿", "score", "win prob"),
        ("Δ", "edge", "vs market"),
        ("ƒ", "kelly", "size"),
        ("⛓", "gate", "code decides"),
        ("◎", "bet", "or skip"),
    ]
    parts = ""
    for i, (ic, t, s) in enumerate(nodes):
        if i:
            parts += '<div class="fl-link"><i></i></div>'
        cls = "fl-node sc" if t == "score" else "fl-node"
        parts += (f'<div class="{cls}" style="animation-delay:{i*0.18:.2f}s">'
                  f'<div class="fl-ic">{ic}</div><div class="fl-t">{t}</div>'
                  f'<div class="fl-s">{s}</div></div>')
    return (f'<div class="dk-flow">{parts}</div>'
            f'<div class="dk-flowllm"><span class="fl-branch"></span>'
            f'<span class="fl-chip">✎ LLM-powered · integrates the +EV signals · sizing &amp; gate stay deterministic</span></div>')


def footer() -> str:
    """A clean terminal status bar — honest system facts, on-brand mono chips."""
    chips = [
        ("data", "TheSportsDB · World Cup 2026"),
        ("model", "deepseek-v3 · advisory"),
        ("gate", "deterministic · ¼-Kelly · 1%/pos"),
        ("policy", "v1.3"),
    ]
    right = "".join(f'<span class="ft-chip"><b>{k}</b> {v}</span>' for k, v in chips)
    return ('<div class="dk-footer">'
            '<div class="ft-brand"><span class="ft-dot"></span><b>sport-quant</b>'
            '<span class="ft-tag">governed decision engine</span></div>'
            f'<div class="ft-right">{right}</div></div>')


def thesis() -> str:
    """The pain point this system solves and how — logic + data, at a glance."""
    cols = [
        ("THE PROBLEM",
         "Prediction markets are owned by sharp syndicates with better data and discipline. "
         "Most “AI tips” are ungrounded hype — no proof their probabilities are even accurate."),
        ("THE METHOD",
         "Multi-source signals (vision · ELO · xG) become one probability. A <b>deterministic "
         "gate</b> — code, not the model — sizes the bet with fractional Kelly and hard caps "
         "(max 1%/position, ~12% deployed). The model advises; the code governs. No prompt-gaming."),
        ("THE PROOF",
         "We measure whether the model is actually <b>right</b>: calibration (Brier · ECE), "
         "closing-line value, and statistically-significant ROI — not just win rate. "
         "See the <b>Calibration</b> tab."),
    ]
    cells = "".join(
        f'<div class="dk-th"><div class="k">{k}</div><div class="b">{b}</div></div>'
        for k, b in cols)
    return f'<div class="dk-thesis">{cells}</div>'


# ---- kpis (Performance / Calibration reuse) --------------------------------
def kpi(label: str, value_html: str) -> str:
    return f'<div class="sq-k"><div class="l">{label}</div><div class="v">{value_html}</div></div>'


def kpi_grid(cells: list[str], cols: int = 4) -> str:
    return f'<div class="sq-kgrid c{cols}">{"".join(cells)}</div>'


def segmented(options: list[str], active: str) -> str:
    return ""
