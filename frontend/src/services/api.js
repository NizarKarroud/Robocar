// ─── Base URL ────────────────────────────────────────────────────────────────
// FastAPI backend runs on port 8000 (see app/main.py + CORSMiddleware)
const BASE = "http://localhost:8000/api/v1";

// ─── Car / Connection ─────────────────────────────────────────────────────────

/**
 * POST /api/v1/car/control/request
 * Initiate MQTT connection to the car.
 * @param {string} carId
 * @param {string} carKey
 * @returns {{ status: "connected" | "rejected" | "timeout" }}
 */
export async function requestConnection(carId, carKey) {
  const res = await fetch(`${BASE}/car/control/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      car_id: carId,
      car_key: carKey,
      timestamp: new Date().toISOString(),
    }),
  });
  if (!res.ok) throw new Error(`Connection request failed: ${res.status}`);
  return res.json(); // { status: "connected" | "rejected" | "timeout" }
}

/**
 * POST /api/v1/car/control/command/follow/line
 * Send a follow-line command to the car.
 * @param {"start" | "stop"} action
 * @returns {void}
 */
export async function sendFollowLineCommand(action) {
  const res = await fetch(`${BASE}/car/control/command/follow/line`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) throw new Error(`Follow-line command failed: ${res.status}`);
  return res.json();
}

// ─── Camera ───────────────────────────────────────────────────────────────────

/**
 * POST /api/v1/camera/request
 * Ask the car to turn on/off the camera stream.
 * @param {"connection" | "disconnection"} requestType
 * @returns {{ status: "accepted"|"rejected"|"disconnected"|"timeout", message: string, url?: string }}
 */
export async function requestCamera(requestType = "connection") {
  const res = await fetch(`${BASE}/camera/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request: requestType }),
  });
  if (!res.ok) throw new Error(`Camera request failed: ${res.status}`);
  return res.json();
  // Returns: { status, message, url? }
  // url is only present when status === "accepted"
  // The url may point to a different host/port than localhost:8000
  // (the car streams directly; the backend proxies via GET /camera/stream)
}

/**
 * GET /api/v1/camera/stream
 * Proxied MJPEG stream URL. Assign directly to <img src>.
 * The backend relays the car's TLS-protected camera over plain HTTP.
 */
export const CAMERA_STREAM_URL = `${BASE}/camera/stream`;

// ─── Client status ────────────────────────────────────────────────────────────

/**
 * GET /api/v1/client/status
 * (Stub endpoint – currently empty on the backend)
 */
export async function getClientStatus() {
  const res = await fetch(`${BASE}/client/status`);
  if (!res.ok) throw new Error(`Status fetch failed: ${res.status}`);
  return res.json();
}
/**
 * POST /api/v1/car/control/command/avoid/topdown
 * Trigger run_avoid_topdown on the car.
 * @param {"start" | "stop"} action
 */
export async function sendAvoidTopdownCommand(action) {
  const res = await fetch(`${BASE}/car/control/command/avoid/topdown`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) throw new Error(`Avoid-topdown command failed: ${res.status}`);
  return res.json();
}

/**
 * POST /api/v1/car/control/command/braitenberg
 * Trigger run_braitenberg on the car.
 * @param {"start" | "stop"} action
 */
export async function sendBraitenbergCommand(action) {
  const res = await fetch(`${BASE}/car/control/command/braitenberg`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) throw new Error(`Braitenberg command failed: ${res.status}`);
  return res.json();
}

/**
 * POST /api/v1/car/control/command/follow/wall
 * Trigger wall-following on the car.
 * @param {"start" | "stop"} action
 */
export async function sendFollowWallCommand(action) {
  const res = await fetch(`${BASE}/car/control/command/follow/wall`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) throw new Error(`Follow-wall command failed: ${res.status}`);
  return res.json();
}

/**
 * POST /api/v1/car/control/command/movement
 * Schedule a timed movement on the car.
 * @param {string} movement  — movement id (e.g. "forward", "rotate_cw")
 * @param {number} duration  — duration in seconds
 */
export async function sendMovementCommand(movement, duration) {
  const res = await fetch(`${BASE}/car/control/command/movement`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command: movement }),  // ← was "movement", duration dropped
  });
  if (!res.ok) throw new Error(`Movement command failed: ${res.status}`);
  return res.json();
}