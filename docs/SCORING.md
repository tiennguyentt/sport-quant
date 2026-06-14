# Scoring & Accuracy — the core logic

*"How do we know the model's predictions are actually accurate?" This is the most important
logic in sport-quant. Generating a recommendation ("bet X, stake $Y") is commodity — any LLM
does it. Proving whether that recommendation has real edge is the IP, and the centerpiece of the
demo.*

> CALIBRATION METHOD (resolved from HF + SOTA research): **Venn-ABERS** (`pip install venn-abers`)
> — distribution-free, finite-sample calibration guarantee; outputs a probability **interval
> [p0,p1]**, so we size Kelly on the conservative `p0`. Conformal prediction (`MAPIE`) is used
> separately as a "skip ambiguous bets" gate, not as the scalar-p source.
> KEY HONEST TRUTH from the research: every public model still loses to **bookmaker closing odds**
> on calibration. So the market close is the benchmark to beat, and CLV (§3) is the proof.

---

## 0. The trap: win rate is the WRONG lens

A 50–60% win rate tells you almost nothing on its own, because it ignores the **odds**.
- At decimal odds 2.0 you need >50% to profit; at 3.0 you profit above 33%.
- Positive ROI with <50% win rate is the *normal* signature of selective +EV betting.

So "we were right ~50-60% of the time" is neither good nor bad. Accuracy must be measured by
**three independent lenses**, all required.

---

## 1. The prediction/bet record (the raw material)

Every prediction logs:

```
id, ts, sport, event, market, selection,
model_prob        p          # the model's P(win)
odds_at_bet       O_bet      # decimal odds we acted on
market_implied    q = 1/O_bet (de-vig where possible)
closing_odds      O_close    # final consensus odds at event start
stake, outcome    o ∈ {0,1}  # 1 = win
payout, pnl
confidence, ci_width
sources[]                    # packets that contributed
policy_version, gate_result
```

Everything below is derived from this log. No record → no claim.

---

## 2. Lens 1 — Calibration (is the probability honest?)

When the model says 62%, do ~62% actually win? This is what makes `p` trustworthy for Kelly
(Kelly assumes `p` is correct; miscalibration → over-bet → ruin).

- **Reliability diagram:** bin predictions (e.g. 50-55, 55-60, …), plot mean predicted `p` vs
  observed win frequency. On the diagonal = calibrated.
- **RPS (Ranked Probability Score)** — the *proper* score for ordinal 1X2 (home/draw/away);
  primary metric for football. Lib: `scoringrules`. Compare directly vs the Dixon-Coles and the
  CatBoost baselines (§4.5) and vs the market.
- **Log loss:** `-mean(o·ln p + (1-o)·ln(1-p))` — most Kelly-aligned (closest to log-wealth,
  punishes confident-wrong hardest). Strictly proper.
- **Brier score:** `BS = mean((p - o)^2)`, vs base-rate baseline `BS_base`. Skill iff `BS < BS_base`.
- **ECE + reliability diagram:** visual calibration check only (binning-sensitive, NOT proper) —
  never report alone. Libs: `sklearn` (`calibration_curve`), `netcal` (ECE).
- **Recalibration:** **Venn-ABERS** on history → calibrated `[p0,p1]`; report pre vs post. Kelly
  uses `p0`.

Verdict signal: `calibrated = (ECE < τ_ece) and (log_loss < log_loss_base) and (RPS < RPS_DC)`.

---

## 3. Lens 2 — CLV / edge (did we actually beat the market?) ← the sharp's metric

The market's closing line is the sharpest available benchmark. Beating it = you are sharper than
the market, and it converges **far faster than PnL** (much lower variance) — so you can know you
have edge after ~50 bets instead of thousands.

- **Closing Line Value:** `CLV% = O_bet / O_close - 1`. Positive = you locked a better price than
  the market closed at.
- **Beat-close rate:** share of bets with `O_bet > O_close`.
- **Mean CLV** and its distribution. Consistent positive mean CLV ≈ durable +EV.
- (Optional) **realized vs predicted edge:** model said edge=`p-q`; does realized ROI track it?

Verdict signal: `beats_market = mean_CLV > 0` (with a CI that excludes 0).

---

## 4. Lens 3 — PnL / ROI with significance (did it make money, for real?)

