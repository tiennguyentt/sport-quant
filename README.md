# sport-quant

An **LLM-powered +EV terminal** for prediction markets (Polymarket & Kalshi). Quantitative models
find mispriced edges; an LLM integrates and explains them; a deterministic risk layer sizes and
gates every bet. **Models advise, code governs.**

## How it works

`signals → score → edge → kelly → gate → bet`

| stage | logic |
|---|---|
| **score** | team-strength ratings → **Elo** win probability + **Dixon-Coles** bivariate-Poisson goals model, blended in a meta-ensemble (the probability is computed here, not by an LLM) |
| **edge** | model probability vs the de-vigged market price: `edge = p − 1/odds` |
| **size** | **fractional Kelly** `f* = (b·p − (1−p))/b`, capped at 1% per position |
| **gate** | a deterministic, code-enforced checklist (min edge, confidence, disagreement, exposure caps) the model cannot override |
| **prove** | calibration that asks *is the model accurate?* — Brier, ECE, CLV, ROI (not just win rate) |
| **explain** | an LLM (deepseek-v3) reads the numbers and writes the plain-language rationale — advisory only |

Live World Cup 2026 fixtures + scores come from TheSportsDB. The LLM streams from OpenRouter.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Set `OPENROUTER_API_KEY` (in `.env` locally, or Streamlit Cloud secrets) for live LLM replies.

## Tests

```bash
pytest tests/ -q
```
