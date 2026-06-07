import { useState } from "react";
import Header        from "./components/Header/Header";
import Toolbar       from "./components/Toolbar/Toolbar";
import DisplayScreen from "./components/DisplayScreen/DisplayScreen";
import ControlPad    from "./components/ControlPad/ControlPad";
import MiniCar       from "./components/MiniCar/MiniCar";
import MovementPanel from "./components/MovementPanel/MovementPanel";
import { useRobotState } from "./hooks/useRobotState";

import "./index.css";

export default function App() {
  const { robotState, dispatch } = useRobotState();
  const [mode,      setMode]      = useState("idle");
  const [darkMode,  setDarkMode]  = useState(true);
  const [connected, setConnected] = useState(false);

  function handleConnected() {
    setConnected(true);
    dispatch({ type: "UPDATE_STATE", payload: { connected: true } });
  }

  function handleLogout() {
    setConnected(false);
    setMode("idle");
    dispatch({ type: "UPDATE_STATE", payload: { connected: false } });
  }

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Header
        darkMode={darkMode}
        toggleTheme={() => setDarkMode(d => !d)}
        connected={connected}
        onConnected={handleConnected}
        onLogout={handleLogout}
      />
      <Toolbar
        mode={mode}
        setMode={setMode}
        dispatch={dispatch}
        connected={connected}
      />
      <main className="main-grid">
        <DisplayScreen
          mode={mode}
          robotState={robotState}
          connected={connected}
        />
        <aside className="side-panel">
          <ControlPad
            dispatch={dispatch}
            mode={mode}
            setMode={setMode}
            connected={connected}
          />
          <MovementPanel connected={connected} mode={mode} />
          <MiniCar tirePressure={robotState.tirePressure} />
        </aside>
      </main>
    </div>
  );
}