"""Design system for sport-quant — a clean, high-level dark dashboard modelled on the
reference αVault UI (de-crypto'd). Dark fintech/terminal aesthetic: near-black canvas,
lifted panels, hairline borders, tabular-mono numbers, green/red P&L, one white CTA.

All visual primitives live here so app.py stays compositional.
"""
from __future__ import annotations

import streamlit as st

# ---- palette ---------------------------------------------------------------
BG      = "#0A0C0F"   # canvas, near-black
PANEL   = "#131619"   # card surface
PANEL2  = "#181C21"   # inset / nested surface
LINE    = "#23282E"   # hairline border
INK     = "#E9ECEF"   # primary text
MUTED   = "#8B929B"   # labels / secondary
DIM     = "#5A616A"   # tertiary
POS     = "#2FE6A8"   # gains (green)
NEG     = "#FF5B6B"   # losses (red)
ACCENT  = "#2FE6A8"   # brand accent
WARN    = "#E7B24B"   # amber


def inject_css() -> None:
    html = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0A0C0F; --panel:#131619; --panel2:#181C21; --line:#23282E;
  --ink:#E9ECEF; --muted:#8B929B; --dim:#5A616A; --pos:#2FE6A8; --neg:#FF5B6B; --accent:#2FE6A8;
}
html,body,[class*="css"]{ font-family:'IBM Plex Sans',sans-serif; }
.stApp{ background:var(--bg); color:var(--ink); }
#MainMenu,header[data-testid="stHeader"],footer{ display:none!important; }
[data-testid="stAppViewContainer"]>.main .block-container{ padding:1.1rem 1.4rem 4rem; max-width:1180px; }
[data-testid="stSidebar"]{ background:#0C0F12; border-right:1px solid var(--line); }
[data-testid="stSidebar"] *{ color:var(--ink); }
.num{ font-family:'IBM Plex Mono',monospace; font-variant-numeric:tabular-nums; }
.pos{ color:var(--pos); } .neg{ color:var(--neg); }

/* top bar */
.sq-top{ display:flex; align-items:center; gap:14px; padding:2px 2px 14px; border-bottom:1px solid var(--line); margin-bottom:16px; }
.sq-logo{ width:30px;height:30px;border-radius:8px;background:var(--ink);color:#0A0C0F;display:grid;place-items:center;
          font-family:'Archivo';font-weight:900;font-size:18px;transform:skewX(-6deg); }
.sq-brand{ font-family:'Archivo';font-weight:800;font-size:18px;letter-spacing:-.02em; }
.sq-pill{ font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);border:1px solid var(--line);
          border-radius:999px;padding:4px 11px;letter-spacing:.04em; }
.sq-pill b{ color:var(--accent); font-weight:600; }
.sq-spacer{ margin-left:auto; }
.sq-chip{ font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);border:1px solid var(--line);
          border-radius:7px;padding:5px 10px; }

/* section heads */
.sq-h{ font-family:'Archivo';font-weight:800;font-size:26px;letter-spacing:-.02em;margin:2px 0 2px; }
.sq-kick{ font-family:'IBM Plex Mono';font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--dim); }

/* cards */
.sq-card{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:18px 18px; }
.sq-card .cap{ font-size:13px;color:var(--muted);font-weight:500;margin-bottom:14px; }

