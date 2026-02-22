"use client";

import { Trophy } from "lucide-react";
import { clsx } from "clsx";

interface LeaderboardEntry {
  rank: number;
  username: string;
  level: string;
  total_points: number;
  co2_saved: number;
}

export function LeaderboardTable({ entries }: { entries: LeaderboardEntry[] }) {
  return (
    <div className="eco-card overflow-hidden">
      <div className="flex items-center gap-2 mb-5">
        <Trophy className="w-5 h-5 text-amber-500" />
        <h3 className="font-semibold">Leaderboard</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 border-b border-gray-50">
              <th className="pb-3 pr-4 font-medium">#</th>
              <th className="pb-3 pr-4 font-medium">User</th>
              <th className="pb-3 pr-4 font-medium">Level</th>
              <th className="pb-3 pr-4 font-medium text-right">Points</th>
              <th className="pb-3 font-medium text-right">CO₂ Saved</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.rank} className="border-b border-gray-50 last:border-0 hover:bg-gray-50/50 transition-colors">
                <td className="py-3 pr-4">
                  <span
                    className={clsx(
                      "w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold",
                      e.rank === 1 && "bg-amber-100 text-amber-700",
                      e.rank === 2 && "bg-gray-100 text-gray-600",
                      e.rank === 3 && "bg-orange-50 text-orange-600",
                      e.rank > 3 && "bg-gray-50 text-gray-400"
                    )}
                  >
                    {e.rank}
                  </span>
                </td>
                <td className="py-3 pr-4 font-medium">{e.username}</td>
                <td className="py-3 pr-4">
                  <span className="eco-badge bg-eco-50 text-eco-700">{e.level}</span>
                </td>
                <td className="py-3 pr-4 text-right font-semibold text-carbon-600">
                  {e.total_points.toLocaleString()}
                </td>
                <td className="py-3 text-right text-gray-500">
                  {e.co2_saved.toFixed(1)} kg
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
