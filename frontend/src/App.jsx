import { useState } from "react";
import Header from "./components/Header/Header";
import Toolbar from "./components/Toolbar/Toolbar";
import DisplayScreen from "./components/DisplayScreen/DisplayScreen";
import ControlPad from "./components/ControlPad/ControlPad";
import StatusBar from "./components/StatusBar/StatusBar";
import { useRobotState } from "./hooks/useRobotState";

import "./index.css";

export default function App() {
  const { robotState, dispatch } = useRobotState();
  const [mode, setMode] = useState("idle"); 
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`app ${darkMode ? "dark" : "light"}`}>
      <Header darkMode={darkMode} toggleTheme={() => setDarkMode(d => !d)} />
      <Toolbar mode={mode} setMode={setMode} dispatch={dispatch} />
      <main className="main-grid">
        <DisplayScreen mode={mode} robotState={robotState} />
        <aside className="side-panel">
          <ControlPad dispatch={dispatch} mode={mode} setMode={setMode} />
          <StatusBar mode={mode} />
        </aside>
      </main>
    </div>
  );
}