/* KPI cells */
.sq-kgrid{ display:grid; gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.sq-kgrid.c4{ grid-template-columns:repeat(4,1fr); } .sq-kgrid.c3{ grid-template-columns:repeat(3,1fr); }
.sq-k{ background:var(--panel); padding:14px 15px; }
.sq-k .l{ font-size:11px;color:var(--muted);letter-spacing:.04em;margin-bottom:7px;display:flex;gap:5px;align-items:center; }
.sq-k .v{ font-family:'IBM Plex Mono';font-weight:600;font-size:21px;letter-spacing:-.01em; }

/* tabs (segmented) */
.sq-seg{ display:inline-flex; background:var(--panel2); border:1px solid var(--line); border-radius:9px; padding:3px; gap:3px; }
.sq-seg .s{ font-size:13px;color:var(--muted);padding:6px 16px;border-radius:7px;font-weight:500; }
.sq-seg .s.on{ background:#262C32;color:var(--ink); }

/* table */
.sq-tbl{ width:100%; border-collapse:collapse; font-size:13px; }
.sq-tbl th{ text-align:right;font-weight:500;font-size:11px;color:var(--muted);letter-spacing:.03em;
            padding:10px 12px;border-bottom:1px solid var(--line); }
.sq-tbl th:first-child,.sq-tbl td:first-child{ text-align:left; }
.sq-tbl td{ padding:13px 12px;border-bottom:1px solid #1A1E23;font-family:'IBM Plex Mono';
            font-variant-numeric:tabular-nums;text-align:right;color:var(--ink); }
.sq-tbl tr:hover td{ background:#15191E; }
.sq-ev{ font-family:'IBM Plex Sans';font-weight:500; }
.sq-cat{ font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);border:1px solid var(--line);
         border-radius:6px;padding:2px 8px; }
.sq-bar{ display:inline-block;height:4px;border-radius:2px;vertical-align:middle;margin-left:8px; }

/* signal card (telegram-style) */
.sq-sig{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:15px 16px; }
.sq-sig .hd{ font-family:'Archivo';font-weight:700;font-size:13px;color:var(--accent);letter-spacing:.02em; }
.sq-sig .sub{ font-family:'IBM Plex Mono';font-size:11px;color:var(--dim);letter-spacing:.1em;margin-bottom:10px; }
.sq-sig .row{ display:flex;justify-content:space-between;font-size:13px;padding:3px 0; }
.sq-sig .row .k{ color:var(--muted); } .sq-sig .row .v{ font-family:'IBM Plex Mono'; }

/* pipeline strip */
.sq-pipe{ display:flex; align-items:stretch; gap:0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.sq-stage{ flex:1; padding:13px 16px; background:var(--panel); border-right:1px solid var(--line); }
.sq-stage:last-child{ border-right:none; }
.sq-stage .n{ font-family:'IBM Plex Mono';font-size:10px;color:var(--dim);letter-spacing:.14em; }
.sq-stage .t{ font-family:'Archivo';font-weight:700;font-size:14px;margin-top:3px; }
.sq-stage.on{ background:#10231C; } .sq-stage.on .t{ color:var(--accent); }

/* gate verdict + checklist */
.sq-verdict{ font-family:'Archivo';font-weight:900;font-size:15px;letter-spacing:.05em;padding:7px 14px;border-radius:8px;display:inline-block; }
.sq-verdict.ok{ background:#10231C;color:var(--pos);border:1px solid #1d4a3a; }
.sq-verdict.no{ background:#2a1418;color:var(--neg);border:1px solid #4a1d24; }
.sq-check{ font-family:'IBM Plex Mono';font-size:12px;padding:5px 0;border-bottom:1px solid #1A1E23;display:flex;gap:8px; }

/* CTA */
.sq-cta{ background:var(--ink);color:#0A0C0F;font-family:'Archivo';font-weight:700;font-size:13px;
         text-align:center;padding:11px;border-radius:9px; }
.sq-foot{ font-size:11px;color:var(--dim);margin-top:8px; }

/* live score ticker */
.sq-ticker{ display:flex; align-items:center; gap:14px; background:#0C0F12; border:1px solid var(--line);
            border-radius:10px; padding:8px 12px; overflow:hidden; margin-bottom:14px; }
.tk-lab{ font-family:'IBM Plex Mono';font-size:11px;color:var(--pos);letter-spacing:.1em;white-space:nowrap;flex:none; }
.tk-track{ display:flex; gap:30px; white-space:nowrap; animation:tk 38s linear infinite; }
.tk-i{ font-size:13px;color:var(--muted); } .tk-i b{ color:var(--ink);font-weight:600; }
.tk-i i{ color:var(--pos);font-style:normal;font-family:'IBM Plex Mono';font-size:11px;margin-left:6px; }
@keyframes tk{ from{transform:translateX(0);} to{transform:translateX(-50%);} }

/* match card (the +EV scanner) */
.sq-match{ position:relative; background:var(--panel); border:1px solid var(--line); border-radius:13px;
           padding:15px 16px 14px; overflow:hidden; height:100%; }
.sq-match::after{ content:""; position:absolute; top:0; right:0; border-width:0 26px 26px 0;
                  border-style:solid; border-color:transparent var(--accent) transparent transparent; opacity:.9; }
.sq-match .lg{ font-family:'IBM Plex Mono';font-size:10px;color:var(--dim);letter-spacing:.12em; }
.sq-match .tm{ font-family:'Archivo';font-weight:700;font-size:15px;line-height:1.32;margin:6px 0 10px; }
.sq-match .mt{ display:flex;justify-content:space-between;font-family:'IBM Plex Mono';font-size:11px;color:var(--muted);
               border-top:1px solid #1A1E23;padding-top:9px; }
.sq-match .ed{ color:var(--pos); }

/* chat thread */
.sq-msg{ display:flex; gap:11px; margin:14px 0; }
.sq-av{ width:30px;height:30px;border-radius:8px;flex:none;display:grid;place-items:center;
        font-family:'Archivo';font-weight:800;font-size:13px; }
.sq-av.u{ background:#1c2228;color:var(--muted); } .sq-av.a{ background:var(--ink);color:#0A0C0F;transform:skewX(-6deg); }
.sq-bub{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:13px 15px; max-width:90%; }
.sq-bub.u{ background:#15191E; color:var(--muted); }
.sq-bub .rsn{ font-size:13.5px; line-height:1.55; color:var(--ink); }
.sq-bub .rec{ font-family:'IBM Plex Mono';font-size:12.5px;margin-top:10px;color:var(--muted); }
.sq-bub .rec b{ color:var(--ink); } .sq-bub .rec .pos{ color:var(--pos); }
.sq-reasons{ margin-top:11px;border-top:1px solid #1A1E23;padding-top:9px; }
hr{ border-color:var(--line); }
</style>
"""
    # Streamlit/markdown ends an HTML block at the first blank line — which would dump
    # the rest of the CSS as visible text. Strip blank lines so the <style> stays intact.
    html = "\n".join(line for line in html.splitlines() if line.strip())
    st.markdown(html, unsafe_allow_html=True)


def money(v: float, *, sign: bool = False, dollar: bool = True) -> str:
    s = f"{'+' if sign and v > 0 else ''}{'-' if v < 0 else ''}{'$' if dollar else ''}{abs(v):,.0f}"
    return s


def cls(v: float) -> str:
    return "pos" if v > 0 else ("neg" if v < 0 else "")


def topbar(brand: str, regime: str = "live") -> None:
    st.markdown(
        f"""<div class="sq-top">
        <div class="sq-logo">▚</div>
        <div class="sq-brand">{brand}</div>
        <span class="sq-pill">AIoT&nbsp; <b>sense → fuse → gate → act</b></span>
        <span class="sq-spacer"></span>
        <span class="sq-chip">policy v1.3</span>
        <span class="sq-chip">recorded scenario · {regime}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def kpi(label: str, value_html: str, *, icon: str = "") -> str:
    ic = f'<span style="color:#5A616A">{icon}</span>' if icon else ""
    return f'<div class="sq-k"><div class="l">{ic}{label}</div><div class="v">{value_html}</div></div>'


def kpi_grid(cells: list[str], cols: int = 4) -> str:
    return f'<div class="sq-kgrid c{cols}">{"".join(cells)}</div>'


def segmented(options: list[str], active: str) -> str:
    segs = "".join(f'<span class="s {"on" if o == active else ""}">{o}</span>' for o in options)
    return f'<div class="sq-seg">{segs}</div>'


def ticker(scores: list[dict]) -> str:
    items = "".join(
        f'<span class="tk-i"><b>{s["home"]}</b> {s["hs"]}–{s["as_"]} <b>{s["away"]}</b>'
        f'<i>{s["min"]}\'</i></span>'
        for s in scores
    )
    return (f'<div class="sq-ticker"><span class="tk-lab">● LIVE SCORES</span>'
            f'<div class="tk-track">{items}{items}</div></div>')


def match_card(f: dict, edge_pct: float) -> str:
    home_away = f["event"].replace(" vs ", "<br>vs ")
    return (f'<div class="sq-match"><div class="lg">{f["category"]}</div>'
            f'<div class="tm">{home_away}</div>'
            f'<div class="mt"><span>{f["start"]} · {f["venue"]}</span>'
            f'<span class="ed">+{edge_pct:.1f}% edge</span></div></div>')


def user_msg(text: str) -> str:
    return (f'<div class="sq-msg" style="flex-direction:row-reverse">'
            f'<div class="sq-av u">YOU</div>'
            f'<div class="sq-bub u">{text}</div></div>')


def engine_msg(body_html: str) -> str:
    return (f'<div class="sq-msg"><div class="sq-av a">▚</div>'
            f'<div class="sq-bub">{body_html}</div></div>')

