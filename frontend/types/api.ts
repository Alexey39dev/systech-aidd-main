// API Response Types based on backend schemas

export type Period = "day" | "week" | "month";

export interface MetricCard {
  label: string;
  value: string | number;
  change: string;
  trend: "up" | "down" | "neutral";
}

export interface TimelinePoint {
  timestamp: string;
  value: number;
}

export interface RecentDialog {
  user_id: number;
  username: string;
  messages_count: number;
  last_activity: string;
}

export interface TopUser {
  user_id: number;
  username: string;
  messages_count: number;
  dialogs_count: number;
}

export interface StatsResponse {
  period: Period;
  metrics: MetricCard[];
  timeline: TimelinePoint[];
  recent_dialogs: RecentDialog[];
  top_users: TopUser[];
}

export interface HealthResponse {
  status: string;
  collector_type: string;
  chat_enabled: boolean;
}

// Chat API Types
export type ChatMode = "normal" | "admin";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  mode?: ChatMode | null;
  sql_query?: string;
}

export interface ChatMessageRequest {
  message: string;
  mode: ChatMode;
  session_id?: string | null;
}

export interface ChatMessageResponse {
  message: string;
  mode: ChatMode;
  sql_query?: string | null;
  metadata?: Record<string, string | number> | null;
  timestamp: string;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  session_id: string;
  total_messages: number;
  last_activity: string | null;
}

export interface ChatSession {
  session_id: string;
  user_id: number;
  created_at: string;
  last_activity: string | null;
  message_count: number;
}
