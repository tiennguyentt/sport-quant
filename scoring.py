# scoring.py
import math
import numpy as np


def _binary_inputs(p, o):
    probabilities = np.asarray(p, dtype=float)
    outcomes = np.asarray(o, dtype=float)
    probabilities, outcomes = np.broadcast_arrays(probabilities, outcomes)

    if probabilities.size == 0:
        raise ValueError("inputs must be non-empty")
    if not np.all(np.isfinite(probabilities)) or not np.all(np.isfinite(outcomes)):
        raise ValueError("inputs must be finite")
    if np.any((probabilities < 0.0) | (probabilities > 1.0)):
        raise ValueError("probabilities must be in [0, 1]")
    if np.any((outcomes != 0.0) & (outcomes != 1.0)):
        raise ValueError("outcomes must be binary")
    return probabilities.ravel(), outcomes.ravel()


def brier(p, o) -> float:
    """Return mean squared probability error for binary outcomes."""
    probabilities, outcomes = _binary_inputs(p, o)
    return float(np.mean((probabilities - outcomes) ** 2))


def log_loss(p, o, eps=1e-15) -> float:
    """Return clipped binary logarithmic loss."""
    probabilities, outcomes = _binary_inputs(p, o)
    if not 0.0 < eps < 0.5:
        raise ValueError("eps must be in (0, 0.5)")
    probabilities = np.clip(probabilities, eps, 1.0 - eps)
    loss = outcomes * np.log(probabilities)
    loss += (1.0 - outcomes) * np.log1p(-probabilities)
    return float(-np.mean(loss))


def rps_1x2(probs, outcome_idx) -> float:
    """Return mean ranked probability score for three ordered outcomes."""
    probabilities = np.asarray(probs, dtype=float)
    single = probabilities.ndim == 1
    if single:
        probabilities = probabilities.reshape(1, -1)
    if probabilities.ndim != 2 or probabilities.shape[1] != 3:
        raise ValueError("probs must have shape (3,) or (n, 3)")
    if not np.all(np.isfinite(probabilities)):
        raise ValueError("probabilities must be finite")
    if np.any((probabilities < 0.0) | (probabilities > 1.0)):
        raise ValueError("probabilities must be in [0, 1]")
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-9):
        raise ValueError("each probability row must sum to one")

    raw_outcomes = np.asarray(outcome_idx)
    if raw_outcomes.ndim == 0:
        raw_outcomes = np.full(probabilities.shape[0], raw_outcomes.item())
    raw_outcomes = raw_outcomes.ravel()
    if raw_outcomes.size != probabilities.shape[0]:
        raise ValueError("one outcome index is required per probability row")
    if not np.all(np.equal(raw_outcomes, np.floor(raw_outcomes))):
        raise ValueError("outcome indices must be integers")

    outcomes = raw_outcomes.astype(int)
    if np.any((outcomes < 0) | (outcomes > 2)):
        raise ValueError("outcome indices must be 0, 1, or 2")

    observed = np.eye(3, dtype=float)[outcomes]
    forecast_cdf = np.cumsum(probabilities, axis=1)[:, :-1]
    observed_cdf = np.cumsum(observed, axis=1)[:, :-1]
    return float(np.mean(np.sum((forecast_cdf - observed_cdf) ** 2, axis=1) / 2.0))


def reliability_bins(p, o, bins=10) -> list:
    """Return mean confidence, empirical accuracy, and count per non-empty bin."""
    probabilities, outcomes = _binary_inputs(p, o)
    if not isinstance(bins, int) or bins <= 0:
        raise ValueError("bins must be a positive integer")

    indices = np.minimum((probabilities * bins).astype(int), bins - 1)
    result = []
    for index in range(bins):
        mask = indices == index
        count = int(np.sum(mask))
        if count:
            result.append(
                (
                    float(np.mean(probabilities[mask])),
                    float(np.mean(outcomes[mask])),
                    count,
                )
            )
    return result


def ece(p, o, bins=10) -> float:
    """Return expected calibration error using equal-width bins."""
    probabilities, outcomes = _binary_inputs(p, o)
    total = probabilities.size
    return float(
        sum(
            count / total * abs(confidence - accuracy)
            for confidence, accuracy, count in reliability_bins(
                probabilities, outcomes, bins
            )
        )
    )


def clv(odds_bet, odds_close) -> float:
    """Return closing-line value using decimal odds."""
    odds_bet = float(odds_bet)
    odds_close = float(odds_close)
    if (
        not math.isfinite(odds_bet)
        or not math.isfinite(odds_close)
        or odds_bet <= 0.0
        or odds_close <= 0.0
    ):
        raise ValueError("odds must be positive and finite")
    return odds_bet / odds_close - 1.0


def roi_with_ci(pnls, stakes, z=1.96) -> dict:
    """Return stake-weighted ROI and a normal-approximation confidence interval."""
    profits = np.asarray(pnls, dtype=float).ravel()
    amounts = np.asarray(stakes, dtype=float).ravel()
    z = float(z)

    if profits.size == 0 or profits.shape != amounts.shape:
        raise ValueError("pnls and stakes must be equal-length non-empty arrays")
    if not np.all(np.isfinite(profits)) or not np.all(np.isfinite(amounts)):
        raise ValueError("pnls and stakes must be finite")
    if np.any(amounts <= 0.0):
        raise ValueError("stakes must be positive")
    if not math.isfinite(z) or z < 0.0:
        raise ValueError("z must be non-negative and finite")

    roi = float(np.sum(profits) / np.sum(amounts))
    if profits.size < 2:
        lo, hi = -math.inf, math.inf
    else:
        residuals = profits - roi * amounts
        variance = (
            profits.size
            / (profits.size - 1)
            * float(np.sum(residuals ** 2))
            / float(np.sum(amounts) ** 2)
        )
        standard_error = math.sqrt(max(0.0, variance))
        lo = roi - z * standard_error
        hi = roi + z * standard_error

    return {
        "roi": roi,
        "lo": float(lo),
        "hi": float(hi),
        "significant": bool(lo > 0.0 or hi < 0.0),
    }


def verdict(brier_v, brier_base, mean_clv, roi_lo) -> dict:
    """Summarize calibration, market advantage, and proven profitability."""
    calibrated = float(brier_v) < float(brier_base)
    beats_market = float(mean_clv) > 0.0
    profitable = float(roi_lo) > 0.0
    return {
        "calibrated": calibrated,
        "beats_market": beats_market,
        "profitable": profitable,
        "edge_is_real": calibrated and beats_market and profitable,
    }
