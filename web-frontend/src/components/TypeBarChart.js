// src/components/TypeBarChart.js
import React, { useMemo } from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

export default function TypeBarChart({ distribution }) {
  const labels = useMemo(() => Object.keys(distribution || {}), [distribution]);
  const values = useMemo(() => Object.values(distribution || {}), [distribution]);

  if (!labels.length) return null;

  const data = {
    labels,
    datasets: [
  {
    label: "Count",
    data: values,
    backgroundColor: "rgba(56, 189, 248, 0.8)",  // bright cyan
    borderColor: "rgba(56, 189, 248, 1)",        // border color
    borderWidth: 2,
    hoverBackgroundColor: "rgba(96, 226, 255, 1)", // brighter on hover
  },
],
  };

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { beginAtZero: true, ticks: { precision: 0 } },
    },
  };

  return (
    <div className="card">
      <h3>Type Distribution</h3>
      <Bar data={data} options={options} />
    </div>
  );
}
