/**
 * SADIE Frontend API Client
 * Connects React UI components to FastAPI Backend endpoints.
 */

const API_BASE = "http://127.0.0.1:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("sadie_token");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {})
    }
  };

  try {
    const response = await fetch(url, config);
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: "Network response was not ok" }));
      throw new Error(errorData.detail || `Request failed with status ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    console.error(`API Error on [${url}]:`, err);
    throw err;
  }
}

export const api = {
  // Authentication
  auth: {
    login: (email, password) => request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
    register: (name, email, password) => request("/auth/register", { method: "POST", body: JSON.stringify({ name, email, password }) }),
    getMe: () => request("/auth/me"),
    logout: () => request("/auth/logout", { method: "POST" })
  },

  // Assistant & Chat
  assistant: {
    chat: (message, conversation_id = null, mode = "normal") =>
      request("/assistant/chat", { method: "POST", body: JSON.stringify({ message, conversation_id, mode }) }),
    getConversations: () => request("/assistant/conversations"),
    getConversation: (id) => request(`/assistant/conversations/${id}`),
    deleteConversation: (id) => request(`/assistant/conversations/${id}`, { method: "DELETE" })
  },

  // Voice Assistant
  voice: {
    chat: (payload) => request("/voice/chat", { method: "POST", body: JSON.stringify(payload) }),
    synthesize: (text, language = "en") => request("/voice/synthesize", { method: "POST", body: JSON.stringify({ text, language }) }),
    transcribe: (audio_base64, language = "en-US") => request("/voice/transcribe", { method: "POST", body: JSON.stringify({ audio_base64, language }) })
  },

  // Study Mode
  study: {
    start: (subject, task_name, duration_minutes) =>
      request("/study/start", { method: "POST", body: JSON.stringify({ subject, task_name, duration_minutes }) }),
    getCurrent: () => request("/study/current"),
    pause: () => request("/study/pause", { method: "POST" }),
    resume: () => request("/study/resume", { method: "POST" }),
    complete: () => request("/study/complete", { method: "POST" }),
    startBreak: (break_type = "short", duration_minutes = 5) =>
      request("/study/break", { method: "POST", body: JSON.stringify({ break_type, duration_minutes }) }),
    getAnalytics: () => request("/study/analytics"),
    getHistory: () => request("/study/history")
  },

  // Coding Mode
  coding: {
    explainConcept: (concept, language = "python") =>
      request("/coding/explain-concept", { method: "POST", body: JSON.stringify({ concept, language }) }),
    diagnoseError: (error_message, language = "python", code_snippet = null) =>
      request("/coding/diagnose-error", { method: "POST", body: JSON.stringify({ error_message, language, code_snippet }) }),
    reviewCode: (code, language = "python") =>
      request("/coding/review-code", { method: "POST", body: JSON.stringify({ code, language }) }),
    getLanguages: () => request("/coding/languages")
  },

  // Tasks & Reminders
  tasks: {
    getTasks: (completed = null) => request(`/tasks${completed !== null ? `?completed=${completed}` : ""}`),
    createTask: (task) => request("/tasks", { method: "POST", body: JSON.stringify(task) }),
    updateTask: (id, updates) => request(`/tasks/${id}`, { method: "PUT", body: JSON.stringify(updates) }),
    deleteTask: (id) => request(`/tasks/${id}`, { method: "DELETE" })
  },

  reminders: {
    getReminders: () => request("/reminders"),
    createReminder: (reminder) => request("/reminders", { method: "POST", body: JSON.stringify(reminder) }),
    deleteReminder: (id) => request(`/reminders/${id}`, { method: "DELETE" })
  },

  // Notes
  notes: {
    getNotes: (query = "") => request(`/notes${query ? `?q=${encodeURIComponent(query)}` : ""}`),
    createNote: (note) => request("/notes", { method: "POST", body: JSON.stringify(note) }),
    updateNote: (id, updates) => request(`/notes/${id}`, { method: "PUT", body: JSON.stringify(updates) }),
    deleteNote: (id) => request(`/notes/${id}`, { method: "DELETE" })
  },

  // Controlled Memory
  memory: {
    getMemories: () => request("/memory"),
    addMemory: (key, value) => request("/memory", { method: "POST", body: JSON.stringify({ key, value }) }),
    deleteMemory: (id) => request(`/memory/${id}`, { method: "DELETE" }),
    clearAll: () => request("/memory", { method: "DELETE" })
  },

  // Tools & System
  tools: {
    listTools: () => request("/tools"),
    executeTool: (tool_name, parameters = {}) =>
      request("/tools/execute", { method: "POST", body: JSON.stringify({ tool_name, parameters }) }),
    playMedia: (platform = "youtube", query = "") =>
      request("/tools/execute", { method: "POST", body: JSON.stringify({ tool_name: "play_media", parameters: { platform, query } }) }),
    getPermissions: () => request("/tools/permissions"),
    updatePermission: (tool_name, is_allowed) =>
      request(`/tools/permissions/${tool_name}`, { method: "PUT", body: JSON.stringify({ is_allowed }) }),
    getTimers: () => request("/tools/timers")
  },

  system: {
    getInfo: () => request("/system/info"),
    getHealth: () => request("/health")
  },

  // Contacts & WhatsApp Messaging
  contacts: {
    getContacts: () => request("/contacts"),
    createContact: (name, phone_number) => request("/contacts", { method: "POST", body: JSON.stringify({ name, phone_number }) }),
    deleteContact: (id) => request(`/contacts/${id}`, { method: "DELETE" }),
    sendMessage: (contact_name, message, phone_number = null) =>
      request("/contacts/send-message", { method: "POST", body: JSON.stringify({ contact_name, message, phone_number }) })
  },

  // Incoming Messages & WhatsApp Voice Announcer
  messages: {
    getNotifications: (unread_only = false) => request(`/messages/notifications?unread_only=${unread_only}`),
    simulateIncoming: (sender = "Sakshi", content = "Hey, are you free for the meeting?", app_name = "WhatsApp") =>
      request("/messages/simulate", { method: "POST", body: JSON.stringify({ sender, content, app_name }) }),
    readAloud: () => request("/messages/read-aloud"),
    markRead: (message_id = null, all = false) =>
      request("/messages/mark-read", { method: "POST", body: JSON.stringify({ message_id, all }) })
  }
};

