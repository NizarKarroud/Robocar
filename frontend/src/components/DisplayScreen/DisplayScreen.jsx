import { useState, useEffect, useRef } from "react";
import { requestCamera, CAMERA_STREAM_URL } from "../../services/api";
import "./DisplayScreen.css";

export default function DisplayScreen({ robotState, connected }) {
  const [camState,   setCamState]   = useState("idle");
  const [streamUrl,  setStreamUrl]  = useState(null);
  const [errorMsg,   setErrorMsg]   = useState("");
  const [imgVisible, setImgVisible] = useState(false);
  const imgRef = useRef(null);

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
    } catch {
      setCamState("error");
      setErrorMsg("Server unreachable");
    }
  }

  useEffect(() => {
    if (!connected) {
      setImgVisible(false);
      setStreamUrl(null);
      setCamState("idle");
      requestCamera("disconnection").catch(() => {});
      return;
    }
    connectCamera();
    return () => { requestCamera("disconnection").catch(() => {}); };
  }, [connected]);

  return (
    <section className="display-screen panel">
      <div className="cam-section">

        {/* Minimal status bar — no disconnect button */}
        <div className="cam-header">
          <span className={`cam-dot ${camState === "live" ? "live" : ""}`} />
          <span className="cam-status-text">
            {camState === "live"       && "LIVE"}
            {camState === "requesting" && "Connecting..."}
            {camState === "error"      && `Error: ${errorMsg}`}
            {camState === "idle"       && "Camera idle"}
          </span>
        </div>

        <div className="cam-body">
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
            <div className="cam-placeholder"><p>Waiting for car response...</p></div>
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