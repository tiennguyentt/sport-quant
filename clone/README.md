# sport-quant — hybrid (pixel-faithful UI + real engine)

Hand-built HTML/CSS frontend (full pixel control, no framework DOM limits) served by a
pure-stdlib Python backend that runs the REAL engine: live World Cup 2026 data + a streaming
OpenRouter LLM whose output is governed by the deterministic gate.

## Run
    OPENROUTER_API_KEY=sk-or-...   # or put it in ../.streamlit/secrets.toml
    python server.py               # → http://localhost:8512

## Deploy (server host, not Streamlit Cloud)
Render / Railway / Fly free tier. Start command: `python server.py` (PORT from env).
Set OPENROUTER_API_KEY as an env var. No pip deps (stdlib only).
