import React, { useState, useEffect } from "react";
import { User, LogIn, LogOut, Activity, ShieldCheck, Volume2, VolumeX } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

export default function Header({ activeMode, onOpenAuthModal, soundEnabled, onToggleSound, onStopAudio }) {
  const { user, logout } = useAuth();
  const [serverOnline, setServerOnline] = useState(true);

  useEffect(() => {
    async function checkHealth() {
      try {
        await api.system.getHealth();
        setServerOnline(true);
      } catch (e) {
        setServerOnline(false);
      }
    }
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header style={{
      height: "64px",
      padding: "0 28px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      background: "rgba(10, 14, 24, 0.6)",
      backdropFilter: "blur(16px)",
      borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
      position: "sticky",
      top: 0,
      zIndex: 30
    }}>
      {/* Left side: System status & mode chip */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "6px 12px",
          borderRadius: "20px",
          background: serverOnline ? "rgba(0, 245, 155, 0.1)" : "rgba(255, 42, 109, 0.1)",
          border: `1px solid ${serverOnline ? "rgba(0, 245, 155, 0.25)" : "rgba(255, 42, 109, 0.25)"}`
        }}>
          <span style={{
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            background: serverOnline ? "var(--accent-emerald)" : "var(--accent-rose)",
            boxShadow: `0 0 8px ${serverOnline ? "var(--accent-emerald)" : "var(--accent-rose)"}`
          }} />
          <span style={{ fontSize: "0.8rem", fontWeight: 600, color: serverOnline ? "var(--accent-emerald)" : "var(--accent-rose)" }}>
            {serverOnline ? "SADIE CORE ONLINE" : "BACKEND CONNECTING..."}
          </span>
        </div>

        <div style={{
          padding: "4px 12px",
          borderRadius: "8px",
          background: "rgba(255, 255, 255, 0.04)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          fontSize: "0.8rem",
          color: "var(--text-secondary)",
          display: "flex",
          alignItems: "center",
          gap: "6px"
        }}>
          <ShieldCheck size={14} color="var(--accent-cyan)" />
          <span>Security Allowlist Active</span>
        </div>
      </div>

      {/* Right side: Audio toggle & User Auth */}
      <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
        {/* Sound / Mute toggle */}
        <button
          onClick={onToggleSound}
          title={soundEnabled ? "Sound Enabled (Click to Mute Audio)" : "Sound Muted (Click to Unmute Audio)"}
          style={{
            background: soundEnabled ? "rgba(0, 229, 255, 0.15)" : "rgba(255, 42, 109, 0.15)",
            border: `1px solid ${soundEnabled ? "rgba(0, 229, 255, 0.35)" : "rgba(255, 42, 109, 0.35)"}`,
            color: soundEnabled ? "var(--accent-cyan)" : "var(--accent-rose)",
            padding: "0 10px",
            height: "36px",
            borderRadius: "8px",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            cursor: "pointer",
            fontSize: "0.78rem",
            fontWeight: 600,
            transition: "all 0.2s ease"
          }}
        >
          {soundEnabled ? <Volume2 size={17} /> : <VolumeX size={17} />}
          <span>{soundEnabled ? "AUDIO ON" : "MUTED"}</span>
        </button>

        {/* User profile / login button */}
        {user ? (
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              padding: "5px 12px",
              borderRadius: "20px",
              background: "rgba(255, 255, 255, 0.06)",
              border: "1px solid rgba(255, 255, 255, 0.1)"
            }}>
              <div style={{
                width: "26px",
                height: "26px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: "0.75rem",
                color: "#050811"
              }}>
                {user.name ? user.name[0].toUpperCase() : "U"}
              </div>
              <span style={{ fontSize: "0.85rem", fontWeight: 500, color: "var(--text-primary)" }}>
                {user.name || user.email}
              </span>
            </div>
            <button
              onClick={logout}
              title="Logout"
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-muted)",
                cursor: "pointer",
                padding: "6px"
              }}
            >
              <LogOut size={18} />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenAuthModal}
            className="btn-primary"
            style={{ padding: "6px 16px", fontSize: "0.85rem" }}
          >
            <LogIn size={15} />
            Sign In / Register
          </button>
        )}
      </div>
    </header>
  );
}
