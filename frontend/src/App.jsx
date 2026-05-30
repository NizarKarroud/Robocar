import { useState } from "react";
import Header      from "./components/Header/Header";
import Toolbar     from "./components/Toolbar/Toolbar";
import DisplayScreen from "./components/DisplayScreen/DisplayScreen";
import ControlPad  from "./components/ControlPad/ControlPad";
import StatusBar   from "./components/StatusBar/StatusBar";
import MiniCar     from "./components/MiniCar/MiniCar";
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
    // Reset app state — logout action is intentionally a no-op for now
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
          <StatusBar mode={mode} connected={connected} />
          <MiniCar tirePressure={robotState.tirePressure} />
        </aside>
      </main>
    </div>
  );
}