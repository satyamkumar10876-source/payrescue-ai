const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0
});

let decisions = [];

function isRawFileOpen() {
  return window.location.protocol === "file:";
}

async function fetchJson(url, options = {}) {
  if (isRawFileOpen()) {
    throw new Error("App is opened as a file. Start Flask with python3 app.py and open http://127.0.0.1:8000.");
  }
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function setRunStatus(text, isError = false) {
  const status = document.getElementById("runStatus");
  const summary = document.getElementById("runSummary");
  status.textContent = text;
  summary.classList.toggle("error", isError);
  summary.innerHTML = `<strong>Agent status:</strong><span>${text}</span>`;
}

function setMetric(id, value, type = "number") {
  const el = document.getElementById(id);
  if (!el) return;
  if (type === "money") {
    el.textContent = money.format(value || 0);
    return;
  }
  if (type === "percent") {
    el.textContent = `${value || 0}%`;
    return;
  }
  el.textContent = value ?? "-";
}

function renderMetrics(metrics) {
  setMetric("total_cases", metrics.total_cases);
  setMetric("recovered_revenue", metrics.recovered_revenue, "money");
  setMetric("revenue_protected", metrics.revenue_protected, "money");
  setMetric("accuracy", metrics.accuracy, "percent");
  setMetric("recovery_precision", metrics.recovery_precision, "percent");
  setMetric("recovery_recall", metrics.recovery_recall, "percent");
  setMetric("false_positive_cost", metrics.false_positive_cost, "money");
  setMetric("duplicate_debit_prevented", metrics.duplicate_debit_prevented);
  document.querySelectorAll(".metric").forEach((card) => {
    card.classList.remove("updated");
    void card.offsetWidth;
    card.classList.add("updated");
  });
}

function renderRows(items) {
  const tbody = document.getElementById("decisionRows");
  tbody.innerHTML = "";
  items.slice(0, 120).forEach((item, index) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${item.case_id}</td>
      <td>${money.format(item.amount)}</td>
      <td>${item.payment_method} / ${item.bank}</td>
      <td><span class="badge ${item.classification}">${item.classification.replaceAll("_", " ")}</span></td>
      <td>${item.decision.replaceAll("_", " ")}</td>
      <td>${Math.round(item.confidence * 100)}%</td>
    `;
    row.addEventListener("click", () => selectCase(item));
    tbody.appendChild(row);
    if (index === 0) selectCase(item);
  });
}

async function selectCase(item) {
  renderAudit(item);
  await renderTimeline(item.case_id);
}

async function renderTimeline(caseId) {
  const container = document.getElementById("timeline");
  container.innerHTML = "<p>Loading payment lifecycle...</p>";
  try {
    const events = await fetchJson(`/api/timeline/${caseId}`);
    container.innerHTML = events.map((event) => `
      <div class="timeline-item">
        <div class="timeline-time">${event.time}</div>
        <div class="timeline-body">
          <span class="timeline-event">${event.event}</span>
          <strong>${event.state}</strong>
          <span>${event.note}</span>
        </div>
      </div>
    `).join("");
  } catch (error) {
    container.innerHTML = `<p>Timeline failed: ${error.message}</p>`;
  }
}

function buildNewCasePayload(form) {
  const values = new FormData(form);
  const now = Date.now();
  const errorCode = values.get("error_code");
  const bankSideErrors = ["payment_timed_out", "gateway_no_response", "bank_unavailable"];
  return {
    case_id: `USER_${now}`,
    order_id: `ORD_USER_${now}`,
    payment_id: `PAY_USER_${now}`,
    amount: Number(values.get("amount")),
    payment_method: values.get("payment_method"),
    bank: values.get("bank"),
    status: values.get("status"),
    error_code: errorCode,
    error_source: bankSideErrors.includes(errorCode) ? "bank" : "customer",
    error_step: errorCode === "session_expired" ? "checkout" : "authorization",
    upi_flow_completed: values.has("upi_flow_completed") ? 1 : 0,
    customer_reported_debit: values.has("customer_reported_debit") ? 1 : 0,
    webhook_received: values.has("webhook_received") ? 1 : 0,
    retry_count_24h: Number(values.get("retry_count_24h")),
    customer_type: values.get("customer_type"),
    checkout_duration_seconds: Number(values.get("checkout_duration_seconds")),
    downtime_active: values.has("downtime_active") ? 1 : 0,
    recovery_success: 0
  };
}

async function addCase(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button");
  button.disabled = true;
  button.textContent = "Analyzing...";
  setRunStatus("Adding merchant payment case and running trust-safe recovery decision...");
  try {
    const result = await fetchJson("/api/cases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildNewCasePayload(form))
    });
    renderMetrics(result.metrics);
    decisions = await fetchJson("/api/audit");
    renderRows(decisions);
    renderAudit(result.decision);
    const timeline = result.timeline || await fetchJson(`/api/timeline/${result.decision.case_id}`);
    document.getElementById("timeline").innerHTML = timeline.map((event) => `
      <div class="timeline-item">
        <div class="timeline-time">${event.time}</div>
        <div class="timeline-body">
          <span class="timeline-event">${event.event}</span>
          <strong>${event.state}</strong>
          <span>${event.note}</span>
        </div>
      </div>
    `).join("");
    setRunStatus(`Custom case added: ${result.decision.classification.replaceAll("_", " ")} -> ${result.decision.decision.replaceAll("_", " ")}.`);
  } catch (error) {
    setRunStatus(`Add case failed: ${error.message}`, true);
  } finally {
    button.disabled = false;
    button.textContent = "Add Case & Analyze";
  }
}

function renderAudit(item) {
  const detail = document.getElementById("auditDetail");
  detail.innerHTML = `
    <div class="audit-block">
      <span>Decision</span>
      <p>${item.decision.replaceAll("_", " ")} for ${item.order_id}</p>
    </div>
    <div class="audit-block">
      <span>Why</span>
      <p>${item.reason}</p>
    </div>
    <div class="audit-block">
      <span>Signals Checked</span>
      <p>${item.signals.join(", ")}</p>
    </div>
    <div class="audit-block">
      <span>Guardrail</span>
      <p>${item.guardrail}</p>
    </div>
    <div class="audit-block">
      <span>Customer Message</span>
      <p>${item.customer_message}</p>
    </div>
  `;
}

async function loadDashboard() {
  if (isRawFileOpen()) {
    setRunStatus("Wrong preview mode: this file was opened directly. Run python3 app.py and open http://127.0.0.1:8000 so APIs, metrics, and agent actions can work.", true);
    return;
  }
  try {
    const metrics = await fetchJson("/api/metrics");
    decisions = await fetchJson("/api/audit");
    renderMetrics(metrics);
    renderRows(decisions);
  } catch (error) {
    setRunStatus(`Dashboard load failed: ${error.message}`, true);
  }
}

async function runAgent() {
  const button = document.getElementById("runAgent");
  const tbody = document.getElementById("decisionRows");
  button.disabled = true;
  button.textContent = "Running...";
  tbody.classList.add("refreshing");
  setRunStatus("Running recovery agent across 1,000 synthetic payment cases...");
  try {
    const result = await fetchJson("/api/run-agent", { method: "POST" });
    renderMetrics(result.metrics);
    decisions = await fetchJson("/api/audit");
    renderRows(decisions);
    const now = new Date().toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    setRunStatus(`Completed at ${now}: ${result.metrics.safe_retry_cases} safe retries, ${result.metrics.limbo_risk_cases} limbo-risk cases, ${money.format(result.metrics.recovered_revenue)} recovered.`);
  } catch (error) {
    setRunStatus(`Agent run failed: ${error.message}. Make sure you opened http://127.0.0.1:8000, not the raw HTML file.`, true);
  } finally {
    button.disabled = false;
    button.textContent = "Run Recovery Agent";
    tbody.classList.remove("refreshing");
  }
}

document.getElementById("runAgent").addEventListener("click", runAgent);
document.getElementById("caseForm").addEventListener("submit", addCase);
loadDashboard();
