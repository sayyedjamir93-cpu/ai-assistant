import React, { useState, useEffect } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle,
  Coffee,
  Plus,
  BookOpen,
  Sparkles,
  BarChart3,
  Clock
} from "lucide-react";
import confetti from "canvas-confetti";
import { api } from "../services/api";

export default function StudyPage({ onPlayAudio }) {
  const [subject, setSubject] = useState("Python");
  const [taskName, setTaskName] = useState("Recursion & Algorithms");
  const [duration, setDuration] = useState(25);
  const [sessionActive, setSessionActive] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const [secondsRemaining, setSecondsRemaining] = useState(25 * 60);
  const [studyTasks, setStudyTasks] = useState([]);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [analytics, setAnalytics] = useState(null);

  // Load active study session and tasks on mount
  useEffect(() => {
    async function loadData() {
      try {
        const cur = await api.study.getCurrent();
        if (cur.is_active && cur.ends_at) {
          setSessionActive(true);
          setSubject(cur.subject || "Python");
          setTaskName(cur.task_name || "");
          setIsPaused(cur.is_paused);
          setIsBreak(cur.is_break);

          const ends = new Date(cur.ends_at).getTime();
          const now = Date.now();
          const leftSec = Math.max(0, Math.floor((ends - now) / 1000));
          setSecondsRemaining(leftSec);
        }

        const tasksList = await api.tasks.getTasks();
        setStudyTasks(tasksList || []);

        const stats = await api.study.getAnalytics();
        setAnalytics(stats);
      } catch (e) {
        console.warn(e);
      }
    }
    loadData();
  }, []);

  // Countdown timer tick
  useEffect(() => {
    let interval = null;
    if (sessionActive && !isPaused && secondsRemaining > 0) {
      interval = setInterval(() => {
        setSecondsRemaining((prev) => prev - 1);
      }, 1000);
    } else if (secondsRemaining === 0 && sessionActive) {
      // Session finished
      confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
    }
    return () => clearInterval(interval);
  }, [sessionActive, isPaused, secondsRemaining]);

  const handleStartSession = async () => {
    try {
      const res = await api.study.start(subject, taskName, duration);
      setSessionActive(true);
      setIsPaused(false);
      setIsBreak(false);
      setSecondsRemaining(duration * 60);

      // Refresh tasks
      const tasksList = await api.tasks.getTasks();
      setStudyTasks(tasksList);
    } catch (err) {
      alert(`Could not start session: ${err.message}`);
    }
  };

  const handlePause = async () => {
    await api.study.pause();
    setIsPaused(true);
  };

  const handleResume = async () => {
    await api.study.resume();
    setIsPaused(false);
  };

  const handleCompleteSession = async () => {
    await api.study.complete();
    setSessionActive(false);
    confetti({ particleCount: 120, spread: 90, origin: { y: 0.6 } });
    const stats = await api.study.getAnalytics();
    setAnalytics(stats);
  };

  const handleStartBreak = async (type) => {
    const mins = type === "short" ? 5 : 15;
    await api.study.startBreak(type, mins);
    setSessionActive(true);
    setIsBreak(true);
    setIsPaused(false);
    setSecondsRemaining(mins * 60);
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;
    try {
      const created = await api.tasks.createTask({
        title: newTaskTitle.trim(),
        description: `Study task for ${subject}`,
        completed: false
      });
      setStudyTasks((prev) => [created, ...prev]);
      setNewTaskTitle("");
    } catch (err) {
      alert(err.message);
    }
  };

  const handleToggleTask = async (task) => {
    try {
      const updated = await api.tasks.updateTask(task.id, { completed: !task.completed });
      setStudyTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
      const stats = await api.study.getAnalytics();
      setAnalytics(stats);
    } catch (err) {
      console.error(err);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const completedCount = studyTasks.filter((t) => t.completed).length;

  return (
    <div style={{ padding: "32px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "28px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.8rem", fontWeight: 700 }}>
            Study Mode & Pomodoro Focus
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Focused academic sprints, timed breaks, and subject task tracking.
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <button onClick={() => handleStartBreak("short")} className="btn-secondary" style={{ padding: "8px 14px", fontSize: "0.82rem" }}>
            <Coffee size={15} color="var(--accent-cyan)" /> 5m Short Break
          </button>
          <button onClick={() => handleStartBreak("long")} className="btn-secondary" style={{ padding: "8px 14px", fontSize: "0.82rem" }}>
            <Coffee size={15} color="var(--accent-purple)" /> 15m Long Break
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "24px" }}>
        
        {/* Left Column: Timer & Controls */}
        <div className="glass-panel" style={{ padding: "32px", display: "flex", flexDirection: "column", alignItems: "center" }}>
          
          {/* Subject / Task Inputs when not active */}
          {!sessionActive ? (
            <div style={{ width: "100%", maxWidth: "420px", display: "flex", flexDirection: "column", gap: "14px", marginBottom: "24px" }}>
              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Subject / Topic
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  className="input-glass"
                  placeholder="e.g. Python, Operating Systems, Math"
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Primary Focus Task
                </label>
                <input
                  type="text"
                  value={taskName}
                  onChange={(e) => setTaskName(e.target.value)}
                  className="input-glass"
                  placeholder="e.g. Master Recursion & Dynamic Programming"
                />
              </div>

              <div>
                <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)", marginBottom: "4px", display: "block" }}>
                  Session Duration
                </label>
                <div style={{ display: "flex", gap: "8px" }}>
                  {[25, 45, 60].map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setDuration(d)}
                      style={{
                        flex: 1,
                        padding: "8px",
                        borderRadius: "8px",
                        background: duration === d ? "rgba(0, 245, 155, 0.2)" : "rgba(255, 255, 255, 0.05)",
                        color: duration === d ? "var(--accent-emerald)" : "var(--text-secondary)",
                        border: `1px solid ${duration === d ? "var(--accent-emerald)" : "rgba(255, 255, 255, 0.1)"}`,
                        cursor: "pointer",
                        fontWeight: 600
                      }}
                    >
                      {d} min
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center", marginBottom: "16px" }}>
              <span style={{
                fontSize: "0.8rem",
                padding: "4px 12px",
                borderRadius: "20px",
                background: isBreak ? "rgba(157, 78, 221, 0.2)" : "rgba(0, 245, 155, 0.2)",
                color: isBreak ? "var(--accent-purple)" : "var(--accent-emerald)",
                fontWeight: 600
              }}>
                {isBreak ? "REST INTERVAL" : `SUBJECT: ${subject.toUpperCase()}`}
              </span>
              <h3 style={{ fontSize: "1.3rem", fontWeight: 700, marginTop: "8px" }}>
                {isBreak ? "Recharge and hydrate" : taskName || subject}
              </h3>
            </div>
          )}

          {/* Large Countdown Circular Display */}
          <div style={{
            position: "relative",
            width: "240px",
            height: "240px",
            borderRadius: "50%",
            background: "radial-gradient(circle, #0e172a 0%, #060a12 100%)",
            border: `4px solid ${isBreak ? "var(--accent-purple)" : "var(--accent-emerald)"}`,
            boxShadow: `0 0 40px ${isBreak ? "rgba(157, 78, 221, 0.3)" : "rgba(0, 245, 155, 0.3)"}`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            margin: "12px 0 28px 0"
          }}>
            <span style={{
              fontFamily: "var(--font-mono)",
              fontSize: "3.2rem",
              fontWeight: 700,
              letterSpacing: "2px",
              color: isBreak ? "var(--accent-purple)" : "var(--accent-emerald)"
            }}>
              {formatTime(secondsRemaining)}
            </span>
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", letterSpacing: "1px", textTransform: "uppercase" }}>
              {isPaused ? "PAUSED" : sessionActive ? "IN PROGRESS" : "READY"}
            </span>
          </div>

          {/* Action Buttons */}
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", justifyContent: "center" }}>
            {!sessionActive ? (
              <button onClick={handleStartSession} className="btn-primary" style={{ padding: "12px 32px", fontSize: "1rem" }}>
                <Play size={18} /> Start Study Session
              </button>
            ) : (
              <>
                {isPaused ? (
                  <button onClick={handleResume} className="btn-primary" style={{ padding: "10px 24px" }}>
                    <Play size={16} /> Resume
                  </button>
                ) : (
                  <button onClick={handlePause} className="btn-secondary" style={{ padding: "10px 24px" }}>
                    <Pause size={16} /> Pause
                  </button>
                )}

                <button onClick={handleCompleteSession} className="btn-primary" style={{ background: "linear-gradient(135deg, #00f59b, #00b4d8)", padding: "10px 24px" }}>
                  <CheckCircle size={16} /> Complete & Save
                </button>
              </>
            )}
          </div>
        </div>

        {/* Right Column: Today's Tasks & Productivity Progress */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          
          {/* Tasks Container */}
          <div className="glass-panel" style={{ padding: "24px", flex: 1, display: "flex", flexDirection: "column" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>Today's Study Tasks</h3>
              <span style={{ fontSize: "0.8rem", color: "var(--accent-cyan)", fontWeight: 600 }}>
                {completedCount}/{studyTasks.length} Completed
              </span>
            </div>

            {/* Task input */}
            <form onSubmit={handleAddTask} style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
              <input
                type="text"
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                placeholder="Add a study subtask..."
                className="input-glass"
                style={{ padding: "8px 12px", fontSize: "0.85rem" }}
              />
              <button type="submit" className="btn-primary" style={{ padding: "0 14px" }}>
                <Plus size={16} />
              </button>
            </form>

            {/* Task list */}
            <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "8px", maxHeight: "260px" }}>
              {studyTasks.map((t) => (
                <div
                  key={t.id}
                  onClick={() => handleToggleTask(t)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    padding: "10px 14px",
                    borderRadius: "8px",
                    background: t.completed ? "rgba(0, 245, 155, 0.06)" : "rgba(255, 255, 255, 0.03)",
                    border: `1px solid ${t.completed ? "rgba(0, 245, 155, 0.2)" : "rgba(255, 255, 255, 0.06)"}`,
                    cursor: "pointer",
                    transition: "all 0.2s ease"
                  }}
                >
                  <input
                    type="checkbox"
                    checked={t.completed}
                    onChange={() => {}}
                    style={{ cursor: "pointer", accentColor: "var(--accent-emerald)" }}
                  />
                  <span style={{
                    fontSize: "0.9rem",
                    color: t.completed ? "var(--text-muted)" : "var(--text-primary)",
                    textDecoration: t.completed ? "line-through" : "none"
                  }}>
                    {t.title}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Analytics Summary */}
          {analytics && (
            <div className="glass-card" style={{ padding: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px" }}>
                <BarChart3 size={18} color="var(--accent-cyan)" />
                <h4 style={{ fontSize: "0.95rem", fontWeight: 600 }}>Study Productivity</h4>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                <span>Total Focus Logged:</span>
                <strong style={{ color: "var(--accent-emerald)" }}>{analytics.total_study_minutes} mins</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "6px" }}>
                <span>Sessions Completed:</span>
                <strong style={{ color: "var(--accent-cyan)" }}>{analytics.sessions_completed}</strong>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
