import "./MiniCar.css";

function tireColor(val) {
  if (val === null || val === undefined) return "var(--t3)";
  if (val >= 301) return "var(--grn)";
  if (val >= 101) return "#aebf43";
  if (val >= 21)  return "#ffa41cc0";
  return "var(--red)";
}

/**
 * MiniCar — top-view SVG car with per-corner distance/pressure readings.
 * Props:
 *   tirePressure: { fl: number|null, fr: number|null, rl: number|null, rr: number|null }
 */
export default function MiniCar({ tirePressure = {} }) {
  const tp = tirePressure;

  return (
    <div className="mini-car panel">
      <div className="panel-label">Tire Distance</div>
      <div className="tire-grid">
        <span className="tire tire--fl" style={{ color: tireColor(tp.fl) }}>
          {tp.fl ?? "—"}
        </span>

        <div className="tire-car-wrap">
          <svg
            className="car-svg"
            viewBox="0 0 60 100"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            {/* Body */}
            <rect x="8"  y="10" width="44" height="80" rx="10"
                  stroke="var(--t2)" strokeWidth="1.5" />
            {/* Windshield */}
            <rect x="14" y="22" width="32" height="30" rx="6"
                  stroke="var(--t2)" strokeWidth="1.2" />
            {/* Divider line */}
            <line x1="14" y1="34" x2="46" y2="34"
                  stroke="var(--t3)" strokeWidth="0.8" />
            {/* Wheels */}
            <rect x="2"  y="14" width="8"  height="16" rx="3" fill="var(--t3)" />
            <rect x="50" y="14" width="8"  height="16" rx="3" fill="var(--t3)" />
            <rect x="2"  y="70" width="8"  height="16" rx="3" fill="var(--t3)" />
            <rect x="50" y="70" width="8"  height="16" rx="3" fill="var(--t3)" />
            {/* Front lights (cyan) */}
            <rect x="14" y="11" width="10" height="4" rx="2"
                  fill="var(--cyan)" opacity="0.7" />
            <rect x="36" y="11" width="10" height="4" rx="2"
                  fill="var(--cyan)" opacity="0.7" />
            {/* Rear lights (red) */}
            <rect x="14" y="85" width="10" height="4" rx="2"
                  fill="var(--red)" opacity="0.7" />
            <rect x="36" y="85" width="10" height="4" rx="2"
                  fill="var(--red)" opacity="0.7" />
          </svg>
        </div>

        <span className="tire tire--fr" style={{ color: tireColor(tp.fr) }}>
          {tp.fr ?? "—"}
        </span>
        <span className="tire tire--rl" style={{ color: tireColor(tp.rl) }}>
          {tp.rl ?? "—"}
        </span>
        <span className="tire tire--rr" style={{ color: tireColor(tp.rr) }}>
          {tp.rr ?? "—"}
        </span>
      </div>
    </div>
  );
}