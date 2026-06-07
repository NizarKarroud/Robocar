import {
  sendFollowLineCommand,
  sendAvoidTopdownCommand,
  sendBraitenbergCommand,
  sendFollowWallCommand,
} from "../../services/api";
import "./Toolbar.css";

export default function Toolbar({ mode, setMode, dispatch, connected }) {
  const isAvoidTopdown  = mode === "avoidTopdown";
  const isBraitenberg   = mode === "braitenberg";
  const isFollowing     = mode === "following";
  const isFollowingWall = mode === "followingWall";
  const isManual        = mode === "manual";
  const isAnyAuto       = isAvoidTopdown || isBraitenberg || isFollowing || isFollowingWall;

  const canGenerate = connected && !isAnyAuto;

  if (!connected) {
    return (
      <nav className="toolbar panel toolbar--locked">
        <button className="tbtn tbtn--primary tbtn--outline tbtn--disabled" disabled>⬆ Avoid Topdown</button>
        <button className="tbtn tbtn--violet tbtn--outline tbtn--disabled" disabled>⚡ Braitenberg</button>
        <div className="toolbar-sep" />
        <button className="tbtn tbtn--ghost tbtn--disabled" disabled>⟳ Follow Line</button>
        <button className="tbtn tbtn--ghost tbtn--disabled" disabled>◈ Follow Wall</button>
        <div className="toolbar-sep" />
        <button className="tbtn tbtn--ghost tbtn--disabled" disabled>↩ Replay</button>
        <div className="toolbar-spacer" />
        <button className="tbtn tbtn--ghost tbtn--disabled" disabled>↗ Generate Graph</button>
      </nav>
    );
  }

  async function handleAvoidTopdown() {
    if (isAvoidTopdown) {
      dispatch({ type: "STOP" }); setMode("idle");
      try { await sendAvoidTopdownCommand("stop"); } catch (e) { console.error(e); }
    } else {
      dispatch({ type: "START" }); setMode("avoidTopdown");
      try { await sendAvoidTopdownCommand("start"); } catch (e) { console.error(e); }
    }
  }

  async function handleBraitenberg() {
    if (isBraitenberg) {
      dispatch({ type: "STOP" }); setMode("idle");
      try { await sendBraitenbergCommand("stop"); } catch (e) { console.error(e); }
    } else {
      dispatch({ type: "START" }); setMode("braitenberg");
      try { await sendBraitenbergCommand("start"); } catch (e) { console.error(e); }
    }
  }

  async function handleFollowLine() {
    if (isFollowing) {
      dispatch({ type: "FOLLOW_LINE_STOP" }); setMode("idle");
      try { await sendFollowLineCommand("stop"); } catch (e) { console.error(e); }
    } else {
      dispatch({ type: "FOLLOW_LINE" }); setMode("following");
      try { await sendFollowLineCommand("start"); } catch (e) { console.error(e); }
    }
  }

  async function handleFollowWall() {
    if (isFollowingWall) {
      dispatch({ type: "FOLLOW_WALL_STOP" }); setMode("idle");
      try { await sendFollowWallCommand("stop"); } catch (e) { console.error(e); }
    } else {
      dispatch({ type: "FOLLOW_WALL" }); setMode("followingWall");
      try { await sendFollowWallCommand("start"); } catch (e) { console.error(e); }
    }
  }

  const busy = isManual;

  return (
    <nav className="toolbar panel">

      <button
        className={`tbtn tbtn--primary ${isAvoidTopdown ? "tbtn--active" : "tbtn--outline"} ${busy || (isAnyAuto && !isAvoidTopdown) ? "tbtn--disabled" : ""}`}
        disabled={busy || (isAnyAuto && !isAvoidTopdown)}
        onClick={handleAvoidTopdown}
      >
        {isAvoidTopdown ? "◼ Topdown" : "⬆ Avoid Topdown"}
      </button>

      <button
        className={`tbtn tbtn--violet ${isBraitenberg ? "tbtn--active" : "tbtn--outline"} ${busy || (isAnyAuto && !isBraitenberg) ? "tbtn--disabled" : ""}`}
        disabled={busy || (isAnyAuto && !isBraitenberg)}
        onClick={handleBraitenberg}
      >
        {isBraitenberg ? "◼ Braitenberg" : "⚡ Braitenberg"}
      </button>

      <div className="toolbar-sep" />

      <button
        className={`tbtn ${isFollowing ? "tbtn--secondary tbtn--active" : "tbtn--ghost"} ${busy || (isAnyAuto && !isFollowing) ? "tbtn--disabled" : ""}`}
        disabled={busy || (isAnyAuto && !isFollowing)}
        onClick={handleFollowLine}
      >
        {isFollowing ? "◼ Line" : "⟳ Follow Line"}
      </button>

      <button
        className={`tbtn ${isFollowingWall ? "tbtn--teal tbtn--active" : "tbtn--ghost"} ${busy || (isAnyAuto && !isFollowingWall) ? "tbtn--disabled" : ""}`}
        disabled={busy || (isAnyAuto && !isFollowingWall)}
        onClick={handleFollowWall}
      >
        {isFollowingWall ? "◼ Wall" : "◈ Follow Wall"}
      </button>

      <div className="toolbar-sep" />

      <button
        className={`tbtn tbtn--ghost ${isAnyAuto ? "tbtn--disabled" : ""}`}
        disabled={isAnyAuto}
        onClick={() => dispatch({ type: "REPLAY" })}
      >
        ↩ Replay
      </button>

      {/* push Generate Graph to the right */}
      <div className="toolbar-spacer" />

      <button
        className={`tbtn tbtn--ghost ${!canGenerate ? "tbtn--disabled" : ""}`}
        disabled={!canGenerate}
      >
        ↗ Generate Graph
      </button>

    </nav>
  );
}