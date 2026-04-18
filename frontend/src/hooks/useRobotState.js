import { useReducer } from "react";

const initialState = {
  speed: 0,
  direction: "IDLE",
  battery: 87,
  signal: 94,
  temperature: 32,
  position: { x: 0, y: 0 },
  connected: true,
  tirePressure: { fl: 1, fr: 32, rl: 320, rr: 200 },
  logs: [
    { time: "00:00:01", msg: "System boot complete" },
    { time: "00:00:02", msg: "Motor drivers online" },
    { time: "00:00:03", msg: "Sensors calibrated" },
    { time: "00:00:04", msg: "Awaiting command..." },
  ],
};

function reducer(state, action) {
  const now = new Date().toISOString().slice(11, 19);
  switch (action.type) {
    case "MOVE_FORWARD":
      return { ...state, direction: "FORWARD", speed: Math.min(state.speed + 10, 100),
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Move forward" }] };
    case "MOVE_BACK":
      return { ...state, direction: "REVERSE", speed: Math.min(state.speed + 10, 100),
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Reverse" }] };
    case "TURN_LEFT":
      return { ...state, direction: "LEFT",
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Turn left" }] };
    case "TURN_RIGHT":
      return { ...state, direction: "RIGHT",
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Turn right" }] };
    case "STOP":
      return { ...state, direction: "IDLE", speed: 0,
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Emergency stop" }] };
    case "RESET":
      return { ...initialState, logs: [...state.logs.slice(-19), { time: now, msg: "System reset" }] };
    case "START":
      return { ...state, logs: [...state.logs.slice(-19), { time: now, msg: "Autonomous mode started" }] };
      // add to reducer switch cases:
case "SET_MODE_AUTO":
  return { ...state, logs: [...state.logs.slice(-19), { time: now, msg: "Switched to autonomous" }] };
case "SET_MODE_MANUAL":
  return { ...state, logs: [...state.logs.slice(-19), { time: now, msg: "Switched to manual" }] };

  case "REPLAY":
  return { ...state, logs: [...state.logs.slice(-19), { time: now, msg: "Replay started" }] };
  
    default:
      return state;
  }
}

export function useRobotState() {
  const [robotState, dispatch] = useReducer(reducer, initialState);
  return { robotState, dispatch };
}