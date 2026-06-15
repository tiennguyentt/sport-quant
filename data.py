# data.py — synthetic, deterministic data for the sport-quant demo.
# No crypto, no live calls. Fixtures, live-score ticker, grounded reasonings, and a
# precomputed recorded run so the app loads instantly.
from __future__ import annotations

import json
import random
import urllib.request

import model

# --- live score ticker (top marquee), mirrors the reference terminal --------
LIVE_SCORES = [
    {"home": "Tottenham", "away": "Arsenal", "hs": 1, "as_": 0, "min": 63},
    {"home": "Real Madrid", "away": "FC Barcelona", "hs": 3, "as_": 1, "min": 89},
    {"home": "Chelsea", "away": "Manchester City", "hs": 0, "as_": 0, "min": 13},
    {"home": "Bayern München", "away": "Werder Bremen", "hs": 2, "as_": 0, "min": 71},
    {"home": "Inter", "away": "Napoli", "hs": 1, "as_": 1, "min": 45},
]

# --- the +EV scanner fixtures (the cards you can "ask" about) ----------------
# Each is a candidate the engine + gate evaluate. A deliberate mix of pass / fail
# so the terminal can show governed APPROVALS and honest REJECTIONS.
FIXTURES = [
    # event, category, selection, model_p, market_p, odds, confidence, ci_width, sources, venue, start
    ("Bruins vs Maple Leafs", "NHL", "Bruins ML", 0.585, 0.523, 1.96, 0.71, 0.12, ["vision", "elo", "xg"], "TD Garden", "7:00 PM"),
    ("Mallorca vs Getafe", "LaLiga", "Under 2.5", 0.612, 0.548, 1.92, 0.69, 0.13, ["vision", "xg", "market"], "Son Moix", "8:30 PM"),
    ("Blazers vs Mavericks", "NBA", "Mavericks -4.5", 0.566, 0.515, 2.02, 0.66, 0.15, ["elo", "xg", "market"], "Moda Center", "9:00 PM"),
    ("Seahawks vs Commanders", "NFL", "Seahawks ML", 0.498, 0.512, 1.98, 0.55, 0.16, ["elo", "market"], "Lumen Field", "1:00 PM"),
    ("Dota2: Xtreme Gaming vs MOUZ", "Dota 2", "Xtreme Gaming", 0.604, 0.541, 1.85, 0.72, 0.11, ["vision", "elo", "xg"], "BO3", "4:00 PM"),
    ("Bayern München vs Werder Bremen", "Bundesliga", "Bayern ML", 0.708, 0.642, 1.56, 0.74, 0.10, ["vision", "elo", "xg", "market"], "Allianz Arena", "6:30 PM"),
    ("Tottenham vs Manchester City", "EPL", "Man City ML", 0.561, 0.547, 1.83, 0.63, 0.14, ["elo", "xg"], "Tottenham Stadium", "11:30 AM"),
    # --- the honest rejections ---
    ("Inter vs Napoli", "Serie A", "Inter ML", 0.512, 0.503, 2.05, 0.58, 0.13, ["elo", "market"], "San Siro", "2:45 PM"),          # edge_too_small
    ("Lakers vs Suns", "NBA", "Over 224.5", 0.547, 0.498, 2.00, 0.49, 0.21, ["xg"], "Crypto.com Arena", "10:30 PM"),                # low_conf, ci_too_wide, weak sources
    ("PSG vs Lyon", "Ligue 1", "PSG -1.5", 0.631, 0.560, 1.78, 0.70, 0.12, ["vision", "elo", "xg"], "Parc des Princes", "9:00 PM"),  # pass
]

FIELDS = ("event", "category", "selection", "model_p", "market_p", "odds",
          "confidence", "ci_width", "sources", "venue", "start")


def fixtures() -> list[dict]:
    """Fixtures as plain dicts."""
    return [dict(zip(FIELDS, f)) for f in FIXTURES]


