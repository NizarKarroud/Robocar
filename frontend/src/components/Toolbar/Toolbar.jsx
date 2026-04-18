import "./Toolbar.css";

export default function Toolbar({ mode, setMode, dispatch }) {
  const isAuto = mode !== "manual";
  const isRunning = mode === "running";

  return (
    <nav className="toolbar panel">
      <button
        className={`tbtn tbtn--primary ${!isAuto || isRunning ? "tbtn--disabled" : ""}`}
        disabled={!isAuto || isRunning}
        onClick={() => { dispatch({ type: "START" }); setMode("running"); }}
      >
        ▶ Start
      </button>
      <button
        className={`tbtn tbtn--danger ${!isAuto || !isRunning ? "tbtn--disabled" : ""}`}
        disabled={!isAuto || !isRunning}
        onClick={() => { dispatch({ type: "STOP" }); setMode("idle"); }}
      >
        ■ Stop
      </button>
      <button className="tbtn tbtn--ghost" onClick={() => dispatch({ type: "REPLAY" })}>
        ↩ Replay
      </button>
    </nav>
  );
}