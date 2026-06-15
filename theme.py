"""Design system for sport-quant — a pixel-faithful rebuild of the reference terminal.

Reference: the reference terminal screenshots — near-black starfield canvas, lime-green accent,
heavy Archivo display type, a live-score ticker, a left rail with a green folded-corner
balance card, a chat panel with avatar bubbles, match cards, and a green input.
De-crypto'd: wallet/staking labels become session/paper-bankroll, same exact visual slots.
"""
from __future__ import annotations

import urllib.parse

import streamlit as st

import fonts_data  # Brand fonts (Kensmark + PP Neue Montreal) embedded as data URIs

# ---- branded favicon — matches dk-mark: dark panel + brand border + lime ◆ + glow --
_FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    # outer background
    '<rect width="32" height="32" rx="7" fill="#060607"/>'
    # inner panel (dk-mark bg) with brand-green border
    '<rect x="1.5" y="1.5" width="29" height="29" rx="5.5" fill="#0d120b" stroke="#2c3a22" stroke-width="1.5"/>'
    # glow filter for the diamond
    '<filter id="g" x="-80%" y="-80%" width="260%" height="260%">'
    '<feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
    '</filter>'
    # lime ◆ diamond
    '<polygon points="16,5 27,16 16,27 5,16" fill="#92CE53" filter="url(#g)"/>'
    # inner highlight on diamond
    '<polygon points="16,8.5 23.5,16 16,23.5 8.5,16" fill="none" stroke="#b8e87a" stroke-width="0.6" opacity="0.45"/>'
    '</svg>'
)
_FAVICON = "data:image/svg+xml," + urllib.parse.quote(_FAVICON_SVG)

# ---- palette (the reference) -------------------------------------------------------
BG      = "#060607"
PANEL   = "#11150F"
PANEL2  = "#161B12"
LINE    = "#222A1C"
INK     = "#F2F4EF"
MUTED   = "#8A938A"
DIM     = "#5A6356"
LIME    = "#92CE53"   # the brand green
POS     = "#92CE53"
NEG     = "#FF5B6B"
ACCENT  = "#92CE53"


