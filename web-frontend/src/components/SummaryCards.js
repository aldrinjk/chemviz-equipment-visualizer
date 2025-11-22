// src/components/SummaryCards.js
import React from "react";

export default function SummaryCards({ summary }) {
  if (!summary) return null;
  const { total_count, averages } = summary;

  const fmt = (v) =>
    v === null || v === undefined ? "–" : Number(v).toFixed(2);

  return (
    <div className="grid">
      <div className="kpi">
        <div className="kpi-label">Total Rows</div>
        <div className="kpi-value">{total_count ?? "–"}</div>
      </div>
      <div className="kpi">
        <div className="kpi-label">Avg Flowrate</div>
        <div className="kpi-value">{fmt(averages?.Flowrate)}</div>
      </div>
      <div className="kpi">
        <div className="kpi-label">Avg Pressure</div>
        <div className="kpi-value">{fmt(averages?.Pressure)}</div>
      </div>
      <div className="kpi">
        <div className="kpi-label">Avg Temperature</div>
        <div className="kpi-value">{fmt(averages?.Temperature)}</div>
      </div>
    </div>
  );
}
