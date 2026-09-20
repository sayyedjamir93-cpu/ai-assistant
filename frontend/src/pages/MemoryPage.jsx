import React, { useState, useEffect } from "react";
import { BrainCircuit, Plus, Trash2, Shield, Info, AlertTriangle } from "lucide-react";
import { api } from "../services/api";

export default function MemoryPage() {
  const [memories, setMemories] = useState([]);
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadMemories();
  }, []);

  const loadMemories = async () => {
    try {
      const list = await api.memory.getMemories();
      setMemories(list || []);
    } catch (e) {
      console.warn(e);
    }
  };

  const handleAddMemory = async (e) => {
    e.preventDefault();
    if (!key.trim() || !value.trim()) return;
    setLoading(true);
    try {
      const created = await api.memory.addMemory(key.trim(), value.trim());
      setMemories((prev) => [created, ...prev]);
      setKey("");
      setValue("");
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.memory.deleteMemory(id);
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to delete all personal memories? This action cannot be undone.")) {
      return;
    }
    try {
      await api.memory.clearAll();
      setMemories([]);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ padding: "32px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "28px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.8rem", fontWeight: 700 }}>
            Controlled Personal Memory
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Review, manage, or delete facts that SADIE has been explicitly asked to remember.
          </p>
        </div>

        {memories.length > 0 && (
          <button onClick={handleClearAll} className="btn-danger" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <Trash2 size={14} /> Clear All Memories
          </button>
        )}
      </div>

      {/* Privacy Notice Banner */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "12px",
        padding: "14px 18px",
        borderRadius: "12px",
        background: "rgba(0, 229, 255, 0.08)",
        border: "1px solid rgba(0, 229, 255, 0.2)",
        marginBottom: "24px",
        fontSize: "0.88rem",
        color: "var(--text-secondary)"
      }}>
        <Shield size={20} color="var(--accent-cyan)" />
        <span>
          <strong>Zero Secret Tracking:</strong> SADIE only retains information when you explicitly say <em>"Remember that..."</em> or add facts below. All memories are transparently editable.
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: "24px" }}>
        
        {/* Add Memory Fact */}
        <div className="glass-panel" style={{ padding: "24px", height: "fit-content" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Plus size={18} color="var(--accent-cyan)" /> Teach SADIE a Fact
          </h3>

          <form onSubmit={handleAddMemory} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                Topic / Subject Key
              </label>
              <input
                type="text"
                required
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="e.g. Python Project Path, Target Graduation Year"
                className="input-glass"
              />
            </div>

            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                Fact / Detail
              </label>
              <textarea
                rows={4}
                required
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="e.g. My primary Python folder is inside Projects/AI-Lab"
                className="input-glass"
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary" style={{ padding: "10px" }}>
              {loading ? "Saving..." : "Store in Memory"}
            </button>
          </form>
        </div>

        {/* Stored Memories List */}
        <div className="glass-panel" style={{ padding: "24px" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
            Stored Memories ({memories.length})
          </h3>

          {memories.length === 0 ? (
            <div style={{ textAlign: "center", padding: "40px 20px", color: "var(--text-muted)" }}>
              <BrainCircuit size={36} style={{ opacity: 0.3, marginBottom: "10px" }} />
              <p>No personal memories stored. You can ask Sadie "Remember that..." anytime!</p>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {memories.map((m) => (
                <div
                  key={m.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    padding: "14px 18px",
                    borderRadius: "10px",
                    background: "rgba(255, 255, 255, 0.03)",
                    border: "1px solid rgba(255, 255, 255, 0.08)"
                  }}
                >
                  <div>
                    <div style={{ fontSize: "0.82rem", fontWeight: 600, color: "var(--accent-cyan)", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                      {m.key}
                    </div>
                    <div style={{ fontSize: "0.95rem", color: "var(--text-primary)", marginTop: "4px", lineHeight: "1.4" }}>
                      {m.value}
                    </div>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginTop: "6px" }}>
                      Stored on {new Date(m.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  <button
                    onClick={() => handleDelete(m.id)}
                    title="Delete Memory"
                    style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer", padding: "4px" }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
