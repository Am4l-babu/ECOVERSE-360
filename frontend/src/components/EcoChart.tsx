"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface DataPoint {
  name: string;
  value: number;
}

interface EcoChartProps {
  data: DataPoint[];
  title: string;
  color?: string;
  unit?: string;
  height?: number;
}

export function EcoChart({
  data,
  title,
  color = "#16b364",
  unit = "",
  height = 260,
}: EcoChartProps) {
  return (
    <div className="eco-card">
      <h3 className="font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`grad-${title}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.15} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} stroke="#d0d0d0" />
          <YAxis tick={{ fontSize: 12 }} stroke="#d0d0d0" />
          <Tooltip
            contentStyle={{
              borderRadius: "12px",
              border: "1px solid #e5e5e5",
              fontSize: "13px",
            }}
            formatter={(v: number) => [`${v} ${unit}`, title]}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            fill={`url(#grad-${title})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
