"use client";

import {
  Wind,
  Trash2,
  Zap,
  Droplets,
  Leaf,
  Users,
  Activity,
  TrendingDown,
} from "lucide-react";
import { StatCard } from "@/components/StatCard";
import { EcoChart } from "@/components/EcoChart";
import { LeaderboardTable } from "@/components/LeaderboardTable";

// Demo data — will be replaced with API calls
const weeklyAQI = [
  { name: "Mon", value: 42 },
  { name: "Tue", value: 38 },
  { name: "Wed", value: 55 },
  { name: "Thu", value: 47 },
  { name: "Fri", value: 34 },
  { name: "Sat", value: 29 },
  { name: "Sun", value: 31 },
];

const weeklyCO2 = [
  { name: "Mon", value: 1200 },
  { name: "Tue", value: 1350 },
  { name: "Wed", value: 980 },
  { name: "Thu", value: 1100 },
  { name: "Fri", value: 1500 },
  { name: "Sat", value: 800 },
  { name: "Sun", value: 650 },
];

const weeklyEnergy = [
  { name: "Mon", value: 340 },
  { name: "Tue", value: 310 },
  { name: "Wed", value: 380 },
  { name: "Thu", value: 290 },
  { name: "Fri", value: 420 },
  { name: "Sat", value: 250 },
  { name: "Sun", value: 210 },
];

const demoLeaderboard = [
  { rank: 1, username: "EcoChampion", level: "Planetary Guardian", total_points: 12450, co2_saved: 342.5 },
  { rank: 2, username: "GreenNinja", level: "Ecosystem Architect", total_points: 9870, co2_saved: 275.1 },
  { rank: 3, username: "TreeHugger", level: "Climate Champion", total_points: 8200, co2_saved: 198.3 },
  { rank: 4, username: "SolarKid", level: "Sustainability Hero", total_points: 6540, co2_saved: 156.7 },
  { rank: 5, username: "WaterSaver", level: "Green Warrior", total_points: 5120, co2_saved: 134.2 },
];

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500 mt-1">Real-time sustainability overview</p>
      </div>

      {/* ── Stat Cards ────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
        <StatCard
          icon={<Wind className="w-6 h-6" />}
          value={42}
          unit="AQI"
          label="Air Quality Index"
          trend={-8.3}
          color="text-eco-600"
        />
        <StatCard
          icon={<TrendingDown className="w-6 h-6" />}
          value="1.2k"
          unit="kg"
          label="CO₂ Saved Today"
          trend={12.5}
          color="text-carbon-600"
        />
        <StatCard
          icon={<Trash2 className="w-6 h-6" />}
          value="87"
          unit="%"
          label="Waste Recycled"
          trend={3.2}
          color="text-amber-500"
        />
        <StatCard
          icon={<Zap className="w-6 h-6" />}
          value="340"
          unit="kWh"
          label="Energy Saved"
          trend={-2.1}
          color="text-blue-500"
        />
      </div>

      {/* ── Charts ────────────────────────────────────────────── */}
      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        <EcoChart
          data={weeklyAQI}
          title="Air Quality Index (7 days)"
          color="#16b364"
          unit="AQI"
        />
        <EcoChart
          data={weeklyCO2}
          title="CO₂ Saved (7 days)"
          color="#9b70f1"
          unit="kg"
        />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        <EcoChart
          data={weeklyEnergy}
          title="Energy Consumption (7 days)"
          color="#3b82f6"
          unit="kWh"
        />
        <LeaderboardTable entries={demoLeaderboard} />
      </div>

      {/* ── Quick Actions ─────────────────────────────────────── */}
      <div className="eco-card">
        <h3 className="font-semibold mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          {[
            { icon: <Leaf className="w-4 h-4" />, label: "Log Recycling" },
            { icon: <Droplets className="w-4 h-4" />, label: "Report Leak" },
            { icon: <Users className="w-4 h-4" />, label: "Start Carpool" },
            { icon: <Activity className="w-4 h-4" />, label: "Join Challenge" },
          ].map((a) => (
            <button key={a.label} className="eco-btn-secondary gap-2">
              {a.icon}
              {a.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
