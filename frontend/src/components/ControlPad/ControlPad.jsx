import { useState, useRef, useEffect } from "react";
import "./ControlPad.css";

const BASE_SIZE  = 110;
const KNOB_SIZE  = 36;
const MAX_RADIUS = (BASE_SIZE - KNOB_SIZE) / 2;
const DEAD_ZONE  = 8;

function getDirection(dx, dy) {
  if (Math.abs(dx) < DEAD_ZONE && Math.abs(dy) < DEAD_ZONE) return null;
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  if (angle > -45   && angle <= 45)   return "TURN_RIGHT";
  if (angle > 45    && angle <= 135)  return "MOVE_BACK";
  if (angle > 135   || angle <= -135) return "TURN_LEFT";
  return "MOVE_FORWARD";
}

function clampToRadius(dx, dy, radius) {
  const dist  = Math.sqrt(dx * dx + dy * dy);
  const scale = Math.min(dist, radius) / (dist || 1);
  return { kx: dx * scale, ky: dy * scale };
}

export default function ControlPad({ dispatch, mode, setMode, connected }) {
  const [knob, setKnob] = useState({ x: 0, y: 0 });
  const dragging = useRef(false);
  const baseRef  = useRef(null);

  const isAnyAuto = ["avoidTopdown", "braitenberg", "following", "followingWall"].includes(mode);
  // Joystick only active in manual mode AND when connected AND no auto algo running
  const enabled = connected && mode === "manual" && !isAnyAuto;

  function getCenterOffset(e) {
    const rect = baseRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width  / 2;
    const cy = rect.top  + rect.height / 2;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { dx: clientX - cx, dy: clientY - cy };
  }

  function onStart(e) {
    if (!enabled) return;
    dragging.current = true;
    const { dx, dy } = getCenterOffset(e);
    const { kx, ky } = clampToRadius(dx, dy, MAX_RADIUS);
    setKnob({ x: kx, y: ky });
  }

  useEffect(() => {
    function handleMove(e) {
      if (!dragging.current || !enabled) return;
      e.preventDefault();
      const { dx, dy } = getCenterOffset(e);
      const { kx, ky } = clampToRadius(dx, dy, MAX_RADIUS);
      setKnob({ x: kx, y: ky });
      const dir = getDirection(dx, dy);
      if (dir) dispatch({ type: dir });
    }
    function handleUp() {
      if (!dragging.current) return;
      dragging.current = false;
      setKnob({ x: 0, y: 0 });
      dispatch({ type: "STOP" });
    }
    window.addEventListener("mousemove", handleMove);
    window.addEventListener("mouseup",   handleUp);
    window.addEventListener("touchmove", handleMove, { passive: false });
    window.addEventListener("touchend",  handleUp);
    return () => {
      window.removeEventListener("mousemove", handleMove);
      window.removeEventListener("mouseup",   handleUp);
      window.removeEventListener("touchmove", handleMove);
      window.removeEventListener("touchend",  handleUp);
    };
  }, [enabled, dispatch]);

  return (
    <div className={`panel ${!connected || isAnyAuto ? "panel--locked" : ""}`}>
      <div className="panel-label">Directional Control</div>

      <div className="joystick-wrap">
        <div
          ref={baseRef}
          className={`joystick-base ${!enabled ? "joystick-base--off" : ""}`}
          onMouseDown={onStart}
          onTouchStart={onStart}
        >
          <div
            className="joystick-knob"
            style={{ transform: `translate(${knob.x}px, ${knob.y}px)` }}
          />
        </div>
      </div>

      <div className="drive-mode">
        <label className={`radio-opt ${!connected ? "radio-opt--disabled" : ""}`}>
          <input
            type="radio"
            name="drivemode"
            value="auto"
            checked={mode !== "manual"}
            disabled={!connected || isAnyAuto}
            onChange={() => { dispatch({ type: "SET_MODE_AUTO" }); setMode("idle"); }}
          />
          <span>Auto</span>
        </label>
        <label className={`radio-opt ${!connected ? "radio-opt--disabled" : ""}`}>
          <input
            type="radio"
            name="drivemode"
            value="manual"
            checked={mode === "manual"}
            disabled={!connected || isAnyAuto}
            onChange={() => { dispatch({ type: "SET_MODE_MANUAL" }); setMode("manual"); }}
          />
          <span>Manual</span>
        </label>
      </div>
    </div>
  );
}