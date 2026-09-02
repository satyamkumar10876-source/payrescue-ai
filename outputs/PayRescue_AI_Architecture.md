# PayRescue AI: Trust-Safe Revenue Recovery for Payment Limbo

## 1. One-Line Pitch

PayRescue AI recovers failed payments only when recovery is safe, detects late-authorisation and payment-limbo risk, prevents duplicate-debit recovery mistakes, and protects merchant revenue plus customer trust.

## 2. Real Business Problem

Most failed-payment recovery systems follow a simple pattern:

```text
Payment failed -> send retry/payment link
```

This is useful, but risky in real payment flows. Sometimes a payment appears failed or pending because the payment gateway did not receive the bank response on time. The customer may have completed the payment flow and the amount may even be debited, but the merchant does not yet have a final success status.

If the merchant immediately sends another retry link, it can create:

- duplicate debit risk
- customer panic and trust loss
- support tickets
- unnecessary refunds
- reconciliation complexity
- wrong recovery actions during bank or UPI downtime

PayRescue AI solves this by deciding whether a failed payment is actually safe to recover now.

## 3. Target Users

- D2C merchants
- SaaS businesses collecting online payments
- Marketplaces
- Subscription businesses
- Finance and support teams handling payment failures

## 4. Core Product Idea

PayRescue AI acts like a recovery control tower for failed, pending, abandoned, and late-authorisation-prone payments.

It does not blindly retry every failed payment. It classifies each case, applies guardrails, and chooses the safest action.

```text
Payment failed / pending / abandoned
        ↓
Classify failure type
        ↓
Detect payment-limbo risk
        ↓
Check downtime or method degradation
        ↓
Choose safe recovery action
        ↓
Apply guardrails
        ↓
Generate customer/merchant message
        ↓
Log decision with reason
        ↓
Show metrics and recovery impact
```

## 5. What The Agent Detects

### 5.1 Retry-Safe Failure

The payment failed clearly and retry is safe.

Examples:

- insufficient balance
- card expired
- user cancelled before authentication
- payment session expired
- invalid payment details

Agent action:

```text
Send retry link or alternate payment method suggestion.
```

### 5.2 Payment Limbo Risk

The payment status is failed, pending, or timed out, but the customer may have completed authentication or may have been debited.

Examples:

- gateway timeout
- no final bank response
- UPI intent flow completed
- customer reports debit
- webhook not received yet
- payment later becomes authorised

Agent action:

```text
Do not send retry link immediately.
Hold case, verify status, reassure customer, and escalate if needed.
```

### 5.3 Downtime-Correlated Failure

The failure happened during a payment method, bank, PSP, or gateway degradation.

Examples:

- UPI bank degradation
- card issuer failure spike
- PSP app unavailable
- multiple similar failures in the same time window

Agent action:

```text
Suggest alternate payment method or delay retry.
Do not retry the same failing method.
```

### 5.4 Low-Intent Abandonment

The user dropped off but signals show low buying intent.

Examples:

- one short checkout visit
- no authentication attempt
- low cart value
- multiple abandoned sessions

Agent action:

```text
Avoid aggressive follow-up or discount.
Maybe send soft reminder only.
```

### 5.5 Human Review Case

The amount is high, confidence is low, or signals conflict.

Agent action:

```text
Send to merchant review queue.
No automatic retry or refund decision.
```

## 6. Key Features

## 6.1 Payment Health Classifier

Classifies each failed or pending payment into a business-safe category.

Possible labels:

```text
SAFE_TO_RETRY
POSSIBLE_LATE_AUTH
PAYMENT_LIMBO_RISK
DOWNTIME_FAILURE
LOW_INTENT_ABANDONMENT
HUMAN_REVIEW_REQUIRED
```

Inputs:

- payment status
- order status
- error code
- error source
- payment method
- bank or PSP
- amount
- time since attempt
- retry count
- webhook events
- customer history
- checkout behavior
- downtime signals

## 6.2 Limbo Risk Detector

Detects cases where retrying too early could create duplicate debit or customer confusion.

Risk signals:

- payment status timed out
- customer completed OTP/UPI step
- no final bank response
- customer reported debit
- high-value transaction
- webhook delay
- same order has multiple attempts
- previous attempt later authorised

Output:

```json
{
  "limbo_risk_score": 0.88,
  "risk_level": "HIGH",
  "reason": "UPI flow completed, no final response, timeout error, high amount."
}
```

## 6.3 Recovery Decision Agent

Chooses the best next action.

Possible actions:

```text
SEND_RETRY_LINK
SUGGEST_ALTERNATE_METHOD
WAIT_FOR_STATUS
SEND_REASSURANCE_MESSAGE
ESCALATE_TO_HUMAN
MARK_LOW_INTENT_NO_ACTION
STOP_FOLLOW_UP
```

Example:

```text
If payment failed due to insufficient funds:
    send retry link after 2 hours

If payment timed out after UPI authentication:
    wait for status and reassure customer

If bank downtime is active:
    suggest card/netbanking instead of same UPI method
```

