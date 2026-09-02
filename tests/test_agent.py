from payrescue_ai.services.agent import analyze_case


BASE_CASE = {
    "case_id": "TEST_001",
    "order_id": "ORD_TEST",
    "payment_id": "PAY_TEST",
    "amount": 12000,
    "payment_method": "UPI",
    "bank": "HDFC",
    "status": "failed",
    "error_code": "payment_timed_out",
    "error_source": "bank",
    "error_step": "authorization",
    "upi_flow_completed": 1,
    "customer_reported_debit": 1,
    "webhook_received": 0,
    "retry_count_24h": 1,
    "customer_type": "repeat",
    "checkout_duration_seconds": 180,
    "downtime_active": 0,
    "ground_truth_label": "PAYMENT_LIMBO_RISK",
    "recovery_success": 0,
}


def test_limbo_blocks_retry():
    result = analyze_case(BASE_CASE)
    assert result["classification"] == "PAYMENT_LIMBO_RISK"
    assert result["decision"] == "WAIT_FOR_STATUS"
    assert result["expected_value_protected"] == 12000


def test_safe_retry_allowed():
    case = dict(BASE_CASE)
    case.update(
        {
            "amount": 1800,
            "error_code": "insufficient_funds",
            "upi_flow_completed": 0,
            "customer_reported_debit": 0,
            "webhook_received": 1,
            "ground_truth_label": "SAFE_TO_RETRY",
            "recovery_success": 1,
        }
    )
    result = analyze_case(case)
    assert result["classification"] == "SAFE_TO_RETRY"
    assert result["decision"] == "SEND_RETRY_LINK"
    assert result["expected_recovery_amount"] == 1800
