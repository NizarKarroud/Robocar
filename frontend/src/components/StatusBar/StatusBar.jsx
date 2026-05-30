import "./StatusBar.css";

export default function StatusBar({ mode, connected }) {
  const isRunning  = mode === "running";
  const canGenerate = connected && !isRunning;

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