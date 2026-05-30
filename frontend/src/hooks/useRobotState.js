import { useReducer } from "react";

const initialState = {
  speed: 0,
  direction: "IDLE",
  battery: null,
  signal: null,
  temperature: null,
  position: { x: 0, y: 0 },
  connected: false,
  tirePressure: { fl: null, fr: null, rl: null, rr: null },
  logs: [],
};

function reducer(state, action) {
  const now = new Date().toISOString().slice(11, 19);

  switch (action.type) {
    case "MOVE_FORWARD":
      return {
        ...state,
        direction: "FORWARD",
        speed: Math.min(state.speed + 10, 100),
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Move forward" }],
      };
    case "MOVE_BACK":
      return {
        ...state,
        direction: "REVERSE",
        speed: Math.min(state.speed + 10, 100),
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Reverse" }],
      };
    case "TURN_LEFT":
      return {
        ...state,
        direction: "LEFT",
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Turn left" }],
      };
    case "TURN_RIGHT":
      return {
        ...state,
        direction: "RIGHT",
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Turn right" }],
      };
    case "STOP":
      return {
        ...state,
        direction: "IDLE",
        speed: 0,
        logs: [...state.logs.slice(-19), { time: now, msg: "CMD: Emergency stop" }],
      };
    case "RESET":
      return {
        ...initialState,
        logs: [...state.logs.slice(-19), { time: now, msg: "System reset" }],
      };
    case "START":
      return {
        ...state,
        logs: [...state.logs.slice(-19), { time: now, msg: "Autonomous mode started" }],
      };
    case "SET_MODE_AUTO":
      return {
        ...state,
        logs: [...state.logs.slice(-19), { time: now, msg: "Switched to autonomous" }],
      };
    case "SET_MODE_MANUAL":
      return {
        ...state,
        logs: [...state.logs.slice(-19), { time: now, msg: "Switched to manual" }],
      };
    case "FOLLOW_LINE":
      return {
        ...state,
        logs: [...state.logs.slice(-19), { time: now, msg: "Follow line started" }],
      };
    case "SERIAL_DATA":
      return {
        ...state,
        logs: [...state.logs.slice(-19), { time: now, msg: `[SERIAL] ${action.payload}` }],
      };
    case "UPDATE_STATE":
      return {
        ...state,
        ...action.payload,
      };
    default:
      return state;
  }
}

export function useRobotState() {
  const [robotState, dispatch] = useReducer(reducer, initialState);
  return { robotState, dispatch };
}