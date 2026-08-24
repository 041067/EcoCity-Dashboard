# Sprint 9 — Gap & Action Engine

The Gap & Action Engine is deterministic: it never accepts a computed score from the client and it never uses a generative model to decide a priority.

## Evidence traceability

Every detected record keeps the persisted provider value that originated it. A typical trace is:

`NASA POWER → ENERGY_SOLAR_POTENTIAL → IndicatorValue → ESGOpportunity → ESG topic → priority explanation`

Targets keep the indicator direction (`higher_is_better` or `lower_is_better`). A gap is only created when the latest stored value does not meet the target. The analysis runner uses an organization-scoped fingerprint (`target:{id}`, `risk:{site}:{indicator}`, or `solar:{site}:{indicator}`) to update the same record on subsequent runs instead of creating duplicates. Signals no longer detected are resolved/dismissed, never deleted.

## Deterministic methodology

| Calculation | Formula / threshold |
| --- | --- |
| Gap | `max(0, target - current)` for higher-is-better; `max(0, current - target)` for lower-is-better. |
| Gap severity | Relative gap: `<10% low`, `<25% medium`, `<50% high`, otherwise `critical`. |
| Target progress | `(current - baseline) / (target - baseline) × 100`, clamped from 0–100. This works in both directions. |
| Tracking status | Achieved when target met; otherwise compare actual progress to the linear annual trajectory: `on_track` (within 10pp), `at_risk` (within 25pp), `off_track`. |
| Risk | `likelihood × impact / 25 × 100`; likelihood and impact are constrained to 1–5. |
| Opportunity | `potential impact × feasibility / 25 × 100`; inputs are constrained to 1–5. |
| Priority | `materiality × 35% + gap severity × 30% + risk × 25% + evidence confidence × 10%`. |
| Priority bands | `<40 low`, `<60 medium`, `<80 high`, `≥80 critical`. |

Climate risk values are emitted by the Sprint 8 `climate_risk_engine` thresholds. Solar opportunities require `ENERGY_SOLAR_POTENTIAL >= 3.5 kWh/m²/day`; the persisted NASA POWER value and reference remain attached to the opportunity.

## API and security

All Sprint 9 resources are nested below `/api/v1/esg/organizations/{organization_id}`. Every read, update, task operation and linked target/gap/risk lookup is filtered by the organization. A foreign identifier from another organization returns `404`, preventing IDOR-style cross-tenant access.

Inputs use strict Pydantic schemas (`extra=forbid`): clients cannot set derived risk scores, priority scores, gap values, action progress, evidence links, audit entries, or indicator direction. Action progress is recalculated from non-cancelled tasks. Mutation events are appended to `audit_entries`; this table is read-only through the API.

Key endpoints:

- `POST /organizations/{id}/analysis/run`
- `GET|POST /organizations/{id}/targets`
- `GET /organizations/{id}/gaps`, `/risks`, `/opportunities`, `/priorities`
- `GET|POST /organizations/{id}/actions`
- `PUT /organizations/{id}/actions/{action_id}/tasks/{task_id}`
- `GET /organizations/{id}/audit`

## Operations

The analysis only reads the already persisted indicator/evidence layer, so an unavailable external provider cannot take down the analysis endpoint. Sprint 8 freshness, cache, fallback and provider circuit-breaker behavior remains in effect during collection.

GitHub Actions run backend lint/tests, dependency audit, offline/online Alembic validation, frontend lint/tests/build and production dependency audit on every branch push and pull request. The Sprint 9 tests cover formulas, idempotency, evidence linkage, task-derived progress, strict-input rejection, audit history and organization isolation.
