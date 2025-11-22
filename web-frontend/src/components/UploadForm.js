// src/components/UploadForm.js
import React, { useState } from "react";
import api from "../api/index";

console.log("API base:", process.env.REACT_APP_API_BASE);
console.log("Has post:", typeof api.post);


export default function UploadForm({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    setError("");
    if (!file) {
      setError("Please choose a CSV file.");
      return;
    }
    const form = new FormData();
    form.append("file", file);
    try {
      setBusy(true);
      await api.post("/upload/", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFile(null);
      if (onUploaded) onUploaded();
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message;
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={handleUpload} className="card">
      <h3>Upload CSV</h3>
      <input
        type="file"
        accept=".csv,text/csv"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <div className="row">
        <button type="submit" disabled={busy}>
          {busy ? "Uploading..." : "Upload"}
        </button>
        {file && <span className="muted">{file.name}</span>}
      </div>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
