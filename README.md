# PayRescue AI

**Trust-safe revenue recovery agent for late authorisations and payment-limbo cases.**

PayRescue AI is a Razorpay Buildathon project for the **AI Revenue Recovery** track. It helps merchants recover failed payments only when recovery is safe, while blocking risky retry actions that can create duplicate debits, support tickets, refunds, and customer trust loss.

## One-Line Pitch

PayRescue AI recovers failed payments only when recovery is safe, detects late-authorisation and payment-limbo risk, prevents duplicate-debit recovery mistakes, and protects merchant revenue plus customer trust.

## Problem

Most payment recovery workflows do this:

```text
Payment failed -> send retry link
```

That can be unsafe. In real payment systems, a payment can appear failed or pending while the customer may already be debited and the final bank/gateway status is delayed. If the merchant sends a retry link too early, the customer may pay twice, raise support tickets, or lose trust.

PayRescue AI solves this by deciding whether each failed, pending, or abandoned payment is safe to recover now.

## What It Does

- Classifies failed payments into safe retry, payment-limbo risk, downtime failure, low-intent abandonment, or human review.
- Blocks unsafe retry links when duplicate-debit risk is possible.
- Suggests alternate payment methods during downtime/degradation.
- Generates trust-safe customer messages.
- Logs every decision with signals, reason, confidence, and guardrail.
- Measures accuracy, recovered revenue, protected revenue, false positive cost, precision, and recall.
- Lets a merchant add a custom failed/pending payment case and analyze it live.
- Shows a webhook timeline simulator for late-authorisation, delayed status, support signals, and capture/refund guardrails.

## Key Features

| Feature | What It Shows |
|---|---|
| Recovery Agent | Runs classification and recovery decisions across a batch of synthetic payment cases. |
| Manual Merchant Input | Lets reviewers add a custom failed/pending/abandoned payment case and analyze it live. |
| Limbo Risk Detector | Identifies cases where a retry link may cause duplicate debit risk. |
| Guardrail Engine | Blocks unsafe money actions when confidence is low or debit risk is possible. |
| Audit Trail | Explains every decision with signals, confidence, reason, and guardrail. |
| Webhook Timeline Simulator | Shows order/payment/webhook/support events behind the agent decision. |
| Metrics Dashboard | Reports accuracy, precision, recall, recovered revenue, protected revenue, and false positive cost. |

## Demo Flow

1. Start the app.
2. Open the dashboard.
3. Click `Run Recovery Agent`.
4. Add a custom merchant payment case from the form.
5. Inspect overview metrics.
6. Click a case in the recovery queue.
7. Review the audit trail and guardrail applied.
8. Show a failure-handling case where the agent refuses to act automatically.

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- JavaScript

The stack was intentionally kept simple and understandable: Python + Flask backend, SQLite persistence, and a clean HTML/CSS/JS dashboard.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:

```text
http://127.0.0.1:8000
```

The app automatically creates a SQLite database and synthetic dataset on first run.

## Project Structure

```text
payrescue-ai/
  app.py
  README.md
  requirements.txt
  docs/
    ARCHITECTURE.md
    METRICS.md
    PITCH_SCRIPT.md
    SUBMISSION_CHECKLIST.md
  payrescue_ai/
    server.py
    data/
      synthetic_payment_cases.csv
    services/
      agent.py
      database.py
      metrics.py
      timeline.py
    static/
      app.js
      styles.css
    templates/
      index.html
  tests/
    test_agent.py
```

## API Endpoints

```text
GET  /api/cases
GET  /api/metrics
GET  /api/audit
GET  /api/decisions
POST /api/run-agent
POST /api/cases
GET  /api/timeline/<case_id>
```

## How Razorpay Could Use It

In production, Razorpay would not ask merchants to manually type every case. The agent would consume:

- Payment attempt events
- Order status events
- Webhook delivery status
- Bank/UPI downtime signals
- Customer support signals such as "amount debited"
- Retry count and checkout behavior

The manual form in this demo simulates those inputs so reviewers can create a payment-limbo or safe-retry case and see the decision immediately.

## Unique Feature: Webhook Timeline Simulator