def inject_css() -> None:
    html = """
<link rel="icon" href="__FAVICON__">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#060607; --panel:#11150F; --panel2:#161B12; --line:#222A1C;
  --ink:#F2F4EF; --muted:#8A938A; --dim:#5A6356; --lime:#92CE53; --pos:#92CE53; --neg:#FF5B6B; --accent:#92CE53;
}
html,body,[class*="css"]{ font-family:'ppNeueMontreal','kensmark',sans-serif; }
html{ -webkit-text-size-adjust:100%; text-size-adjust:100%; }
*{ -webkit-tap-highlight-color:transparent; }
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
/* hide Streamlit Cloud chrome that floats over the composer (status widget,
   manage-app badge, deploy button, "hosted with Streamlit" viewer badge,
   top decoration bar). Mostly owner-only, but cleared so nothing collides. */
[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
.stAppDeployButton,
[data-testid="stAppViewBlockContainer"]>[data-testid="stDecoration"],
[class*="viewerBadge"],
a[href*="streamlit.io/cloud"],
a[href*="share.streamlit.io"]{ display:none!important; }
[data-testid="stAppViewContainer"]>.main .block-container,
[data-testid="stMainBlockContainer"], .block-container{ padding:.6rem 1.4rem 4.5rem!important; max-width:1240px; }
.num{ font-family:'IBM Plex Mono',monospace; font-variant-numeric:tabular-nums; }
.pos{ color:var(--pos); } .neg{ color:var(--neg); }
/* sidebar = the reference left rail */
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
.dk-hero{ font-family:'ppNeueMontreal',sans-serif;font-weight:700;font-size:27px;line-height:1.26;letter-spacing:-.02em;max-width:740px;margin:4px auto 22px;text-align:center;color:var(--ink); }
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
/* the reference match card */
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
.dk-teamrow .s .pct{ font-size:.42em;font-weight:700;opacity:.7;margin-left:1px;vertical-align:.95em; }
.dk-prog{ height:3px;background:#1a2113;border-radius:2px;overflow:hidden;margin:6px 0 12px; }
.dk-prog>i{ display:block;height:100%;background:var(--lime); }
.dk-meta{ display:flex;justify-content:space-between;align-items:flex-end; }
.dk-meta .m{ font-family:'IBM Plex Mono';font-size:10px;color:var(--muted);line-height:1.9;letter-spacing:.02em; }
.dk-meta .m b{ color:var(--dim);font-weight:500; }
.dk-meta .m .dot{ display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--lime);margin-right:7px;vertical-align:middle; }
.dk-edge{ color:var(--lime);font-weight:700;font-family:'kensmark'; }
/* chat panel */
.dk-chat{ position:relative; overflow:hidden; background:rgba(13,16,11,.55); border:1px solid var(--line); border-radius:18px; padding:24px 26px; min-height:calc(100vh - 300px); }
.dk-chat::after{ content:""; position:absolute; top:0; right:0; border-width:0 40px 40px 0; border-style:solid; border-color:transparent var(--lime) transparent transparent; opacity:.85; }
.dk-arr{ position:absolute; top:50%; transform:translateY(-50%); width:30px;height:30px;border-radius:50%;background:#0d120b;border:1px solid var(--line);display:grid;place-items:center;color:var(--muted);font-size:17px;z-index:2; }
.dk-arr.l{ left:-14px; } .dk-arr.r{ right:-14px; }
.dk-msg{ display:flex; gap:13px; margin:20px 0; align-items:flex-start; animation:msgIn .4s cubic-bezier(.2,.7,.2,1) both; }
@keyframes msgIn{ from{opacity:0;transform:translateY(7px);} to{opacity:1;transform:none;} }
.dk-av{ width:34px;height:34px;border-radius:10px;flex:none;display:grid;place-items:center;font-size:15px;font-family:'kensmark';font-weight:800; }
.dk-av.a{ background:#0d120b;border:1px solid #2c3a22;color:var(--lime); }
.dk-av.u{ background:linear-gradient(135deg,#92CE53,#5f8f1f);color:#060607; }
.dk-txt{ font-family:'ppNeueMontreal',sans-serif;font-weight:400;font-size:15px;line-height:1.6;color:#E8EBE4;max-width:680px;padding-top:5px; }
.dk-msg.u{ flex-direction:row-reverse; }
.dk-bub{ font-family:'ppNeueMontreal',sans-serif;font-weight:400;font-size:15px;line-height:1.55;color:#0c1208;background:var(--lime);border-radius:14px 14px 4px 14px;padding:11px 15px;max-width:70%; }
.dk-time.u{ text-align:right;margin:4px 4px 0 0; }
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
/* the match cards live in a horizontally-scrolling strip (a carousel, like the source) */
.dk-strip{ display:flex; gap:16px; overflow-x:auto; overflow-y:hidden; padding:6px 2px 14px;
  scroll-snap-type:x proximity; scrollbar-color:#2c3a22 transparent; }
.dk-strip::-webkit-scrollbar{ height:9px; }
.dk-strip::-webkit-scrollbar-track{ background:transparent; }
.dk-strip::-webkit-scrollbar-thumb{ background:#26301c; border-radius:5px; }
.dk-strip::-webkit-scrollbar-thumb:hover{ background:#3a521f; }
.dk-card2{ flex:0 0 300px; scroll-snap-align:start; position:relative; overflow:hidden;
  background:linear-gradient(180deg,#0e120b,#0a0d07); border:1px solid var(--line); border-radius:14px;
  padding:14px 16px; transition:border-color .15s, transform .15s; }
/* compact landing card internals — smaller, cleaner, more breathing room */
.dk-card2 .lg{ font-size:9.5px; }
.dk-card2 .dk-teamrow{ margin:8px 0; }
.dk-card2 .dk-teamrow .t{ font-size:14px; }
.dk-card2 .dk-teamrow .s{ font-size:27px; }
.dk-card2 .dk-ph{ width:27px; height:27px; font-size:12px; }
.dk-card2 .dk-prog{ margin:5px 0 9px; }
.dk-card2 .dk-cfoot{ margin-top:10px; padding-top:9px; }
.dk-card2 .dk-foot3{ font-size:9.5px; line-height:1.75; }
.dk-card2 .dk-evtag{ font-size:12px; }
.dk-card2 .dk-askbtn{ padding:7px 14px; font-size:11px; }
.dk-card2:hover{ border-color:#3a521f; transform:translateY(-2px); }
.dk-card2::after{ content:""; position:absolute; top:0; right:0; border-width:0 30px 30px 0;
  border-style:solid; border-color:transparent var(--lime) transparent transparent;
  filter:drop-shadow(-3px 3px 5px rgba(146,206,83,.45)); }
.dk-cfoot{ display:flex; justify-content:space-between; align-items:flex-end; gap:12px; margin-top:13px;
  border-top:1px solid #161b12; padding-top:12px; }
.dk-foot3{ font-family:'IBM Plex Mono'; font-size:10.5px; line-height:1.95; color:var(--dim); }
.dk-foot3 b{ color:var(--dim); font-weight:500; letter-spacing:.05em; }
.dk-foot3 .v{ color:var(--lime); }
.dk-cbtn{ display:flex; flex-direction:column; align-items:flex-end; gap:8px; flex:none; }
.dk-evtag{ font-family:'kensmark'; font-weight:800; font-size:13px; color:var(--lime);
  text-shadow:0 0 12px rgba(146,206,83,.4); }
.dk-askbtn{ display:inline-block; background:var(--lime); color:#060607!important; font-family:'kensmark';
  font-weight:700; font-size:12px; padding:9px 18px; border-radius:9px; text-decoration:none;
  white-space:nowrap; box-shadow:0 0 14px rgba(146,206,83,.3); transition:.15s; }
.dk-askbtn:hover{ background:#B7F564; transform:translateY(-1px); }
/* tick-ruler scrubber decor (between the cards and the composer) */
.sq-ruler{ position:relative; height:30px; margin:10px 0 4px;
  background-image:repeating-linear-gradient(90deg, rgba(138,147,138,.32) 0 1px, transparent 1px 14px);
  -webkit-mask-image:linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent);
          mask-image:linear-gradient(90deg, transparent, #000 5%, #000 95%, transparent); }
.sq-ruler::before{ content:""; position:absolute; inset:0;
  background-image:repeating-linear-gradient(90deg, rgba(146,206,83,.22) 0 1px, transparent 1px 70px);
  height:30px; }
.sq-ruler .mk{ position:absolute; left:50%; top:50%; transform:translate(-50%,-50%);
  font-family:'IBM Plex Mono'; color:var(--lime); letter-spacing:26px; font-size:14px;
  padding-left:26px; text-shadow:0 0 10px rgba(146,206,83,.6); }
/* chat composer — a centered rounded box FIXED to the bottom (chrome stays, cards scroll) */
[data-testid="stForm"]{ position:fixed; left:50%; bottom:16px; top:auto!important; transform:translateX(-50%);
  width:min(780px,92vw); height:auto!important; z-index:60; margin:0!important;
  background:rgba(15,19,12,.96); border:1px solid var(--line)!important; border-radius:16px;
  padding:14px 16px 12px!important; box-shadow:0 14px 50px rgba(0,0,0,.55); }
[data-testid="stForm"] [data-testid="stTextInput"] input{ background:transparent; border:none; border-radius:0;
  color:var(--ink); font-family:'ppNeueMontreal',sans-serif; font-size:16px; padding:6px 4px; }
[data-testid="stForm"] [data-testid="stTextInput"] input::placeholder{ color:var(--dim); font-family:'ppNeueMontreal',sans-serif; }
[data-testid="stForm"] [data-testid="stTextInput"] input:focus{ border:none; box-shadow:none; }
/* the decorative attach / mic icons (left of the send button) */
[data-testid="stForm"] [data-testid="stMarkdownContainer"] [data-testid="stIconMaterial"]{
  color:var(--dim); font-size:22px; margin-right:8px; }
/* green send pill, bottom-right of the composer */
[data-testid="stForm"] [data-testid="stFormSubmitButton"]>button{ background:var(--lime); color:#060607;
  border:none; border-radius:9px; min-height:40px; padding:0 20px!important; font-family:'kensmark';
  font-weight:700; font-size:13px; box-shadow:0 0 14px rgba(146,206,83,.3); transform:none; }
[data-testid="stForm"] [data-testid="stFormSubmitButton"]>button:hover{ background:#B7F564; transform:translateY(-1px); }
[data-testid="stForm"] [data-testid="stFormSubmitButton"] [data-testid="stIconMaterial"]{ font-size:18px; }
/* the brand mark IS the home button — make it look like a logo, not a green button */
.st-key-home_brand button{ background:transparent!important; border:none!important; box-shadow:none!important;
  color:var(--ink)!important; padding:5px 2px!important; justify-content:flex-start!important; transform:none!important; }
.st-key-home_brand button:hover{ background:transparent!important; box-shadow:none!important; transform:none!important; }
.st-key-home_brand button p{ font-family:'kensmark'!important; font-weight:800!important; font-size:17px!important; letter-spacing:-.01em!important; }
.st-key-home_brand button:hover p{ color:var(--lime)!important; }
/* the ◆ is rendered with Streamlit's emerald :green — recolor to the brand lime
   so the mark matches the numbers, buttons, watermark and favicon (#92CE53) */
.st-key-home_brand button p span,
.st-key-home_brand button p span *{ color:var(--lime)!important; }
/* rail home — quiet ghost utility button, not a hero CTA */
.st-key-home_rail button{ background:transparent!important; border:1px solid var(--line)!important;
  box-shadow:none!important; color:var(--muted)!important; font-family:'IBM Plex Mono'!important;
  font-size:11px!important; font-weight:400!important; letter-spacing:.04em!important;
  padding:7px 0!important; transform:none!important; margin-top:10px; }
.st-key-home_rail button:hover{ background:rgba(146,206,83,.07)!important;
  border-color:var(--lime)!important; color:var(--lime)!important; box-shadow:none!important; transform:none!important; }
/* model selectbox in the header */
[data-testid="stSelectbox"] div[data-baseweb="select"]>div{ background:rgba(17,21,15,.9); border:1px solid var(--line); border-radius:9px; font-family:'IBM Plex Mono'; font-size:12px; color:var(--ink); min-height:34px; }
/* override Streamlit's default navy (#262730) wherever it leaks: text-input &
   select wrappers, and the select dropdown menu — recolor to the brand dark */
[data-baseweb="base-input"],[data-baseweb="input"]{ background:transparent!important; }
[data-testid="stSelectbox"] [data-baseweb="select"]>div:first-child{ background:rgba(17,21,15,.95)!important; }
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] ul[role="listbox"],
[data-baseweb="menu"] li{ background:#0d120b!important; }
[data-baseweb="menu"] li:hover{ background:rgba(146,206,83,.10)!important; }
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
/* LANDING — locked to the viewport (Grok-style): watermark fills the void,
   the card slide pins to the bottom just above the fixed composer. NO scroll. */
.sq-landing{ display:flex; flex-direction:column;
  height:calc(100vh - 150px); max-height:calc(100vh - 150px);
  overflow:hidden; padding-bottom:128px; box-sizing:border-box; }
/* lock EVERY scroll ancestor while the landing is shown — only the chat scrolls */
[data-testid="stMainBlockContainer"]:has(.sq-landing),
.block-container:has(.sq-landing),
section.main:has(.sq-landing),
[data-testid="stAppViewContainer"]:has(.sq-landing){ overflow:hidden !important; }
/* the faint, softly-pulsing centre mark (the calm void) */
.sq-wm{ flex:1 1 auto; min-height:0; display:flex; flex-direction:column;
  align-items:center; justify-content:center; text-align:center; gap:20px; }
.sq-wm-mark{ font-size:92px; line-height:1; color:var(--lime); opacity:.14;
  text-shadow:0 0 50px rgba(146,206,83,.55); animation:wmPulse 4.5s ease-in-out infinite; }
@keyframes wmPulse{ 0%,100%{opacity:.11;transform:scale(1);} 50%{opacity:.2;transform:scale(1.04);} }
.sq-wm-sub{ font-family:'ppNeueMontreal',sans-serif; font-size:14px; color:var(--muted);
  max-width:330px; line-height:1.55; }
.sq-wm-sub b{ color:var(--lime); font-weight:600; }
/* top bar stays ONE row: wordmark left, hamburger icon right (never wraps) */
[data-testid="stHorizontalBlock"]:has(.st-key-home_brand){ flex-wrap:nowrap !important; align-items:center; }
[data-testid="stHorizontalBlock"]:has(.st-key-home_brand) [data-testid="stColumn"]{ min-width:0 !important; }
/* pin the hamburger to the header's right edge */
[data-testid="stPopover"]{ display:flex!important; justify-content:flex-end!important; }
/* thinking state — shown while waiting for the first LLM token */
.sq-thinking{ display:flex;align-items:center;gap:12px;padding-top:6px; }
.sq-thinking .sq-tl{ font-family:'IBM Plex Mono';font-size:11.5px;color:var(--muted);letter-spacing:.1em; }
.sq-thinking .dk-dots{ margin-left:0; }
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
/* ---- hamburger menu: nav + model + status collapsed into a popover -------- */
/* trigger = a quiet bordered terminal control (NOT the green CTA button) */
[data-testid="stPopover"] button,
[data-testid="stPopover"] button:hover,
[data-testid="stPopover"] button:focus,
[data-testid="stPopover"] button:active,
[data-testid="stPopover"] button[aria-expanded="true"]{
  background:transparent!important; border:none!important; box-shadow:none!important;
  outline:none!important; border-radius:8px!important; padding:0!important;
  width:44px!important; min-width:44px!important; height:44px!important; min-height:44px!important;
  display:flex!important; align-items:center!important; justify-content:center!important;
  font-size:0!important; letter-spacing:0!important; transform:none!important; position:relative; }
[data-testid="stPopover"] button{ color:var(--ink)!important; }
[data-testid="stPopover"] button:hover{ color:var(--lime)!important; }
/* a crisp, centred 3-bar hamburger drawn in CSS (no ☰ glyph, no border) */
[data-testid="stPopover"] button::before{
  content:""!important; width:22px; height:2px; border-radius:2px; background:currentColor;
  box-shadow:0 -6px 0 currentColor, 0 6px 0 currentColor; }
/* kill the default dropdown chevron — a clean ☰ icon only, Grok-style */
[data-testid="stPopover"] button [data-testid="stIconMaterial"],
[data-testid="stPopover"] button svg{ display:none!important; }
/* hide the ☰ text label entirely — the 3-bar icon is drawn via ::before */
[data-testid="stPopover"] button div[data-testid="stMarkdownContainer"],
[data-testid="stPopover"] button p{ display:none!important; }
/* the menu opens as a full-height SIDE DRAWER that slides in (native pattern) */
[data-testid="stPopoverBody"]{
  position:fixed!important; top:0!important; right:0!important; bottom:0!important; left:auto!important;
  width:82vw!important; max-width:340px!important; min-width:0!important;
  height:100vh!important; height:100dvh!important; max-height:100dvh!important;
  background:#0b0f08!important; border:none!important; border-left:1px solid var(--line)!important;
  border-radius:0!important; box-shadow:-24px 0 70px rgba(0,0,0,.65)!important;
  padding:74px 24px 32px!important; overflow-y:auto!important;
  animation:drawerIn .24s cubic-bezier(.2,.7,.2,1) both!important; }
@keyframes drawerIn{ from{transform:translateX(102%);} to{transform:translateX(0);} }
/* a dim scrim over the content behind the drawer */
[data-testid="stPopoverBody"]::after{
  content:""; position:fixed; top:0; bottom:0; left:0; right:min(82vw,340px);
  background:rgba(3,4,2,.55); pointer-events:none; z-index:-1;
  animation:scrimIn .24s ease both; }
@keyframes scrimIn{ from{opacity:0;} to{opacity:1;} }
/* bigger, tappable drawer nav rows */
[data-testid="stPopoverBody"] div[role="radiogroup"] label{ font-size:16px!important; padding:13px 12px!important; }
[data-testid="stPopoverBody"] .menu-sec{ font-size:11px; }
.menu-sec{ font-family:'IBM Plex Mono';font-size:10px;letter-spacing:.16em;color:var(--dim);
  text-transform:uppercase;margin:2px 2px 8px; }
.menu-sec.t{ margin-top:14px;border-top:1px solid var(--line);padding-top:14px; }
.menu-status{ font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);
  margin-top:14px;border-top:1px solid var(--line);padding-top:12px; }
.menu-status .on{ color:var(--lime); }
/* menu nav = full-width stacked rows; hover lights lime */
[data-testid="stPopover"] div[role="radiogroup"]{ flex-direction:column; gap:2px; align-items:stretch; }
[data-testid="stPopover"] div[role="radiogroup"] label{ width:100%; justify-content:flex-start;
  padding:8px 12px; border-radius:8px; margin:0; }
[data-testid="stPopover"] div[role="radiogroup"] label:hover{ background:rgba(146,206,83,.08); color:var(--lime); }
/* ============================================================================
   MOBILE-FIRST RESPONSIVE  —  the terminal collapses to a single-column phone UI.
   Desktop assumes a wide canvas (fixed-width cards, viewport-locked landing,
   multi-column grids); below 768px we unlock height, bleed cards to the edges,
   and stack every grid so nothing is clipped or crushed.
   ========================================================================== */
@media (max-width:768px){
  /* tighter gutters; leave room at the bottom for the fixed composer */
  [data-testid="stAppViewContainer"]>.main .block-container,
  [data-testid="stMainBlockContainer"], .block-container{ padding:.4rem .85rem 7rem!important; }
  /* ONLY the chat rail stacks on mobile. The header row and the composer's
     inner row stay inline — a global wrap was dropping the composer's send
     button to its own full-width line (the heavy, non-Grok composer). */
  [data-testid="stHorizontalBlock"]:has(.st-key-home_rail){ flex-wrap:wrap!important; row-gap:12px; }
  [data-testid="stHorizontalBlock"]:has(.st-key-home_rail) > [data-testid="stColumn"]{
    flex:1 1 100%!important; width:100%!important; min-width:100%!important; }
  [data-testid="stForm"] [data-testid="stHorizontalBlock"]{ flex-wrap:nowrap!important; }
  [data-testid="stForm"] [data-testid="stColumn"]{ min-width:0!important; }
  .dk-status, .dk-clock{ display:none; }       /* desktop-only chrome */
  /* LANDING — undo the viewport lock so the page scrolls naturally on a phone */
  /* landing locked to the dynamic viewport (dvh tracks mobile browser chrome) —
     watermark fills the void, slide pins above the composer, NO page scroll */
  .sq-landing{ height:calc(100dvh - 132px); max-height:calc(100dvh - 132px);
    overflow:hidden; padding-bottom:calc(134px + env(safe-area-inset-bottom)); }
  [data-testid="stMainBlockContainer"]:has(.sq-landing),
  .block-container:has(.sq-landing),
  section.main:has(.sq-landing),
  [data-testid="stAppViewContainer"]:has(.sq-landing){ overflow:hidden!important; }
  .sq-wm-mark{ font-size:72px; }
  .sq-wm-sub{ font-size:13px; max-width:280px; }
  .dk-sub{ font-size:13px; }
  .dk-filter{ display:none; }                 /* floating 'All Leagues' chip just clutters mobile */
  /* match cards — one near-full-width card per view, edge-to-edge, snap between them */
  .dk-strip{ gap:12px; scroll-snap-type:x mandatory;
    margin:0 -.85rem; padding:4px .85rem 14px; }
  .dk-card2{ flex:0 0 80vw; padding:14px 15px; }
  .dk-card{ padding:14px 14px 12px; }
  /* live ticker — slightly more compact */
  .dk-tick{ gap:10px; padding:7px 11px; margin-bottom:12px; }
  .dk-tick .lab{ font-size:10px; }
  .dk-mi .nm{ font-size:12px; } .dk-mi .sc{ font-size:13px; }
  /* fixed composer hugs the screen edges */
  [data-testid="stForm"]{ width:calc(100vw - 20px); bottom:10px; padding:11px 13px 10px!important; }
  [data-testid="stForm"] [data-testid="stTextInput"] input{ font-size:16px; }  /* ≥16px = no iOS zoom */
  /* CHAT — the rail stacks above the conversation; trim its bulk */
  .dk-rail{ padding:13px 14px; }
  .dk-bal .v{ font-size:21px; }
  .st-key-home_rail{ margin-bottom:6px; }
  .dk-chat{ padding:16px 15px; min-height:auto; border-radius:14px; }
  .dk-chat::after{ border-width:0 28px 28px 0; }
  .dk-txt{ font-size:14px; padding-top:3px; }
  .dk-bub{ max-width:86%; font-size:14px; }
  .dk-msg{ gap:10px; margin:16px 0; }
  .dk-av{ width:30px;height:30px;font-size:13px; }
  .dk-time{ margin-left:40px; }
  /* explainer grids collapse; the pipeline scrolls instead of crushing 6 nodes */
  .dk-thesis{ grid-template-columns:1fr; }
  .sq-kgrid.c4{ grid-template-columns:repeat(2,1fr); }
  .sq-kgrid.c3{ grid-template-columns:repeat(2,1fr); }
  .dk-flow{ overflow-x:auto; padding-bottom:8px; -webkit-overflow-scrolling:touch; }
  .fl-node{ flex:0 0 88px; } .fl-link{ flex:0 0 22px; }
  .dk-flowllm{ padding-left:0; } .fl-chip{ font-size:9.5px; }
  /* page headings + big numbers scale down */
  .sq-h{ font-size:23px; } .dk-teamrow .s{ font-size:30px; }
  .sq-card{ padding:15px 14px; }
  /* perf/calibration tables stay inside the screen */
  .sq-tbl{ font-size:12px; } .sq-tbl td,.sq-tbl th{ padding:9px 7px; }
  /* LaTeX blocks can overflow horizontally rather than blow out the layout */
  [data-testid="stMarkdownContainer"] .katex-display{ overflow-x:auto; overflow-y:hidden; }
  /* ---- NATIVE-APP POLISH ---------------------------------------------------
     hidden scrollbars, momentum scroll, iOS safe-area, ≥44px touch targets so
     the terminal reads like a native app rather than a shrunk desktop site. */
  .dk-strip{ scrollbar-width:none; -webkit-overflow-scrolling:touch; }
  .dk-strip::-webkit-scrollbar{ display:none; height:0; }
  .dk-flow{ scrollbar-width:none; } .dk-flow::-webkit-scrollbar{ display:none; }
  .sq-ruler{ display:none; }                  /* drop the desktop tick-ruler decor on mobile */
  /* the fixed composer + page bottom respect the iOS home indicator */
  [data-testid="stForm"]{ bottom:calc(10px + env(safe-area-inset-bottom)); }
  [data-testid="stAppViewContainer"]>.main .block-container,
  [data-testid="stMainBlockContainer"], .block-container{
    padding-bottom:calc(7rem + env(safe-area-inset-bottom))!important; }
  /* comfortable native touch targets */
  [data-testid="stPopover"] button{ width:44px!important; height:44px!important; min-height:44px!important; }
  [data-testid="stForm"] [data-testid="stFormSubmitButton"]>button{ min-height:46px!important; }
  .dk-askbtn{ min-height:42px; display:inline-flex; align-items:center; }
  [data-testid="stPopover"] div[role="radiogroup"] label{ min-height:44px; }
  .st-key-home_brand button{ min-height:40px; }
}
@media (max-width:430px){
  .dk-hero{ font-size:18px; }
  .dk-card2{ flex:0 0 88vw; }
  .sq-kgrid.c4,.sq-kgrid.c3{ grid-template-columns:1fr; }
  .sq-h{ font-size:21px; }
}
</style>
"""
    # Streamlit/markdown ends an HTML block at the first blank line — which would dump
    # the rest of the CSS as visible text. Strip blank lines so the <style> stays intact.
    html = "\n".join(line for line in html.splitlines() if line.strip())
    # embed the real Brand fonts (Kensmark + PP Neue Montreal) right after <style>
    html = html.replace("<style>", "<style>" + fonts_data.FONT_CSS, 1)
    html = html.replace("__FAVICON__", _FAVICON, 1)
    st.markdown(html, unsafe_allow_html=True)


