import { useState, useEffect, useRef } from "react";
import { requestCamera, CAMERA_STREAM_URL } from "../../services/api";
import "./DisplayScreen.css";

export default function DisplayScreen({ robotState, connected }) {
  const [camState,  setCamState]  = useState("idle");
  const [streamUrl, setStreamUrl] = useState(null);
  const [errorMsg,  setErrorMsg]  = useState("");
  // imgVisible is separate from camState — we hide the image INSTANTLY on disconnect
  // while camState transitions, to prevent last-frame freeze showing
  const [imgVisible, setImgVisible] = useState(false);
  const imgRef = useRef(null);

  const speed    = robotState.speed;
  const barColor = speed > 70 ? "var(--red)" : speed > 40 ? "var(--amb)" : "var(--cyan)";

  async function connectCamera() {
    setCamState("requesting");
    setErrorMsg("");
    setStreamUrl(null);
    setImgVisible(false);

    try {
      const data = await requestCamera("connection");

      if (data.status === "accepted") {
        setStreamUrl(CAMERA_STREAM_URL);
        setCamState("live");
        setImgVisible(true);
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
    // Immediately wipe the image src so the last frame disappears right away,
    // before the async disconnection request even resolves
    setImgVisible(false);
    setStreamUrl(null);
    setCamState("idle");

    try {
      await requestCamera("disconnection");
    } catch {
      // best-effort
    }
  }

  // Auto-connect when user logs in; disconnect when they log out
  useEffect(() => {
    if (!connected) {
      // User logged out — wipe feed immediately
      setImgVisible(false);
      setStreamUrl(null);
      setCamState("idle");
      requestCamera("disconnection").catch(() => {});
      return;
    }
    connectCamera();
    return () => {
      requestCamera("disconnection").catch(() => {});
    };
  }, [connected]);

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

        {/* Header bar — always visible, shows status + disconnect button when live */}
        <div className="cam-header">
          <span className={`cam-dot ${camState === "live" ? "live" : ""}`} />
          <span className="cam-status-text">
            {camState === "live"       && "LIVE"}
            {camState === "requesting" && "Connecting..."}
            {camState === "error"      && `Error: ${errorMsg}`}
            {camState === "idle"       && "Camera idle"}
          </span>
          {camState === "live" && (
            <button className="cam-disconnect-btn" onClick={disconnectCamera}>
              ✕ Disconnect
            </button>
          )}
        </div>

        <div className="cam-body">
          {/* The img tag stays in the DOM only while imgVisible — prevents last-frame flash */}
          {imgVisible && streamUrl && (
            <img
              ref={imgRef}
              src={streamUrl}
              alt="Camera feed"
              className="cam-img"
              onError={() => {
                setImgVisible(false);
                setCamState("error");
                setErrorMsg("Stream lost");
              }}
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