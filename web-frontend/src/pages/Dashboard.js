// src/pages/Dashboard.js
import React, { useEffect, useState, useCallback } from "react";
import api, { setAuthToken } from "../api/index";
import UploadForm from "../components/UploadForm";
import SummaryCards from "../components/SummaryCards";
import TypeBarChart from "../components/TypeBarChart";
import HistoryTable from "../components/HistoryTable";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [authToken, setAuthTokenState] = useState(null);
  const [authUser, setAuthUser] = useState(null);
  const [authError, setAuthError] = useState("");

  const [rawRows, setRawRows] = useState([]);
  const [rawFilename, setRawFilename] = useState("");

  // Load raw rows of latest dataset
  const loadRawRows = useCallback(async () => {
    try {
      const res = await api.get("/dataset/latest/rows/");
      setRawRows(res.data.rows || []);
      setRawFilename(res.data.filename || "");
    } catch (err) {
      // if no dataset yet, just clear table
      if (err?.response?.status === 404) {
        setRawRows([]);
        setRawFilename("");
      } else {
        console.error(err);
      }
    }
  }, []);

  // Load summary + history (+ raw rows)
  const load = useCallback(
    async () => {
      setError("");
      try {
        const [s, h] = await Promise.all([
          api.get("/summary/latest/").catch((e) => {
            // if none uploaded yet
            if (e?.response?.status === 404) return { data: null };
            throw e;
          }),
          api.get("/history/"),
        ]);
        setSummary(s?.data || null);
        setHistory(h.data.items || []);
        await loadRawRows();
      } catch (err) {
        const msg = err?.response?.data?.detail || err.message;
        setError(msg);
      }
    },
    [loadRawRows]
  );

  // Initial load
  useEffect(() => {
    load();
  }, [load]);

  // Download PDF with auth header
  const handleDownloadPdf = async () => {
    setError("");
    try {
      const res = await api.get("/report/latest/", {
        responseType: "blob", // get raw PDF bytes
      });

      const blob = new Blob([res.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "latest_equipment_report.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message;
      setError(msg);
    }
  };

  // Load saved auth token on first render
  useEffect(() => {
    const saved = localStorage.getItem("authToken");
    const savedUser = localStorage.getItem("authUser");
    if (saved) {
      setAuthToken(saved);
      setAuthTokenState(saved);
      if (savedUser) setAuthUser(savedUser);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError("");
    try {
      const res = await api.post("/auth/login/", { username, password });
      const token = res.data.token;
      const user = res.data.username;
      setAuthToken(token);
      setAuthTokenState(token);
      setAuthUser(user);
      localStorage.setItem("authToken", token);
      localStorage.setItem("authUser", user);
      setUsername("");
      setPassword("");
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message;
      setAuthError(msg);
    }
  };

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout/");
    } catch (e) {
      // ignore errors, we will still clear locally
    }
    setAuthToken(null);
    setAuthTokenState(null);
    setAuthUser(null);
    localStorage.removeItem("authToken");
    localStorage.removeItem("authUser");
  };

  return (
    <div className="container">
      <header>
        <h2>Chemical Equipment Parameter Visualizer</h2>
        <div className="muted">
          API: {process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api"}
        </div>
      </header>

      {/* Auth card */}
      <div className="card" style={{ marginBottom: "12px" }}>
        {authToken ? (
          <div className="row" style={{ justifyContent: "space-between" }}>
            <div>
              Logged in as <b>{authUser}</b>
            </div>
            <button onClick={handleLogout}>Log out</button>
          </div>
        ) : (
          <>
            <h3>Login (required for upload & PDF)</h3>
            <form onSubmit={handleLogin} className="row">
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button type="submit">Login</button>
            </form>
            {authError && <div className="error">{authError}</div>}
          </>
        )}
      </div>

      {/* PDF download */}
      <div style={{ marginBottom: "12px" }}>
        <button onClick={handleDownloadPdf}>Download Latest Report (PDF)</button>
      </div>

      {/* Upload form */}
      <div className="card" style={{ marginBottom: "16px" }}>
  <div className="upload-header">
    <h3>Upload CSV</h3>
    <span className="muted">
      Supported: <code>.csv</code> &nbsp;•&nbsp; Last 5 uploads shown below
    </span>
  </div>
  <UploadForm onUploaded={load} />
</div>

      {error && <div className="error">{error}</div>}

      {/* Summary + chart */}
      {summary ? (
  <>
    <div className="card">
      <SummaryCards summary={summary} />
    </div>
    <div className="card chart-card">
      <h3>Type Distribution</h3>
      <TypeBarChart distribution={summary.type_distribution} />
    </div>
  </>
) : (
  <div className="card">
    No dataset yet. Upload a CSV to see insights.
  </div>
)}

      {/* Raw Data Table */}
      {rawRows.length > 0 && (
        <div className="card" style={{ marginTop: "24px" }}>
          <h3>
            Raw Data (First 50 Rows)
            {rawFilename ? ` – ${rawFilename}` : ""}
          </h3>
          <div style={{ overflowX: "auto" }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Equipment Name</th>
                  <th>Type</th>
                  <th>Flowrate</th>
                  <th>Pressure</th>
                  <th>Temperature</th>
                </tr>
              </thead>
              <tbody>
                {rawRows.map((row, index) => (
                  <tr key={index}>
                    <td>{row["Equipment Name"]}</td>
                    <td>{row["Type"]}</td>
                    <td>{row["Flowrate"]}</td>
                    <td>{row["Pressure"]}</td>
                    <td>{row["Temperature"]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* History table */}
      <HistoryTable items={history} />
    </div>
  );
}
