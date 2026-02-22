"use client";

import { ReactNode } from "react";
import { clsx } from "clsx";

interface StatCardProps {
  icon: ReactNode;
  value: string | number;
  unit?: string;
  label: string;
  trend?: number;          // percentage change
  color?: string;          // tailwind text color
}

export function StatCard({ icon, value, unit, label, trend, color = "text-eco-600" }: StatCardProps) {
  return (
    <div className="eco-card flex items-start gap-4">
      <div className={clsx("w-12 h-12 rounded-xl flex items-center justify-center", color === "text-eco-600" ? "bg-eco-50" : "bg-gray-50")}>
        <span className={color}>{icon}</span>
      </div>
      <div>
        <p className={clsx("stat-value", color)}>
          {value}
          {unit && <span className="text-lg font-medium ml-1 text-gray-400">{unit}</span>}
        </p>
        <p className="stat-label">{label}</p>
        {trend !== undefined && (
          <p className={clsx("text-xs mt-1 font-medium", trend >= 0 ? "text-eco-500" : "text-red-500")}>
            {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}% vs last week
          </p>
        )}
      </div>
    </div>
  );
}
