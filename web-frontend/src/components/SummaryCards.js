// src/components/SummaryCards.js
import React from "react";
import "./SummaryCards.css";

export default function SummaryCards({ summary }) {
  if (!summary) return null;

  const total = summary.total_count || 0;
  const av = summary.averages || {};

  const cards = [
    { label: "Total Rows", value: total, color: "#FFF58A" },
    { label: "Avg Flowrate", value: av.Flowrate?.toFixed?.(2) ?? av.Flowrate, color: "#FFBBE1" },
    { label: "Avg Pressure", value: av.Pressure?.toFixed?.(2) ?? av.Pressure, color: "#DD7BDF" },
    { label: "Avg Temperature", value: av.Temperature?.toFixed?.(2) ?? av.Temperature, color: "#B3BFFF" },
  ];

  return (
    <section className="summary-section">
      <h3 className="summary-title">Dataset Summary</h3>
      <div className="summary-grid">
        {cards.map((c) => (
          <div
            key={c.label}
            className="summary-card"
            style={{ "--accent": c.color }}
          >
            <div className="summary-label">{c.label}</div>
            <div className="summary-value">{c.value ?? "—"}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
