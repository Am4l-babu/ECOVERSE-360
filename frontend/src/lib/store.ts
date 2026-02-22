import { create } from "zustand";

// ── Auth Store ───────────────────────────────────────────────────────────
interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  eco_level: string;
  total_points: number;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token:
    typeof window !== "undefined"
      ? localStorage.getItem("ecoverse_token")
      : null,
  setAuth: (user, token) => {
    localStorage.setItem("ecoverse_token", token);
    set({ user, token });
  },
  logout: () => {
    localStorage.removeItem("ecoverse_token");
    set({ user: null, token: null });
  },
}));

// ── Dashboard Store ──────────────────────────────────────────────────────
interface DashboardStats {
  aqi: number;
  co2_saved: number;
  bins_collected: number;
  points_earned: number;
  active_sensors: number;
  active_users: number;
}

interface DashboardState {
  stats: DashboardStats | null;
  loading: boolean;
  setStats: (stats: DashboardStats) => void;
  setLoading: (loading: boolean) => void;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  stats: null,
  loading: false,
  setStats: (stats) => set({ stats, loading: false }),
  setLoading: (loading) => set({ loading }),
}));
