def build_timeline(case, decision):
    amount = int(case["amount"])
    events = [
        {
            "time": "T+00:00",
            "event": "order.created",
            "state": "Order opened",
            "note": f"Merchant order {case['order_id']} created for Rs {amount}.",
        },
        {
            "time": "T+00:20",
            "event": "payment.created",
            "state": "Payment attempt started",
            "note": f"Customer selected {case['payment_method']} via {case['bank']}.",
        },
    ]

    if case["upi_flow_completed"]:
        events.append(
            {
                "time": "T+01:10",
                "event": "authentication.completed",
                "state": "Customer completed auth flow",
                "note": "This increases late-authorisation risk when the final bank response is delayed.",
            }
        )

    if case["webhook_received"]:
        events.append(
            {
                "time": "T+02:00",
                "event": "payment.failed",
                "state": "Final failure status received",
                "note": f"Failure reason: {case['error_code']}. Recovery can be evaluated safely.",
            }
        )
    else:
        events.append(
            {
                "time": "T+02:00",
                "event": "gateway.no_response",
                "state": "Final bank status missing",
                "note": "No success webhook received yet. The payment may still resolve later.",
            }
        )

    if case["customer_reported_debit"]:
        events.append(
            {
                "time": "T+04:30",
                "event": "support.signal",
                "state": "Customer reports debit",
                "note": "Retry link becomes risky because the customer may have already paid.",
            }
        )

    if case["downtime_active"]:
        events.append(
            {
                "time": "T+05:00",
                "event": "downtime.detected",
                "state": "Payment method degraded",
                "note": f"{case['payment_method']} on {case['bank']} is marked degraded for this demo.",
            }
        )

    events.append(
        {
            "time": "T+10:00",
            "event": "agent.decision",
            "state": decision["decision"].replace("_", " ").title(),
            "note": decision["reason"],
        }
    )

    if decision["classification"] == "PAYMENT_LIMBO_RISK":
        events.extend(
            [
                {
                    "time": "T+15:00",
                    "event": "status.poll.scheduled",
                    "state": "Wait and verify",
                    "note": "Agent blocks immediate retry and schedules a status check.",
                },
                {
                    "time": "T+3 days",
                    "event": "capture_or_refund_guardrail",
                    "state": "Capture/refund timeout guardrail",
                    "note": "Late-authorised payments should be captured, reconciled, or refunded within the timeout window.",
                },
            ]
        )
    elif decision["decision"] == "SEND_RETRY_LINK":
        events.append(
            {
                "time": "T+10:05",
                "event": "recovery.link.prepared",
                "state": "Safe retry prepared",
                "note": "Debit-risk signals are absent, so recovery can continue.",
            }
        )
    elif decision["decision"] == "SUGGEST_ALTERNATE_METHOD":
        events.append(
            {
                "time": "T+10:05",
                "event": "alternate.method.recommended",
                "state": "Same-method retry blocked",
                "note": "Agent avoids repeating the failing rail during degradation.",
            }
        )
    else:
        events.append(
            {
                "time": "T+10:05",
                "event": "manual.review.created",
                "state": "Human review",
                "note": decision["guardrail"],
            }
        )

    return events
