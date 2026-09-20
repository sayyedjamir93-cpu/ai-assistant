import React, { useState, useEffect } from "react";
import { CheckSquare, Plus, Trash2, Calendar, Bell, Clock } from "lucide-react";
import { api } from "../services/api";

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [filter, setFilter] = useState("all"); // 'all' | 'pending' | 'completed'

  // New task form state
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newDueDate, setNewDueDate] = useState("");

  // New reminder form state
  const [remTitle, setRemTitle] = useState("");
  const [remTime, setRemTime] = useState("");

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const taskList = await api.tasks.getTasks();
      setTasks(taskList || []);
      const remList = await api.reminders.getReminders();
      setReminders(remList || []);
    } catch (e) {
      console.warn(e);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      const created = await api.tasks.createTask({
        title: newTitle.trim(),
        description: newDescription.trim() || null,
        due_date: newDueDate ? new Date(newDueDate).toISOString() : null,
        completed: false
      });
      setTasks((prev) => [created, ...prev]);
      setNewTitle("");
      setNewDescription("");
      setNewDueDate("");
    } catch (err) {
      alert(err.message);
    }
  };

  const handleToggleTask = async (task) => {
    try {
      const updated = await api.tasks.updateTask(task.id, { completed: !task.completed });
      setTasks((prev) => prev.map((t) => (t.id === task.id ? updated : t)));
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteTask = async (id) => {
    try {
      await api.tasks.deleteTask(id);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateReminder = async (e) => {
    e.preventDefault();
    if (!remTitle.trim() || !remTime) return;
    try {
      const created = await api.reminders.createReminder({
        title: remTitle.trim(),
        remind_at: new Date(remTime).toISOString()
      });
      setReminders((prev) => [...prev, created]);
      setRemTitle("");
      setRemTime("");
    } catch (err) {
      alert(err.message);
    }
  };

  const handleDeleteReminder = async (id) => {
    try {
      await api.reminders.deleteReminder(id);
      setReminders((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const filteredTasks = tasks.filter((t) => {
    if (filter === "pending") return !t.completed;
    if (filter === "completed") return t.completed;
    return true;
  });

  return (
    <div style={{ padding: "32px", maxWidth: "1200px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: "28px" }}>
        <h2 style={{ fontFamily: "var(--font-display)", fontSize: "1.8rem", fontWeight: 700 }}>
          Tasks & Scheduled Reminders
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>
          Organize assignments, track pending deadlines, and schedule alerts.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.3fr 0.7fr", gap: "24px" }}>
        
        {/* Tasks Section */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          
          {/* Create Task Form */}
          <div className="glass-panel" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Plus size={16} color="var(--accent-cyan)" /> Create New Task
            </h3>
            <form onSubmit={handleCreateTask} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <input
                type="text"
                required
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="Task title (e.g. Finish Data Structures problem set)..."
                className="input-glass"
              />
              <div style={{ display: "flex", gap: "10px" }}>
                <input
                  type="text"
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Optional details / description"
                  className="input-glass"
                  style={{ flex: 1 }}
                />
                <input
                  type="datetime-local"
                  value={newDueDate}
                  onChange={(e) => setNewDueDate(e.target.value)}
                  className="input-glass"
                  style={{ width: "220px", cursor: "pointer" }}
                />
              </div>
              <button type="submit" className="btn-primary" style={{ padding: "10px", width: "100%" }}>
                Add Task
              </button>
            </form>
          </div>

          {/* Tasks Board with Filter */}
          <div className="glass-panel" style={{ padding: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700 }}>Task Board ({filteredTasks.length})</h3>
              
              <div style={{ display: "flex", gap: "6px" }}>
                {["all", "pending", "completed"].map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    style={{
                      padding: "4px 10px",
                      borderRadius: "6px",
                      background: filter === f ? "rgba(0, 229, 255, 0.2)" : "transparent",
                      color: filter === f ? "var(--accent-cyan)" : "var(--text-muted)",
                      border: "none",
                      fontSize: "0.78rem",
                      cursor: "pointer",
                      textTransform: "capitalize",
                      fontWeight: filter === f ? 600 : 400
                    }}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {filteredTasks.length === 0 ? (
                <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", textAlign: "center", padding: "30px" }}>
                  No tasks found in this view.
                </p>
              ) : (
                filteredTasks.map((t) => (
                  <div
                    key={t.id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "12px 16px",
                      borderRadius: "10px",
                      background: t.completed ? "rgba(0, 245, 155, 0.05)" : "rgba(255, 255, 255, 0.03)",
                      border: `1px solid ${t.completed ? "rgba(0, 245, 155, 0.2)" : "rgba(255, 255, 255, 0.08)"}`
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <input
                        type="checkbox"
                        checked={t.completed}
                        onChange={() => handleToggleTask(t)}
                        style={{ cursor: "pointer", width: "16px", height: "16px", accentColor: "var(--accent-emerald)" }}
                      />
                      <div>
                        <div style={{
                          fontSize: "0.95rem",
                          fontWeight: 500,
                          color: t.completed ? "var(--text-muted)" : "var(--text-primary)",
                          textDecoration: t.completed ? "line-through" : "none"
                        }}>
                          {t.title}
                        </div>
                        {t.description && (
                          <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "2px" }}>
                            {t.description}
                          </p>
                        )}
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      {t.due_date && (
                        <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                          <Calendar size={13} />
                          {new Date(t.due_date).toLocaleDateString()}
                        </div>
                      )}
                      <button
                        onClick={() => handleDeleteTask(t.id)}
                        style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Reminders Column */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          
          {/* Create Reminder */}
          <div className="glass-panel" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}>
              <Bell size={16} color="var(--accent-purple)" /> Schedule Reminder
            </h3>
            <form onSubmit={handleCreateReminder} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <input
                type="text"
                required
                value={remTitle}
                onChange={(e) => setRemTitle(e.target.value)}
                placeholder="Reminder note..."
                className="input-glass"
              />
              <input
                type="datetime-local"
                required
                value={remTime}
                onChange={(e) => setRemTime(e.target.value)}
                className="input-glass"
                style={{ cursor: "pointer" }}
              />
              <button type="submit" className="btn-secondary" style={{ padding: "10px" }}>
                Save Reminder
              </button>
            </form>
          </div>

          {/* Active Reminders List */}
          <div className="glass-panel" style={{ padding: "20px" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "14px" }}>
              Active Reminders ({reminders.length})
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {reminders.map((r) => (
                <div
                  key={r.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "rgba(157, 78, 221, 0.08)",
                    border: "1px solid rgba(157, 78, 221, 0.2)"
                  }}
                >
                  <div>
                    <div style={{ fontSize: "0.88rem", fontWeight: 500 }}>{r.title}</div>
                    <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.75rem", color: "var(--accent-purple)", marginTop: "2px" }}>
                      <Clock size={12} />
                      {new Date(r.remind_at).toLocaleString()}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteReminder(r.id)}
                    style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
