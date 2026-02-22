import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT on every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("ecoverse_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auth ─────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  profile: () => api.get("/auth/me"),
};

// ── Dashboard ────────────────────────────────────────────────────────────
export const dashboardApi = {
  stats: () => api.get("/dashboard/stats"),
  zones: () => api.get("/dashboard/zones"),
  trends: (metric: string, days = 30) =>
    api.get(`/dashboard/trends/${metric}?days=${days}`),
  activityFeed: (limit = 20) =>
    api.get(`/dashboard/activity-feed?limit=${limit}`),
  carbonSummary: () => api.get("/dashboard/carbon-summary"),
};

// ── Sensors ──────────────────────────────────────────────────────────────
export const sensorApi = {
  list: () => api.get("/sensors"),
  get: (id: string) => api.get(`/sensors/${id}`),
  stats: (id: string, hours = 24) =>
    api.get(`/sensors/${id}/stats?hours=${hours}`),
};

// ── EcoPoints ────────────────────────────────────────────────────────────
export const ecoApi = {
  balance: () => api.get("/ecopoints/balance"),
  history: (page = 1) => api.get(`/ecopoints/history?page=${page}`),
  leaderboard: (limit = 20) =>
    api.get(`/ecopoints/leaderboard?limit=${limit}`),
  earn: (data: { activity_type: string; metadata?: Record<string, unknown> }) =>
    api.post("/ecopoints/earn", data),
};

// ── Digital Twin ─────────────────────────────────────────────────────────
export const twinApi = {
  state: () => api.get("/digital-twin/state"),
  simulate: (scenario: Record<string, unknown>) =>
    api.post("/digital-twin/simulate", scenario),
  zones: () => api.get("/digital-twin/zones"),
  alerts: () => api.get("/digital-twin/alerts"),
};

export default api;
