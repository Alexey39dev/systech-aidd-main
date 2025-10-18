// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Available periods for filtering
export const PERIODS = ["day", "week", "month"] as const;
export type Period = (typeof PERIODS)[number];

// Application routes
export const ROUTES = {
  HOME: "/",
  DASHBOARD: "/dashboard",
  CHAT: "/chat", // Future feature
} as const;

// API endpoints
export const API_ENDPOINTS = {
  STATS: "/api/stats",
  HEALTH: "/health",
  CHAT_MESSAGE: "/api/chat/message",
  CHAT_HISTORY: "/api/chat/history",
} as const;

// Default values
export const DEFAULT_PERIOD: Period = "day";
export const REFRESH_INTERVAL = 30000; // 30 seconds