def money(v: float, *, sign: bool = False, dollar: bool = True) -> str:
    return f"{'+' if sign and v > 0 else ''}{'-' if v < 0 else ''}{'$' if dollar else ''}{abs(v):,.0f}"


def cls(v: float) -> str:
    return "pos" if v > 0 else ("neg" if v < 0 else "")


# ---- sidebar (the reference left rail) --------------------------------------------
def rail(brand: str, bankroll: str) -> str:
    return (
        f'<div class="dk-rail">'
        f'<div class="dk-brand"><div class="dk-mark">◆</div>'
        f'<div><b>{brand}</b><span>V0.1 · GOVERNED</span></div></div>'
        f'<div class="dk-row"><span class="k">Session</span><span class="v">SQ · PAPER</span></div>'
        f'<div class="dk-bal"><div class="l">Paper Bankroll</div><div class="v">${bankroll}</div></div>'
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
        f'<span class="s">{f["model_p"]*100:.0f}<span class="pct">%</span></span></div>'
        f'<div class="dk-teamrow"><span class="dk-tm">{_badge(away, f.get("away_badge"))}'
        f'<span class="t">{away}</span></span>'
        f'<span class="s">{(1-f["model_p"])*100:.0f}<span class="pct">%</span></span></div>'
        f'<div class="dk-prog"><i style="width:{fill:.0f}%"></i></div>'
        f'<div class="dk-meta"><div class="m"><span class="dot"></span><b>START:</b> {f["start"]}<br>'
        f'<b>STADIUM:</b> {f["venue"]}<br><b>MODEL:</b> {f["confidence"]*100:.0f}% conf</div>'
        f'<div class="dk-edge">+{edge_pct:.1f}% EV</div></div></div>'
    )


