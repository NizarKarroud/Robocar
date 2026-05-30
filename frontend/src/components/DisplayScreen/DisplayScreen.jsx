import { useState, useEffect } from "react";
import { requestCamera, CAMERA_STREAM_URL } from "../../services/api";
import "./DisplayScreen.css";

export default function DisplayScreen({ robotState }) {
  const [camState,  setCamState]  = useState("idle");
  const [streamUrl, setStreamUrl] = useState(null);
  const [errorMsg,  setErrorMsg]  = useState("");

  const speed    = robotState.speed;
  const barColor = speed > 70 ? "var(--red)" : speed > 40 ? "var(--amb)" : "var(--cyan)";

  async function connectCamera() {
    setCamState("requesting");
    setErrorMsg("");
    setStreamUrl(null);

    try {
      const data = await requestCamera("connection");

      if (data.status === "accepted") {
        // Use the proxied stream endpoint (backend relays the car's TLS stream)
        setStreamUrl(CAMERA_STREAM_URL);
        setCamState("live");
      } else {
        setCamState("error");
        setErrorMsg(data.message || "Request rejected");
      }
    } catch (err) {
      setCamState("error");
      setErrorMsg("Server unreachable");
    }
  }

  async function disconnectCamera() {
    try {
      await requestCamera("disconnection");
    } catch {
      // best-effort
    }
    setStreamUrl(null);
    setCamState("idle");
  }

  useEffect(() => {
    connectCamera();
    return () => {
      // Disconnect camera cleanly when component unmounts
      requestCamera("disconnection").catch(() => {});
    };
  }, []);

  return (
    <section className="display-screen panel">

      {/* Speed strip */}
      <div className="speed-strip">
        <span className="spd-num" style={{ color: barColor }}>{speed}</span>
        <span className="spd-unit">KM/H</span>
        <div className="spd-bar-wrap">
          <div className="spd-bar" style={{ width: `${speed}%`, background: barColor }} />
        </div>
      </div>

      {/* Camera feed */}
       <div className="cam-section">
        {/* Status dot — only visible when NOT live */}
        {camState !== "live" && (
          <div className="cam-header">
            <span className="cam-dot" />
            <span className="cam-status-text">
              {camState === "requesting" && "Connecting..."}
              {camState === "error"      && `Error: ${errorMsg}`}
              {camState === "idle"       && "Idle"}
            </span>
          </div>
        )}
 
        <div className="cam-body">
          {camState === "live" && streamUrl && (
            <img
              src={streamUrl}
              alt="Camera feed"
              className="cam-img"
              onError={() => { setCamState("error"); setErrorMsg("Stream lost"); }}
            />
          )}
          {camState === "requesting" && (
            <div className="cam-placeholder">
              <p>Waiting for car response...</p>
            </div>
          )}
          {(camState === "error" || camState === "idle") && (
            <div className="cam-placeholder">
              {camState === "error" && <p className="cam-err-msg">{errorMsg}</p>}
              {connected && (
                <button className="cam-retry-btn" onClick={connectCamera}>
                  {camState === "error" ? "↺ Retry" : "▶ Connect"}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}