- **ROI** = `Σpnl / Σstake`.
- **Confidence interval** on ROI (bootstrap or normal approx). At 50-60% win rates, a "profitable"
  100-bet stretch can be pure variance — so we report **"edge significant at N bets"** or
  **"not yet distinguishable from luck."**
- **Risk-adjusted:** a Sharpe-like ratio of per-bet returns; max drawdown.
- **Confidence-bucket check:** do the model's *high-confidence* bets actually return more? (If not,
  its confidence is meaningless.)

Verdict signal: `profitable = ROI_CI_low > 0`.

---

## 4.5 Benchmark — is the LLM actually better than a cheap model? (the sharpest demo device)

Don't grade the LLM in a vacuum. Run a **strong non-LLM baseline** on the same fixtures and put
them head-to-head on RPS / log-loss / CLV. This is the most credible way to answer "is the LLM
accurate" — by comparison, not assertion.

- **Baseline:** CatBoost / LightGBM on `pi-ratings + Elo + rolling xG` features (research shows
  this is the cheap high-leverage model; full Bayesian state-space is ~21% better RPS but high
  effort — out of scope for the demo). Lib: `catboost` / `lightgbm`.
- **Reference benchmark:** the de-vigged **market closing line** — the thing nobody publicly beats
  on calibration. Show the LLM, the CatBoost baseline, and the market side by side.
- Demo line: *"The LLM only earns a bet when it beats both a gradient-boosting baseline and the
  market — measured by RPS and CLV, not by its own confidence."*

Honest framing to keep (anti-slop): a model can show +ROI yet ~0 CLV (originator effect) — so we
report both and never claim edge from a single lens.

## 5. The verdict metric

The model is **"accurate / has edge"** iff **all three** hold:

```
edge_is_real = calibrated AND beats_market AND profitable
             = (ECE<τ and BS<BS_base) AND (mean_CLV>0) AND (ROI_CI_low>0)
```

Win rate is just a surface symptom of these. The demo states this explicitly: *we do not claim
the AI is right because it won — we show it is calibrated, beats the closing line, and is
significantly profitable.*

---

## 6. Self-learning loop — per-source attribution & reweighting

Each prediction fuses several `sources`/packets. Score each source's **marginal** contribution:

- **Leave-one-out:** rerun consensus without source `s`; attribute the delta in PnL + Brier.
- **Source weight:** `w_s ← EWMA(risk-adjusted PnL contribution + calibration contribution)`.
- Up-weight sources with strong, calibrated PnL history; throttle/replace weak ones.

This is the "multi-source engine" made measurable — and it visibly mutates weights in the
**Calibration Lab** page ("replay settlements → reweight → before/after").

---

## 7. How scoring wires into the gate (models advise, code measures)

The deterministic gate consumes the *scoring history*, not the model's self-report:

- `min confidence + calibration quality` check → throttles a model whose rolling ECE/Brier is bad.
- `min edge` check → uses de-vigged market prob, not raw model prob.
- `CLV history` check (optional) → require the source's recent mean CLV ≥ 0 before sizing up.

So a model that has been poorly calibrated or has negative CLV history cannot push a bet through,
no matter how confident its text sounds. That is the whole thesis.

---

## 8. What to build (Day 1 centerpiece) + the libraries

Smallest viable rigorous stack: `scikit-learn` + `netcal` + `scoringrules` + `venn-abers`
(+ `catboost` for the benchmark, `mapie` for the optional skip-gate). All pip-installable.

1. The prediction-log schema (§1) + a settlement function.
2. `scoring.py`: **RPS** (scoringrules), log-loss, Brier, ECE + reliability (sklearn/netcal),
   CLV, ROI+CI, confidence-bucket, verdict.
3. `calibration.py`: **Venn-ABERS** fit/apply → `[p0,p1]`; pre/post report; Kelly uses `p0`.
4. `baseline.py`: CatBoost on pi-ratings+Elo+xG → head-to-head vs LLM vs market (§4.5).
5. `sources.py`: leave-one-out attribution + EWMA reweighting.
6. The **Calibration Lab** Streamlit page rendering all of the above on the recorded run.

Data: mirror the **Kaggle European Soccer DB** (HF: `julien-c/kaggle-hugomathien-soccer`, ~25K
matches with odds) for realistic fixtures; canonical 1X2 + closing odds from football-data.co.uk.
