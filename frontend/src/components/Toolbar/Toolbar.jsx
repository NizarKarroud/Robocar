import { sendFollowLineCommand } from "../../services/api";
import "./Toolbar.css";

export default function Toolbar({ mode, setMode, dispatch, connected }) {
  const isRunning    = mode === "running";
  const isFollowing  = mode === "following";
  const isManual     = mode === "manual";

  // Nothing works before login
  if (!connected) {
    return (
      <nav className="toolbar panel toolbar--locked">
        <button className="tbtn tbtn--primary tbtn--disabled" disabled>▶ Start</button>
        <button className="tbtn tbtn--danger  tbtn--disabled" disabled>■ Stop</button>
        <button className="tbtn tbtn--ghost   tbtn--disabled" disabled>↩ Replay</button>
        <button className="tbtn tbtn--ghost   tbtn--disabled" disabled>⟳ Follow Line</button>
      </nav>
    );
  }

  // ── Start / Stop: single toggle button ───────────────────────────────────
  function handleStartStop() {
    if (isRunning) {
      dispatch({ type: "STOP" });
      setMode("idle");
    } else {
      dispatch({ type: "START" });
      setMode("running");
    }
  }

  // ── Follow Line: same button toggles start/stop, sends matching backend cmd ─
  async function handleFollowLine() {
    if (isFollowing) {
      dispatch({ type: "FOLLOW_LINE_STOP" });
      setMode("idle");
      try { await sendFollowLineCommand("stop"); } catch (e) { console.error(e); }
    } else {
      dispatch({ type: "FOLLOW_LINE" });
      setMode("following");
      try { await sendFollowLineCommand("start"); } catch (e) { console.error(e); }
    }
  }

  return (
    <nav className="toolbar panel">

      {/* Start / Stop — one button, two states */}
      <button
        className={`tbtn ${isRunning ? "tbtn--danger tbtn--active" : "tbtn--primary"} ${isManual || isFollowing ? "tbtn--disabled" : ""}`}
        disabled={isManual || isFollowing}
        onClick={handleStartStop}
      >
        {isRunning ? "■ Stop" : "▶ Start"}
      </button>

      {/* Replay */}
      <button
        className={`tbtn tbtn--ghost ${isRunning || isFollowing ? "tbtn--disabled" : ""}`}
        disabled={isRunning || isFollowing}
        onClick={() => dispatch({ type: "REPLAY" })}
      >
        ↩ Replay
      </button>

      {/* Follow Line toggle */}
      <button
        className={`tbtn ${isFollowing ? "tbtn--secondary tbtn--active" : "tbtn--ghost"} ${isRunning || isManual ? "tbtn--disabled" : ""}`}
        disabled={isRunning || isManual}
        onClick={handleFollowLine}
      >
        {isFollowing ? "◼ Stop Line" : "⟳ Follow Line"}
      </button>

    </nav>
  );
}