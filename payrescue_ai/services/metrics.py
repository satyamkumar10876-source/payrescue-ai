from collections import Counter


def calculate_metrics(decisions):
    total = len(decisions)
    if total == 0:
        return {}

    correct = sum(1 for item in decisions if item.get("correct") or item["classification"] == item.get("ground_truth_label"))
    recoverable_predictions = [item for item in decisions if item["classification"] in {"SAFE_TO_RETRY", "DOWNTIME_FAILURE"}]
    true_recoverable_predictions = [item for item in recoverable_predictions if item.get("ground_truth_label") in {"SAFE_TO_RETRY", "DOWNTIME_FAILURE"}]
    actual_recoverable = [item for item in decisions if item.get("ground_truth_label") in {"SAFE_TO_RETRY", "DOWNTIME_FAILURE"}]

    precision = len(true_recoverable_predictions) / len(recoverable_predictions) if recoverable_predictions else 0
    recall = len(true_recoverable_predictions) / len(actual_recoverable) if actual_recoverable else 0

    counts = Counter(item["classification"] for item in decisions)
    duplicate_debit_prevented = sum(1 for item in decisions if item["classification"] == "PAYMENT_LIMBO_RISK" and item["decision"] == "WAIT_FOR_STATUS")

    return {
        "total_cases": total,
        "accuracy": round(correct / total * 100, 1),
        "recovery_precision": round(precision * 100, 1),
        "recovery_recall": round(recall * 100, 1),
        "safe_retry_cases": counts["SAFE_TO_RETRY"],
        "limbo_risk_cases": counts["PAYMENT_LIMBO_RISK"],
        "downtime_cases": counts["DOWNTIME_FAILURE"],
        "low_intent_cases": counts["LOW_INTENT_ABANDONMENT"],
        "human_review_cases": sum(1 for item in decisions if item["human_review_required"] or item["decision"] == "ESCALATE_TO_HUMAN"),
        "recovered_revenue": sum(item["expected_recovery_amount"] for item in decisions),
        "revenue_protected": sum(item["expected_value_protected"] for item in decisions),
        "duplicate_debit_prevented": duplicate_debit_prevented,
        "false_positive_cost": sum(item["false_positive_cost"] for item in decisions),
        "unnecessary_messages_prevented": counts["LOW_INTENT_ABANDONMENT"] + duplicate_debit_prevented,
        "average_confidence": round(sum(item["confidence"] for item in decisions) / total * 100, 1),
    }
