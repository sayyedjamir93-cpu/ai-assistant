import React, { useState, useEffect } from "react";
import { User, LogIn, LogOut, Activity, ShieldCheck, Volume2, VolumeX, Menu, Sparkles } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";

export default function Header({ activeMode, onOpenAuthModal, soundEnabled, onToggleSound, onStopAudio, onOpenMobileMenu }) {
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
      height: "60px",
      padding: "0 16px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      background: "rgba(10, 14, 24, 0.75)",
      backdropFilter: "blur(16px)",
      WebkitBackdropFilter: "blur(16px)",
      borderBottom: "1px solid rgba(255, 255, 255, 0.06)",
      position: "sticky",
      top: 0,
      zIndex: 30,
      gap: "10px"
    }}>
      {/* Left side: Hamburger button (mobile) + Brand / System status */}
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        {/* Mobile Hamburger Menu Button */}
        <button
          onClick={onOpenMobileMenu}
          className="mobile-only"
          title="Open Menu"
          style={{
            background: "rgba(255, 255, 255, 0.06)",
            border: "1px solid rgba(255, 255, 255, 0.12)",
            borderRadius: "8px",
            color: "var(--accent-cyan)",
            width: "38px",
            height: "38px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            flexShrink: 0
          }}
        >
          <Menu size={20} />
        </button>

        {/* Mobile Brand Title */}
        <div className="mobile-only" style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          <span style={{
            fontFamily: "var(--font-display)",
            fontWeight: 800,
            fontSize: "1.1rem",
            letterSpacing: "1px",
            background: "linear-gradient(90deg, #00e5ff, #ffffff)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent"
          }}>
            SADIE
          </span>
        </div>

        {/* System Online Badge (desktop full, mobile compact dot) */}
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "6px",
          padding: "5px 10px",
          borderRadius: "20px",
          background: serverOnline ? "rgba(0, 245, 155, 0.1)" : "rgba(255, 42, 109, 0.1)",
          border: `1px solid ${serverOnline ? "rgba(0, 245, 155, 0.25)" : "rgba(255, 42, 109, 0.25)"}`
        }}>
          <span style={{
            width: "8px",
            height: "8px",
            borderRadius: "50%",
            background: serverOnline ? "var(--accent-emerald)" : "var(--accent-rose)",
            boxShadow: `0 0 8px ${serverOnline ? "var(--accent-emerald)" : "var(--accent-rose)"}`,
            flexShrink: 0
          }} />
          <span style={{
            fontSize: "0.75rem",
            fontWeight: 600,
            color: serverOnline ? "var(--accent-emerald)" : "var(--accent-rose)",
            whiteSpace: "nowrap"
          }}>
            {serverOnline ? "ONLINE" : "OFFLINE"}
          </span>
        </div>

        {/* Desktop-only Security Chip */}
        <div className="desktop-only" style={{
          padding: "4px 12px",
          borderRadius: "8px",
          background: "rgba(255, 255, 255, 0.04)",
          border: "1px solid rgba(255, 255, 255, 0.08)",
          fontSize: "0.8rem",
          color: "var(--text-secondary)",
          alignItems: "center",
          gap: "6px"
        }}>
          <ShieldCheck size={14} color="var(--accent-cyan)" />
          <span>Security Sandbox Active</span>
        </div>
      </div>

      {/* Right side: Audio toggle & User Auth */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
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
            gap: "5px",
            cursor: "pointer",
            fontSize: "0.76rem",
            fontWeight: 600,
            transition: "all 0.2s ease",
            flexShrink: 0
          }}
        >
          {soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
          <span className="desktop-only">{soundEnabled ? "AUDIO ON" : "MUTED"}</span>
        </button>

        {/* User profile / login button */}
        {user ? (
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "4px 8px",
              borderRadius: "20px",
              background: "rgba(255, 255, 255, 0.06)",
              border: "1px solid rgba(255, 255, 255, 0.1)"
            }}>
              <div style={{
                width: "24px",
                height: "24px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-purple))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: "0.72rem",
                color: "#050811",
                flexShrink: 0
              }}>
                {user.name ? user.name[0].toUpperCase() : "U"}
              </div>
              <span className="desktop-only" style={{ fontSize: "0.82rem", fontWeight: 500, color: "var(--text-primary)", maxWidth: "120px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
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
                padding: "6px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center"
              }}
            >
              <LogOut size={16} />
            </button>
          </div>
        ) : (
          <button
            onClick={onOpenAuthModal}
            className="btn-primary"
            style={{ padding: "6px 12px", fontSize: "0.8rem", whiteSpace: "nowrap" }}
          >
            <LogIn size={14} />
            <span className="desktop-only">Sign In</span>
          </button>
        )}
      </div>
    </header>
  );
}
