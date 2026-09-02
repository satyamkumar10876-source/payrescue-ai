# Metrics

## Classification Accuracy

```text
accuracy = correct_predictions / total_predictions
```

This measures how often the agent's class matches the synthetic ground-truth label.

## Recovery Precision

```text
precision = true_recoverable_predictions / all_recoverable_predictions
```

This measures whether cases marked recoverable were actually safe and useful to recover.

## Recovery Recall

```text
recall = true_recoverable_predictions / actual_recoverable_cases
```

This measures how many recoverable cases the agent successfully found.

## Recovered Revenue

```text
recovered_revenue = sum(successfully simulated recovered amounts)
```

This is the amount won back through safe retry or alternate payment method actions.

## Revenue Protected

```text
revenue_protected = sum(limbo-risk amounts where retry was blocked)
```

This measures value protected by avoiding risky retry actions.

## False Positive Cost

False positive means the agent recommended recovery when it should not have.

```text
false_positive_cost =
  unnecessary message cost
  + support escalation cost
  + wrong discount cost
  + duplicate debit risk penalty
```

## Human Review Rate

```text
human_review_rate = human_review_cases / total_cases
```

This ensures the agent does not over-automate sensitive payment cases.
