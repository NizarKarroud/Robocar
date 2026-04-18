import "./DisplayScreen.css";

export default function DisplayScreen({ robotState }) {
  const speed = robotState.speed;
  const barColor = speed > 70 ? "var(--red)" : speed > 40 ? "var(--amb)" : "var(--cyan)";


  function tireColor(val) {
  if (val >= 301)  return "var(--grn)";
  if (val >= 101)  return "#aebf43"; 
  if (val >= 21)   return "#ffa41cc0";   
  return "var(--red)";
  }

  return (
    <section className="display-screen panel">
      <div className="speed-strip">
        <span className="spd-num" style={{ color: barColor }}>{speed}</span>
        <span className="spd-unit">KM/H</span>
        <div className="spd-bar-wrap">
          <div className="spd-bar" style={{ width: `${speed}%`, background: barColor }} />
        </div>
      </div>
      <div className="viz-area">
      <div className="tire-overlay">
<div className="tire tire--front" style={{ color: tireColor(robotState.tirePressure.fl) }}>
  {robotState.tirePressure.fl}
</div>
<div className="tire tire--left"  style={{ color: tireColor(robotState.tirePressure.fr) }}>
  {robotState.tirePressure.fr}
</div>
<div className="tire tire--right" style={{ color: tireColor(robotState.tirePressure.rl) }}>
  {robotState.tirePressure.rl}
</div>
<div className="tire tire--back"  style={{ color: tireColor(robotState.tirePressure.rr) }}>
  {robotState.tirePressure.rr}
</div>
  <svg className="car-svg" viewBox="0 0 60 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="10" width="44" height="80" rx="10" stroke="var(--t2)" strokeWidth="1.5"/>
    <rect x="14" y="22" width="32" height="30" rx="6" stroke="var(--t2)" strokeWidth="1.2"/>
    <line x1="14" y1="34" x2="46" y2="34" stroke="var(--t3)" strokeWidth="0.8"/>
    <rect x="2" y="14" width="8" height="16" rx="3" fill="var(--t3)"/>
    <rect x="50" y="14" width="8" height="16" rx="3" fill="var(--t3)"/>
    <rect x="2" y="70" width="8" height="16" rx="3" fill="var(--t3)"/>
    <rect x="50" y="70" width="8" height="16" rx="3" fill="var(--t3)"/>
    <rect x="14" y="11" width="10" height="4" rx="2" fill="var(--cyan)" opacity="0.7"/>
    <rect x="36" y="11" width="10" height="4" rx="2" fill="var(--cyan)" opacity="0.7"/>
    <rect x="14" y="85" width="10" height="4" rx="2" fill="var(--red)" opacity="0.7"/>
    <rect x="36" y="85" width="10" height="4" rx="2" fill="var(--red)" opacity="0.7"/>
  </svg>
</div>
        <div className="viz-inner">
          <div className="viz-icon">◈</div>
          <p className="viz-label">3D Visualization</p>
          <p className="viz-hint">React Three Fiber goes here</p>
        </div>
      </div>
    </section>
  );
}