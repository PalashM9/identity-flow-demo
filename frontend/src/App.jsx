import { useEffect, useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";
const API_USERNAME = "demo_user";
const API_PASSWORD = "demo_password_change_me";

function createAuthHeader() {
  return `Basic ${btoa(`${API_USERNAME}:${API_PASSWORD}`)}`;
}

function statusClass(status) {
  if (status === "VERIFIED") return "status verified";
  if (status === "REJECTED") return "status rejected";
  return "status review";
}

function formatDate(dateValue) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric"
  }).format(new Date(`${dateValue}T00:00:00`));
}

export default function App() {
  const [people, setPeople] = useState([]);
  const [selectedPersonId, setSelectedPersonId] = useState("");
  const [health, setHealth] = useState("checking");
  const [loadingPeople, setLoadingPeople] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [correlationId, setCorrelationId] = useState(
    `ui-demo-${crypto.randomUUID()}`
  );
  const [uploadFile, setUploadFile] = useState(null);

  const selectedPerson = useMemo(
    () => people.find((person) => person.id === selectedPersonId),
    [people, selectedPersonId]
  );

  async function loadHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error("Health check failed");
      setHealth("online");
    } catch {
      setHealth("offline");
    }
  }

  async function loadPeople() {
    setLoadingPeople(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/v1/demo-people`, {
        headers: {
          Authorization: createAuthHeader()
        }
      });

      if (!response.ok) {
        throw new Error(`Could not load demo people: HTTP ${response.status}`);
      }

      const data = await response.json();
      setPeople(data);

      if (data.length > 0) {
        setSelectedPersonId(data[0].id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingPeople(false);
    }
  }

  useEffect(() => {
    loadHealth();
    loadPeople();
  }, []);

  async function verifyDemoDocument() {
    if (!selectedPersonId) return;

    setProcessing(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/v1/verifications/${selectedPersonId}`,
        {
          method: "POST",
          headers: {
            Authorization: createAuthHeader(),
            "X-Correlation-Id": correlationId
          }
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Verification request failed.");
      }

      setResult({
        ...data,
        mode: "Simulated document verification"
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  }

  async function verifyUploadedDocument() {
    if (!selectedPersonId || !uploadFile) {
      setError("Select a fictional demo identity and upload a fictional PNG or JPEG card.");
      return;
    }

    setProcessing(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", uploadFile);

      const response = await fetch(
        `${API_BASE_URL}/v1/verifications/upload/${selectedPersonId}`,
        {
          method: "POST",
          headers: {
            Authorization: createAuthHeader(),
            "X-Correlation-Id": correlationId
          },
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "OCR verification request failed.");
      }

      setResult({
        ...data,
        mode: `OCR upload: ${uploadFile.name}`
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  }

  function resetDemo() {
    setResult(null);
    setError("");
    setUploadFile(null);
    setCorrelationId(`ui-demo-${crypto.randomUUID()}`);
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <div>
          <h1>Identity Flow Console</h1>
          <p className="subtitle">
            OCR, deterministic decisioning, audit events, signed webhooks, Node.js integration,
            Terraform, and MCP.
          </p>
        </div>

        <div className={`health-pill ${health}`}>
          <span className="health-dot" />
          API {health === "online" ? "Online" : health === "offline" ? "Offline" : "Checking"}
        </div>
      </header>



      <section className="dashboard-grid">
        <section className="panel people-panel">
          <div className="panel-header">
            <div>
              <p className="section-kicker">Step 1</p>
              <h2>Fictional identity records</h2>
            </div>
            <button className="text-button" onClick={loadPeople} disabled={loadingPeople}>
              Refresh
            </button>
          </div>

          {loadingPeople ? (
            <p className="muted">Loading fictional identities…</p>
          ) : (
            <div className="people-list">
              {people.map((person) => (
                <button
                  className={`person-card ${person.id === selectedPersonId ? "selected" : ""}`}
                  key={person.id}
                  onClick={() => {
                    setSelectedPersonId(person.id);
                    setResult(null);
                    setError("");
                  }}
                >
                  <div className="avatar">{person.full_name.charAt(0)}</div>
                  <div className="person-details">
                    <strong>{person.full_name}</strong>
                    <span>{person.document_number}</span>
                    <small>
                      DOB: {formatDate(person.date_of_birth)} · Expiry:{" "}
                      {formatDate(person.expires_on)}
                    </small>
                  </div>
                  {person.id === selectedPersonId && <span className="selected-mark">✓</span>}
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="panel action-panel">
          <div className="panel-header">
            <div>
              <p className="section-kicker">Step 2</p>
              <h2>Run verification workflow</h2>
            </div>
          </div>

          {selectedPerson ? (
            <div className="selected-summary">
              <span className="summary-label">Selected fictional applicant</span>
              <strong>{selectedPerson.full_name}</strong>
              <span>{selectedPerson.document_number}</span>
            </div>
          ) : (
            <p className="muted">Select a fictional identity record.</p>
          )}

          <label className="field-label" htmlFor="correlation">
            Correlation ID
          </label>
          <input
            id="correlation"
            value={correlationId}
            onChange={(event) => setCorrelationId(event.target.value)}
            placeholder="ui-demo-..."
          />

          <div className="action-block">
            <h3>Option A — Simulated document</h3>
            <p>
              Uses the seeded fictional OCR text. This demonstrates API orchestration, deterministic
              decisioning, audit logging, an outbox event, and HMAC-signed webhook delivery.
            </p>
            <button
              className="primary-button"
              onClick={verifyDemoDocument}
              disabled={!selectedPersonId || processing || health !== "online"}
            >
              {processing ? "Processing…" : "Verify demo document"}
            </button>
          </div>

          <div className="divider" />

          <div className="action-block">
            <h3>Option B — OCR upload</h3>
            <p>
              Upload only a fictional image generated in <code>demo_data</code>. Never upload a real
              identity document.
            </p>

            <label className="file-input-label">
              <input
                type="file"
                accept=".png,.jpg,.jpeg"
                onChange={(event) => setUploadFile(event.target.files?.[0] || null)}
              />
              <span>{uploadFile ? uploadFile.name : "Choose fictional demo card"}</span>
            </label>

            <button
              className="secondary-button"
              onClick={verifyUploadedDocument}
              disabled={!selectedPersonId || !uploadFile || processing || health !== "online"}
            >
              {processing ? "Running OCR…" : "Upload and run OCR"}
            </button>
          </div>

          <button className="reset-button" onClick={resetDemo} disabled={processing}>
            Reset current demo
          </button>
        </section>
      </section>

      {error && (
        <section className="result-card error-card">
          <div>
            <p className="section-kicker">Request failed</p>
            <h2>Integration response</h2>
          </div>
          <p>{error}</p>
        </section>
      )}

      {result && (
        <section className="result-card">
          <div className="result-heading">
            <div>
              <p className="section-kicker">Step 3 and 4</p>
              <h2>Verification result</h2>
              <p className="muted">{result.mode}</p>
            </div>
            <span className={statusClass(result.status)}>{result.status.replace("_", " ")}</span>
          </div>

          <div className="result-grid">
            <div>
              <span>Decision reason</span>
              <strong>{result.decision_reason}</strong>
            </div>
            <div>
              <span>Application ID</span>
              <code>{result.application_id}</code>
            </div>
            <div>
              <span>Correlation ID</span>
              <code>{result.correlation_id}</code>
            </div>
            <div>
              <span>Webhook behavior</span>
              <strong>HMAC-signed event emitted to Node.js receiver</strong>
            </div>
          </div>

        </section>
      )}
    </main>
  );
}