## 6.4 Guardrail Engine

Prevents unsafe actions.

Rules:

```text
If confidence < 75% -> human review
If possible debit risk is high -> block retry link
If amount > 10000 and status unclear -> human review
If customer opted out -> no message
If retry count > 2 in 24h -> stop follow-up
If downtime active -> do not retry same method
If AI output invalid -> fallback rule-based decision
```

## 6.5 Customer Message Generator

Generates safe customer communication based on the decision.

For safe retry:

```text
Your payment could not be completed. You can safely retry using this secure payment link.
```

For limbo risk:

```text
We are verifying your payment status. If any amount was debited, it will be updated or refunded as per bank confirmation. Please wait before retrying.
```

For downtime:

```text
Your selected payment method is currently facing issues. You can complete the payment using another method.
```

## 6.6 Merchant Dashboard

Dashboard sections:

1. Overview
2. Recovery Queue
3. Limbo Risk Cases
4. Downtime Events
5. Audit Trail
6. Metrics

Overview cards:

- total cases analysed
- safe retry cases
- limbo-risk cases
- recovered revenue
- revenue protected
- duplicate debit risk prevented
- false positive cost
- human review cases

## 6.7 Audit Trail

Every agent decision must be explainable.

Audit log structure:

```json
{
  "case_id": "PR_1021",
  "order_id": "ORD_7009",
  "payment_id": "PAY_8841",
  "payment_status": "failed",
  "failure_type": "POSSIBLE_LATE_AUTH",
  "decision": "WAIT_FOR_STATUS",
  "confidence": 0.88,
  "signals": [
    "gateway timeout",
    "UPI flow completed",
    "no final bank response",
    "same bank showing degraded success rate"
  ],
  "reason": "Retry may create duplicate debit risk. Waiting for status confirmation is safer.",
  "guardrail_applied": "Block retry link for possible late authorization",
  "next_action": "Check status after 15 minutes",
  "expected_value_protected": 12499,
  "timestamp": "2026-09-02T12:10:00Z"
}
```

## 7. System Architecture

```text
Frontend Dashboard
        |
        | Upload/view synthetic payment cases
        v
Backend API
        |
        | Validates and normalizes payment/order data
        v
Data Layer
        |
        | payments, orders, checkout events, webhooks, downtime events
        v
Payment Health Classifier
        |
        | labels each failed/pending case
        v
Limbo Risk Detector
        |
        | calculates duplicate-debit and late-authorisation risk
        v
Downtime Correlator
        |
        | checks method/bank/PSP degradation signals
        v
Recovery Decision Agent
        |
        | chooses best recovery action
        v
Guardrail Engine
        |
        | blocks unsafe actions
        v
Action Simulator
        |
        | simulates retry, wait, alternate method, reassurance, review
        v
Metrics Engine + Audit Logger
        |
        | stores outcome, reasoning, and performance
        v
Dashboard Reports
```

## 8. Suggested Code Architecture

```text
payrescue-ai/
  README.md
  .env.example
  package.json
  docker-compose.yml

  data/
    synthetic_payments.csv
    synthetic_orders.csv
    synthetic_webhooks.csv
    synthetic_downtime_events.csv
    ground_truth_labels.csv

  backend/
    app/
      main.py
      config.py

      models/
        payment_case.py
        decision.py
        audit_log.py
        metrics.py

      services/
        data_loader.py
        normalizer.py
        payment_health_classifier.py
        limbo_risk_detector.py
        downtime_correlator.py
        recovery_decision_agent.py
        guardrail_engine.py
        action_simulator.py
        metrics_engine.py
        audit_logger.py
        message_generator.py

      routes/
        cases.py
        decisions.py
        metrics.py
        audit.py

      tests/
        test_limbo_detector.py
        test_guardrails.py
        test_metrics.py

  frontend/
    src/
      app/
        page.tsx
        cases/page.tsx
        audit/page.tsx
        metrics/page.tsx

      components/
        OverviewCards.tsx
        RecoveryQueue.tsx
        LimboRiskTable.tsx
        AuditTrail.tsx
        MetricsPanel.tsx
        DecisionDrawer.tsx

      lib/
        api.ts
        formatters.ts
```

## 9. Data Model

### Payment Case

```json
{
  "case_id": "PR_1021",
  "order_id": "ORD_7009",
  "payment_id": "PAY_8841",
  "amount": 12499,
  "currency": "INR",
  "payment_method": "UPI",
  "bank": "HDFC",
  "status": "failed",
  "error_code": "payment_timed_out",
  "error_source": "bank",
  "error_step": "authorization",
  "upi_flow_completed": true,
  "customer_reported_debit": true,
  "webhook_received": false,
  "retry_count_24h": 1,
  "customer_type": "repeat",
  "checkout_duration_seconds": 188,
  "created_at": "2026-09-02T11:48:00Z"
}
```

### Decision Output

```json
{
  "case_id": "PR_1021",
  "classification": "PAYMENT_LIMBO_RISK",
  "confidence": 0.88,
  "decision": "WAIT_FOR_STATUS",
  "customer_message_type": "REASSURANCE",
  "expected_recovery_amount": 0,
  "expected_value_protected": 12499,
  "human_review_required": false
}
```

