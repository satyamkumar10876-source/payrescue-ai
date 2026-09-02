from .database import load_cases, save_decisions


def _confidence(score):
    return round(max(0.51, min(score, 0.99)), 2)


def analyze_case(case):
    signals = []
    amount = int(case["amount"])
    confidence = 0.72
    classification = "HUMAN_REVIEW_REQUIRED"
    decision = "ESCALATE_TO_HUMAN"
    guardrail = "Unclear payment state requires manual review."
    expected_recovery_amount = 0
    expected_value_protected = 0
    false_positive_cost = 0
    human_review_required = False

    if case["customer_reported_debit"]:
        signals.append("customer reported debit")
        confidence += 0.08
    if case["upi_flow_completed"]:
        signals.append("UPI/customer authentication flow completed")
        confidence += 0.05
    if not case["webhook_received"]:
        signals.append("no final success webhook received")
        confidence += 0.05
    if case["downtime_active"]:
        signals.append(f"{case['bank']} {case['payment_method']} downtime/degradation active")
        confidence += 0.06
    if amount > 10000:
        signals.append("high-value transaction")
        confidence += 0.03
    if case["retry_count_24h"] > 2:
        signals.append("customer already retried more than twice in 24 hours")

    limbo_risk = (
        case["customer_reported_debit"]
        or (
            case["status"] in {"failed", "pending"}
            and case["upi_flow_completed"]
            and not case["webhook_received"]
            and case["error_code"] in {"payment_timed_out", "gateway_no_response"}
        )
    )

    if limbo_risk:
        classification = "PAYMENT_LIMBO_RISK"
        decision = "WAIT_FOR_STATUS"
        guardrail = "Retry link blocked because duplicate debit risk is possible."
        expected_value_protected = amount
        message = (
            "We are verifying your payment status. If any amount was debited, it will be "
            "updated or refunded as per bank confirmation. Please wait before retrying."
        )
        reason = "Payment may be late-authorised or stuck in limbo; immediate retry can create duplicate debit risk."
        return _pack(case, classification, decision, confidence, signals, reason, guardrail, message, 0, expected_value_protected, 0, False)

    if case["downtime_active"]:
        classification = "DOWNTIME_FAILURE"
        decision = "SUGGEST_ALTERNATE_METHOD"
        guardrail = "Same payment method retry blocked during active degradation."
        expected_recovery_amount = amount if case["recovery_success"] else 0
        false_positive_cost = 250 if not case["recovery_success"] else 0
        message = "Your selected payment method is facing issues. You can complete the payment using another method."
        reason = "Failure is correlated with active payment-method or bank degradation; alternate method is safer than same-method retry."
        return _pack(case, classification, decision, confidence, signals, reason, guardrail, message, expected_recovery_amount, 0, false_positive_cost, False)

    if case["status"] == "abandoned" and int(case["checkout_duration_seconds"]) < 90:
        classification = "LOW_INTENT_ABANDONMENT"
        decision = "MARK_LOW_INTENT_NO_ACTION"
        guardrail = "Avoid discount or aggressive follow-up for low-intent abandonment."
        message = "No automatic customer message is sent for this low-intent case."
        reason = "Checkout intent is weak, so aggressive recovery may create cost without meaningful revenue upside."
        return _pack(case, classification, decision, confidence, signals or ["short checkout session"], reason, guardrail, message, 0, 0, 0, False)

    if case["error_code"] in {"insufficient_funds", "session_expired", "user_cancelled"}:
        classification = "SAFE_TO_RETRY"
        decision = "SEND_RETRY_LINK"
        guardrail = "Retry allowed because debit-risk signals are absent."
        if case["retry_count_24h"] > 2:
            decision = "STOP_FOLLOW_UP"
            guardrail = "Contact limit reached; do not message again today."
            expected_recovery_amount = 0
            message = "No further automatic follow-up is sent today."
        else:
            expected_recovery_amount = amount if case["recovery_success"] else 0
            message = "Your payment could not be completed. You can safely retry using this secure payment link."
        false_positive_cost = 350 if not case["recovery_success"] else 0
        reason = "Failure is customer-side or session-side and does not show late-authorisation risk."
        return _pack(case, classification, decision, confidence + 0.1, signals or ["clear customer/session-side failure"], reason, guardrail, message, expected_recovery_amount, 0, false_positive_cost, False)

    human_review_required = True
    if amount > 10000:
        guardrail = "High-value unclear case requires human approval."
    confidence = 0.67
    message = "This case needs manual review before any customer-facing recovery action."
    reason = "Signals are conflicting or insufficient for an automatic money movement decision."
    return _pack(case, classification, decision, confidence, signals or ["insufficient evidence"], reason, guardrail, message, 0, 0, 0, human_review_required)


def _pack(case, classification, decision, confidence, signals, reason, guardrail, message, expected_recovery, value_protected, false_positive_cost, human_review_required):
    if confidence < 0.75 and decision not in {"MARK_LOW_INTENT_NO_ACTION", "ESCALATE_TO_HUMAN"}:
        decision = "ESCALATE_TO_HUMAN"
        guardrail = "Confidence below 75%; automatic action blocked."
        human_review_required = True
        expected_recovery = 0

    return {
        "case_id": case["case_id"],
        "order_id": case["order_id"],
        "payment_id": case["payment_id"],
        "amount": case["amount"],
        "payment_method": case["payment_method"],
        "bank": case["bank"],
        "status": case["status"],
        "ground_truth_label": case["ground_truth_label"],
        "classification": classification,
        "decision": decision,
        "confidence": _confidence(confidence),
        "signals": signals,
        "reason": reason,
        "guardrail": guardrail,
        "customer_message": message,
        "expected_recovery_amount": int(expected_recovery),
        "expected_value_protected": int(value_protected),
        "false_positive_cost": int(false_positive_cost),
        "human_review_required": human_review_required,
        "correct": classification == case["ground_truth_label"],
    }


def run_agent():
    decisions = [analyze_case(case) for case in load_cases()]
    save_decisions(decisions)
    return decisions
