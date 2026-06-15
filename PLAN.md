# sport-quant — Detailed Build Plan

*A 3-model synthesis (Claude + Codex/GPT-5.5 product review + Grok reverse-engineering report).
De-crypto'd, AIoT-framed quantitative prediction-market terminal as a public Streamlit demo for an
interview window (a few days, then taken down).*

---

## 0. The one decision everything hangs on: the REFRAME

This is **not** a sports-betting product. It is a **closed-loop AIoT decision system operating
under uncertainty**, and sports markets are merely the **simulation environment**.

- Spine: **simulated vision sensors → edge AI fusion → deterministic safety gate → actuation →
  audited outcome → calibration → reweight.**
- The wow is **controlled autonomy: models advise, code governs.**
- The single strongest interview moment:
  > "The models wanted to act. The deterministic policy refused — here is the exact rule and the
  > evidence that stopped them."

This reframe (a) removes the betting/token "dark part" from the surface, (b) makes it read as
real AIoT engineering, (c) reuses the "code-enforced gate, models cannot override" philosophy
already proven in knowledge-engine.

**Recruiter's 5-second takeaway:** simulated sensors detect an event → multiple models estimate
an opportunity → a deterministic gate decides whether the system may act → every decision is
audited and calibrated against outcomes.

---

## 1. Brand

- Repo / category: **sport-quant** (working name).
- Product brand candidates: **FieldSignal**, **Governed**, **Arbiter**, **Crucible**, **Gatekeep**.
  Lead candidate: something that says *governed + signal*. (DECISION OPEN — see §11.)
- Keep "betting", "quant", "token", "portfolio returns" **out of the hero**. They can exist
  quietly in the simulation/ledger.

---

## 2. Scope

### IN — build for real
- The **deterministic gate** (the differentiator).
- **Risk + fractional-Kelly** sizing math.
- The **replay engine** (recorded scenario, timestamped snapshots).
- The **audit trail** (immutable decision records + provenance).
- The **calibration** math (reliability, Brier, per-source reweighting).

### MOCK — honestly labelled
- **CV "packets"**: timestamped JSON (source id, event type, confidence, tracking summary,
  latency, integrity flags). Show one packet visually next to a simple field diagram.
- **Model outputs**: seeded, deterministic ensemble (not "live LLMs analyzing video").
- **Reasoning text**: optional free model (deepseek free / OpenRouter free), with a **recorded
  fallback** so it is instant and never breaks. No proprietary LLM needed.
- **Sports surface**: synthetic fixtures NHL / NBA / NFL / LaLiga / Dota2 (match the reference
  UI). A **Telegram-style "SIGNAL DETECTED" card** as a UI element only (no real integration).

### OUT — hard exclusions
All crypto/token/vault economics ($the engine, USDC, units, DAO, staking, buyback, fees flywheel,
wallets, on-chain). Real CV. Real odds APIs. Auth. Autonomous real execution. Multi-user.
(Other sports appear only as recorded ledger history.)

---

## 3. Pages (Streamlit, 4)

1. **Live Decision Room** (front door)
   - "Recorded scenario replay" badge + play / pause / speed (1×/4×) / reset / **inject anomaly**.
   - Four-stage pipeline strip: **Sensor → Fusion → Gate → Action**.
   - Incoming packet timeline; current event + model consensus.
   - Large gate verdict: `APPROVED` / `REJECTED` / `QUARANTINED`.
   - Scanner table: event · model prob · market-implied · edge% · confidence · suggested size · status.
   - Expandable **decision evidence** drawer.

2. **Decision Audit**
   - Searchable decision ledger; gate checklist + reason codes; fractional-Kelly calc shown;
     packet + model provenance; policy version, timestamps, immutable decision id.

3. **Performance**
   - Paper bankroll, deployed exposure, PnL curve, drawdown, win rate, settled decisions table.
   - Explicit **synthetic-data disclaimer**.

4. **Calibration Lab**
   - Reliability diagram (predicted vs observed), Brier / calibration error, per-source weights,
     before/after reweighting comparison.

---

## 4. The deterministic gate (the differentiator) — ordered checks

1. Schema + integrity validation
2. Packet freshness + source quorum
3. Cross-source disagreement threshold
4. Minimum confidence + calibration quality
5. Minimum expected-edge threshold
6. Anomaly / outlier checks
7. Position cap: max 1%
8. Total deployed cap: max 10–12%
9. Correlated-exposure cap
10. Final policy decision **with reason codes**

Models **cannot** set approval, override thresholds, or determine final size. Persist inputs,
policy version, every check, the output, and rejection reasons. This is the audited spine.

---

## 5. Core use-cases to demo (priority order)

1. **Sensor-to-decision replay** — packets flow in → inference → an APPROVED signal.
2. **Inspect a REJECTED signal** — stale data / model disagreement / insufficient edge / risk
   cap. (More credible than only showing wins.)
3. **Audit an approved decision** — full provenance: packets, model estimates, gate checks,
   final prob, sizing, decision id.
4. **Performance + calibration** — settled decisions, PnL, calibration error, source reweighting.
5. **Inject an anomaly** — corrupt/delay a packet → gate **fails closed**. (The wow.)

---

## 6. Instant but live-feeling

One precomputed **60–90s scenario** stored as timestamped snapshots, replayed through
`st.session_state` with pause / speed / reset / inject-anomaly. Always called a **"recorded live
scenario,"** never "live data." Motion comes from replaying authentic system transitions — not
spinners or RNG. (Reuse knowledge-engine's recorded-run-instant pattern + dark theme.)

---

## 7. Reuse from knowledge-engine (head start)

- Gate philosophy + UI ("code-enforced, models cannot override").
- Dark "Forensic Ledger" design system (`theme.py`).
- Recorded-run-instant pattern + honest no-key handling.
- AppTest smoke-test harness.

---

## 8. Three-day build sequence

- **Day 1** — Schemas: packet / prediction / gate-result / decision / settlement. Build ONE full
  replay through the REAL gate + sizing logic. (Engine before UI.)
- **Day 2** — The 4 pages. Add approved / rejected / anomalous scenarios.
- **Day 3** — Narrative polish, disclaimers + provenance, deterministic-replay test, deploy
  public on Streamlit Cloud, rehearse a failure-free run, record a fallback video.

---

## 9. Anti-slop guardrails

Short reasoning, visible formulas, fixed seeds, real rejection cases, versioned policy,
provenance, honest simulation labels. No fake "live", no random metrics, no polished dashboard
without traceable decisions. Slop tell = lots of generated prose + unexplained confidence scores.

---

## 10. Where the 3 models agreed / diverged

- **Agreed:** the deterministic eval-gate is the differentiator; build gate/risk/replay/audit/
  calibration for real and mock the rest honestly; recorded-run for instant feel; show rejections.
- **Grok (report):** supplied the real algorithm menu (Elo / Davidson / Dixon-Coles / Sarmanov →
  ensemble → fractional Kelly → calibration loop) and the "chat removed because users prompt-gamed
  the eval layer" lesson.
- **Codex (product):** the AIoT-governance reframe ("models advise, code governs"), cut betting
  framing from the hero, prioritize the rejected-signal + anomaly demos.
- **Claude (resolve):** keep the vivid sports surface + the Telegram signal card the user asked
  for (UI only), but lead with the AIoT-governance narrative. Sports = simulation skin; AIoT
  governance = spine.

---

## 11. Open decisions before Day 1

1. **Brand name** (FieldSignal / other).
2. **Confirm the AIoT-governance framing** leads (recommended: yes).
3. **Reasoning source**: recorded-first with optional free-LLM (recommended) vs fully recorded.
