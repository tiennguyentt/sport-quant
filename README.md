# sport-quant

A **governed sports-prediction terminal** — a de-crypto'd rebuild of SIRE's intelligence layer,
framed as an AIoT decision system: **streaming signals → edge fusion → a deterministic gate →
sized action → audited outcome → calibration.**

> **Models advise, code governs.** The terminal proposes a Kelly-sized bet; a deterministic policy
> approves or refuses it. No free-form prompt-gaming (the lesson SIRE learned the hard way).
> Synthetic data, paper bankroll, no crypto, no real money.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Pages

- **Terminal** (front door / interaction layer) — live score ticker, +EV match cards you ask
  about, and gated chat answers (`APPROVED` with stake + reasoning, or `REJECTED` with reason codes).
- **Performance** — paper portfolio dashboard (P&L, win rate, settled trades), modelled on the
  reference αVault UI.
- **Calibration** — the core: is the model actually accurate? Brier / log-loss / ECE, CLV,
  ROI-with-CI, reliability diagram, and a measured verdict (calibrated · beats market · profitable).

## Architecture

| File | Role | Author |
|---|---|---|
| `engine.py` | `Candidate`, fractional Kelly, the 10-check deterministic `gate_check` | Codex (GPT-5.5) |
| `scoring.py` | Brier, log-loss, RPS, ECE, reliability, CLV, ROI±CI, verdict | Codex (GPT-5.5) |
| `data.py` | synthetic fixtures, live scores, grounded reasonings, recorded run | Opus |
| `theme.py` | dark dashboard design system + components | Opus |
| `streamlit_app.py` | the three pages, gated chat interaction | Opus |
| `PLAN.md`, `docs/SCORING.md` | 3-model plan + the accuracy spec | Claude + Codex + Grok |

Planning & reverse-engineering: Grok. See `docs/SCORING.md` for the scoring methodology
(the most important logic) and `PLAN.md` for the full build plan.

## Tests

```bash
pytest tests/ -q
```
