import { API_BASE_URL, API_ENDPOINTS } from "./constants";
import type { StatsResponse, Period, HealthResponse } from "@/types/api";

// Локальный интерфейс для ошибки API (переименован, чтобы избежать конфликта)
interface ApiErrorResponse {
  detail: string;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: ApiErrorResponse
  ) {
    super(message);
    this.name = "ApiError";
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

    throw new ApiError(
      errorData?.detail || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData || undefined
    );
  }

  return response.json();
}

export async function fetchStats(period: Period): Promise<StatsResponse> {
  try {
    const url = new URL(API_ENDPOINTS.STATS, API_BASE_URL);
    url.searchParams.set("period", period);

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      // Add cache control for development
      cache: "no-cache",
    });

    return handleResponse<StatsResponse>(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Network or other errors
    throw new ApiError(
      `Failed to fetch stats: ${error instanceof Error ? error.message : "Unknown error"}`,
      0
    );
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  try {
    const url = new URL(API_ENDPOINTS.HEALTH, API_BASE_URL);

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    return handleResponse<HealthResponse>(response);
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    throw new ApiError(
      `Failed to fetch health status: ${error instanceof Error ? error.message : "Unknown error"}`,
      0
    );
  }
}

// Utility function to check if API is available
export async function isApiAvailable(): Promise<boolean> {
  try {
    await fetchHealth();
    return true;
  } catch {
    return false;
  }
}
