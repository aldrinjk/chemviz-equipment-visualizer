// src/pages/Dashboard.js
import React, { useEffect, useState, useCallback } from "react";
import api, { setAuthToken } from "../api";   // <-- import setAuthToken
import UploadForm from "../components/UploadForm";
import SummaryCards from "../components/SummaryCards";
import TypeBarChart from "../components/TypeBarChart";
import HistoryTable from "../components/HistoryTable";

export default function Dashboard({ authUser, onLogout }) {
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");

  // local state for the displayed username
  const [displayUser, setDisplayUser] = useState(authUser || "");

  // keep displayUser in sync with prop and localStorage
  useEffect(() => {
    if (authUser) {
      setDisplayUser(authUser);
      return;
    }

    // if no prop, fall back to localStorage
    const savedUser = localStorage.getItem("authUser");
    if (savedUser) {
      setDisplayUser(savedUser);
    }
  }, [authUser]);

  const load = useCallback(async () => {
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
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message;
      setError(msg);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleDownloadPdf = async () => {
    setError("");
    try {
      const res = await api.get("/report/latest/", {
        responseType: "blob",
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

  const handleLogoutClick = async () => {
    try {
      // tell backend to invalidate token (if still valid)
      await api.post("/auth/logout/");
    } catch (e) {
      // ignore API errors, we'll still clear local auth
    }

    // clear client-side auth completely
    localStorage.removeItem("authToken");
    localStorage.removeItem("authUser");
    setAuthToken(null);      // <-- removes Authorization header from axios
    setDisplayUser("—");

    // if App passed a logout handler, use that to switch back to LoginPage
    if (onLogout) {
      onLogout();
    } else {
      // fallback: hard refresh, App will see no token and show login
      window.location.href = "/";
    }
  };

  return (
    <div className="container">
      <header>
        <h2>Chemical Equipment Parameter Visualizer</h2>
        <div className="muted">
          API: {process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000/api"}
        </div>
      </header>

      {/* Top bar: logged-in state */}
      <div className="card">
        <div className="row" style={{ justifyContent: "space-between" }}>
          <div>
            Logged in as{" "}
            <b>
              {displayUser && displayUser.trim().length > 0
                ? displayUser
                : "—"}
            </b>
          </div>
          <button className="btn-ghost" onClick={handleLogoutClick}>
            Log out
          </button>
        </div>
      </div>

      {/* PDF button */}
      <div className="card">
        <div className="row" style={{ justifyContent: "space-between" }}>
          <div className="muted">
            Download a printable report of the latest dataset.
          </div>
          <button onClick={handleDownloadPdf}>
            Download Latest Report (PDF)
          </button>
        </div>
      </div>

      {/* Upload section */}
      <UploadForm onUploaded={load} />

      {error && <div className="error">{error}</div>}

      {/* Summary + chart */}
      {summary ? (
        <>
          <SummaryCards summary={summary} />

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

      {/* History table */}
      <HistoryTable items={history} />
    </div>
  );
}
