"""Quantitative scoring core — the base logic, NOT an LLM.

Team strength ratings → Elo win probability. This is where the probability comes from:
a deterministic rating model, computed in the backend. The LLM never produces the number —
it only explains the numbers this module + engine.py (edge, fractional Kelly, the gate) produce.

P(A beats B) = 1 / (1 + 10 ** ((R_B - R_A) / 400))   (+ home advantage when not neutral)
"""
from __future__ import annotations

# Approx strength ratings (Elo-scale) for the demo's fixtures. Real systems fit these from
# results + xG; here they're a static table so the math is reproducible and honest.
TEAM_RATINGS = {
    "Brazil": 2030, "Argentina": 2055, "France": 2010, "Spain": 1995, "England": 1955,
    "Germany": 1965, "Portugal": 1935, "Netherlands": 1925, "Belgium": 1915, "Italy": 1910,
    "Croatia": 1860, "Uruguay": 1855, "Colombia": 1840, "Morocco": 1815, "USA": 1775,
    "Mexico": 1760, "Japan": 1790, "South Korea": 1745, "Senegal": 1760, "Switzerland": 1790,
    "Denmark": 1800, "Australia": 1715, "Canada": 1705, "Czech Republic": 1725, "Sweden": 1740,
    "Poland": 1745, "Ecuador": 1735, "Paraguay": 1700, "South Africa": 1665, "Tunisia": 1690,
    "Nigeria": 1745, "Ghana": 1690, "Bosnia-Herzegovina": 1700, "Curaçao": 1500, "Curacao": 1500,
    "Cape Verde": 1530, "Jordan": 1560, "Panama": 1610, "Costa Rica": 1640, "Egypt": 1700,
    "Turkey": 1780, "Türkiye": 1780, "Norway": 1760, "Spirit": 1700, "Vitality": 1720,
}
DEFAULT_RATING = 1655
HOME_ADV = 55


def rating(team: str) -> float:
    return float(TEAM_RATINGS.get(team, DEFAULT_RATING))


def win_prob(home: str, away: str, neutral: bool = True) -> float:
    """Elo model — P(home wins) from the rating gap (+ home advantage if not neutral)."""
    adv = 0.0 if neutral else HOME_ADV
    diff = rating(home) - rating(away) + adv
    return 1.0 / (1.0 + 10.0 ** (-diff / 400.0))


# ---------------------------------------------------------------------------
# Dixon–Coles model (bivariate Poisson on goals) — the second base model.
# Expected goals come from each team's attack/defence strength; the joint score
# distribution is corrected for low scores (the Dixon–Coles tau term, ρ).
# ---------------------------------------------------------------------------
import math

MU_HOME, MU_AWAY, RHO = 1.36, 1.12, -0.06   # base goal rates + low-score dependence


def _strength(team: str) -> tuple[float, float]:
    """Map a rating to (attack, defence) multipliers on the expected-goals scale."""
    s = (rating(team) - 1700.0) / 300.0      # standardized strength
    return math.exp(0.34 * s), math.exp(-0.30 * s)   # attack>1 / defence<1 for strong sides


def _pois(k: int, lam: float) -> float:
    return math.exp(-lam) * lam ** k / math.factorial(k)


def _tau(x: int, y: int, lam: float, mu: float, rho: float) -> float:
    if x == 0 and y == 0:
        return 1.0 - lam * mu * rho
    if x == 0 and y == 1:
        return 1.0 + lam * rho
    if x == 1 and y == 0:
        return 1.0 + mu * rho
    if x == 1 and y == 1:
        return 1.0 - rho
    return 1.0


def dixon_coles(home: str, away: str, max_goals: int = 8) -> tuple[float, float, float]:
    """Return (P_home, P_draw, P_away) from the Dixon–Coles bivariate Poisson."""
    a_h, d_h = _strength(home)
    a_a, d_a = _strength(away)
    lam = MU_HOME * a_h * d_a    # home expected goals
    mu = MU_AWAY * a_a * d_h     # away expected goals
    ph = pd = pa = 0.0
    for x in range(max_goals + 1):
        for y in range(max_goals + 1):
            p = _tau(x, y, lam, mu, RHO) * _pois(x, lam) * _pois(y, mu)
            ph += p if x > y else 0.0
            pd += p if x == y else 0.0
            pa += p if x < y else 0.0
    t = ph + pd + pa
    return ph / t, pd / t, pa / t


# meta-ensemble weights (Dixon–Coles goals model + Elo ratings model)
W_DC, W_ELO = 0.6, 0.4


def ensemble_prob(home: str, away: str) -> float:
    """meta-ensemble P(home wins): blend Dixon–Coles and Elo."""
    p_dc = dixon_coles(home, away)[0]
    p_elo = win_prob(home, away)
    return W_DC * p_dc + W_ELO * p_elo


if __name__ == "__main__":
    for h, a in [("Brazil", "Morocco"), ("Germany", "Curaçao"), ("USA", "Paraguay")]:
        dc = dixon_coles(h, a)
        print(f"{h} vs {a}: DC(h/d/a)={tuple(round(x,3) for x in dc)} "
              f"Elo={win_prob(h,a):.3f} ensemble={ensemble_prob(h,a):.3f}")