def card_head(f: dict, edge_pct: float) -> str:
    """Top of a match card: category, two team rows (logo + name + big green number), edge bar."""
    home, _, away = f["event"].partition(" vs ")
    fill = min(100, max(8, edge_pct * 9))
    return (
        f'<div class="dk-cardtop"><div class="lg">{f["category"]}</div>'
        f'<div class="dk-teamrow"><span class="dk-tm">{_badge(home, f.get("home_badge"))}'
        f'<span class="t">{home}</span></span>'
        f'<span class="s">{f["model_p"]*100:.0f}<span class="pct">%</span></span></div>'
        f'<div class="dk-teamrow"><span class="dk-tm">{_badge(away, f.get("away_badge"))}'
        f'<span class="t">{away}</span></span>'
        f'<span class="s">{(1-f["model_p"])*100:.0f}<span class="pct">%</span></span></div>'
        f'<div class="dk-prog"><i style="width:{fill:.0f}%"></i></div></div>'
    )


def card_foot(f: dict) -> str:
    """Bottom-left of a match card: START / STADIUM / TIME, mono with green values (the source layout)."""
    return (f'<div class="dk-foot3"><div><b>START:</b> <span class="v">{f["start"]}</span></div>'
            f'<div><b>STADIUM:</b> <span class="v">{f["venue"]}</span></div>'
            f'<div><b>TIME:</b> <span class="v">PRE-MATCH</span></div></div>')


