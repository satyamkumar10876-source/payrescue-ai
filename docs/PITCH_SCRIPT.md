# Five-Minute Pitch Script

## 0:00 - 0:30

Introduce the problem. Failed payment recovery is useful, but blindly sending retry links can be unsafe when the payment is pending, late-authorised, or stuck in limbo.

## 0:30 - 1:15

Explain payment limbo. A customer may complete UPI or card authentication, but the merchant may not receive final status immediately. If recovery is triggered too early, duplicate debit and trust loss can happen.

## 1:15 - 2:15

Show the dashboard. Click `Run Recovery Agent` and explain the main metrics: recovered revenue, protected revenue, accuracy, precision, recall, and false positive cost.

## 2:15 - 3:15

Open a payment-limbo case. Show the audit trail: signals checked, confidence, reason, guardrail, and customer message.

## 3:15 - 4:15

Show failure handling. Explain that low-confidence, high-value, possible-debit, and downtime cases are blocked from unsafe automatic retry.

## 4:15 - 5:00

Close with the value. PayRescue AI does not just recover revenue; it recovers revenue safely while protecting customer trust and reducing support/reconciliation load.
