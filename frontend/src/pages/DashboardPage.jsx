import React, { useState, useEffect } from "react";
import {
  Mic,
  Sparkles,
  Play,
  Clock,
  CheckCircle2,
  Brain,
  Wrench,
  Search,
  BookOpen,
  Code,
  Code2,
  Copy,
  Check,
  Terminal,
  Volume2,
  Music,
  Tv,
  ExternalLink,
  MessageSquare,
  Send,
  Bell,
  BellRing
} from "lucide-react";
import VoiceVisualizer from "../components/VoiceVisualizer";
import { api } from "../services/api";

export default function DashboardPage({ activeMode, setActiveMode, setActiveTab, onPlayAudio, onStopAudio, soundEnabled, onToggleSound }) {
  const [voiceState, setVoiceState] = useState("idle"); // idle | listening | processing | speaking
  const [transcript, setTranscript] = useState("");
  const [responseMessage, setResponseMessage] = useState("Hello! I am SADIE, your AI personal assistant. How can I help you today?");
  const [lastToolResult, setLastToolResult] = useState(null);
  const [copiedCode, setCopiedCode] = useState(false);
  const [incomingNotifications, setIncomingNotifications] = useState([]);
  const [unreadMsgCount, setUnreadMsgCount] = useState(0);
  const [simulatingMsg, setSimulatingMsg] = useState(false);
  const [stats, setStats] = useState({
    totalStudyMin: 0,
    tasksCompleted: 0,
    activeTimersCount: 0,
    cpuUsage: 0
  });

  const loadNotifications = async () => {
    try {
      const notifRes = await api.messages.getNotifications();
      if (notifRes.messages) {
        setIncomingNotifications(notifRes.messages);
        setUnreadMsgCount(notifRes.unread_count || 0);
      }
    } catch (e) {
      console.warn("Could not load notifications:", e);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  useEffect(() => {
    async function loadStats() {
      try {
        const analytics = await api.study.getAnalytics();
        const timersRes = await api.tools.getTimers();
        const sys = await api.system.getInfo();
        setStats({
          totalStudyMin: analytics.total_study_minutes || 0,
          tasksCompleted: analytics.total_tasks_completed || 0,
          activeTimersCount: timersRes.timers ? timersRes.timers.filter(t => t.is_active).length : 0,
          cpuUsage: sys.cpu ? sys.cpu.current_usage_percent : 0
        });
      } catch (e) {
        console.warn("Could not load stats:", e);
      }
    }
    loadStats();
  }, []);

  // Handle Voice Assistant Interaction via Web Speech API / Direct pipeline
  const handleStartVoice = () => {
    if (voiceState === "speaking") {
      if (onStopAudio) onStopAudio();
      setVoiceState("idle");
      return;
    }

    if (voiceState === "listening") {
      setVoiceState("idle");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = "en-US";
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setVoiceState("listening");
        setTranscript("Listening...");
      };

      recognition.onresult = async (event) => {
        const spoken = event.results[0][0].transcript;
        setTranscript(spoken);
        setVoiceState("processing");
        await processUserQuery(spoken);
      };

      recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        setVoiceState("idle");
        setTranscript("Microphone timed out. Click below to try again or type in chat.");
      };

      recognition.onend = () => {
        if (voiceState === "listening") {
          setVoiceState("idle");
        }
      };

      recognition.start();
    } else {
      // Fallback prompt simulation
      const sample = prompt("Web Speech API not supported in this browser. Enter voice prompt to Sadie:", "create sum program on python language");
      if (sample) {
        setTranscript(sample);
        setVoiceState("processing");
        processUserQuery(sample);
      }
    }
  };

  const processUserQuery = async (queryText) => {
    try {
      const chatRes = await api.voice.chat({
        text_fallback: queryText,
        mode: activeMode,
        synthesize_voice: soundEnabled
      });

      setResponseMessage(chatRes.response_text);
      setLastToolResult(chatRes.tool_result);
      setVoiceState("speaking");

      if (chatRes.audio_base64 && onPlayAudio && soundEnabled) {
        onPlayAudio(chatRes.audio_base64, () => setVoiceState("idle"));
      } else {
        setTimeout(() => setVoiceState("idle"), 2500);
      }
    } catch (err) {
      setResponseMessage(`I encountered an issue: ${err.message}`);
      setVoiceState("idle");
    }
  };

  const handleSimulateWhatsApp = async (sender = "Sakshi", content = "Hey Jamir, are you free for the project discussion?") => {
    setSimulatingMsg(true);
    try {
      const simRes = await api.messages.simulateIncoming(sender, content, "WhatsApp");
      setResponseMessage(simRes.spoken_text);
      setVoiceState("speaking");
      if (simRes.audio_base64 && onPlayAudio && soundEnabled) {
        onPlayAudio(simRes.audio_base64, () => setVoiceState("idle"));
      } else {
        setTimeout(() => setVoiceState("idle"), 3500);
      }
      await loadNotifications();
    } catch (err) {
      console.error("Simulation error:", err);
    } finally {
      setSimulatingMsg(false);
    }
  };

  const handleReadMessagesAloud = async () => {
    try {
      const readRes = await api.messages.readAloud();
      setResponseMessage(readRes.spoken_text);
      setVoiceState("speaking");
      if (readRes.audio_base64 && onPlayAudio && soundEnabled) {
        onPlayAudio(readRes.audio_base64, () => setVoiceState("idle"));
      } else {
        setTimeout(() => setVoiceState("idle"), 3000);
      }
      await loadNotifications();
    } catch (err) {
      console.error("Read aloud error:", err);
    }
  };

  const quickPrompts = [
    { label: "🔊 Read WhatsApp Messages", action: () => processUserQuery("read my whatsapp messages") },
    { label: "💬 WhatsApp Sakshi", action: () => processUserQuery("send a whatsapp message to sakshi saying I will join soon") },
    { label: "🐍 Python Sum in VS Code", action: () => processUserQuery("create sum program on python language") },
    { label: "🤖 Ask ChatGPT", action: () => processUserQuery("ask ChatGPT how to create a react app") },
    { label: "🔍 Search Google", action: () => processUserQuery("search Google for latest tech news") },
    { label: "📧 Open Gmail / Mail", action: () => processUserQuery("open gmail") },
    { label: "📁 Open File Explorer", action: () => processUserQuery("open files") },
    { label: "🎵 Play Music", action: () => processUserQuery("Suggest me a good song and play it") }
  ];

  return (
    <div className="page-container">
      
      {/* Top Hero Section */}
      <div className="glass-panel" style={{
        padding: "32px 16px",
        textAlign: "center",
        position: "relative",
        overflow: "hidden",
        marginBottom: "24px"
      }}>
        {/* Subtle Ambient Glow */}
        <div style={{
          position: "absolute",
          top: "-50%",
          left: "50%",
          transform: "translateX(-50%)",
          width: "500px",
          height: "300px",
          background: "radial-gradient(circle, rgba(0, 229, 255, 0.12) 0%, rgba(157, 78, 221, 0.05) 50%, transparent 80%)",
          pointerEvents: "none"
        }} />

        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", padding: "6px 14px", borderRadius: "20px", background: "rgba(0, 229, 255, 0.1)", border: "1px solid rgba(0, 229, 255, 0.25)", marginBottom: "16px" }}>
          <Sparkles size={14} color="var(--accent-cyan)" />
          <span style={{ fontSize: "0.76rem", fontWeight: 600, color: "var(--accent-cyan)" }}>
            VOICE-ENABLED DESKTOP INTELLIGENCE
          </span>
        </div>

        <h2 style={{
          fontFamily: "var(--font-display)",
          fontSize: "clamp(1.4rem, 4.5vw, 2.3rem)",
          fontWeight: 800,
          letterSpacing: "-0.5px",
          marginBottom: "8px"
        }}>
          How can I assist your productivity today?
        </h2>

        {/* Voice Visualizer Interactive Orb */}
        <VoiceVisualizer voiceState={voiceState} onClickMic={handleStartVoice} />

        {/* User recognized voice speech */}
        {transcript && (
          <div style={{
            margin: "12px auto",
            maxWidth: "600px",
            padding: "8px 16px",
            borderRadius: "8px",
            background: "rgba(255, 255, 255, 0.05)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            fontSize: "0.9rem",
            color: "var(--accent-cyan)"
          }}>
            🗣️ <em>"{transcript}"</em>
          </div>
        )}

        {/* Sadie's Live Response */}
        <div style={{
          maxWidth: "750px",
          margin: "16px auto 24px auto",
          padding: "16px 20px",
          borderRadius: "14px",
          background: "rgba(15, 23, 42, 0.75)",
          border: "1px solid rgba(0, 229, 255, 0.2)",
          fontSize: "1.05rem",
          color: "var(--text-primary)",
          lineHeight: "1.6"
        }}>
          "{responseMessage}"

          {/* Media Player Direct Launch Card */}
          {lastToolResult?.result?.platform && (
            <div style={{
              marginTop: "14px",
              padding: "14px",
              borderRadius: "12px",
              background: lastToolResult.result.platform === "youtube" ? "rgba(255, 0, 51, 0.12)" : "rgba(30, 215, 96, 0.12)",
              border: `1px solid ${lastToolResult.result.platform === "youtube" ? "rgba(255, 0, 51, 0.35)" : "rgba(30, 215, 96, 0.35)"}`,
              display: "flex",
              flexDirection: "column",
              gap: "12px"
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "12px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px", textAlign: "left" }}>
                  {lastToolResult.result.platform === "youtube" ? (
                    <Tv size={22} color="#ff4d4d" />
                  ) : (
                    <Music size={22} color="#1ed760" />
                  )}
                  <div>
                    <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-primary)" }}>
                      {lastToolResult.result.query || `Open ${lastToolResult.result.platform.toUpperCase()}`}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                      {lastToolResult.result.platform === "spotify" ? "Windows Spotify Desktop • Auto-Stream Active" : "YouTube Direct Video Autoplay"}
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  {lastToolResult.result.url && (
                    <a
                      href={lastToolResult.result.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-secondary"
                      style={{
                        padding: "6px 12px",
                        fontSize: "0.78rem",
                        textDecoration: "none",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px"
                      }}
                    >
                      <ExternalLink size={12} /> {lastToolResult.result.platform === "spotify" ? "Open Spotify" : "Open YouTube"}
                    </a>
                  )}

                  {(lastToolResult.result.youtube_fallback_url || (lastToolResult.result.platform === "youtube" && lastToolResult.result.url)) && (
                    <a
                      href={lastToolResult.result.youtube_fallback_url || lastToolResult.result.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-primary"
                      style={{
                        padding: "6px 14px",
                        fontSize: "0.8rem",
                        background: "linear-gradient(135deg, #ff0055, #ff5500)",
                        textDecoration: "none",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px"
                      }}
                    >
                      <Play size={14} /> Instant AutoPlay Video
                    </a>
                  )}
                </div>
              </div>

              {/* Direct In-App Video/Music Player */}
              {(lastToolResult.result.youtube_embed_url || lastToolResult.result.embed_url) && (
                <div style={{
                  borderRadius: "8px",
                  overflow: "hidden",
                  width: "100%",
                  height: "220px",
                  background: "#000"
                }}>
                  <iframe
                    src={lastToolResult.result.youtube_embed_url || lastToolResult.result.embed_url}
                    title="Live Stream Player"
                    style={{ width: "100%", height: "100%", border: "none" }}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                    allowFullScreen
                  />
                </div>
              )}
            </div>
          )}

          {/* VS Code Program Created Card */}
          {lastToolResult?.result?.filename && lastToolResult?.result?.code && (
            <div style={{
              marginTop: "16px",
              padding: "16px",
              borderRadius: "12px",
              background: "rgba(10, 16, 32, 0.9)",
              border: "1px solid rgba(0, 229, 255, 0.35)",
              textAlign: "left"
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px", flexWrap: "wrap", gap: "10px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <div style={{
                    padding: "6px 10px",
                    borderRadius: "6px",
                    background: "rgba(0, 229, 255, 0.15)",
                    color: "var(--accent-cyan)",
                    fontWeight: 700,
                    fontSize: "0.8rem",
                    display: "flex",
                    alignItems: "center",
                    gap: "6px"
                  }}>
                    <Code2 size={16} />
                    <span>{lastToolResult.result.language?.toUpperCase() || "CODE"}</span>
                  </div>
                  <div>
                    <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text-primary)" }}>
                      {lastToolResult.result.filename}
                    </div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                      Workspace File • Opened in VS Code on Windows
                    </div>
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(lastToolResult.result.code);
                      setCopiedCode(true);
                      setTimeout(() => setCopiedCode(false), 2000);
                    }}
                    className="btn-secondary"
                    style={{ padding: "6px 12px", fontSize: "0.78rem" }}
                  >
                    {copiedCode ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
                    {copiedCode ? "Copied!" : "Copy Code"}
                  </button>
                  <button
                    onClick={() => api.tools.execute("open_application", { app_name: "code" })}
                    className="btn-primary"
                    style={{ padding: "6px 14px", fontSize: "0.78rem" }}
                  >
                    <Terminal size={13} /> Open VS Code
                  </button>
                </div>
              </div>

              {/* Code Preview Block */}
              <pre style={{
                background: "rgba(5, 8, 18, 0.95)",
                padding: "12px 16px",
                borderRadius: "8px",
                border: "1px solid rgba(255, 255, 255, 0.08)",
                color: "#e2e8f0",
                fontSize: "0.85rem",
                fontFamily: "Consolas, 'Courier New', monospace",
                overflowX: "auto",
                maxHeight: "220px",
                margin: 0,
                lineHeight: "1.5"
              }}>
                {lastToolResult.result.code}
              </pre>
            </div>
          )}
        </div>

        {/* Main Voice Button */}
        <div style={{ display: "flex", justifyContent: "center", gap: "12px" }}>
          <button
            onClick={handleStartVoice}
            className="btn-primary"
            style={{ padding: "14px 32px", fontSize: "1.05rem" }}
          >
            <Mic size={20} />
            {voiceState === "listening" ? "STOP LISTENING" : "TALK TO SADIE"}
          </button>
        </div>

        {/* Quick Suggestion Chips */}
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "10px",
          marginTop: "28px"
        }}>
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={p.action}
              className="btn-secondary"
              style={{ padding: "7px 14px", fontSize: "0.82rem" }}
            >
              <Sparkles size={13} color="var(--accent-cyan)" />
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Live WhatsApp & Messages Voice Announcer Card */}
      <div className="glass-card" style={{
        padding: "24px",
        marginBottom: "28px",
        border: "1px solid rgba(37, 211, 102, 0.35)",
        background: "linear-gradient(135deg, rgba(10, 25, 20, 0.7) 0%, rgba(13, 19, 33, 0.8) 100%)",
        boxShadow: "0 8px 32px rgba(0, 0, 0, 0.3)"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{
              width: "38px",
              height: "38px",
              borderRadius: "10px",
              background: "rgba(37, 211, 102, 0.15)",
              border: "1px solid rgba(37, 211, 102, 0.4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <MessageSquare size={20} color="#25D366" />
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <h3 style={{ fontSize: "1.1rem", fontWeight: 700, margin: 0, color: "var(--text-primary)" }}>
                  WhatsApp & Message Voice Announcer
                </h3>
                {unreadMsgCount > 0 && (
                  <span style={{
                    padding: "2px 8px",
                    borderRadius: "12px",
                    background: "rgba(37, 211, 102, 0.2)",
                    border: "1px solid rgba(37, 211, 102, 0.4)",
                    color: "#25D366",
                    fontSize: "0.75rem",
                    fontWeight: 700
                  }}>
                    {unreadMsgCount} New
                  </span>
                )}
              </div>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", margin: "2px 0 0 0" }}>
                SADIE speaks aloud whenever incoming messages arrive and narrates notifications.
              </p>
            </div>
          </div>

          {/* Action Trigger Buttons */}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
            <button
              onClick={handleReadMessagesAloud}
              className="btn-secondary"
              style={{
                padding: "8px 14px",
                fontSize: "0.82rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                borderColor: "rgba(0, 229, 255, 0.3)"
              }}
            >
              <Volume2 size={15} color="var(--accent-cyan)" /> Read Messages Aloud
            </button>

            <button
              onClick={() => handleSimulateWhatsApp("Sakshi", "Hey Jamir, are you free for the meeting? Let's discuss the project.")}
              disabled={simulatingMsg}
              className="btn-primary"
              style={{
                padding: "8px 14px",
                fontSize: "0.82rem",
                background: "linear-gradient(135deg, #25D366 0%, #128C7E 100%)",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px"
              }}
            >
              <BellRing size={15} /> {simulatingMsg ? "Speaking..." : "Simulate WhatsApp (Sakshi)"}
            </button>

            <button
              onClick={() => handleSimulateWhatsApp("Alex", "Hey! Just sent over the latest updates on WhatsApp.")}
              disabled={simulatingMsg}
              className="btn-secondary"
              style={{
                padding: "8px 14px",
                fontSize: "0.82rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px"
              }}
            >
              <Bell size={15} /> Simulate from Alex
            </button>
          </div>
        </div>

        {/* Message Feed Display */}
        {incomingNotifications.length > 0 ? (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
            gap: "12px",
            marginTop: "12px"
          }}>
            {incomingNotifications.slice(0, 3).map((msg) => (
              <div
                key={msg.id}
                style={{
                  padding: "12px 16px",
                  borderRadius: "10px",
                  background: "rgba(0, 0, 0, 0.35)",
                  border: msg.is_read ? "1px solid rgba(255, 255, 255, 0.08)" : "1px solid rgba(37, 211, 102, 0.4)",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: "10px"
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.9rem", color: "#25D366", display: "flex", alignItems: "center", gap: "6px" }}>
                      <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: msg.is_read ? "#64748b" : "#25D366", display: "inline-block" }} />
                      {msg.sender}
                    </span>
                    <span style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                      {msg.created_at || "Just now"}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-primary)", lineHeight: "1.4" }}>
                    "{msg.content}"
                  </div>
                </div>

                <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: "8px" }}>
                  <button
                    onClick={() => {
                      api.tools.execute("send_whatsapp", {
                        contact_name: msg.sender,
                        message: `Hey ${msg.sender}, got your message!`
                      });
                    }}
                    className="btn-secondary"
                    style={{
                      padding: "4px 10px",
                      fontSize: "0.75rem",
                      display: "inline-flex",
                      alignItems: "center",
                      gap: "4px",
                      borderColor: "rgba(37, 211, 102, 0.3)",
                      color: "#25D366"
                    }}
                  >
                    <Send size={12} /> Reply
                  </button>

                  {!msg.is_read && (
                    <button
                      onClick={async () => {
                        await api.messages.markRead(msg.id);
                        loadNotifications();
                      }}
                      className="btn-secondary"
                      style={{ padding: "4px 10px", fontSize: "0.75rem" }}
                    >
                      <Check size={12} /> Mark Read
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            padding: "16px",
            textAlign: "center",
            fontSize: "0.85rem",
            color: "var(--text-muted)",
            background: "rgba(0, 0, 0, 0.2)",
            borderRadius: "8px"
          }}>
            No incoming notifications yet. Click "Simulate WhatsApp (Sakshi)" above to test SADIE speaking the message out loud!
          </div>
        )}
      </div>

      {/* Metrics & Quick Status Ribbon */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
        gap: "12px",
        marginBottom: "24px"
      }}>
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>AI Brain Status</span>
            <Brain size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--accent-cyan)" }}>
            Active & Ready
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            NLP Intent + Security Sandbox
          </p>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Study Focus Time</span>
            <Clock size={18} color="var(--accent-emerald)" />
          </div>
          <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--accent-emerald)" }}>
            {stats.totalStudyMin} mins
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Focused Pomodoro Sessions
          </p>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>Tasks Completed</span>
            <CheckCircle2 size={18} color="var(--accent-purple)" />
          </div>
          <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--accent-purple)" }}>
            {stats.tasksCompleted} Tasks
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Productivity Logged
          </p>
        </div>

        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>System Resource</span>
            <Wrench size={18} color="var(--accent-amber)" />
          </div>
          <div style={{ fontSize: "1.4rem", fontWeight: 700, color: "var(--accent-amber)" }}>
            {stats.cpuUsage}% CPU
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "4px" }}>
            Hardware Diagnostics
          </p>
        </div>
      </div>
    </div>
  );
}
