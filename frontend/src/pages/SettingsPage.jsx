import React, { useState, useEffect } from "react";
import { ShieldCheck, ToggleLeft, ToggleRight, User, Key, Sliders, CheckCircle, Save } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

export default function SettingsPage() {
  const { user } = useAuth();
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    loadPermissions();
  }, []);

  const loadPermissions = async () => {
    try {
      const perms = await api.tools.getPermissions();
      setPermissions(perms || []);
    } catch (e) {
      console.warn(e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (toolName, currentStatus) => {
    try {
      const newStatus = !currentStatus;
      await api.tools.updatePermission(toolName, newStatus);
      setPermissions((prev) =>
        prev.map((p) => (p.tool_name === toolName ? { ...p, is_allowed: newStatus } : p))
      );
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      alert(`Could not update permission: ${err.message}`);
    }
  };

  return (
    <div className="page-container" style={{ maxWidth: "1000px" }}>
      {/* Header */}
      <div style={{ marginBottom: "24px" }}>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "clamp(1.3rem, 3.5vw, 1.8rem)", fontWeight: 700 }}>
          Settings & Security Control
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          Manage user permissions, security guardrails, allowlists, and assistant configuration.
        </p>
      </div>

      {saveSuccess && (
        <div style={{
          padding: "10px 16px",
          borderRadius: "8px",
          background: "rgba(0, 245, 155, 0.15)",
          border: "1px solid rgba(0, 245, 155, 0.3)",
          color: "var(--accent-emerald)",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginBottom: "20px",
          fontSize: "0.85rem"
        }}>
          <CheckCircle size={16} />
          <span>Security permission updated successfully.</span>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
        
        {/* Tool Permissions Guardrails */}
        <div className="glass-panel" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "18px" }}>
            <ShieldCheck size={22} color="var(--accent-cyan)" />
            <div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700 }}>Tool Permission Guardrails</h3>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                Enable or disable specific desktop automation capabilities for your account.
              </p>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {permissions.map((p) => (
              <div
                key={p.tool_name}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "14px 16px",
                  borderRadius: "10px",
                  background: "rgba(255, 255, 255, 0.03)",
                  border: "1px solid rgba(255, 255, 255, 0.06)",
                  flexWrap: "wrap",
                  gap: "10px"
                }}
              >
                <div>
                  <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>
                    {p.display_name}
                  </div>
                  <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "2px" }}>
                    Tool identifier: <code>{p.tool_name}</code>
                  </div>
                </div>

                <button
                  onClick={() => handleToggle(p.tool_name, p.is_allowed)}
                  style={{
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    color: p.is_allowed ? "var(--accent-emerald)" : "var(--text-muted)",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    fontSize: "0.9rem",
                    fontWeight: 600
                  }}
                >
                  <span>{p.is_allowed ? "Allowed" : "Disabled"}</span>
                  {p.is_allowed ? <ToggleRight size={28} /> : <ToggleLeft size={28} />}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Security Allowlist Configuration */}
        <div className="glass-panel" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "18px" }}>
            <Sliders size={22} color="var(--accent-purple)" />
            <div>
              <h3 style={{ fontSize: "1.05rem", fontWeight: 700 }}>Security Allowlists</h3>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                Applications and directories Sadie is authorized to interact with.
              </p>
            </div>
          </div>

          <div className="grid-stack-mobile cols-2">
            <div className="glass-card" style={{ padding: "16px" }}>
              <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--accent-cyan)", marginBottom: "10px" }}>
                Allowed Applications
              </h4>
              <ul style={{ paddingLeft: "18px", fontSize: "0.85rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <li><code>calc.exe</code> (Calculator)</li>
                <li><code>notepad.exe</code> (Notepad)</li>
                <li><code>code</code> (Visual Studio Code)</li>
                <li><code>chrome</code> (Chrome Browser)</li>
              </ul>
            </div>

            <div className="glass-card" style={{ padding: "16px" }}>
              <h4 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--accent-purple)", marginBottom: "10px" }}>
                Allowed Directories
              </h4>
              <ul style={{ paddingLeft: "18px", fontSize: "0.85rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "4px" }}>
                <li><code>Documents</code></li>
                <li><code>Downloads</code></li>
                <li><code>Projects</code></li>
                <li><code>Study Materials</code></li>
              </ul>
            </div>
          </div>
        </div>

        {/* User Profile */}
        <div className="glass-panel" style={{ padding: "28px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
            <User size={22} color="var(--accent-emerald)" />
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>User Profile</h3>
          </div>

          <div style={{ fontSize: "0.9rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "6px" }}>
            <div><strong>Name:</strong> {user?.name || "Student Demo"}</div>
            <div><strong>Email:</strong> {user?.email || "student@sadie.ai"}</div>
            <div><strong>Status:</strong> Active & Authenticated</div>
          </div>
        </div>
      </div>
    </div>
  );
}
