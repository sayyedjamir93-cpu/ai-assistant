import React, { useState, useEffect } from "react";
import { StickyNote, Search, Plus, Trash2, Mic, Edit3, Save, X } from "lucide-react";
import { api } from "../services/api";

export default function NotesPage() {
  const [notes, setNotes] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [editingNote, setEditingNote] = useState(null);
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    loadNotes();
  }, [searchQuery]);

  const loadNotes = async () => {
    try {
      const data = await api.notes.getNotes(searchQuery);
      setNotes(data || []);
    } catch (e) {
      console.warn(e);
    }
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    try {
      const created = await api.notes.createNote({
        title: title.trim(),
        content: content.trim()
      });
      setNotes((prev) => [created, ...prev]);
      setTitle("");
      setContent("");
    } catch (err) {
      alert(err.message);
    }
  };

  const handleUpdateNote = async (e) => {
    e.preventDefault();
    if (!editingNote) return;
    try {
      const updated = await api.notes.updateNote(editingNote.id, {
        title: editingNote.title,
        content: editingNote.content
      });
      setNotes((prev) => prev.map((n) => (n.id === editingNote.id ? updated : n)));
      setEditingNote(null);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteNote = async (id) => {
    try {
      await api.notes.deleteNote(id);
      setNotes((prev) => prev.filter((n) => n.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  // Voice Note Recorder (Speak into Note)
  const handleVoiceNote = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition not supported.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const spoken = event.results[0][0].transcript;
      setContent((prev) => (prev ? `${prev} ${spoken}` : spoken));
      if (!title) {
        setTitle(spoken.split(".")[0].slice(0, 40));
      }
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  return (
    <div style={{ padding: "32px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "28px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.8rem", fontWeight: 700 }}>
            Notes & Voice Dictation
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Capture study concepts, algorithm notes, and dictate notes directly by voice.
          </p>
        </div>

        {/* Search Bar */}
        <div style={{ position: "relative", width: "300px" }}>
          <Search size={16} color="var(--text-muted)" style={{ position: "absolute", left: "14px", top: "12px" }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search notes by keyword..."
            className="input-glass"
            style={{ paddingLeft: "38px" }}
          />
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "24px" }}>
        
        {/* Create Note Card */}
        <div className="glass-panel" style={{ padding: "24px", height: "fit-content" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}>
            <Plus size={18} color="var(--accent-cyan)" /> New Note
          </h3>

          <form onSubmit={handleCreateNote} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div>
              <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                Note Title
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Python Recursion Summary"
                className="input-glass"
              />
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>Content</label>
                <button
                  type="button"
                  onClick={handleVoiceNote}
                  style={{
                    background: isListening ? "rgba(255, 42, 109, 0.2)" : "transparent",
                    border: "none",
                    color: isListening ? "var(--accent-rose)" : "var(--accent-cyan)",
                    cursor: "pointer",
                    fontSize: "0.75rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px"
                  }}
                >
                  <Mic size={14} /> {isListening ? "Listening..." : "Dictate by Voice"}
                </button>
              </div>
              <textarea
                rows={6}
                required
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Type or dictate your note..."
                className="input-glass"
              />
            </div>

            <button type="submit" className="btn-primary" style={{ padding: "10px" }}>
              Save Note
            </button>
          </form>
        </div>

        {/* Notes Grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "16px",
          height: "fit-content"
        }}>
          {notes.length === 0 ? (
            <div className="glass-card" style={{ padding: "40px", textAlign: "center", gridColumn: "1 / -1", color: "var(--text-muted)" }}>
              <StickyNote size={36} style={{ opacity: 0.3, marginBottom: "10px" }} />
              <p>No notes found. Create your first note or dictate using voice!</p>
            </div>
          ) : (
            notes.map((n) => (
              <div key={n.id} className="glass-card" style={{ padding: "18px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                <div>
                  <h4 style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--accent-cyan)", marginBottom: "8px" }}>
                    {n.title}
                  </h4>
                  <p style={{ fontSize: "0.88rem", color: "var(--text-primary)", lineHeight: "1.5", whiteSpace: "pre-wrap" }}>
                    {n.content}
                  </p>
                </div>

                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginTop: "16px",
                  paddingTop: "10px",
                  borderTop: "1px solid rgba(255, 255, 255, 0.06)",
                  fontSize: "0.75rem",
                  color: "var(--text-muted)"
                }}>
                  <span>{new Date(n.updated_at).toLocaleDateString()}</span>
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button
                      onClick={() => setEditingNote(n)}
                      style={{ background: "transparent", border: "none", color: "var(--text-secondary)", cursor: "pointer" }}
                    >
                      <Edit3 size={15} />
                    </button>
                    <button
                      onClick={() => handleDeleteNote(n.id)}
                      style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Edit Note Modal */}
      {editingNote && (
        <div style={{
          position: "fixed",
          inset: 0,
          background: "rgba(5, 8, 17, 0.8)",
          backdropFilter: "blur(12px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 100,
          padding: "20px"
        }}>
          <div className="glass-panel" style={{ width: "100%", maxWidth: "500px", padding: "28px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "1.2rem", fontWeight: 700 }}>Edit Note</h3>
              <button onClick={() => setEditingNote(null)} style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}>
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleUpdateNote} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <input
                type="text"
                value={editingNote.title}
                onChange={(e) => setEditingNote({ ...editingNote, title: e.target.value })}
                className="input-glass"
              />
              <textarea
                rows={8}
                value={editingNote.content}
                onChange={(e) => setEditingNote({ ...editingNote, content: e.target.value })}
                className="input-glass"
              />
              <button type="submit" className="btn-primary" style={{ padding: "10px" }}>
                <Save size={16} /> Save Changes
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
