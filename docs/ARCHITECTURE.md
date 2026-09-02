# Architecture

## Product

PayRescue AI is a trust-safe recovery control tower for failed, pending, abandoned, and late-authorisation-prone payments.

## Main Flow

```text
Synthetic payment cases
        ↓
Payment Health Classifier
        ↓
Limbo Risk Detector
        ↓
Downtime Correlator
        ↓
Recovery Decision Agent
        ↓
Guardrail Engine
        ↓
Webhook Timeline Simulator
        ↓
Audit Logger
        ↓
Metrics Dashboard
```

## Modules

`payrescue_ai/services/database.py`

Creates and reads the SQLite database. It also seeds 1,000 synthetic payment cases with labels for evaluation.

`payrescue_ai/services/agent.py`

Contains the decision logic. It classifies cases, chooses actions, applies guardrails, and returns explainable decisions.

`payrescue_ai/services/metrics.py`

Calculates accuracy, precision, recall, recovered revenue, protected revenue, false positive cost, and human-review counts.

`payrescue_ai/services/timeline.py`

Builds a human-readable payment lifecycle for each case. It shows order creation, payment attempt, auth completion, missing webhook/failure, support debit signal, agent decision, and capture/refund guardrails.

`payrescue_ai/server.py`

Exposes the dashboard and REST-like JSON endpoints.

`payrescue_ai/templates/index.html`

Single-page dashboard.

`payrescue_ai/static/app.js`

Fetches metrics/audit data and renders the interactive UI.

## Money-Movement Guardrail Principle

The project follows one core rule:

```text
When payment state is unclear, do not trigger customer-facing recovery automatically.
```

This is why limbo-risk cases are routed to wait, verify, reassure, or human review instead of immediate retry.
