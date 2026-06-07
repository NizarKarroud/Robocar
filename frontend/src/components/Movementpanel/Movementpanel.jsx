import { useState, useRef } from "react";
import { sendMovementCommand } from "../../services/api";
import "./MovementPanel.css";

const MOVEMENTS = [
  { id: "move_forward",          icon: "↑", group: "cardinal" },
  { id: "move_backward",         icon: "↓", group: "cardinal" },
  { id: "strafe_right",          icon: "→", group: "cardinal" },
  { id: "strafe_left",           icon: "←", group: "cardinal" },
  { id: "rotate_cw",             icon: "↻", group: "rotate"   },
  { id: "rotate_ccw",            icon: "↺", group: "rotate"   },
  { id: "diagonal_front_right",  icon: "↗", group: "diag"     },
  { id: "diagonal_front_left",   icon: "↖", group: "diag"     },
  { id: "diagonal_rear_right",   icon: "↘", group: "diag"     },
  { id: "diagonal_rear_left",    icon: "↙", group: "diag"     },
  { id: "arc_right_gentle",      icon: "⤵", group: "arc"      },
  { id: "arc_left_gentle",       icon: "⤴", group: "arc"      },
];

const DURATIONS = [10, 20, 30, 45, 60, 90, 120];

export default function MovementPanel({ connected, mode }) {
  const isAnyAuto = ["avoidTopdown", "braitenberg", "following", "followingWall"].includes(mode);
  const locked = !connected || isAnyAuto;

  const [selected,  setSelected]  = useState(null);
  const [duration,  setDuration]  = useState(30);
  const [scheduled, setScheduled] = useState(null);
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);
  const timerRef = useRef(null);

  function reset() {
    setScheduled(null);
    setSelected(null);
  }

  function handleCancel() {
    clearTimeout(timerRef.current);
    reset();
  }

  function handleSelect(id) {
    setSelected(prev => prev === id ? null : id);
    setError(null);
  }

  async function handleGo() {
    if (!selected || locked) return;
    setLoading(true);
    setError(null);
    try {
      await sendMovementCommand(selected, duration);
      const mv = MOVEMENTS.find(m => m.id === selected);
      setScheduled({ movement: mv, duration });
      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(reset, duration * 1000);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`mv-panel panel ${locked ? "mv-panel--locked" : ""}`}>
      <div className="panel-label">Mouvement programmé</div>
      <div className="mv-body">

        <div className="mv-grid">
          {MOVEMENTS.map(mv => (
            <button
              key={mv.id}
              className={`mv-btn mv-btn--${mv.group} ${selected === mv.id ? "mv-btn--sel" : ""}`}
              disabled={locked}
              onClick={() => handleSelect(mv.id)}
              title={mv.id.replace(/_/g, " ")}
            >
              {mv.icon}
            </button>
          ))}
        </div>

        <div className="mv-dur-row">
          {DURATIONS.map(s => (
            <button
              key={s}
              className={`mv-dur-chip ${duration === s ? "mv-dur-chip--active" : ""}`}
              disabled={locked}
              onClick={() => setDuration(s)}
            >
              {s}s
            </button>
          ))}
        </div>

        {error && <div className="mv-error">{error}</div>}

        {scheduled ? (
          <div className="mv-scheduled">
            <span>{scheduled.movement.icon}</span>
            <span className="mv-sched-dur">{scheduled.duration}s</span>
            <span className="mv-sched-dot" />
            <button className="mv-cancel-btn" onClick={handleCancel}>✕</button>
          </div>
        ) : (
          <button
            className={`mv-go-btn ${!selected || locked ? "mv-go-btn--off" : ""}`}
            disabled={!selected || locked || loading}
            onClick={handleGo}
          >
            {loading
              ? "⏳"
              : selected
                ? `▶ ${MOVEMENTS.find(m => m.id === selected).icon} · ${duration}s`
                : "▶ —"}
          </button>
        )}

      </div>
    </div>
  );
}