## 10. Metrics

### 10.1 Accuracy

Measures how many classifications match the ground-truth labels.

```text
accuracy = correct_predictions / total_predictions
```

Example:

```text
Correct predictions: 218
Total predictions: 246
Accuracy: 88.6%
```

### 10.2 Recovery Precision

Of the cases marked recoverable, how many were actually safe and useful to recover.

```text
precision = true_recoverable_predictions / all_recoverable_predictions
```

### 10.3 Recovery Recall

Of all actually recoverable cases, how many the agent found.

```text
recall = true_recoverable_predictions / actual_recoverable_cases
```

### 10.4 Recovered Revenue

Money recovered through safe retry or alternate method actions.

```text
recovered_revenue = sum(amount of successful simulated recoveries)
```

### 10.5 Revenue Protected

Value protected by avoiding unsafe retry in limbo-risk cases.

```text
revenue_protected = sum(amount of limbo-risk cases where retry was blocked)
```

### 10.6 False Positive Cost

False positive means the agent selected a recovery action when it should not have.

```text
false_positive_cost =
  unnecessary_message_cost
  + support_escalation_cost
  + wrong_discount_cost
  + duplicate_debit_risk_penalty
```

Example:

```text
False positive cases: 7
Messaging/support cost: Rs 1,250
Wrong discount cost: Rs 2,000
Duplicate debit risk penalty: Rs 3,000
False positive cost: Rs 6,250
```

### 10.7 Suggested Demo Metrics

```text
Total cases analysed: 1,000
Failed/pending/abandoned cases: 246
Safe retry cases: 88
Payment-limbo risk cases: 31
Downtime-correlated failures: 47
Recovered revenue: Rs 1,86,400
Revenue protected from duplicate debit risk: Rs 78,900
Duplicate debit attempts prevented: 18
Recovery precision: 90.8%
Recovery recall: 84.2%
Classification accuracy: 88.6%
False positives: 7
False positive cost: Rs 6,250
Unnecessary messages prevented: 64
Average decision time: 1.2 sec
Human review cases: 22
```

## 11. Failure Handling

### 11.1 Low Confidence

```text
Condition:
confidence < 75%

Action:
Send to human review.
Do not send retry link automatically.
```

### 11.2 Possible Customer Debit

```text
Condition:
customer_reported_debit = true OR possible_late_auth = true

Action:
Block retry link.
Send reassurance message.
Schedule status check.
```

### 11.3 Active Downtime

```text
Condition:
bank/payment method downtime active

Action:
Do not retry same method.
Suggest alternate method or wait.
```

### 11.4 High-Value Transaction

```text
Condition:
amount > Rs 10,000 AND status unclear

Action:
Human review required.
```

### 11.5 Invalid AI Output

```text
Condition:
LLM response is invalid JSON or missing required fields

Action:
Retry once.
If still invalid, use fallback rule engine.
Log the failure.
```

### 11.6 Over-Contact Protection

```text
Condition:
retry_count_24h > 2

Action:
Stop follow-up.
Mark as contact limit reached.
```

## 12. Demo Flow

The working demo should show:

1. Dashboard opens with 1,000 synthetic payment cases.
2. User clicks "Run Recovery Agent".
3. Agent classifies failed, pending, abandoned, and limbo-risk cases.
4. Dashboard shows:
   - safe retry cases
   - payment-limbo cases
   - downtime-correlated cases
   - recovered revenue
   - protected revenue
5. User opens one case and sees:
   - decision
   - confidence
   - signals
   - reasoning
   - guardrail applied
6. User opens audit trail.
7. User opens metrics page.
8. User sees one failure-handling example where the agent refuses to act automatically.

## 13. README Checklist

Public GitHub repo should include:

- clear problem statement
- one-line pitch
- architecture diagram
- setup commands
- sample dataset
- demo screenshots
- metrics explanation
- audit trail explanation
- failure handling explanation
- known limitations
- 5-minute pitch video link

## 14. What To Say In Pitch Video

Suggested structure:

```text
0:00 - 0:30
Introduce problem: failed payment recovery can be unsafe when payment is in limbo.

0:30 - 1:15
Explain late authorisation/payment-limbo and duplicate debit risk.

1:15 - 2:15
Show dashboard and run the agent.

2:15 - 3:15
Open case details and explain audit trail.

3:15 - 4:15
Show metrics: recovered revenue, protected revenue, precision, recall, false positive cost.

4:15 - 5:00
Show failure handling: low-confidence/high-value/possible debit case goes to human review.
```

## 15. Why This Project Is Strong

- It solves a real fintech payment problem.
- It is not just a chatbot or dashboard.
- It is not a direct clone of failed-payment recovery.
- It uses AI meaningfully for classification, decisioning, explanation, and communication.
- It has measurable business impact.
- It has audit trails for every money-related action.
- It has guardrails and failure handling.
- It can be built with synthetic data and still feel realistic.

