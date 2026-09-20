import React from "react";
import {
  LayoutDashboard,
  MessageSquare,
  GraduationCap,
  Code2,
  CheckSquare,
  StickyNote,
  BrainCircuit,
  Wrench,
  Settings,
  Sparkles,
  Volume2,
  X
} from "lucide-react";

export default function Sidebar({ activeTab, setActiveTab, activeMode, setActiveMode, isMobileOpen, onCloseMobile }) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "chat", label: "Assistant Chat", icon: MessageSquare },
    { id: "study", label: "Study Mode", icon: GraduationCap, badge: activeMode === "study" ? "ACTIVE" : null },
    { id: "coding", label: "Coding Mode", icon: Code2, badge: activeMode === "coding" ? "ACTIVE" : null },
    { id: "tasks", label: "Tasks & Reminders", icon: CheckSquare },
    { id: "notes", label: "Notes & Voice", icon: StickyNote },
    { id: "memory", label: "Controlled Memory", icon: BrainCircuit },
    { id: "tools", label: "Desktop Tools & System", icon: Wrench },
    { id: "settings", label: "Settings & Security", icon: Settings },
  ];

  const renderNavContent = (isDrawer = false) => (
    <>
      {/* Brand Header */}
      <div style={{
        padding: "20px",
        display: "flex",
        alignItems: "center",
        justifyContent: isDrawer ? "space-between" : "flex-start",
        gap: "12px",
        borderBottom: "1px solid rgba(255, 255, 255, 0.06)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            width: "38px",
            height: "38px",
            borderRadius: "10px",
            background: "linear-gradient(135deg, #00e5ff 0%, #9d4edd 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 0 20px rgba(0, 229, 255, 0.4)"
          }}>
            <Sparkles size={20} color="#050811" />
          </div>
          <div>
            <h1 style={{
              fontFamily: "var(--font-display)",
              fontWeight: 800,
              fontSize: "1.2rem",
              letterSpacing: "1.5px",
              background: "linear-gradient(90deg, #00e5ff, #ffffff)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}>
              SADIE
            </h1>
            <p style={{ fontSize: "0.68rem", color: "var(--text-muted)", letterSpacing: "0.5px" }}>
              AI PERSONAL ASSISTANT
            </p>
          </div>
        </div>

        {isDrawer && (
          <button
            onClick={onCloseMobile}
            style={{
              background: "rgba(255, 255, 255, 0.06)",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              borderRadius: "8px",
              color: "var(--text-secondary)",
              width: "34px",
              height: "34px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor: "pointer"
            }}
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Navigation Links */}
      <nav style={{ flex: 1, padding: "14px 10px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "4px" }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                setActiveTab(item.id);
                if (isDrawer && onCloseMobile) onCloseMobile();
              }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "12px",
                padding: "10px 14px",
                borderRadius: "10px",
                border: "none",
                background: isActive
                  ? "linear-gradient(90deg, rgba(0, 229, 255, 0.15), rgba(157, 78, 221, 0.08))"
                  : "transparent",
                color: isActive ? "var(--accent-cyan)" : "var(--text-secondary)",
                fontFamily: "var(--font-display)",
                fontWeight: isActive ? 600 : 500,
                fontSize: "0.9rem",
                cursor: "pointer",
                textAlign: "left",
                transition: "all 0.2s ease",
                borderLeft: isActive ? "3px solid var(--accent-cyan)" : "3px solid transparent"
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)";
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.background = "transparent";
              }}
            >
              <Icon size={18} color={isActive ? "var(--accent-cyan)" : "var(--text-secondary)"} />
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge && (
                <span style={{
                  fontSize: "0.65rem",
                  padding: "2px 6px",
                  borderRadius: "6px",
                  background: "rgba(0, 229, 255, 0.2)",
                  color: "var(--accent-cyan)",
                  fontWeight: 700
                }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Mode Status Footer */}
      <div style={{
        padding: "16px",
        background: "rgba(15, 21, 35, 0.9)",
        borderTop: "1px solid rgba(255, 255, 255, 0.06)",
        fontSize: "0.8rem",
        marginBottom: isDrawer ? "env(safe-area-inset-bottom, 0px)" : "0"
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "8px" }}>
          <span style={{ color: "var(--text-muted)" }}>Current Mode:</span>
          <span style={{
            color: activeMode === "study" ? "var(--accent-emerald)" : activeMode === "coding" ? "var(--accent-purple)" : "var(--accent-cyan)",
            fontWeight: 600,
            textTransform: "uppercase",
            fontSize: "0.75rem"
          }}>
            {activeMode}
          </span>
        </div>
        <div style={{ display: "flex", gap: "6px" }}>
          <button
            onClick={() => setActiveMode("normal")}
            style={{
              flex: 1,
              padding: "6px",
              fontSize: "0.75rem",
              borderRadius: "6px",
              background: activeMode === "normal" ? "rgba(0, 229, 255, 0.2)" : "rgba(255,255,255,0.05)",
              color: activeMode === "normal" ? "var(--accent-cyan)" : "var(--text-muted)",
              border: "none",
              cursor: "pointer",
              fontWeight: activeMode === "normal" ? 600 : 400
            }}
          >
            Normal
          </button>
          <button
            onClick={() => { setActiveMode("study"); setActiveTab("study"); if (isDrawer && onCloseMobile) onCloseMobile(); }}
            style={{
              flex: 1,
              padding: "6px",
              fontSize: "0.75rem",
              borderRadius: "6px",
              background: activeMode === "study" ? "rgba(0, 245, 155, 0.2)" : "rgba(255,255,255,0.05)",
              color: activeMode === "study" ? "var(--accent-emerald)" : "var(--text-muted)",
              border: "none",
              cursor: "pointer",
              fontWeight: activeMode === "study" ? 600 : 400
            }}
          >
            Study
          </button>
          <button
            onClick={() => { setActiveMode("coding"); setActiveTab("coding"); if (isDrawer && onCloseMobile) onCloseMobile(); }}
            style={{
              flex: 1,
              padding: "6px",
              fontSize: "0.75rem",
              borderRadius: "6px",
              background: activeMode === "coding" ? "rgba(157, 78, 221, 0.2)" : "rgba(255,255,255,0.05)",
              color: activeMode === "coding" ? "var(--accent-purple)" : "var(--text-muted)",
              border: "none",
              cursor: "pointer",
              fontWeight: activeMode === "coding" ? 600 : 400
            }}
          >
            Coding
          </button>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Sidebar (hidden on screens < 768px via CSS) */}
      <aside
        className="desktop-only"
        style={{
          width: "250px",
          minWidth: "250px",
          background: "rgba(10, 14, 24, 0.85)",
          backdropFilter: "blur(20px)",
          borderRight: "1px solid rgba(255, 255, 255, 0.08)",
          flexDirection: "column",
          height: "100vh",
          position: "sticky",
          top: 0,
          zIndex: 40
        }}
      >
        {renderNavContent(false)}
      </aside>

      {/* Mobile Slide-over Drawer & Overlay */}
      {isMobileOpen && (
        <>
          <div className="mobile-drawer-backdrop" onClick={onCloseMobile} />
          <div className="mobile-drawer-content">
            {renderNavContent(true)}
          </div>
        </>
      )}
    </>
  );
}
