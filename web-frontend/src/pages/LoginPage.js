// src/pages/LoginPage.js
import React, { useState } from "react";
import api, { setAuthToken } from "../api";
import "./LoginPage.css";

export default function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const res = await api.post("/auth/login/", { username, password });
      const token = res.data.token;
      const user = res.data.username;

      // set axios auth header
      setAuthToken(token);

      // persist auth
      localStorage.setItem("authToken", token);
      localStorage.setItem("authUser", user);

      // notify App.js so it can switch to Dashboard
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message;
      setError(msg);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1 className="login-title">Log in</h1>

        <p className="login-subtitle">
          Login is required to upload CSV files or view any datasets.
        </p>

        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="text"
            placeholder="Username"
            className="login-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            className="login-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <div className="login-error">{error}</div>}

          <button type="submit" className="login-button">
            Log in
          </button>
        </form>

        <div className="login-footer">or, sign up</div>
      </div>
    </div>
  );
}
