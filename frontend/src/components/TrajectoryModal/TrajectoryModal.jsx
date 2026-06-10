import { useState, useEffect } from "react";
import { getSessions, getTrajectory } from "../../services/api";

export default function TrajectoryModal({ onClose }) {
  const [sessions, setSessions]     = useState([]);
  const [selected, setSelected]     = useState(null);
  const [trajectory, setTrajectory] = useState(null);
  const [loading, setLoading]       = useState(false);

  useEffect(() => {
    getSessions().then(setSessions).catch(console.error);
  }, []);

  async function handleSelect(id) {
    setSelected(id);
    setLoading(true);
    try {
      const traj = await getTrajectory(id);
      setTrajectory(traj);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  // compute SVG path from points
  function renderPath() {
    if (!trajectory?.points?.length) return null;
    const pts = trajectory.points;
    const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const W = 400, H = 300, PAD = 20;
    const rangeX = maxX - minX || 1, rangeY = maxY - minY || 1;
    const scale = Math.min((W - PAD*2) / rangeX, (H - PAD*2) / rangeY);
    const tx = p => PAD + (p.x - minX) * scale;
    const ty = p => H - PAD - (p.y - minY) * scale;
    const d = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${tx(p).toFixed(1)} ${ty(p).toFixed(1)}`).join(" ");
    return (
      <svg width={W} height={H} style={{ background: "#111", borderRadius: 8 }}>
        <path d={d} fill="none" stroke="#00e5ff" strokeWidth="2" />
        <circle cx={tx(pts[0])} cy={ty(pts[0])} r={5} fill="#00ff88" />
        <circle cx={tx(pts[pts.length-1])} cy={ty(pts[pts.length-1])} r={5} fill="#ff4444" />
      </svg>
    );
  }

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={e => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={{ margin: 0 }}>Trajectory Graph</h2>
          <button onClick={onClose} style={styles.closeBtn}>✕</button>
        </div>

        <div style={styles.body}>
          <div style={styles.sidebar}>
            <p style={styles.label}>Sessions</p>
            {sessions.length === 0 && <p style={{ color: "#888" }}>No sessions yet</p>}
            {sessions.map(s => (
              <button
                key={s.id}
                style={{ ...styles.sessionBtn, ...(selected === s.id ? styles.sessionBtnActive : {}) }}
                onClick={() => handleSelect(s.id)}
              >
                <strong>#{s.id}</strong> {s.mode}<br />
                <small>{s.started_at?.slice(0, 19).replace("T", " ")}</small>
              </button>
            ))}
          </div>

          <div style={styles.canvas}>
            {loading && <p style={{ color: "#888" }}>Loading…</p>}
            {!loading && trajectory && renderPath()}
            {!loading && trajectory && (
              <p style={{ color: "#888", marginTop: 8 }}>
                {trajectory.total_points} points · mode: {trajectory.mode}
              </p>
            )}
            {!loading && !trajectory && <p style={{ color: "#555" }}>Select a session</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  overlay:  { position:"fixed", inset:0, background:"rgba(0,0,0,.7)", zIndex:1000, display:"flex", alignItems:"center", justifyContent:"center" },
  modal:    { background:"#1a1a2e", borderRadius:12, width:700, maxHeight:"80vh", display:"flex", flexDirection:"column", overflow:"hidden", border:"1px solid #333" },
  header:   { display:"flex", justifyContent:"space-between", alignItems:"center", padding:"16px 20px", borderBottom:"1px solid #333" },
  closeBtn: { background:"none", border:"none", color:"#aaa", fontSize:20, cursor:"pointer" },
  body:     { display:"flex", flex:1, overflow:"hidden" },
  sidebar:  { width:200, borderRight:"1px solid #333", padding:12, overflowY:"auto", display:"flex", flexDirection:"column", gap:8 },
  label:    { color:"#888", fontSize:12, textTransform:"uppercase", margin:"0 0 8px" },
  sessionBtn: { background:"#111", border:"1px solid #333", color:"#ccc", borderRadius:6, padding:"8px 10px", cursor:"pointer", textAlign:"left" },
  sessionBtnActive: { borderColor:"#00e5ff", color:"#00e5ff" },
  canvas:   { flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", padding:20 },
};