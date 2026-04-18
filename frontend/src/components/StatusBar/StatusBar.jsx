import "./StatusBar.css";

export default function StatusBar({ mode }) {
  const isRunning = mode === "running";
  const isAuto = mode !== "manual";
  const canGenerate = !isRunning;

  return (
    <div className="panel">
      <div className="panel-label">Graphe de trajectoire</div>
      <div className="graph-body">
        <button
          className={`graph-btn ${!canGenerate ? "graph-btn--disabled" : ""}`}
          disabled={!canGenerate}
        >
          Generate graph
        </button>
      </div>
    </div>
  );
}