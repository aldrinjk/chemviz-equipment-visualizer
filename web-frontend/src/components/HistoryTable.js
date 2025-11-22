// src/components/HistoryTable.js
import React from "react";
import "./HistoryTable.css";

export default function HistoryTable({ items }) {
  if (!items || items.length === 0) {
    return (
      <section className="history-section">
        <h3 className="history-title">Last 5 Uploads</h3>
        <div className="history-empty">No uploads yet. Upload a CSV to see history.</div>
      </section>
    );
  }

  return (
    <section className="history-section">
      <h3 className="history-title">Last 5 Uploads</h3>

      <div className="history-table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>File</th>
              <th>Uploaded At</th>
              <th>Total Rows</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <tr key={it.dataset_id}>
                <td className="history-filename">{it.filename}</td>
                <td>{new Date(it.uploaded_at).toLocaleString()}</td>
                <td>{it.summary?.total_count ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