def card(f: dict, edge_pct: float) -> str:
    """A full match card with the inline 'Ask' button (a ?ask= link, so it works inside HTML)."""
    href = "?ask=" + urllib.parse.quote(f["event"])
    return (f'<div class="dk-card2">{card_head(f, edge_pct)}'
            f'<div class="dk-cfoot">{card_foot(f)}'
            f'<div class="dk-cbtn"><div class="dk-evtag">+{edge_pct:.1f}% EV</div>'
            f'<a class="dk-askbtn" target="_self" href="{href}">Ask the model</a></div></div></div>')


def card_strip(cards_html: str) -> str:
    """The horizontally-scrolling strip the cards live in (a carousel, matches the source)."""
    return f'<div class="dk-strip">{cards_html}</div>'


def scrubber() -> str:
    """The tick-ruler decor that sits between the scrolling cards and the composer."""
    return '<div class="sq-ruler"><span class="mk">[ ]</span></div>'


def landing_hero() -> str:
    """Grok-style calm centre: a large faint, softly-pulsing brand mark and one
    muted line of value prop — fills the void between the top bar and the slide."""
    return ('<div class="sq-wm"><div class="sq-wm-mark">◆</div>'
            '<div class="sq-wm-sub">Ask the engine for a <b>+EV edge</b> — '
            'the deterministic gate decides the bet.</div></div>')


# ---- chat bubbles ----------------------------------------------------------
def user_msg(text: str, ts: str = "") -> str:
    # no avatar on the user side — a clean right-aligned bubble (asymmetric, only the engine is marked).
    t = f'<div class="dk-time u">{ts}</div>' if ts else ""
    return f'<div class="dk-msg u"><div class="dk-bub">{text}</div></div>{t}'


def engine_msg(body_html: str, ts: str = "") -> str:
    t = f'<div class="dk-time">{ts}</div>' if ts else ""
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
            '<div class="ft-brand"><span class="ft-dot"></span><b>Sport Quant</b>'
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
