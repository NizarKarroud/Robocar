import "./Toolbar.css";

export default function Toolbar({ mode, setMode, dispatch, connected }) {
  const isAuto    = mode !== "manual";
  const isRunning = mode === "running";

  // Nothing works before login
  if (!connected) {
    return (
      <nav className="toolbar panel toolbar--locked">
        <button className="tbtn tbtn--primary tbtn--disabled"  disabled>▶ Start</button>
        <button className="tbtn tbtn--danger  tbtn--disabled"  disabled>■ Stop</button>
        <button className="tbtn tbtn--ghost   tbtn--disabled"  disabled>↩ Replay</button>
        <button className="tbtn tbtn--ghost   tbtn--disabled"  disabled>⟳ Follow Line</button>
      </nav>
    );
  }

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

      <button
        className="tbtn tbtn--ghost"
        onClick={() => dispatch({ type: "REPLAY" })}
      >
        ↩ Replay
      </button>

      <button
        className={`tbtn tbtn--ghost ${isRunning ? "tbtn--disabled" : ""}`}
        disabled={isRunning}
        onClick={() => dispatch({ type: "FOLLOW_LINE" })}
      >
        ⟳ Follow Line
      </button>
    </nav>
  );
}