Razorpay's public docs explain that payment state can arrive through webhooks such as `payment.authorized`, `payment.captured`, and `payment.failed`. Late-authorisation cases can occur when the final bank response is delayed.

The timeline simulator shows the lifecycle behind each decision:

```text
order.created
-> payment.created
-> authentication.completed
-> gateway.no_response
-> support.signal
-> agent.decision
-> status.poll.scheduled
-> capture_or_refund_guardrail
```

This makes PayRescue AI more than a static classifier. It explains how Razorpay-style payment events would be interpreted before any retry, refund, or customer message is triggered.

## Example Decision

```json
{
  "case_id": "PR_1021",
  "classification": "PAYMENT_LIMBO_RISK",
  "decision": "WAIT_FOR_STATUS",
  "confidence": 0.88,
  "signals": [
    "customer reported debit",
    "UPI/customer authentication flow completed",
    "no final success webhook received"
  ],
  "reason": "Payment may be late-authorised or stuck in limbo; immediate retry can create duplicate debit risk.",
  "guardrail": "Retry link blocked because duplicate debit risk is possible."
}
```

## Failure Handling

| Failure/Risk | Agent Behavior |
|---|---|
| Confidence below 75 percent | Send to human review. |
| Possible customer debit | Block retry link and wait for status. |
| Active downtime/degradation | Do not retry the same payment method. |
| High-value unclear payment | Require manual approval. |
| Too many retries in 24 hours | Stop customer follow-up. |
| Invalid/unclear agent output | Fall back to rule-based decisioning. |

## Architecture

```text
Payment/order events
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
Action Simulator
        ↓
Metrics Engine + Audit Logger
        ↓
Dashboard
```

## Agent Classes

```text
SAFE_TO_RETRY
PAYMENT_LIMBO_RISK
DOWNTIME_FAILURE
LOW_INTENT_ABANDONMENT
HUMAN_REVIEW_REQUIRED
```

## Metrics

The dashboard reports:

- Classification accuracy
- Recovery precision
- Recovery recall
- Recovered revenue
- Revenue protected from duplicate-debit risk
- Duplicate debit attempts prevented
- False positive cost
- Unnecessary messages prevented
- Human review cases

## False Positive Cost

False positive cost estimates the business damage when the agent recommends recovery when it should not.

```text
false_positive_cost =
  unnecessary message/support cost
  + wrong discount cost
  + duplicate debit risk penalty
```

## Audit Trail Example

```json
{
  "case_id": "PR_1021",
  "classification": "PAYMENT_LIMBO_RISK",
  "decision": "WAIT_FOR_STATUS",
  "confidence": 0.88,
  "signals": [
    "customer reported debit",
    "UPI/customer authentication flow completed",
    "no final success webhook received"
  ],
  "reason": "Payment may be late-authorised or stuck in limbo; immediate retry can create duplicate debit risk.",
  "guardrail": "Retry link blocked because duplicate debit risk is possible."
}
```

## Failure Handling

- Confidence below 75 percent -> human review.
- Possible customer debit -> block retry link and wait for status.
- Active downtime -> do not retry same payment method.
- High-value unclear payment -> manual review.
- Too many retries in 24 hours -> stop follow-up.
- Invalid AI/agent output -> fallback rule-based decision.

## Why It Is Different

This is not a basic failed-payment recovery tool. It focuses on trust-safe recovery: the agent tries to recover revenue only when doing so will not create duplicate debit, customer panic, or unnecessary support load.

## Buildathon Checklist

- Real fintech problem: failed payment recovery can be unsafe during late authorisation.
- Working demo: local dashboard and APIs.
- Public GitHub ready: clean README and runnable app.
- Architecture: documented above and in `outputs/PayRescue_AI_Architecture.md`.
- Metrics: accuracy, recovery amount, false positive cost, precision, recall.
- Audit trail: every decision has signals, reason, confidence, and guardrail.
- Failure handling: uncertain or unsafe cases are blocked and sent to review.

## Honest Limitation

This project uses synthetic data for the Buildathon demo. In a production Razorpay environment, the same pipeline would consume real payment attempts, order events, webhooks, downtime signals, and support/customer signals.
