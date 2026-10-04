import { useState, useEffect } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [token, setToken] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evidence, setEvidence] = useState([]);
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [documents, setDocuments] = useState([]);
  async function handleAuth() {
    setError("");
    setMessage("");

    const endpoint = mode === "login" ? "/login" : "/register";

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Authentication failed");
      }

      if (mode === "register") {
        setMessage("Account created successfully. Please sign in.");
        setMode("login");
        setPassword("");
      } else {
        setToken(data.access_token);
        setEmail("");
        setPassword("");
      }
    } catch (err) {
      setError(err.message);
    }
  }
  async function loadDocuments(authToken) {
  try {
    const response = await fetch(`${API_URL}/documents`, {
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Could not load documents");
    }

    setDocuments(data.documents || []);
  } catch (err) {
    setError(err.message);
  }
}
useEffect(() => {
  if (token) {
    loadDocuments(token);
  }
}, [token]);
  async function uploadDocument() {
    if (!selectedFile) return;

    setUploading(true);
    setError("");
    setMessage("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Document upload failed");
      }

      setMessage(
        `${data.filename} uploaded and indexed successfully.`
      );

      setSelectedFile(null);

      const input = document.getElementById("document-upload");

      if (input) {
        input.value = "";
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }
  async function deleteDocument(documentId, filename) {
  const confirmed = window.confirm(
    `Delete "${filename}" from your knowledge base?`
  );

  if (!confirmed) return;

  try {
    const response = await fetch(
      `${API_URL}/documents/${documentId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Could not delete document");
    }

    setMessage(`${filename} deleted successfully.`);

    await loadDocuments(token);
  } catch (err) {
    setError(err.message);
  }
}

  async function askAgent() {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");
    setEvidence([]);

    try {
      const response = await fetch(`${API_URL}/agent`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          query: question,
          top_k: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Agent request failed");
      }

      setAnswer(data.answer);
      setEvidence(data.evidence || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-left">
          <div className="brand">
            <div className="brand-icon">KI</div>
            <span>Knowledge Intelligence</span>
          </div>

          <div className="hero-content">
            <div className="eyebrow">
              AI-POWERED KNOWLEDGE
            </div>

            <h1>
              Turn your documents
              <br />
              into <span>intelligent decisions.</span>
            </h1>

            <p>
              Upload your organization's knowledge, ask questions,
              and get answers grounded in your authorized documents.
            </p>

            <div className="features">
              <div>
                <strong>01</strong>
                <span>Evidence-grounded answers</span>
              </div>

              <div>
                <strong>02</strong>
                <span>Permission-aware knowledge</span>
              </div>

              <div>
                <strong>03</strong>
                <span>Source-level traceability</span>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-right">
          <div className="auth-card">
            <div className="auth-logo">KI</div>

            <div className="auth-heading">
              <h2>
                {mode === "login"
                  ? "Welcome back"
                  : "Create your account"}
              </h2>

              <p>
                {mode === "login"
                  ? "Sign in to your knowledge workspace."
                  : "Create your secure knowledge workspace."}
              </p>
            </div>

            <div className="auth-tabs">
              <button
                className={mode === "login" ? "active" : ""}
                onClick={() => {
                  setMode("login");
                  setError("");
                  setMessage("");
                }}
              >
                Sign in
              </button>

              <button
                className={mode === "register" ? "active" : ""}
                onClick={() => {
                  setMode("register");
                  setError("");
                  setMessage("");
                }}
              >
                Register
              </button>
            </div>

            <label>Email address</label>

            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <button
              className="primary-button"
              onClick={handleAuth}
            >
              {mode === "login"
                ? "Sign in →"
                : "Create account →"}
            </button>

            {message && (
              <div className="success-message">
                {message}
              </div>
            )}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">KI</div>

          <div>
            <strong>Knowledge</strong>
            <span>Intelligence</span>
          </div>
        </div>

        <div className="sidebar-label">
          WORKSPACE
        </div>

        <div className="sidebar-item active">
          ◈ &nbsp; Knowledge Base
        </div>

        <div className="sidebar-documents">
  <div className="sidebar-item">
    ▣ &nbsp; Documents
  </div>

  {documents.length === 0 ? (
    <div className="no-documents">
      No documents yet
    </div>
  ) : (
    <div className="document-list">
      {documents.map((document) => (
        <div
          className="document-item"
          key={document.id}
        >
          <div className="document-info">
            <span className="document-icon">
              PDF
            </span>

            <span
              className="document-name"
              title={document.filename}
            >
              {document.filename}
            </span>
          </div>

          <button
            className="delete-document"
            onClick={() =>
              deleteDocument(
                document.id,
                document.filename
              )
            }
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )}
</div>

        <div className="sidebar-bottom">
          <button
            className="sidebar-logout"
            onClick={() => {
              setToken("");
              setAnswer("");
              setEvidence([]);
              setQuestion("");
            }}
          >
            Sign out
          </button>
        </div>
      </aside>

      <main className="workspace">
        <div className="workspace-header">
          <div className="eyebrow">
            KNOWLEDGE WORKSPACE
          </div>

          <h1>Your organization's intelligence</h1>

          <p>
            Upload documents and ask questions grounded in
            your authorized knowledge.
          </p>
        </div>

        <div className="workspace-grid">
          <section className="upload-card">
            <div className="section-label">
              KNOWLEDGE BASE
            </div>

            <h2>Add a document</h2>

            <label
              htmlFor="document-upload"
              className="upload-area"
            >
              <div className="upload-icon">↑</div>

              <strong>
                {selectedFile
                  ? selectedFile.name
                  : "Upload a PDF document"}
              </strong>

              <span>
                {selectedFile
                  ? "Ready to upload"
                  : "Click to choose a PDF"}
              </span>
            </label>

            <input
              id="document-upload"
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => {
                setSelectedFile(
                  e.target.files?.[0] || null
                );
              }}
              hidden
            />

            <button
              className="upload-button"
              disabled={!selectedFile || uploading}
              onClick={uploadDocument}
            >
              {uploading
                ? "Processing..."
                : "Upload & Index"}
            </button>
          </section>

          <section className="query-card">
            <div className="section-label">
              ASK YOUR KNOWLEDGE
            </div>

            <h2>What would you like to know?</h2>

            <textarea
              value={question}
              onChange={(e) =>
                setQuestion(e.target.value)
              }
              placeholder="Ask a question about your documents..."
            />

            <div className="query-footer">
              <span>
                Answers are generated from retrieved evidence.
              </span>

              <button
                className="ask-button"
                onClick={askAgent}
                disabled={loading}
              >
                {loading
                  ? "Thinking..."
                  : "Ask Agent →"}
              </button>
            </div>
          </section>
        </div>

        {message && (
          <div className="success-message">
            {message}
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {answer && (
          <section className="result-card">
            <div className="section-label">
              AGENT RESPONSE
            </div>

            <div className="answer-text">
              {answer}
            </div>
          </section>
        )}

        {evidence.length > 0 && (
          <section className="evidence-section">
            <div className="section-label">
              SOURCE EVIDENCE
            </div>

            <h2>
              Retrieved from your knowledge base
            </h2>

            <div className="evidence-grid">
              {evidence.map((item) => (
                <div
                  className="evidence-card"
                  key={item.chunk_id}
                >
                  <div className="evidence-meta">
                    <strong>{item.filename}</strong>

                    <span>
                      Page {item.page_number}
                    </span>
                  </div>

                  <p>{item.text}</p>

                  <div className="relevance">
                    Relevance:{" "}
                    {item.score.toFixed(3)}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;