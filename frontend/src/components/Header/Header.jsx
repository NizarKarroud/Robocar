import { useState } from "react";
import { requestConnection } from "../../services/api";
import "./Header.css";

export default function Header({ darkMode, toggleTheme, connected, onConnected, onLogout }) {
  const [showLogin, setShowLogin] = useState(false);
  const [carId,     setCarId]     = useState("");
  const [carKey,    setCarKey]    = useState("");
  const [status,    setStatus]    = useState("idle"); // idle | loading | error
  const [errorMsg,  setErrorMsg]  = useState("");

  async function handleConnect() {
    if (!carId.trim() || !carKey.trim()) {
      setStatus("error");
      setErrorMsg("Car ID and Key are required");
      return;
    }
    setStatus("loading");
    setErrorMsg("");
    try {
      const data = await requestConnection(carId.trim(), carKey.trim());
      if (data.status === "connected") {
        setStatus("idle");
        setShowLogin(false);
        setCarId("");
        setCarKey("");
        onConnected({ carId: carId.trim() });
      } else if (data.status === "timeout") {
        setStatus("error");
        setErrorMsg("Car did not respond — check it's online");
      } else {
        setStatus("error");
        setErrorMsg("Rejected — wrong ID or Key");
      }
    } catch {
      setStatus("error");
      setErrorMsg("Server unreachable (is the backend running?)");
    }
  }

  function handleClose() {
    setShowLogin(false);
    setStatus("idle");
    setErrorMsg("");
  }

  return (
    <>
      <header className="header panel">
        <span className="logo-text">RoboCar</span>
        <div className="header-right">
          <button className="theme-btn" onClick={toggleTheme}>
            {darkMode ? "☀ LIGHT MODE" : "☾ DARK MODE"}
          </button>

          {connected ? (
            <button className="logout-btn" onClick={onLogout}>
              ⏻ Logout
            </button>
          ) : (
            <button className="login-btn" onClick={() => setShowLogin(true)}>
              Connect
            </button>
          )}
        </div>
      </header>

      {showLogin && (
        <div className="modal-overlay" onClick={handleClose}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <p className="modal-title">Connect to Car</p>

            <label className="modal-label">ID_CAR</label>
            <input
              className="modal-input"
              type="text"
              placeholder="e.g. txt-001"
              value={carId}
              onChange={e => setCarId(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleConnect()}
              disabled={status === "loading"}
              autoFocus
            />

            <label className="modal-label">KEY</label>
            <input
              className="modal-input"
              type="password"
              placeholder="Enter key"
              value={carKey}
              onChange={e => setCarKey(e.target.value)}
              onKeyDown={e => e.key === "Enter" && handleConnect()}
              disabled={status === "loading"}
            />

            {status === "error" && (
              <p className="modal-error">{errorMsg}</p>
            )}

            <div className="modal-actions">
              <button
                className={`modal-submit ${status === "loading" ? "modal-submit--loading" : ""}`}
                onClick={handleConnect}
                disabled={status === "loading"}
              >
                {status === "loading" ? "Connecting..." : "Connect"}
              </button>
              <button className="modal-cancel" onClick={handleClose}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}