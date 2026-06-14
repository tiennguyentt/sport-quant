# engine.py
from dataclasses import dataclass, field
import math
import random


@dataclass
class Candidate:
    event: str
    category: str
    selection: str
    model_p: float
    market_p: float
    odds: float
    confidence: float
    ci_width: float
    sources: list


@dataclass
class PortfolioState:
    bankroll: float = 100_000.0
    deployed_frac: float = 0.0
    open_events: set = field(default_factory=set)
    source_weights: dict = field(
        default_factory=lambda: {
            "vision": 1.0,
            "elo": 1.0,
            "xg": 1.0,
            "market": 1.0,
        }
    )


def edge(model_p, odds) -> float:
    """Return probability edge over the odds-implied probability."""
    return float(model_p) - 1.0 / float(odds)


def fractional_kelly(
    model_p,
    odds,
    bankroll,
    kelly_fraction=0.25,
    max_pos=0.01,
) -> float:
    """Return a non-negative, fractionally Kelly-sized currency stake."""
    p = float(model_p)
    decimal_odds = float(odds)
    capital = float(bankroll)

    if (
        not all(map(math.isfinite, (p, decimal_odds, capital)))
        or decimal_odds <= 1.0
        or capital <= 0.0
        or edge(p, decimal_odds) <= 0.0
    ):
        return 0.0

    b = decimal_odds - 1.0
    full_kelly = (b * p - (1.0 - p)) / b
    requested = capital * max(0.0, full_kelly * float(kelly_fraction))
    cap = capital * max(0.0, float(max_pos))
    return min(requested, cap)


def _unit_interval(value) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and 0.0 <= number <= 1.0


def gate_check(c: Candidate, st: PortfolioState) -> tuple[bool, list]:
    """Apply ordered, deterministic governance checks without mutation."""
    reasons = []

    valid_schema = (
        _unit_interval(c.model_p)
        and _unit_interval(c.market_p)
        and _unit_interval(c.confidence)
        and _unit_interval(c.ci_width)
        and isinstance(c.sources, list)
    )
    try:
        valid_schema = valid_schema and math.isfinite(float(c.odds)) and c.odds > 1.0
    except (TypeError, ValueError):
        valid_schema = False

    if not valid_schema:
        reasons.append("invalid_schema")

    sources = c.sources if isinstance(c.sources, list) else []
    if len(sources) < 2:
        reasons.append("insufficient_sources")

    if valid_schema and abs(c.model_p - c.market_p) < 0.022:
        reasons.append("diff_too_small")

    if valid_schema and c.confidence < 0.52:
        reasons.append("low_confidence")
    if valid_schema and c.ci_width > 0.19:
        reasons.append("ci_too_wide")

    if valid_schema and edge(c.model_p, c.odds) < 0.028:
        reasons.append("edge_too_small")

    if valid_schema and not 0.02 < c.model_p < 0.98:
        reasons.append("probability_anomaly")

    stake = (
        fractional_kelly(c.model_p, c.odds, st.bankroll)
        if valid_schema
        else 0.0
    )
    if st.bankroll <= 0.0 or stake > 0.01 * st.bankroll + 1e-12:
        reasons.append("position_cap")

    added_frac = stake / st.bankroll if st.bankroll > 0.0 else math.inf
    if st.deployed_frac + added_frac > 0.115 + 1e-12:
        reasons.append("deployed_cap")

    if c.event in st.open_events:
        reasons.append("event_concentration")

    weights = []
    for source in sources:
        try:
            weights.append(float(st.source_weights.get(source, 0.0)))
        except (TypeError, ValueError):
            weights.append(0.0)
    if not weights or min(weights) < 0.07:
        reasons.append("weak_source")

    return not reasons, reasons


if __name__ == "__main__":
    rng = random.Random(20260614)
    candidate = Candidate(
        event="ARS-MCI",
        category="football",
        selection="ARS",
        model_p=0.58 + rng.uniform(-0.005, 0.005),
        market_p=0.51,
        odds=2.05,
        confidence=0.71,
        ci_width=0.14,
        sources=["elo", "xg", "market"],
    )
    state = PortfolioState(deployed_frac=0.04)
    passed, failures = gate_check(candidate, state)
    print(
        {
            "event": candidate.event,
            "passed": passed,
            "fail_reasons": failures,
            "edge": round(edge(candidate.model_p, candidate.odds), 6),
            "stake": round(
                fractional_kelly(candidate.model_p, candidate.odds, state.bankroll),
                2,
            ),
        }
    )
