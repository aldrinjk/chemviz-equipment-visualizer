// src/components/TypeBarChart.js
import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
} from "recharts";

const COLORS = ["#FFF58A", "#FFBBE1", "#DD7BDF", "#B3BFFF"];

export default function TypeBarChart({ distribution }) {
  const data = Object.entries(distribution || {}).map(([name, value]) => ({
    name,
    count: value,
  }));

  if (!data.length) {
    return <div className="muted">No type data available.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(179,191,255,0.25)" />
        <XAxis dataKey="name" stroke="#9CA3AF" />
        <YAxis stroke="#9CA3AF" />
        <Tooltip
          contentStyle={{
            backgroundColor: "#020617",
            borderRadius: 10,
            border: "1px solid rgba(179,191,255,0.5)",
            fontSize: 12,
          }}
        />
        <Bar dataKey="count" radius={[8, 8, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
