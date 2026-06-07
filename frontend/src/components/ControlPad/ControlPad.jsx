import { useState, useRef, useEffect, useCallback } from "react";
import "./ControlPad.css";
import { sendJoystickCommand } from "../../services/api";

const BASE_SIZE  = 110;
const KNOB_SIZE  = 36;
const MAX_RADIUS = (BASE_SIZE - KNOB_SIZE) / 2;
const DEAD_ZONE  = 8;
const MAX_PWM    = 350;
const SEND_INTERVAL_MS = 80;

export default function ControlPad({ mode, connected, dispatch, setMode, onDragChange }) {
  const [knob, setKnob] = useState({ x: 0, y: 0 });
  const dragging   = useRef(false);
  const baseRef    = useRef(null);
  const lastSend   = useRef(0);
  const frameRef   = useRef(null);
  const currentVel = useRef({ vx: 0, vy: 0, omega: 0 });

  const isAnyAuto = ["avoidTopdown","braitenberg","following","followingWall"].includes(mode);
  const enabled   = connected && mode === "manual" && !isAnyAuto;

  function toVelocity(dx, dy) {
    const vx =  (-dy / MAX_RADIUS) * MAX_PWM;
    const vy =  ( dx / MAX_RADIUS) * MAX_PWM;
    return { vx, vy, omega: 0 };
  }

  const sendVelocity = useCallback(async (vx, vy, omega) => {
    const now = Date.now();
    if (now - lastSend.current < SEND_INTERVAL_MS) return;
    lastSend.current = now;
    try {
      await sendJoystickCommand(Math.round(vx), Math.round(vy), Math.round(omega));
    } catch (e) {
      console.warn("Joystick send error:", e);
    }
  }, []);

  const sendStop = useCallback(async () => {
    lastSend.current = 0; // force send even if interval not elapsed
    try {
      await sendJoystickCommand(0, 0, 0);
    } catch (e) {
      console.warn("Joystick stop error:", e);
    }
  }, []);

  function getCenterOffset(e) {
    const rect = baseRef.current.getBoundingClientRect();
    const cx = rect.left + rect.width  / 2;
    const cy = rect.top  + rect.height / 2;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return { dx: clientX - cx, dy: clientY - cy };
  }

  function clamp(dx, dy) {
    const dist  = Math.sqrt(dx * dx + dy * dy);
    const scale = Math.min(dist, MAX_RADIUS) / (dist || 1);
    return { kx: dx * scale, ky: dy * scale };
  }

  function onStart(e) {
    if (!enabled) return;
    e.preventDefault();
    dragging.current = true;
    onDragChange?.(true);
    const { dx, dy } = getCenterOffset(e);
    const { kx, ky } = clamp(dx, dy);
    setKnob({ x: kx, y: ky });
    const vel = toVelocity(kx, ky);
    currentVel.current = vel;
    sendVelocity(vel.vx, vel.vy, vel.omega);
  }

  useEffect(() => {
    function handleMove(e) {
      if (!dragging.current || !enabled) return;
      e.preventDefault();
      const { dx, dy } = getCenterOffset(e);
      const { kx, ky } = clamp(dx, dy);
      setKnob({ x: kx, y: ky });
      if (Math.abs(kx) < DEAD_ZONE && Math.abs(ky) < DEAD_ZONE) {
        currentVel.current = { vx: 0, vy: 0, omega: 0 };
        sendStop(); // immediate stop when in deadzone
      } else {
        currentVel.current = toVelocity(kx, ky);
      }
    }

    function handleUp() {
      if (!dragging.current) return;
      dragging.current = false;
      onDragChange?.(false);
      setKnob({ x: 0, y: 0 });
      currentVel.current = { vx: 0, vy: 0, omega: 0 };
      sendStop(); // immediate stop on release
    }

    function sendLoop() {
      if (dragging.current) {
        const { vx, vy, omega } = currentVel.current;
        sendVelocity(vx, vy, omega);
      }
      frameRef.current = setTimeout(sendLoop, SEND_INTERVAL_MS);
    }
    frameRef.current = setTimeout(sendLoop, SEND_INTERVAL_MS);

    window.addEventListener("mousemove",  handleMove);
    window.addEventListener("mouseup",    handleUp);
    window.addEventListener("touchmove",  handleMove, { passive: false });
    window.addEventListener("touchend",   handleUp);

    return () => {
      clearTimeout(frameRef.current);
      window.removeEventListener("mousemove",  handleMove);
      window.removeEventListener("mouseup",    handleUp);
      window.removeEventListener("touchmove",  handleMove);
      window.removeEventListener("touchend",   handleUp);
    };
  }, [enabled, sendVelocity, sendStop]);

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