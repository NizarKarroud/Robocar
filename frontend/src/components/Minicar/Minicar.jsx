import "./MiniCar.css";

function sensorColor(val) {
  if (val === null || val === undefined) return "var(--t3)";
  if (val > 60)  return "var(--grn)";
  if (val > 20)  return "#ffa41cc0";
  return "var(--red)";
}

function fmt(val) {
  return val != null ? `${val}` : "—";
}

export default function MiniCar({ sensors = {} }) {
  const { left, right, front } = sensors ?? {};

  return (
    <div className="mini-car panel">
      <div className="panel-label">Sensors (cm)</div>
      <div className="sensor-grid">

        {/* Front — centered above car */}
        <span className="sensor sensor--front" style={{ color: sensorColor(front) }}>
          {fmt(front)}
        </span>

        {/* Left | Car SVG | Right */}
        <span className="sensor sensor--left" style={{ color: sensorColor(left) }}>
          {fmt(left)}
        </span>

        <div className="sensor-car-wrap">
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

        <span className="sensor sensor--right" style={{ color: sensorColor(right) }}>
          {fmt(right)}
        </span>

      </div>
    </div>
  );
}