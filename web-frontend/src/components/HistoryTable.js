// src/components/HistoryTable.js
import React from "react";

export default function HistoryTable({ items }) {
  if (!items?.length) return null;
  return (
    <div className="card">
      <h3>Last 5 Uploads</h3>
      <div className="table">
        <div className="thead">
          <div>File</div>
          <div>Uploaded At</div>
          <div>Total Rows</div>
        </div>
        {items.map((it) => (
          <div className="trow" key={it.dataset_id}>
            <div>{it.filename}</div>
            <div>{new Date(it.uploaded_at).toLocaleString()}</div>
            <div>{it.summary?.total_count ?? "–"}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