# --- grounded plain-language reasonings (recorded; no live LLM needed) -------
REASONINGS = {
    "Bruins vs Maple Leafs": "Vision packets show Boston controlling high-danger chances 5v5; "
        "Elo and xG agree the line is short. Model 58.5% vs market 52.3% → a 6.2pt edge on the moneyline.",
    "Mallorca vs Getafe": "Two low-xG sides at altitude; rolling xG and vision both point under. "
        "Model 61.2% on Under 2.5 vs 54.8% implied — a clean defensive-script edge.",
    "Blazers vs Mavericks": "Elo gap plus pace-adjusted xG favour Dallas covering -4.5. Edge is real "
        "but confidence is mid (0.66) and the interval is wide; sized small.",
    "Seahawks vs Commanders": "Sources disagree and the model lands below the market price — no edge. "
        "The terminal does not surface a bet here.",
    "Dota2: Xtreme Gaming vs MOUZ": "Vision draft-value model rates XG's lineup highly in BO3; "
        "Elo and xG concur. 60.4% vs 54.1% implied → strong, well-calibrated edge.",
    "Bayern München vs Werder Bremen": "The prediction strongly favours Bayern. All four sources align: "
        "vision, Elo, and xG put Bayern at 70.8% vs 64.2% implied. Bayern ML carries a 6.6pt edge; "
        "BTTS-no is the secondary value given Bayern's defensive xG. Avoid over 2.5 unless the price moves.",
    "Tottenham vs Manchester City": "City favoured but the edge is thin (1.4pt) on only two sources; "
        "below the gate's minimum edge — held back.",
    "Inter vs Napoli": "Marginal model lean, no real separation from the market. Gate refuses on edge.",
    "Lakers vs Suns": "Single noisy source, low confidence, wide interval. The gate fails this closed.",
    "PSG vs Lyon": "Vision and xG both back PSG to cover at home; 63.1% vs 56.0% implied — a sized, governed bet.",
}


# --- recorded run: settled paper bets + derived KPIs ------------------------
# The five reference events carry the realized PnL signs from the dashboard mock.
_REFERENCE_SETTLED = [
    ("Bruins vs Maple Leafs", "NHL", 1736.00, 1.96, 1, 3224),
    ("Mallorca vs Getafe", "LaLiga", 2914.56, 1.92, 1, 1968),
    ("Blazers vs Mavericks", "NBA", 1688.23, 2.02, 1, 1512),
    ("Seahawks vs Commanders", "NFL", 367.20, 1.98, 0, -367),
    ("Dota2: Xtreme Gaming vs MOUZ", "Dota 2", 1895.00, 1.85, 1, 2890),
]

_CATS = ["NHL", "NBA", "NFL", "LaLiga", "EPL", "Bundesliga", "Dota 2", "Serie A"]
_TEAMS = [
    "Rangers vs Devils", "Celtics vs Heat", "Bills vs Jets", "Sevilla vs Betis",
    "Arsenal vs Everton", "Dortmund vs Leipzig", "Spirit vs Vitality", "Roma vs Lazio",
    "Oilers vs Flames", "Nuggets vs Jazz", "Chiefs vs Raiders", "Atletico vs Villarreal",
    "Liverpool vs Brighton", "Leverkusen vs Mainz", "G2 vs Falcons", "Milan vs Torino",
]


def recorded_run(seed: int = 7) -> dict:
    rng = random.Random(seed)
    settled = []
    # pinned reference bets first
    for event, cat, stake, odds, outcome, pnl in _REFERENCE_SETTLED:
        model_p = round(1.0 / odds + rng.uniform(0.05, 0.09), 3)
        settled.append({
            "event": event, "category": cat, "stake": stake, "odds": odds,
            "outcome": outcome, "pnl": float(pnl), "realized_pnl": float(pnl),
            "odds_close": round(odds * (1.0 - rng.uniform(0.0, 0.05)), 3),
            "model_p": model_p,
        })
    # synthetic tail: ~55% win rate, positive ROI
    for i in range(35):
        event = rng.choice(_TEAMS)
        cat = rng.choice(_CATS)
        stake = round(rng.uniform(300, 3000), 2)
        odds = round(rng.uniform(1.55, 2.45), 2)
        model_p = round(1.0 / odds + rng.uniform(0.02, 0.10), 3)
        win = 1 if rng.random() < 0.55 else 0
        pnl = round(stake * (odds - 1.0), 2) if win else -stake
        odds_close = round(odds * (1.0 - rng.uniform(-0.02, 0.06)), 3)
        settled.append({
            "event": event, "category": cat, "stake": stake, "odds": odds,
            "outcome": win, "pnl": pnl, "realized_pnl": pnl,
            "odds_close": odds_close, "model_p": model_p,
        })

    gains = sum(s["pnl"] for s in settled if s["pnl"] > 0)
    losses = sum(s["pnl"] for s in settled if s["pnl"] < 0)
    wins = sum(1 for s in settled if s["outcome"] == 1)
    pnl = gains + losses
    deployed = round(sum(s["stake"] for s in settled[:6]), 2)
    pending = round(rng.uniform(2500, 4000), 2)

    curve, run = [], 0.0
    for s in settled:
        run += s["pnl"]
        curve.append(round(run, 2))

    kpis = {
        "pnl": round(pnl, 2),
        "total_gains": round(gains, 2),
        "total_losses": round(losses, 2),
        "win_rate": round(100.0 * wins / len(settled), 1),
        "deployed": deployed,
        "pending": pending,
        "n_bets": len(settled),
    }
    return {"settled": settled, "kpis": kpis, "pnl_curve": curve}


