import { useState, useRef, useEffect } from "react";
import "./ControlPad.css";

const SIZE = 110;   
const KNOB = 36;    
const MAX  = (SIZE - KNOB) / 2;  

function getDirection(dx, dy) {
  if (Math.abs(dx) < 8 && Math.abs(dy) < 8) return null;
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  if (angle > -45  && angle <= 45)  return "TURN_RIGHT";
  if (angle > 45   && angle <= 135) return "MOVE_BACK";
  if (angle > 135  || angle <= -135) return "TURN_LEFT";
  return "MOVE_FORWARD";
}

export default function ControlPad({ dispatch, mode, setMode }) {
  const [knob, setKnob] = useState({ x: 0, y: 0 });
  const dragging = useRef(false);
  const baseRef = useRef(null);
  const enabled = mode === "manual";

  function getOffset(e) {
  const rect = baseRef.current.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  const dx = clientX - cx;
  const dy = clientY - cy;
  const dist = Math.sqrt(dx * dx + dy * dy);
  const scale = Math.min(dist, MAX) / (dist || 1);
  return { dx, dy, kx: dx * scale, ky: dy * scale };
}

function onStart(e) {
  if (!enabled) return;
  dragging.current = true;
  const { kx, ky } = getOffset(e);
  setKnob({ x: kx, y: ky });
}


useEffect(() => {
  function handleMove(e) {
    if (!dragging.current || !enabled) return;
    e.preventDefault();
    const rect = baseRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const scale = Math.min(dist, MAX) / (dist || 1);
    setKnob({ x: dx * scale, y: dy * scale });
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
  window.addEventListener("mouseup", handleUp);
  return () => {
    window.removeEventListener("mousemove", handleMove);
    window.removeEventListener("mouseup", handleUp);
  };
}, [enabled, dispatch]);

  return (
    <div className="panel">
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

      {/* Auto / Manual radio */}
      <div className="drive-mode">
        <label className="radio-opt">
          <input
            type="radio"
            name="drivemode"
            value="auto"
            checked={mode !== "manual"}
            onChange={() => { dispatch({ type: "SET_MODE_AUTO" }); setMode("idle"); }}
          />
          <span>Auto</span>
        </label>
        <label className="radio-opt">
          <input
            type="radio"
            name="drivemode"
            value="manual"
            checked={mode === "manual"}
          onChange={() => { dispatch({ type: "SET_MODE_MANUAL" }); setMode("manual"); }}
          />
          <span>Manual</span>
        </label>
      </div>
    </div>
  );
}