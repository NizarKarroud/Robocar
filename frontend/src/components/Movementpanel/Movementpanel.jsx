import { useState } from "react";
import "./MovementPanel.css";

const MOVEMENTS = [
  { id: "forward",      icon: "↑", group: "cardinal" },
  { id: "backward",     icon: "↓", group: "cardinal" },
  { id: "strafe_right", icon: "→", group: "cardinal" },
  { id: "strafe_left",  icon: "←", group: "cardinal" },
  { id: "rotate_cw",   icon: "↻", group: "rotate"   },
  { id: "rotate_ccw",  icon: "↺", group: "rotate"   },
  { id: "diag_fr",     icon: "↗", group: "diag"     },
  { id: "diag_fl",     icon: "↖", group: "diag"     },
  { id: "diag_br",     icon: "↘", group: "diag"     },
  { id: "diag_bl",     icon: "↙", group: "diag"     },
  { id: "arc_right",   icon: "⤵", group: "arc"      },
  { id: "arc_left",    icon: "⤴", group: "arc"      },
];

const DURATIONS = [10, 20, 30, 45, 60, 90, 120];

export default function MovementPanel({ connected, mode }) {
  const isAnyAuto = ["avoidTopdown", "braitenberg", "following", "followingWall"].includes(mode);
  const locked = !connected || isAnyAuto;
  const [selected,  setSelected]  = useState(null);
  const [duration,  setDuration]  = useState(30);
  const [scheduled, setScheduled] = useState(null);

  function handleSelect(id) {
    setSelected(prev => prev === id ? null : id);
  }

  function handleGo() {
    if (!selected) return;
    const mv = MOVEMENTS.find(m => m.id === selected);
    setScheduled({ movement: mv, duration });
    console.log("[MovementPanel]", selected, duration + "s");
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

        {scheduled ? (
          <div className="mv-scheduled">
            <span>{scheduled.movement.icon}</span>
            <span className="mv-sched-dur">{scheduled.duration}s</span>
            <span className="mv-sched-dot" />
            <button className="mv-cancel-btn" onClick={() => setScheduled(null)}>✕</button>
          </div>
        ) : (
          <button
            className={`mv-go-btn ${!selected || !connected ? "mv-go-btn--off" : ""}`}
            disabled={!selected || locked}
            onClick={handleGo}
          >
            {selected ? `▶ ${MOVEMENTS.find(m => m.id === selected).icon} · ${duration}s` : "▶ —"}
          </button>
        )}

      </div>
    </div>
  );
}