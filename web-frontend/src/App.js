// src/App.js
import React, { useState, useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import LoginPage from "./pages/LoginPage";
import api, { setAuthToken } from "./api";

export default function App() {
  const [authToken, setAuthTokenState] = useState(null);
  const [authUser, setAuthUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Run on first load
  useEffect(() => {
    const storedToken = localStorage.getItem("authToken");
    const storedUser = localStorage.getItem("authUser");

    if (storedToken) {
      setAuthToken(storedToken);
      setAuthTokenState(storedToken);
      setAuthUser(storedUser || "");
      api.defaults.headers.common["Authorization"] = `Token ${storedToken}`;
    } else {
      setAuthUser(null);
      setAuthTokenState(null);
    }
    setLoading(false);
  }, []);

  // Called when login succeeds
  const handleLoginSuccess = () => {
    const token = localStorage.getItem("authToken");
    const user = localStorage.getItem("authUser");

    if (token) {
      setAuthTokenState(token);
      setAuthUser(user);
      setAuthToken(token);
    }
  };

  // Called when dashboard logout button is pressed
  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("authUser");

    setAuthTokenState(null);
    setAuthUser(null);
    setAuthToken(null); // clears axios header
  };

  if (loading) return <div></div>;

  // If no token → show login page
  if (!authToken) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // If token exists → show dashboard
  return <Dashboard authUser={authUser} onLogout={handleLogout} />;
}
