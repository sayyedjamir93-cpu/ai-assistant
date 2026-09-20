import React from "react";
import { Mic, Volume2, Sparkles, Loader2 } from "lucide-react";

export default function VoiceVisualizer({ voiceState, onClickMic }) {
  // voiceState: 'idle' | 'listening' | 'processing' | 'speaking'

  const getStateColor = () => {
    switch (voiceState) {
      case "listening":
        return "var(--accent-cyan)";
      case "processing":
        return "var(--accent-purple)";
      case "speaking":
        return "var(--accent-emerald)";
      default:
        return "var(--accent-cyan)";
    }
  };

  const getStatusLabel = () => {
    switch (voiceState) {
      case "listening":
        return "LISTENING TO YOUR VOICE...";
      case "processing":
        return "THINKING & ROUTING TOOLS...";
      case "speaking":
        return "SADIE IS SPEAKING...";
      default:
        return "READY • CLICK TO TALK";
    }
  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px 0"
    }}>
      {/* Central Interactive Orb */}
      <div style={{ position: "relative", width: "160px", height: "160px", display: "flex", alignItems: "center", justifyContent: "center" }}>
        
        {/* Pulsing Outer Rings */}
        <div style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          borderRadius: "50%",
          border: `2px solid ${getStateColor()}`,
          opacity: voiceState === "listening" ? 0.8 : 0.25,
          transform: voiceState === "listening" ? "scale(1.2)" : "scale(1)",
          transition: "all 0.5s ease"
        }} className={voiceState === "listening" ? "animate-pulse-ring" : ""} />

        <div style={{
          position: "absolute",
          width: "130px",
          height: "130px",
          borderRadius: "50%",
          background: `radial-gradient(circle, ${getStateColor()} 0%, rgba(157, 78, 221, 0.2) 60%, transparent 80%)`,
          filter: "blur(18px)",
          opacity: 0.6
        }} />

        {/* Core Glowing Button */}
        <button
          onClick={onClickMic}
          title="Click to activate voice"
          style={{
            position: "relative",
            width: "100px",
            height: "100px",
            borderRadius: "50%",
            background: "linear-gradient(135deg, #0c1322 0%, #152037 100%)",
            border: `2px solid ${getStateColor()}`,
            boxShadow: `0 0 35px ${getStateColor()}66, inset 0 0 20px ${getStateColor()}33`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            zIndex: 10
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = "scale(1.08)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "scale(1)";
          }}
        >
          {voiceState === "listening" && <Mic size={40} color="var(--accent-cyan)" />}
          {voiceState === "processing" && <Loader2 size={40} color="var(--accent-purple)" className="animate-spin" />}
          {voiceState === "speaking" && <Volume2 size={40} color="var(--accent-emerald)" />}
          {voiceState === "idle" && <Mic size={38} color="var(--accent-cyan)" />}
        </button>
      </div>

      {/* Audio Wave Frequency Bars */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "4px",
        height: "36px",
        margin: "18px 0 10px 0"
      }}>
        {[14, 24, 34, 18, 28, 36, 20, 32, 16, 26, 12].map((height, i) => (
          <div
            key={i}
            style={{
              width: "4px",
              height: voiceState === "listening" || voiceState === "speaking" ? `${height}px` : "6px",
              background: getStateColor(),
              borderRadius: "2px",
              boxShadow: `0 0 8px ${getStateColor()}`,
              transition: "height 0.2s ease",
              animation: (voiceState === "listening" || voiceState === "speaking")
                ? `wave-bar 1.2s infinite ease-in-out ${i * 0.1}s`
                : "none"
            }}
          />
        ))}
      </div>

      {/* Status Pill */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        padding: "6px 16px",
        borderRadius: "20px",
        background: "rgba(15, 21, 35, 0.8)",
        border: "1px solid rgba(255, 255, 255, 0.08)",
        fontSize: "0.8rem",
        fontWeight: 600,
        letterSpacing: "1px",
        color: getStateColor()
      }}>
        <span style={{
          width: "7px",
          height: "7px",
          borderRadius: "50%",
          background: getStateColor(),
          boxShadow: `0 0 8px ${getStateColor()}`
        }} />
        {getStatusLabel()}
      </div>
    </div>
  );
}
