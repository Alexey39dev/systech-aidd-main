"use client";

import { useState, useEffect, useCallback } from "react";
import { sendMessage, fetchChatHistory, clearChatHistory, getSessionId, setSessionId, ChatApiError } from "@/lib/chat-api";
import type { ChatMessage, ChatMode } from "@/types/api";

interface UseChatOptions {
  initialMode?: ChatMode;
  autoLoadHistory?: boolean;
}

interface UseChatReturn {
  messages: ChatMessage[];
  mode: ChatMode;
  isLoading: boolean;
  error: string | null;
  sessionId: string | null;
  sendMessage: (message: string) => Promise<void>;
  setMode: (mode: ChatMode) => void;
  clearHistory: () => Promise<void>;
  retry: () => void;
}

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { initialMode = "normal", autoLoadHistory = true } = options;
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [mode, setMode] = useState<ChatMode>(initialMode);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionIdState] = useState<string | null>(null);

  // Инициализация session ID
  useEffect(() => {
    const savedSessionId = getSessionId();
    if (savedSessionId) {
      setSessionIdState(savedSessionId);
    }
  }, []);

  // Загрузка истории при инициализации
  useEffect(() => {
    if (autoLoadHistory && sessionId) {
      loadHistory();
    }
  }, [sessionId, autoLoadHistory]);

  const loadHistory = useCallback(async () => {
    if (!sessionId) return;

    try {
      setError(null);
      const history = await fetchChatHistory(sessionId);
      setMessages(history.messages);
    } catch (err) {
      console.error("Failed to load chat history:", err);
      // Не показываем ошибку загрузки истории как критическую
    }
  }, [sessionId]);

  const handleSendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      // Добавляем сообщение пользователя в UI сразу
      const userMessage: ChatMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
        mode: null,
      };
      setMessages(prev => [...prev, userMessage]);

      // Отправляем запрос
      const response = await sendMessage(message, mode, sessionId || undefined);
      
      // Обновляем session ID если получили новый
      if (response.metadata?.session_id && response.metadata.session_id !== sessionId) {
        const newSessionId = response.metadata.session_id as string;
        setSessionIdState(newSessionId);
        setSessionId(newSessionId);
      }

      // Добавляем ответ ассистента
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.message,
        timestamp: response.timestamp,
        mode: response.mode,
        sql_query: response.sql_query || undefined,
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (err) {
      console.error("Failed to send message:", err);
      
      let errorMessage = "Произошла ошибка при отправке сообщения";
      if (err instanceof ChatApiError) {
        if (err.status === 503) {
          errorMessage = "Чат временно недоступен";
        } else if (err.status === 400) {
          errorMessage = "Некорректный запрос";
        } else if (err.status >= 500) {
          errorMessage = "Ошибка сервера";
        } else {
          errorMessage = err.message;
        }
      }
      
      setError(errorMessage);
      
      // Удаляем сообщение пользователя при ошибке
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [mode, sessionId]);

  const handleSetMode = useCallback((newMode: ChatMode) => {
    setMode(newMode);
  }, []);

  const handleClearHistory = useCallback(async () => {
    if (!sessionId) return;

    try {
      setError(null);
      await clearChatHistory(sessionId);
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear history:", err);
      setError("Не удалось очистить историю");
    }
  }, [sessionId]);

  const retry = useCallback(() => {
    setError(null);
    if (sessionId) {
      loadHistory();
    }
  }, [sessionId, loadHistory]);

  return {
    messages,
    mode,
    isLoading,
    error,
    sessionId,
    sendMessage: handleSendMessage,
    setMode: handleSetMode,
    clearHistory: handleClearHistory,
    retry,
  };
}
