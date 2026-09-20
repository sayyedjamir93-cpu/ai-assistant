import React, { useState, useEffect } from "react";
import {
  Wrench,
  Cpu,
  HardDrive,
  Activity,
  Folder,
  ExternalLink,
  Search,
  CheckCircle,
  AlertCircle,
  Calculator,
  FileText,
  Code,
  Globe,
  MessageSquare,
  Phone,
  Send,
  Plus,
  Trash2,
  Play,
  Music,
  Tv,
  Radio,
  PlayCircle
} from "lucide-react";
import { api } from "../services/api";

export default function ToolsPage() {
  const [sysInfo, setSysInfo] = useState(null);
  const [loadingSys, setLoadingSys] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [actionFeedback, setActionFeedback] = useState(null);

  // Media Player (YouTube & Spotify) State
  const [mediaPlatform, setMediaPlatform] = useState("youtube");
  const [mediaQuery, setMediaQuery] = useState("");
  const [mediaLoading, setMediaLoading] = useState(false);

  // Contacts & WhatsApp State
  const [contacts, setContacts] = useState([]);
  const [contactName, setContactName] = useState("");
  const [contactPhone, setContactPhone] = useState("");
  const [targetContact, setTargetContact] = useState("Sakshi");
  const [msgText, setMsgText] = useState("Hii");

  useEffect(() => {
    loadSysInfo();
    loadContacts();
    const interval = setInterval(loadSysInfo, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadContacts = async () => {
    try {
      const list = await api.contacts.getContacts();
      setContacts(list || []);
    } catch (e) {
      console.warn("Could not load contacts:", e);
    }
  };

  const handleAddContact = async (e) => {
    e.preventDefault();
    if (!contactName.trim()) return;
    try {
      const created = await api.contacts.createContact(contactName.trim(), contactPhone.trim());
      setContacts((prev) => [...prev.filter(c => c.id !== created.id), created]);
      setContactName("");
      setContactPhone("");
      setActionFeedback({ success: true, message: `Saved contact ${created.name} for WhatsApp messaging.` });
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (err) {
      alert(`Could not save contact: ${err.message}`);
    }
  };

  const handleDeleteContact = async (id) => {
    try {
      await api.contacts.deleteContact(id);
      setContacts((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleSendWhatsApp = async (e) => {
    if (e) e.preventDefault();
    if (!targetContact.trim() || !msgText.trim()) return;
    try {
      const res = await api.contacts.sendMessage(targetContact.trim(), msgText.trim());
      setActionFeedback({ success: true, message: res.status_message || `Opened WhatsApp to message ${targetContact}` });
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      setActionFeedback({ success: false, message: err.message });
      setTimeout(() => setActionFeedback(null), 5000);
    }
  };


  const loadSysInfo = async () => {
    try {
      const data = await api.system.getInfo();
      setSysInfo(data);
    } catch (e) {
      console.warn(e);
    } finally {
      setLoadingSys(false);
    }
  };

  const handleLaunchApp = async (appName) => {
    try {
      const res = await api.tools.executeTool("open_application", { app_name: appName });
      setActionFeedback({ success: true, message: res.result?.message || `Opened ${appName}` });
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      setActionFeedback({ success: false, message: err.message });
      setTimeout(() => setActionFeedback(null), 5000);
    }
  };

  const handleOpenFolder = async (folderName) => {
    try {
      const res = await api.tools.executeTool("open_folder", { folder_name: folderName });
      setActionFeedback({ success: true, message: res.result?.message || `Opened folder: ${folderName}` });
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      setActionFeedback({ success: false, message: err.message });
      setTimeout(() => setActionFeedback(null), 5000);
    }
  };

  const handleWebSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const res = await api.tools.executeTool("web_search", { query: searchQuery.trim() });
      setSearchResults(res.result?.results || []);
    } catch (err) {
      alert(`Search error: ${err.message}`);
    } finally {
      setSearchLoading(false);
    }
  };

  const handlePlayMedia = async (platform = mediaPlatform, query = mediaQuery) => {
    try {
      setMediaLoading(true);
      const res = await api.tools.playMedia(platform, query);
      setActionFeedback({
        success: true,
        message: res.message || res.result?.message || `Playing on ${platform.toUpperCase()}!`
      });
      setTimeout(() => setActionFeedback(null), 4000);
    } catch (err) {
      setActionFeedback({ success: false, message: `Could not play media: ${err.message}` });
      setTimeout(() => setActionFeedback(null), 5000);
    } finally {
      setMediaLoading(false);
    }
  };

  const apps = [
    { name: "YouTube", executable: "youtube", icon: Tv, desc: "Watch Videos & Tutorials" },
    { name: "Spotify", executable: "spotify", icon: Music, desc: "Stream Music & Podcasts" },
    { name: "VS Code", executable: "code", icon: Code, desc: "Visual Studio Code" },
    { name: "Calculator", executable: "calc.exe", icon: Calculator, desc: "Windows Calculator" },
    { name: "Notepad", executable: "notepad.exe", icon: FileText, desc: "Text & Code Scratchpad" },
    { name: "Web Browser", executable: "chrome", icon: Globe, desc: "Chrome / Default Browser" }
  ];

  const folders = [
    { name: "Documents", desc: "User Documents Directory" },
    { name: "Downloads", desc: "Downloaded Assignments & Files" },
    { name: "Projects", desc: "Active Code & Workspace" },
    { name: "Study Materials", desc: "Course Notes & Books" }
  ];

  return (
    <div style={{ padding: "32px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "28px" }}>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.8rem", fontWeight: 700 }}>
          Desktop Tools & System Diagnostics
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Sandboxed launcher for allowlisted applications, folder navigation, web search, and hardware telemetry.
        </p>
      </div>

      {actionFeedback && (
        <div style={{
          padding: "12px 18px",
          borderRadius: "10px",
          background: actionFeedback.success ? "rgba(0, 245, 155, 0.15)" : "rgba(255, 42, 109, 0.15)",
          border: `1px solid ${actionFeedback.success ? "rgba(0, 245, 155, 0.3)" : "rgba(255, 42, 109, 0.3)"}`,
          color: actionFeedback.success ? "var(--accent-emerald)" : "var(--accent-rose)",
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "20px"
        }}>
          {actionFeedback.success ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
          <span>{actionFeedback.message}</span>
        </div>
      )}

      {/* Hardware / System Telemetry Gauges */}
      {sysInfo && (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
          gap: "18px",
          marginBottom: "28px"
        }}>
          <div className="glass-card" style={{ padding: "20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>CPU Utilization</span>
              <Cpu size={20} color="var(--accent-cyan)" />
            </div>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--accent-cyan)" }}>
              {sysInfo.cpu?.current_usage_percent}%
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
              {sysInfo.cpu?.total_cores} Cores ({sysInfo.cpu?.physical_cores} Physical)
            </p>
          </div>

          <div className="glass-card" style={{ padding: "20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>System Memory</span>
              <Activity size={20} color="var(--accent-purple)" />
            </div>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--accent-purple)" }}>
              {sysInfo.memory?.used_gb} / {sysInfo.memory?.total_gb} GB
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
              {sysInfo.memory?.percent_used}% Used ({sysInfo.memory?.available_gb} GB Free)
            </p>
          </div>

          <div className="glass-card" style={{ padding: "20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Primary Storage</span>
              <HardDrive size={20} color="var(--accent-emerald)" />
            </div>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "var(--accent-emerald)" }}>
              {sysInfo.storage?.free_gb} GB Free
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
              Total: {sysInfo.storage?.total_gb} GB ({sysInfo.storage?.percent_used}% Used)
            </p>
          </div>

          <div className="glass-card" style={{ padding: "20px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
              <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>OS & Runtime</span>
              <Wrench size={20} color="var(--accent-amber)" />
            </div>
            <div style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text-primary)" }}>
              {sysInfo.os?.system} {sysInfo.os?.release}
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
              Python {sysInfo.runtime?.python_version} • SADIE v{sysInfo.application?.version}
            </p>
          </div>
        </div>
      )}

      {/* Applications & Folders Launchers */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", marginBottom: "28px" }}>
        
        {/* Approved Apps */}
        <div className="glass-panel" style={{ padding: "24px" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
            Approved Applications
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            {apps.map((a, i) => {
              const Icon = a.icon;
              return (
                <button
                  key={i}
                  onClick={() => handleLaunchApp(a.executable)}
                  className="glass-card"
                  style={{
                    padding: "16px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    textAlign: "left",
                    cursor: "pointer",
                    border: "1px solid rgba(255, 255, 255, 0.08)"
                  }}
                >
                  <Icon size={24} color="var(--accent-cyan)" style={{ marginBottom: "8px" }} />
                  <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>{a.name}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>{a.desc}</div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Approved Folders */}
        <div className="glass-panel" style={{ padding: "24px" }}>
          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "16px" }}>
            Approved Folders
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            {folders.map((f, i) => (
              <button
                key={i}
                onClick={() => handleOpenFolder(f.name)}
                className="glass-card"
                style={{
                  padding: "16px",
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                  textAlign: "left",
                  cursor: "pointer",
                  border: "1px solid rgba(255, 255, 255, 0.08)"
                }}
              >
                <Folder size={24} color="var(--accent-purple)" style={{ marginBottom: "8px" }} />
                <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>{f.name}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "2px" }}>{f.desc}</div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Web Search Tool */}
      <div className="glass-panel" style={{ padding: "24px" }}>
        <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "14px" }}>
          Live Web Search Tool
        </h3>
        <form onSubmit={handleWebSearch} style={{ display: "flex", gap: "12px", marginBottom: "18px" }}>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search topic or news (e.g. 'FastAPI tutorial', 'Latest Python 3.12 features')..."
            className="input-glass"
            style={{ flex: 1 }}
          />
          <button type="submit" disabled={searchLoading} className="btn-primary" style={{ padding: "0 24px" }}>
            <Search size={16} /> {searchLoading ? "Searching..." : "Search"}
          </button>
        </form>

        {searchResults.length > 0 && (
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {searchResults.map((r, i) => (
              <div key={i} className="glass-card" style={{ padding: "14px 18px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
                  <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--accent-cyan)" }}>
                    {r.title}
                  </h4>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{r.source}</span>
                </div>
                <p style={{ fontSize: "0.85rem", color: "var(--text-primary)", lineHeight: "1.4" }}>
                  {r.summary}
                </p>
                {r.url && (
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ fontSize: "0.75rem", color: "var(--accent-cyan)", display: "inline-flex", alignItems: "center", gap: "4px", marginTop: "6px", textDecoration: "none" }}
                  >
                    Visit Source <ExternalLink size={12} />
                  </a>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Media & Entertainment Player (YouTube & Spotify) */}
      <div className="glass-panel" style={{ padding: "24px", marginTop: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <Music size={22} color="var(--accent-cyan)" />
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>Entertainment & Media Player (YouTube & Spotify)</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              Say or type: <em>"Play Bohemian Rhapsody on Spotify"</em> or <em>"Play Python tutorial on YouTube"</em> to stream songs and videos.
            </p>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "20px" }}>
          {/* Quick Play Form */}
          <div className="glass-card" style={{ padding: "20px" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--accent-cyan)", marginBottom: "12px" }}>
              Launch Song / Video
            </h4>
            
            <form onSubmit={(e) => { e.preventDefault(); handlePlayMedia(); }} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                  Select Platform
                </label>
                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    type="button"
                    onClick={() => setMediaPlatform("youtube")}
                    style={{
                      flex: 1,
                      padding: "10px",
                      borderRadius: "8px",
                      background: mediaPlatform === "youtube" ? "rgba(255, 0, 51, 0.2)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${mediaPlatform === "youtube" ? "rgba(255, 0, 51, 0.5)" : "rgba(255, 255, 255, 0.08)"}`,
                      color: mediaPlatform === "youtube" ? "#ff4d4d" : "var(--text-secondary)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "8px",
                      cursor: "pointer",
                      fontWeight: 600
                    }}
                  >
                    <Tv size={16} /> YouTube
                  </button>

                  <button
                    type="button"
                    onClick={() => setMediaPlatform("spotify")}
                    style={{
                      flex: 1,
                      padding: "10px",
                      borderRadius: "8px",
                      background: mediaPlatform === "spotify" ? "rgba(30, 215, 96, 0.2)" : "rgba(255, 255, 255, 0.05)",
                      border: `1px solid ${mediaPlatform === "spotify" ? "rgba(30, 215, 96, 0.5)" : "rgba(255, 255, 255, 0.08)"}`,
                      color: mediaPlatform === "spotify" ? "#1ed760" : "var(--text-secondary)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "8px",
                      cursor: "pointer",
                      fontWeight: 600
                    }}
                  >
                    <Music size={16} /> Spotify
                  </button>
                </div>
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "6px", display: "block" }}>
                  Song / Artist / Video Title (Optional)
                </label>
                <input
                  type="text"
                  value={mediaQuery}
                  onChange={(e) => setMediaQuery(e.target.value)}
                  placeholder={mediaPlatform === "youtube" ? "e.g. Bohemian Rhapsody, Python Crash Course..." : "e.g. Starboy, Shape of You, Top Hits..."}
                  className="input-glass"
                />
              </div>

              <div style={{ display: "flex", gap: "10px" }}>
                <button
                  type="submit"
                  disabled={mediaLoading}
                  className="btn-primary"
                  style={{
                    flex: 1,
                    background: mediaPlatform === "youtube" ? "linear-gradient(135deg, #ff0055, #ff5500)" : "linear-gradient(135deg, #1ed760, #00b4d8)",
                    padding: "11px"
                  }}
                >
                  <Play size={16} /> {mediaLoading ? "Launching..." : (mediaQuery.trim() ? `Play on ${mediaPlatform.toUpperCase()}` : `Open ${mediaPlatform.toUpperCase()}`)}
                </button>
              </div>
            </form>
          </div>

          {/* Quick Play Presets */}
          <div className="glass-card" style={{ padding: "20px", display: "flex", flexDirection: "column" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--accent-purple)", marginBottom: "12px" }}>
              Quick Suggestions & Presets
            </h4>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {[
                { title: "Bohemian Rhapsody", platform: "spotify", tag: "Rock Anthem" },
                { title: "Lofi Hip Hop Radio - Beats to Study/Relax", platform: "youtube", tag: "Focus Music" },
                { title: "Starboy - The Weeknd", platform: "spotify", tag: "Pop/Synth" },
                { title: "Python Full Course for Beginners", platform: "youtube", tag: "Coding Tutorial" }
              ].map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => {
                    setMediaPlatform(item.platform);
                    setMediaQuery(item.title);
                    handlePlayMedia(item.platform, item.title);
                  }}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(255, 255, 255, 0.04)",
                    border: "1px solid rgba(255, 255, 255, 0.06)",
                    cursor: "pointer",
                    transition: "all 0.2s ease"
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = "rgba(0, 245, 255, 0.1)"}
                  onMouseLeave={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)"}
                >
                  <div>
                    <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)" }}>{item.title}</div>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px", marginTop: "2px" }}>
                      <span style={{ color: item.platform === "youtube" ? "#ff4d4d" : "#1ed760", fontWeight: 600, textTransform: "uppercase" }}>{item.platform}</span> • {item.tag}
                    </div>
                  </div>
                  <PlayCircle size={18} color="var(--accent-cyan)" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* WhatsApp Messaging & Contacts Section */}
      <div className="glass-panel" style={{ padding: "24px", marginTop: "28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "16px" }}>
          <MessageSquare size={22} color="var(--accent-emerald)" />
          <div>
            <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>WhatsApp Assistant & Contacts</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
              Speak or trigger auto-replies: <em>"Sadie send hii to sakshi"</em> to open WhatsApp with pre-filled messages.
            </p>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "20px" }}>
          {/* Quick Message Sender */}
          <div className="glass-card" style={{ padding: "20px" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--accent-cyan)", marginBottom: "12px" }}>
              Quick Message Sender
            </h4>
            <form onSubmit={handleSendWhatsApp} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Target Contact Name
                </label>
                <input
                  type="text"
                  required
                  value={targetContact}
                  onChange={(e) => setTargetContact(e.target.value)}
                  placeholder="e.g. Sakshi"
                  className="input-glass"
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Message to Send
                </label>
                <input
                  type="text"
                  required
                  value={msgText}
                  onChange={(e) => setMsgText(e.target.value)}
                  placeholder="e.g. Hii"
                  className="input-glass"
                />
              </div>

              <button type="submit" className="btn-primary" style={{ background: "linear-gradient(135deg, #00f59b, #00b4d8)", padding: "10px" }}>
                <Send size={16} /> Open WhatsApp & Send Message
              </button>
            </form>
          </div>

          {/* Contacts Book */}
          <div className="glass-card" style={{ padding: "20px", display: "flex", flexDirection: "column" }}>
            <h4 style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--accent-purple)", marginBottom: "12px" }}>
              Saved Contacts ({contacts.length})
            </h4>

            {/* Add Contact inline */}
            <form onSubmit={handleAddContact} style={{ display: "flex", gap: "8px", marginBottom: "14px" }}>
              <input
                type="text"
                required
                value={contactName}
                onChange={(e) => setContactName(e.target.value)}
                placeholder="Name (e.g. Sakshi)"
                className="input-glass"
                style={{ flex: 1, padding: "8px 10px", fontSize: "0.82rem" }}
              />
              <input
                type="text"
                value={contactPhone}
                onChange={(e) => setContactPhone(e.target.value)}
                placeholder="Phone (optional)"
                className="input-glass"
                style={{ width: "130px", padding: "8px 10px", fontSize: "0.82rem" }}
              />
              <button type="submit" className="btn-primary" style={{ padding: "0 12px" }}>
                <Plus size={16} />
              </button>
            </form>

            <div style={{ flex: 1, overflowY: "auto", maxHeight: "160px", display: "flex", flexDirection: "column", gap: "6px" }}>
              {contacts.length === 0 ? (
                <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", textAlign: "center", padding: "20px 0" }}>
                  No contacts saved yet. Add a contact above!
                </p>
              ) : (
                contacts.map((c) => (
                  <div
                    key={c.id}
                    onClick={() => setTargetContact(c.name)}
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      padding: "8px 12px",
                      borderRadius: "6px",
                      background: targetContact.toLowerCase() === c.name.toLowerCase() ? "rgba(0, 245, 155, 0.15)" : "rgba(255, 255, 255, 0.04)",
                      border: `1px solid ${targetContact.toLowerCase() === c.name.toLowerCase() ? "rgba(0, 245, 155, 0.3)" : "rgba(255, 255, 255, 0.06)"}`,
                      cursor: "pointer"
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "0.88rem", fontWeight: 600, color: "var(--text-primary)" }}>{c.name}</div>
                      {c.phone_number && <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{c.phone_number}</div>}
                    </div>
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); handleDeleteContact(c.id); }}
                      style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

