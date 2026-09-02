from flask import Flask, jsonify, render_template, request

from .services.agent import run_agent
from .services.agent import analyze_case
from .services.database import add_payment_case, init_db, load_cases, load_decisions
from .services.metrics import calculate_metrics
from .services.timeline import build_timeline


def create_app():
    app = Flask(__name__)
    init_db()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/cases")
    def api_cases():
        limit = request.args.get("limit", default=80, type=int)
        return jsonify(load_cases(limit=limit))

    @app.post("/api/cases")
    def api_add_case():
        payload = request.get_json(force=True)
        required = [
            "case_id",
            "order_id",
            "payment_id",
            "amount",
            "payment_method",
            "bank",
            "status",
            "error_code",
            "error_source",
            "error_step",
            "upi_flow_completed",
            "customer_reported_debit",
            "webhook_received",
            "retry_count_24h",
            "customer_type",
            "checkout_duration_seconds",
            "downtime_active",
        ]
        missing = [field for field in required if field not in payload or payload[field] in {"", None}]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
        try:
            add_payment_case(payload)
            case = load_cases(limit=None)[-1]
            decision = analyze_case(case)
            decisions = run_agent()
            return jsonify(
                {
                    "case": case,
                    "decision": decision,
                    "timeline": build_timeline(case, decision),
                    "metrics": calculate_metrics(decisions),
                }
            ), 201
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 409

    @app.get("/api/decisions")
    def api_decisions():
        return jsonify(load_decisions())

    @app.get("/api/metrics")
    def api_metrics():
        decisions = load_decisions()
        if not decisions:
            decisions = run_agent()
        return jsonify(calculate_metrics(decisions))

    @app.get("/api/audit")
    def api_audit():
        decisions = load_decisions()
        if not decisions:
            decisions = run_agent()
        return jsonify(decisions[:120])

    @app.get("/api/timeline/<case_id>")
    def api_timeline(case_id):
        cases = {case["case_id"]: case for case in load_cases(limit=None)}
        decisions = {decision["case_id"]: decision for decision in load_decisions()}
        if not decisions:
            run_agent()
            decisions = {decision["case_id"]: decision for decision in load_decisions()}
        if case_id not in cases or case_id not in decisions:
            return jsonify({"error": "Case not found"}), 404
        return jsonify(build_timeline(cases[case_id], decisions[case_id]))

    @app.post("/api/run-agent")
    def api_run_agent():
        decisions = run_agent()
        return jsonify({"metrics": calculate_metrics(decisions), "decisions": decisions[:20]})

    return app


def run(host="127.0.0.1", port=8000):
    app = create_app()
    app.run(host=host, port=port, debug=False)
