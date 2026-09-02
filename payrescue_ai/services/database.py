import csv
import json
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "payrescue.db"
CSV_PATH = DATA_DIR / "synthetic_payment_cases.csv"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_cases (
            case_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            payment_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            payment_method TEXT NOT NULL,
            bank TEXT NOT NULL,
            status TEXT NOT NULL,
            error_code TEXT NOT NULL,
            error_source TEXT NOT NULL,
            error_step TEXT NOT NULL,
            upi_flow_completed INTEGER NOT NULL,
            customer_reported_debit INTEGER NOT NULL,
            webhook_received INTEGER NOT NULL,
            retry_count_24h INTEGER NOT NULL,
            customer_type TEXT NOT NULL,
            checkout_duration_seconds INTEGER NOT NULL,
            downtime_active INTEGER NOT NULL,
            ground_truth_label TEXT NOT NULL,
            recovery_success INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS decisions (
            case_id TEXT PRIMARY KEY,
            classification TEXT NOT NULL,
            decision TEXT NOT NULL,
            confidence REAL NOT NULL,
            reason TEXT NOT NULL,
            signals_json TEXT NOT NULL,
            guardrail TEXT NOT NULL,
            customer_message TEXT NOT NULL,
            expected_recovery_amount INTEGER NOT NULL,
            expected_value_protected INTEGER NOT NULL,
            false_positive_cost INTEGER NOT NULL,
            human_review_required INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    count = conn.execute("SELECT COUNT(*) AS count FROM payment_cases").fetchone()["count"]
    if count == 0:
        seed_cases(conn)
    conn.commit()
    conn.close()


def seed_cases(conn):
    rows = []
    methods = ["UPI", "CARD", "NETBANKING", "WALLET"]
    banks = ["HDFC", "SBI", "ICICI", "AXIS", "KOTAK", "PNB"]
    errors = [
        ("payment_timed_out", "bank", "authorization"),
        ("insufficient_funds", "customer", "authorization"),
        ("user_cancelled", "customer", "authentication"),
        ("bank_unavailable", "bank", "authorization"),
        ("gateway_no_response", "gateway", "authorization"),
        ("session_expired", "customer", "checkout"),
    ]

    for i in range(1, 1001):
        amount = 499 + ((i * 173) % 24500)
        method = methods[i % len(methods)]
        bank = banks[(i * 3) % len(banks)]
        error_code, error_source, error_step = errors[(i * 7) % len(errors)]
        status = "failed"
        if i % 17 == 0:
            status = "pending"
        if i % 29 == 0:
            status = "abandoned"

        upi_flow_completed = 1 if method == "UPI" and i % 3 != 0 else 0
        customer_reported_debit = 1 if error_code in {"payment_timed_out", "gateway_no_response"} and i % 5 == 0 else 0
        webhook_received = 0 if error_code in {"payment_timed_out", "gateway_no_response", "bank_unavailable"} else 1
        retry_count_24h = i % 4
        customer_type = "repeat" if i % 3 == 0 else "new"
        checkout_duration = 20 + ((i * 19) % 360)
        downtime_active = 1 if error_code in {"bank_unavailable", "gateway_no_response"} and i % 2 == 0 else 0

        if customer_reported_debit or (upi_flow_completed and not webhook_received and amount > 5000):
            label = "PAYMENT_LIMBO_RISK"
            recovery_success = 0
        elif downtime_active:
            label = "DOWNTIME_FAILURE"
            recovery_success = 1 if i % 4 != 0 else 0
        elif status == "abandoned" and checkout_duration < 90:
            label = "LOW_INTENT_ABANDONMENT"
            recovery_success = 0
        elif error_code in {"insufficient_funds", "session_expired", "user_cancelled"}:
            label = "SAFE_TO_RETRY"
            recovery_success = 1 if i % 3 != 0 else 0
        else:
            label = "HUMAN_REVIEW_REQUIRED"
            recovery_success = 0

        rows.append(
            (
                f"PR_{i:04d}",
                f"ORD_{7000 + i}",
                f"PAY_{9000 + i}",
                amount,
                method,
                bank,
                status,
                error_code,
                error_source,
                error_step,
                upi_flow_completed,
                customer_reported_debit,
                webhook_received,
                retry_count_24h,
                customer_type,
                checkout_duration,
                downtime_active,
                label,
                recovery_success,
            )
        )

    conn.executemany(
        """
        INSERT INTO payment_cases (
            case_id, order_id, payment_id, amount, payment_method, bank, status,
            error_code, error_source, error_step, upi_flow_completed,
            customer_reported_debit, webhook_received, retry_count_24h,
            customer_type, checkout_duration_seconds, downtime_active,
            ground_truth_label, recovery_success
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    with CSV_PATH.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
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
                "ground_truth_label",
                "recovery_success",
            ]
        )
        writer.writerows(rows)


def load_cases(limit=None):
    conn = connect()
    query = "SELECT * FROM payment_cases ORDER BY case_id"
    if limit:
        query += f" LIMIT {int(limit)}"
    rows = [dict(row) for row in conn.execute(query).fetchall()]
    conn.close()
    return rows


def add_payment_case(payload):
    conn = connect()
    existing = conn.execute(
        "SELECT COUNT(*) AS count FROM payment_cases WHERE case_id = ?",
        (payload["case_id"],),
    ).fetchone()["count"]
    if existing:
        conn.close()
        raise ValueError(f"Case {payload['case_id']} already exists.")

    conn.execute(
        """
        INSERT INTO payment_cases (
            case_id, order_id, payment_id, amount, payment_method, bank, status,
            error_code, error_source, error_step, upi_flow_completed,
            customer_reported_debit, webhook_received, retry_count_24h,
            customer_type, checkout_duration_seconds, downtime_active,
            ground_truth_label, recovery_success
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["case_id"],
            payload["order_id"],
            payload["payment_id"],
            int(payload["amount"]),
            payload["payment_method"],
            payload["bank"],
            payload["status"],
            payload["error_code"],
            payload["error_source"],
            payload["error_step"],
            int(payload["upi_flow_completed"]),
            int(payload["customer_reported_debit"]),
            int(payload["webhook_received"]),
            int(payload["retry_count_24h"]),
            payload["customer_type"],
            int(payload["checkout_duration_seconds"]),
            int(payload["downtime_active"]),
            payload.get("ground_truth_label") or infer_ground_truth(payload),
            int(payload.get("recovery_success", 0)),
        ),
    )
    conn.commit()
    conn.close()


def infer_ground_truth(payload):
    amount = int(payload["amount"])
    if int(payload["customer_reported_debit"]) or (
        payload["status"] in {"failed", "pending"}
        and int(payload["upi_flow_completed"])
        and not int(payload["webhook_received"])
        and payload["error_code"] in {"payment_timed_out", "gateway_no_response"}
    ):
        return "PAYMENT_LIMBO_RISK"
    if int(payload["downtime_active"]):
        return "DOWNTIME_FAILURE"
    if payload["status"] == "abandoned" and int(payload["checkout_duration_seconds"]) < 90:
        return "LOW_INTENT_ABANDONMENT"
    if payload["error_code"] in {"insufficient_funds", "session_expired", "user_cancelled"} and amount >= 0:
        return "SAFE_TO_RETRY"
    return "HUMAN_REVIEW_REQUIRED"


def save_decisions(decisions):
    conn = connect()
    conn.execute("DELETE FROM decisions")
    conn.executemany(
        """
        INSERT INTO decisions (
            case_id, classification, decision, confidence, reason, signals_json,
            guardrail, customer_message, expected_recovery_amount,
            expected_value_protected, false_positive_cost, human_review_required
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["case_id"],
                item["classification"],
                item["decision"],
                item["confidence"],
                item["reason"],
                json.dumps(item["signals"]),
                item["guardrail"],
                item["customer_message"],
                item["expected_recovery_amount"],
                item["expected_value_protected"],
                item["false_positive_cost"],
                1 if item["human_review_required"] else 0,
            )
            for item in decisions
        ],
    )
    conn.commit()
    conn.close()


def load_decisions():
    conn = connect()
    rows = [
        dict(row)
        for row in conn.execute(
            """
            SELECT
                d.*,
                p.order_id,
                p.payment_id,
                p.amount,
                p.payment_method,
                p.bank,
                p.status,
                p.ground_truth_label
            FROM decisions d
            JOIN payment_cases p ON p.case_id = d.case_id
            ORDER BY d.case_id
            """
        ).fetchall()
    ]
    conn.close()
    for row in rows:
        row["signals"] = json.loads(row.pop("signals_json"))
        row["correct"] = row["classification"] == row["ground_truth_label"]
    return rows
