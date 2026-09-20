import React, { useState, useEffect, useRef } from "react";
import { Send, Mic, Sparkles, Volume2, Bot, User, Trash2, Plus, Wrench, Play, Music, Tv, ExternalLink, Code2, Copy, Check, Terminal } from "lucide-react";
import { api } from "../services/api";

export default function ChatPage({ activeMode, setActiveMode, onPlayAudio, onStopAudio, soundEnabled }) {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      sender: "sadie",
      content: "Hello! I am SADIE, your voice & AI desktop assistant. How can I help you today? You can ask me to play any song on YouTube/Spotify, suggest music, explain algorithms, open programs, start timers, or create tasks.",
      tool_calls: null,
      created_at: new Date().toISOString()
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    async function fetchConversations() {
      try {
        const list = await api.assistant.getConversations();
        setConversations(list || []);
      } catch (e) {
        console.warn("Could not fetch conversations:", e);
      }
    }
    fetchConversations();
  }, [currentConvId]);

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || loading) return;

    const userQuery = inputText.trim();
    setInputText("");
    const tempUserMsg = {
      id: `temp_${Date.now()}`,
      sender: "user",
      content: userQuery,
      created_at: new Date().toISOString()
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const response = await api.assistant.chat(userQuery, currentConvId, activeMode);
      setCurrentConvId(response.conversation_id);
      
      const sadieMsg = {
        id: `sadie_${Date.now()}`,
        sender: "sadie",
        content: response.message,
        tool_calls: response.tool_required ? JSON.stringify({ tool: response.tool_name, params: response.tool_parameters, result: response.tool_result }) : null,
        created_at: new Date().toISOString()
      };
      setMessages((prev) => [...prev, sadieMsg]);

      // If sound enabled, synthesize audio
      if (soundEnabled && onPlayAudio) {
        try {
          const synth = await api.voice.synthesize(response.message);
          if (synth.audio_base64 && onPlayAudio) {
            onPlayAudio(synth.audio_base64);
          }
        } catch (voiceErr) {
          console.warn("Audio synthesis error:", voiceErr);
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: "sadie",
          content: `⚠️ Error: ${err.message}`,
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleMicInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
      setIsListening(false);
    };
    recognition.onerror = () => setIsListening(false);
    recognition.onend = () => setIsListening(false);
    recognition.start();
  };

  const startNewChat = () => {
    setCurrentConvId(null);
    setMessages([
      {
        id: "welcome",
        sender: "sadie",
        content: "Started a fresh conversation. What would you like to work on?",
        tool_calls: null,
        created_at: new Date().toISOString()
      }
    ]);
  };

  return (
    <div style={{ display: "flex", height: "calc(100vh - 64px)", overflow: "hidden" }}>
      {/* Conversations History Sidebar */}
      <div style={{
        width: "240px",
        minWidth: "240px",
        background: "rgba(10, 15, 26, 0.7)",
        borderRight: "1px solid rgba(255, 255, 255, 0.06)",
        padding: "16px 12px",
        display: "flex",
        flexDirection: "column"
      }}>
        <button
          onClick={startNewChat}
          className="btn-primary"
          style={{ width: "100%", padding: "10px", fontSize: "0.85rem", marginBottom: "16px" }}
        >
          <Plus size={16} /> New Chat
        </button>

        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "10px", textTransform: "uppercase", letterSpacing: "1px" }}>
          Recent Conversations
        </div>

        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "6px" }}>
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={async () => {
                setCurrentConvId(c.id);
                try {
                  const detail = await api.assistant.getConversation(c.id);
                  setMessages(detail.messages || []);
                } catch (e) {
                  console.error(e);
                }
              }}
              style={{
                background: currentConvId === c.id ? "rgba(0, 229, 255, 0.15)" : "transparent",
                border: `1px solid ${currentConvId === c.id ? "rgba(0, 229, 255, 0.3)" : "transparent"}`,
                color: currentConvId === c.id ? "var(--accent-cyan)" : "var(--text-secondary)",
                padding: "8px 10px",
                borderRadius: "6px",
                textAlign: "left",
                fontSize: "0.82rem",
                display: "flex",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <Bot size={14} />
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {c.title}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "transparent" }}>
        {/* Messages Stream */}
        <div style={{ flex: 1, overflowY: "auto", padding: "24px 32px", display: "flex", flexDirection: "column", gap: "18px" }}>
          {messages.map((msg) => {
            const isUser = msg.sender === "user";
            return (
              <div
                key={msg.id}
                style={{
                  display: "flex",
                  gap: "12px",
                  alignSelf: isUser ? "flex-end" : "flex-start",
                  maxWidth: "80%"
                }}
              >
                {!isUser && (
                  <div style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "10px",
                    background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    boxShadow: "0 0 15px rgba(0, 229, 255, 0.3)"
                  }}>
                    <Sparkles size={18} color="#050811" />
                  </div>
                )}

                <div>
                  <div style={{
                    padding: "14px 18px",
                    borderRadius: isUser ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                    background: isUser
                      ? "linear-gradient(135deg, rgba(0, 229, 255, 0.2), rgba(0, 180, 216, 0.2))"
                      : "rgba(18, 26, 44, 0.8)",
                    border: `1px solid ${isUser ? "rgba(0, 229, 255, 0.4)" : "rgba(255, 255, 255, 0.08)"}`,
                    backdropFilter: "blur(12px)",
                    color: "var(--text-primary)",
                    fontSize: "0.95rem",
                    lineHeight: "1.6",
                    whiteSpace: "pre-wrap"
                  }}>
                    {msg.content}

                    {/* Tool execution badge & media player if present */}
                    {msg.tool_calls && (() => {
                      try {
                        const toolData = JSON.parse(msg.tool_calls);
                        const isMedia = toolData.tool === "play_media" || toolData.tool_name === "play_media" || toolData.params?.platform;
                        const mediaPlat = toolData.params?.platform || "youtube";
                        const mediaQuery = toolData.params?.query || "";
                        const directUrl = toolData.result?.result?.url || (mediaPlat === "youtube"
                          ? (mediaQuery ? `https://www.youtube.com/results?search_query=${encodeURIComponent(mediaQuery)}` : "https://www.youtube.com")
                          : (mediaQuery ? `https://open.spotify.com/search/${encodeURIComponent(mediaQuery)}` : "https://open.spotify.com"));
                        const embedUrl = toolData.result?.result?.embed_url;

                        if (isMedia) {
                          return (
                            <div style={{
                              marginTop: "12px",
                              padding: "12px",
                              borderRadius: "10px",
                              background: mediaPlat === "youtube" ? "rgba(255, 0, 51, 0.12)" : "rgba(30, 215, 96, 0.12)",
                              border: `1px solid ${mediaPlat === "youtube" ? "rgba(255, 0, 51, 0.35)" : "rgba(30, 215, 96, 0.35)"}`,
                              display: "flex",
                              flexDirection: "column",
                              gap: "10px"
                            }}>
                              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "10px" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                  {mediaPlat === "youtube" ? <Tv size={18} color="#ff4d4d" /> : <Music size={18} color="#1ed760" />}
                                  <div>
                                    <div style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--text-primary)" }}>
                                      {mediaQuery ? `Playing: ${mediaQuery}` : `Open ${mediaPlat.toUpperCase()}`}
                                    </div>
                                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>
                                      {mediaPlat === "spotify" ? "Windows Spotify Desktop • Auto-Stream Active" : "YouTube Direct Video Autoplay"}
                                    </div>
                                  </div>
                                </div>
                                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                                  <a
                                    href={directUrl}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="btn-secondary"
                                    style={{
                                      padding: "4px 10px",
                                      fontSize: "0.72rem",
                                      textDecoration: "none",
                                      display: "inline-flex",
                                      alignItems: "center",
                                      gap: "4px"
                                    }}
                                  >
                                    <ExternalLink size={10} /> {mediaPlat === "spotify" ? "Spotify" : "YouTube"}
                                  </a>
                                  {(toolData.result?.result?.youtube_fallback_url || mediaPlat === "youtube") && (
                                    <a
                                      href={toolData.result?.result?.youtube_fallback_url || directUrl}
                                      target="_blank"
                                      rel="noreferrer"
                                      className="btn-primary"
                                      style={{
                                        padding: "4px 10px",
                                        fontSize: "0.72rem",
                                        background: "linear-gradient(135deg, #ff0055, #ff5500)",
                                        textDecoration: "none",
                                        display: "inline-flex",
                                        alignItems: "center",
                                        gap: "4px"
                                      }}
                                    >
                                      <Play size={10} /> AutoPlay Video
                                    </a>
                                  )}
                                </div>
                              </div>

                              {(toolData.result?.result?.youtube_embed_url || embedUrl) && (
                                <div style={{
                                  borderRadius: "6px",
                                  overflow: "hidden",
                                  width: "100%",
                                  height: "180px",
                                  background: "#000"
                                }}>
                                  <iframe
                                    src={toolData.result?.result?.youtube_embed_url || embedUrl}
                                    title="Live Stream Player"
                                    style={{ width: "100%", height: "100%", border: "none" }}
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                                    allowFullScreen
                                  />
                                </div>
                              )}
                            </div>
                          );
                        }

                        const isCode = toolData.tool === "create_code_file" || toolData.tool_name === "create_code_file" || toolData.result?.result?.code;
                        if (isCode) {
                          const lang = toolData.result?.result?.language || toolData.params?.language || "code";
                          const fname = toolData.result?.result?.filename || toolData.params?.filename || "program.py";
                          const codeText = toolData.result?.result?.code || "";

                          return (
                            <div style={{
                              marginTop: "12px",
                              padding: "12px",
                              borderRadius: "10px",
                              background: "rgba(10, 16, 32, 0.9)",
                              border: "1px solid rgba(0, 229, 255, 0.35)",
                              display: "flex",
                              flexDirection: "column",
                              gap: "8px"
                            }}>
                              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "6px" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                                  <Code2 size={16} color="var(--accent-cyan)" />
                                  <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--text-primary)" }}>{fname}</span>
                                  <span style={{ fontSize: "0.7rem", color: "var(--accent-cyan)", background: "rgba(0, 229, 255, 0.15)", padding: "2px 6px", borderRadius: "4px" }}>
                                    {lang.toUpperCase()}
                                  </span>
                                </div>
                                <button
                                  onClick={() => api.tools.execute("open_application", { app_name: "code" })}
                                  className="btn-primary"
                                  style={{ padding: "4px 10px", fontSize: "0.72rem" }}
                                >
                                  <Terminal size={11} /> Open in VS Code
                                </button>
                              </div>
                              {codeText && (
                                <pre style={{
                                  background: "rgba(5, 8, 18, 0.95)",
                                  padding: "10px",
                                  borderRadius: "6px",
                                  color: "#e2e8f0",
                                  fontSize: "0.8rem",
                                  fontFamily: "Consolas, 'Courier New', monospace",
                                  overflowX: "auto",
                                  maxHeight: "180px",
                                  margin: 0,
                                  lineHeight: "1.4"
                                }}>
                                  {codeText}
                                </pre>
                              )}
                            </div>
                          );
                        }

                        return (
                          <div style={{
                            marginTop: "10px",
                            padding: "6px 10px",
                            borderRadius: "6px",
                            background: "rgba(0, 245, 155, 0.1)",
                            border: "1px solid rgba(0, 245, 155, 0.3)",
                            color: "var(--accent-emerald)",
                            fontSize: "0.78rem",
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                          }}>
                            <Wrench size={13} />
                            <span>Tool Executed: {toolData.tool || toolData.tool_name || "Custom Tool"}</span>
                          </div>
                        );
                      } catch (e) {
                        return null;
                      }
                    })()}
                  </div>

                  {!isUser && (
                    <button
                      onClick={async () => {
                        if (onStopAudio) onStopAudio();
                        const synth = await api.voice.synthesize(msg.content);
                        if (synth.audio_base64 && onPlayAudio) onPlayAudio(synth.audio_base64);
                      }}
                      title="Listen with Sadie's Voice"
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "var(--text-muted)",
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: "4px",
                        fontSize: "0.75rem",
                        marginTop: "4px"
                      }}
                    >
                      <Volume2 size={13} /> Speak
                    </button>
                  )}
                </div>

                {isUser && (
                  <div style={{
                    width: "36px",
                    height: "36px",
                    borderRadius: "10px",
                    background: "rgba(255, 255, 255, 0.1)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0
                  }}>
                    <User size={18} color="var(--text-primary)" />
                  </div>
                )}
              </div>
            );
          })}
          {loading && (
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--accent-cyan)", fontSize: "0.85rem" }}>
              <Sparkles size={16} className="animate-spin" />
              <span>Sadie is thinking...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div style={{
          padding: "16px 24px",
          background: "rgba(10, 14, 24, 0.9)",
          borderTop: "1px solid rgba(255, 255, 255, 0.08)"
        }}>
          <form onSubmit={handleSendMessage} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <button
              type="button"
              onClick={handleMicInput}
              title="Speak to Sadie"
              style={{
                width: "44px",
                height: "44px",
                borderRadius: "10px",
                background: isListening ? "rgba(255, 42, 109, 0.2)" : "rgba(255, 255, 255, 0.06)",
                border: `1px solid ${isListening ? "var(--accent-rose)" : "rgba(255, 255, 255, 0.1)"}`,
                color: isListening ? "var(--accent-rose)" : "var(--accent-cyan)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                cursor: "pointer"
              }}
            >
              <Mic size={20} />
            </button>

            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask Sadie a question or give a command (e.g. 'Explain recursion', 'Open calc', 'Start 25m timer')..."
              className="input-glass"
              style={{ flex: 1, padding: "12px 18px", borderRadius: "10px" }}
            />

            <button
              type="submit"
              disabled={loading || !inputText.trim()}
              className="btn-primary"
              style={{ height: "44px", padding: "0 22px", borderRadius: "10px" }}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
