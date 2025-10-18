import { API_BASE_URL } from "./constants";
import type { 
  ChatMessageRequest, 
  ChatMessageResponse, 
  ChatHistoryResponse,
  ChatMode 
} from "@/types/api";

// Локальный интерфейс для ошибки API
interface ApiErrorResponse {
  detail: string;
}

class ChatApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: ApiErrorResponse
  ) {
    super(message);
    this.name = "ChatApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ApiErrorResponse | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Ignore JSON parse errors
    }

    throw new ChatApiError(
      errorData?.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData || undefined
    );
  }

  return response.json();
}

export async function sendMessage(
  message: string, 
  mode: ChatMode, 
  sessionId?: string
): Promise<ChatMessageResponse> {
  try {
    const url = new URL("/api/chat/message", API_BASE_URL);
    
    const requestBody: ChatMessageRequest = {
      message,
      mode,
      session_id: sessionId || null,
    };

    const response = await fetch(url.toString(), {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
        ...(sessionId && { "X-Session-ID": sessionId }),
      },
      body: JSON.stringify(requestBody),
    });

    return handleResponse<ChatMessageResponse>(response);
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    throw new ChatApiError(
      `Failed to send message: ${error instanceof Error ? error.message : "Unknown error"}`,
      0
    );
  }
}

export async function fetchChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
  try {
    const url = new URL("/api/chat/history", API_BASE_URL);
    url.searchParams.set("session_id", sessionId);

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        "Accept": "application/json",
        "X-Session-ID": sessionId,
      },
    });

    return handleResponse<ChatHistoryResponse>(response);
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    throw new ChatApiError(
      `Failed to fetch chat history: ${error instanceof Error ? error.message : "Unknown error"}`,
      0
    );
  }
}

export async function clearChatHistory(sessionId: string): Promise<void> {
  try {
    const url = new URL("/api/chat/history", API_BASE_URL);
    url.searchParams.set("session_id", sessionId);

    const response = await fetch(url.toString(), {
      method: "DELETE",
      headers: {
        "Accept": "application/json",
        "X-Session-ID": sessionId,
      },
    });

    await handleResponse<{ message: string; session_id: string }>(response);
  } catch (error) {
    if (error instanceof ChatApiError) {
      throw error;
    }

    throw new ChatApiError(
      `Failed to clear chat history: ${error instanceof Error ? error.message : "Unknown error"}`,
      0
    );
  }
}

// Utility function to check if chat API is available
export async function isChatApiAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) return false;
    
    const health = await response.json();
    return health.chat_enabled === true || health.chat_enabled === "True";
  } catch {
    return false;
  }
}

// Session management utilities
export function getSessionId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("chat_session_id");
}

export function setSessionId(sessionId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("chat_session_id", sessionId);
}

export function clearSessionId(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("chat_session_id");
}

export { ChatApiError };
