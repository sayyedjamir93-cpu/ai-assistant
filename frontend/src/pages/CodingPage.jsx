import React, { useState } from "react";
import { Code2, Bug, BookOpen, CheckCircle, Sparkles, Copy, Check } from "lucide-react";
import { api } from "../services/api";

export default function CodingPage() {
  const [activeTab, setActiveTab] = useState("diagnostic"); // 'diagnostic' | 'concept' | 'review' | 'cheatsheet'

  // Diagnostic State
  const [errorMessage, setErrorMessage] = useState("IndexError: list index out of range");
  const [errorLanguage, setErrorLanguage] = useState("python");
  const [errorSnippet, setErrorSnippet] = useState("arr = [10, 20]\nprint(arr[5])");
  const [diagnosticResult, setDiagnosticResult] = useState(null);
  const [diagnosticLoading, setDiagnosticLoading] = useState(false);

  // Concept State
  const [conceptQuery, setConceptQuery] = useState("Python Recursion");
  const [conceptLang, setConceptLang] = useState("python");
  const [conceptResult, setConceptResult] = useState(null);
  const [conceptLoading, setConceptLoading] = useState(false);

  // Code Review State
  const [reviewCode, setReviewCode] = useState("def is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, n):\n        if n % i == 0:\n            return False\n    return True");
  const [reviewResult, setReviewResult] = useState(null);
  const [reviewLoading, setReviewLoading] = useState(false);

  const [copied, setCopied] = useState(false);

  const handleDiagnose = async (e) => {
    e.preventDefault();
    if (!errorMessage.trim()) return;
    setDiagnosticLoading(true);
    try {
      const res = await api.coding.diagnoseError(errorMessage, errorLanguage, errorSnippet);
      setDiagnosticResult(res);
    } catch (err) {
      alert(`Diagnostic error: ${err.message}`);
    } finally {
      setDiagnosticLoading(false);
    }
  };

  const handleExplainConcept = async (e) => {
    e.preventDefault();
    if (!conceptQuery.trim()) return;
    setConceptLoading(true);
    try {
      const res = await api.coding.explainConcept(conceptQuery, conceptLang);
      setConceptResult(res);
    } catch (err) {
      alert(`Concept error: ${err.message}`);
    } finally {
      setConceptLoading(false);
    }
  };

  const handleReviewCode = async (e) => {
    e.preventDefault();
    if (!reviewCode.trim()) return;
    setReviewLoading(true);
    try {
      const res = await api.coding.reviewCode(reviewCode, "python");
      setReviewResult(res);
    } catch (err) {
      alert(`Review error: ${err.message}`);
    } finally {
      setReviewLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.3rem, 3.5vw, 1.8rem)", fontWeight: 700 }}>
          Coding Mode & Technical Assistant
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          Debug runtime errors, unpack algorithms, review code snippets, and master programming concepts.
        </p>
      </div>

      {/* Mode Subtabs */}
      <div className="mobile-scroll-tabs" style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
        {[
          { id: "diagnostic", label: "Error Diagnostics", icon: Bug },
          { id: "concept", label: "Concept Explainer", icon: BookOpen },
          { id: "review", label: "Code Reviewer", icon: Code2 }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={isActive ? "btn-primary" : "btn-secondary"}
              style={{ padding: "8px 16px", fontSize: "0.82rem" }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* 1. Error Diagnostics View */}
      {activeTab === "diagnostic" && (
        <div className="grid-stack-mobile cols-1-2">
          {/* Diagnostic Form */}
          <div className="glass-panel" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Bug size={18} color="var(--accent-rose)" /> Diagnose Error / Stack Trace
            </h3>

            <form onSubmit={handleDiagnose} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Error Message or Exception
                </label>
                <input
                  type="text"
                  required
                  value={errorMessage}
                  onChange={(e) => setErrorMessage(e.target.value)}
                  placeholder="e.g. IndexError: list index out of range"
                  className="input-glass"
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Programming Language
                </label>
                <select
                  value={errorLanguage}
                  onChange={(e) => setErrorLanguage(e.target.value)}
                  className="input-glass"
                  style={{ cursor: "pointer" }}
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="cpp">C++</option>
                  <option value="c">C</option>
                  <option value="html_css">HTML / CSS</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Optional Code Snippet
                </label>
                <textarea
                  rows={5}
                  value={errorSnippet}
                  onChange={(e) => setErrorSnippet(e.target.value)}
                  placeholder="Paste relevant code lines..."
                  className="input-glass"
                  style={{ fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}
                />
              </div>

              <button type="submit" disabled={diagnosticLoading} className="btn-primary" style={{ padding: "12px", width: "100%" }}>
                {diagnosticLoading ? "Diagnosing..." : "Run Error Diagnostic"}
              </button>
            </form>
          </div>

          {/* Diagnostic Results Card */}
          <div className="glass-panel" style={{ padding: "24px" }}>
            {diagnosticResult ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{
                    padding: "4px 12px",
                    borderRadius: "6px",
                    background: "rgba(255, 42, 109, 0.15)",
                    border: "1px solid rgba(255, 42, 109, 0.3)",
                    color: "var(--accent-rose)",
                    fontWeight: 700,
                    fontSize: "0.85rem"
                  }}>
                    {diagnosticResult.error_name}
                  </span>
                  <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", textTransform: "uppercase" }}>
                    {diagnosticResult.language}
                  </span>
                </div>

                <div>
                  <h4 style={{ fontSize: "0.9rem", color: "var(--accent-cyan)", marginBottom: "4px" }}>Meaning:</h4>
                  <p style={{ fontSize: "0.92rem", color: "var(--text-primary)", lineHeight: "1.5" }}>
                    {diagnosticResult.meaning}
                  </p>
                </div>

                <div>
                  <h4 style={{ fontSize: "0.9rem", color: "var(--accent-purple)", marginBottom: "6px" }}>Possible Causes:</h4>
                  <ul style={{ paddingLeft: "20px", fontSize: "0.88rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                    {diagnosticResult.possible_causes.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 style={{ fontSize: "0.9rem", color: "var(--accent-emerald)", marginBottom: "6px" }}>How to Fix:</h4>
                  <ul style={{ paddingLeft: "20px", fontSize: "0.88rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                    {diagnosticResult.how_to_fix.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <h4 style={{ fontSize: "0.9rem", color: "var(--accent-cyan)" }}>Defensive Code Example:</h4>
                    <button
                      onClick={() => copyToClipboard(diagnosticResult.code_example)}
                      style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", display: "flex", alignItems: "center", gap: "4px", fontSize: "0.75rem" }}
                    >
                      {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
                      {copied ? "Copied" : "Copy Code"}
                    </button>
                  </div>
                  <pre className="code-container">
                    <code>{diagnosticResult.code_example}</code>
                  </pre>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: "center", padding: "60px 20px", color: "var(--text-muted)" }}>
                <Bug size={40} style={{ opacity: 0.3, marginBottom: "12px" }} />
                <p>Enter an error message on the left to receive a structured diagnostic and fix.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 2. Concept Explainer View */}
      {activeTab === "concept" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          <div className="glass-panel" style={{ padding: "20px" }}>
            <form onSubmit={handleExplainConcept} style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <input
                type="text"
                value={conceptQuery}
                onChange={(e) => setConceptQuery(e.target.value)}
                placeholder="Enter concept (e.g., Recursion, Pointers, Binary Trees)..."
                className="input-glass"
                style={{ flex: 1, minWidth: "200px" }}
              />
              <select
                value={conceptLang}
                onChange={(e) => setConceptLang(e.target.value)}
                className="input-glass"
                style={{ width: "130px", cursor: "pointer" }}
              >
                <option value="python">Python</option>
                <option value="cpp">C++</option>
                <option value="javascript">JavaScript</option>
                <option value="c">C</option>
              </select>
              <button type="submit" disabled={conceptLoading} className="btn-primary" style={{ padding: "10px 20px" }}>
                {conceptLoading ? "Explaining..." : "Explain"}
              </button>
            </form>
          </div>

          {conceptResult && (
            <div className="glass-panel" style={{ padding: "24px 16px", display: "flex", flexDirection: "column", gap: "18px" }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--accent-cyan)" }}>
                {conceptResult.summary}
              </h3>
              <div style={{ fontSize: "0.92rem", lineHeight: "1.7", color: "var(--text-primary)", whiteSpace: "pre-wrap" }}>
                {conceptResult.explanation}
              </div>
              <div>
                <h4 style={{ fontSize: "0.95rem", color: "var(--accent-emerald)", marginBottom: "8px" }}>Worked Code Example:</h4>
                <pre className="code-container">
                  <code>{conceptResult.example_code}</code>
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Code Reviewer View */}
      {activeTab === "review" && (
        <div className="grid-stack-mobile cols-2">
          <div className="glass-panel" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "14px" }}>Paste Code to Review</h3>
            <textarea
              rows={12}
              value={reviewCode}
              onChange={(e) => setReviewCode(e.target.value)}
              className="input-glass"
              style={{ fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}
            />
            <button onClick={handleReviewCode} disabled={reviewLoading} className="btn-primary" style={{ width: "100%", marginTop: "14px", padding: "12px" }}>
              {reviewLoading ? "Analyzing..." : "Review Code & Suggest Improvements"}
            </button>
          </div>

          <div className="glass-panel" style={{ padding: "24px" }}>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "14px", color: "var(--accent-purple)" }}>
              Analysis & Feedback
            </h3>
            {reviewResult ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  Lines analyzed: {reviewResult.lines_analyzed}
                </div>
                <div style={{ fontSize: "0.92rem", lineHeight: "1.6", whiteSpace: "pre-wrap" }}>
                  {reviewResult.feedback}
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", textAlign: "center", padding: "40px 0" }}>
                Click "Review Code" on the left to analyze the snippet.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