# ---------------------------------------------------------------------------
# REAL data: World Cup 2026 via TheSportsDB free API (no key). Fixtures, scores,
# and real team crest badges. Model probabilities stay illustrative (free APIs
# carry no betting odds). Falls back to the synthetic data above on any failure.
# ---------------------------------------------------------------------------
_API = "https://www.thesportsdb.com/api/v1/json/3"
WC_LEAGUE = "4429"  # FIFA World Cup


def _fetch(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "sport-quant/0.1"})
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.load(r)


def _pricing(home: str, away: str) -> dict:
    """Quant scoring for a fixture: the probability is COMPUTED by the rating model
    (model.win_prob), not invented. Market odds are synthetic (free API has no odds),
    so a small, deterministic mispricing is layered in to create real +EV / -EV cases."""
    model_p = model.ensemble_prob(home, away)          # <-- Dixon-Coles + Elo ensemble, not an LLM
    r = random.Random(sum(ord(c) for c in home + away))
    # an efficient-but-imperfect market: implied prob near the true prob, sometimes mispriced
    implied = min(0.93, max(0.07, model_p + r.uniform(-0.085, 0.045)))
    odds = round(1.0 / implied, 2)
    edge = model_p - 1.0 / odds
    return {
        "selection": f"{home} ML",
        "model_p": round(model_p, 3),
        "market_p": round(1.0 / odds, 3),
        "odds": odds,
        # confidence rises with rating separation; widest interval on coin-flips
        "confidence": round(min(0.85, 0.55 + abs(model_p - 0.5) * 0.7), 2),
        "ci_width": round(0.18 - abs(model_p - 0.5) * 0.18, 2),
        "sources": ["elo", "xg", "form"] if edge > 0 else ["elo", "market"],
    }


def _wc_events() -> list[dict]:
    """All real WC2026 events we can pull from the free tier, deduped."""
    evs, seen = [], set()
    for ep in (f"eventsnextleague.php?id={WC_LEAGUE}",
               f"eventsseason.php?id={WC_LEAGUE}&s=2026",
               f"eventspastleague.php?id={WC_LEAGUE}"):
        try:
            for e in (_fetch(f"{_API}/{ep}") or {}).get("events") or []:
                k = e.get("strEvent")
                if k and k not in seen and e.get("strHomeTeam") and e.get("strAwayTeam"):
                    seen.add(k)
                    evs.append(e)
        except Exception:
            continue
    return evs


def live_fixtures() -> list[dict] | None:
    evs = _wc_events()
    if not evs:
        return None
    out = []
    for e in evs[:8]:
        home, away = e["strHomeTeam"], e["strAwayTeam"]
        row = {"event": f"{home} vs {away}", "category": "World Cup 2026",
               "venue": e.get("strVenue") or "TBD",
               "start": (e.get("strTimestamp") or "")[11:16] or "TBD",
               "home_badge": e.get("strHomeTeamBadge"),
               "away_badge": e.get("strAwayTeamBadge")}
        row.update(_pricing(home, away))
        out.append(row)
    return out or None


def live_scores() -> list[dict] | None:
    evs = [e for e in _wc_events() if e.get("intHomeScore") is not None]
    if not evs:
        return None
    out = []
    for e in evs[:6]:
        out.append({"home": e["strHomeTeam"], "away": e["strAwayTeam"],
                    "hs": int(e.get("intHomeScore") or 0), "as_": int(e.get("intAwayScore") or 0),
                    "min": "FT",
                    "home_badge": e.get("strHomeTeamBadge"),
                    "away_badge": e.get("strAwayTeamBadge")})
    return out or None


if __name__ == "__main__":
    print(recorded_run()["kpis"])
    lf = live_fixtures()
    print("live WC2026 fixtures:", len(lf) if lf else "unavailable")

