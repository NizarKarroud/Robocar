import { useState } from "react";
import "./Header.css";

export default function Header({ darkMode, toggleTheme }) {
  const [showLogin, setShowLogin] = useState(false);

  return (
    <>
      <header className="header panel">
        <span className="logo-text">RoboCar</span>
        <div className="header-right">
          <button className="theme-btn" onClick={toggleTheme}>
            {darkMode ? "☀ LIGHT MODE" : "☾ DARK MODE"}
          </button>
          <button className="login-btn" onClick={() => setShowLogin(true)}>
            Login
          </button>
        </div>
      </header>

      {showLogin && (
        <div className="modal-overlay" onClick={() => setShowLogin(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <p className="modal-title">Connect to Car</p>
            <label className="modal-label">ID_CAR</label>
            <input className="modal-input" type="text" placeholder="Enter car ID" />
            <label className="modal-label">KEY</label>
            <input className="modal-input" type="password" placeholder="Enter key" />
            <div className="modal-actions">
              <button className="modal-submit">Connect</button>
              <button className="modal-cancel" onClick={() => setShowLogin(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}