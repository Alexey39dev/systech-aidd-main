"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Bot, User, Copy, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ModeToggle } from "./mode-toggle";
import { SQLDisplay } from "./sql-display";
import type { ChatMode, ChatMessage } from "@/types/api";

interface ChatCardProps {
  className?: string;
  mode?: ChatMode;
  initialMode?: ChatMode;
  onModeChange?: (mode: ChatMode) => void;
  onSendMessage?: (message: string, mode: ChatMode) => Promise<void>;
  messages?: ChatMessage[];
  isLoading?: boolean;
  error?: string | null;
}

export function ChatCard({
  className,
  mode: externalMode,
  initialMode = "normal",
  onModeChange,
  onSendMessage,
  messages = [],
  isLoading = false,
  error = null,
}: ChatCardProps) {
  const [input, setInput] = useState("");
  const [internalMode, setInternalMode] = useState<ChatMode>(initialMode);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Используем внешний mode если передан, иначе внутренний
  const mode = externalMode ?? internalMode;

  // Автоскролл к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !onSendMessage) return;

    const message = input.trim();
    setInput("");
    
    try {
      await onSendMessage(message, mode);
    } catch (err) {
      console.error("Error sending message:", err);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleModeChange = (newMode: ChatMode) => {
    if (externalMode === undefined) {
      // Если mode не передан извне, обновляем внутреннее состояние
      setInternalMode(newMode);
    }
    onModeChange?.(newMode);
  };

  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error("Failed to copy text:", err);
    }
  };

  return (
    <div className={cn("relative w-full max-w-2xl mx-auto h-[600px] rounded-2xl overflow-hidden p-[2px]", className)}>
      {/* Animated Outer Border */}
      <div className="absolute inset-0 rounded-2xl border-2 border-white/20 animate-spin-slow" />

      {/* Inner Card */}
      <div className="relative flex flex-col w-full h-full rounded-xl border border-white/10 overflow-hidden bg-black/90 backdrop-blur-xl">
        {/* Inner Animated Background */}
        <div 
          className="absolute inset-0 bg-gradient-to-br from-gray-800 via-black to-gray-900 animate-gradient-shift"
          style={{ backgroundSize: "200% 200%" }}
        />

        {/* Floating Particles - simplified */}
        {Array.from({ length: 10 }).map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 rounded-full bg-white/10 animate-float"
            style={{ 
              left: `${Math.random() * 100}%`, 
              bottom: "-10%",
              animationDelay: `${i * 0.5}s`,
              animationDuration: `${5 + Math.random() * 3}s`
            }}
          />
        ))}

        {/* Header */}
        <div className="px-4 py-3 border-b border-white/10 relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-white" />
            <h2 className="text-lg font-semibold text-white">AI Assistant</h2>
          </div>
          <ModeToggle mode={mode} onModeChange={handleModeChange} />
        </div>

        {/* Messages */}
        <div className="flex-1 px-4 py-3 overflow-y-auto space-y-3 text-sm flex flex-col relative z-10">
          {messages.length === 0 && !isLoading && !error && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center text-white/60">
                <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Привет! Я ваш AI-ассистент.</p>
                <p className="text-sm mt-1">
                  {mode === "admin" 
                    ? "Задавайте вопросы о статистике диалогов" 
                    : "Как дела? Чем могу помочь?"
                  }
                </p>
              </div>
            </div>
          )}

          {error && (
            <div className="px-3 py-2 rounded-xl bg-red-500/20 text-red-200 border border-red-500/30">
              <p className="text-sm">Ошибка: {error}</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                "px-3 py-2 rounded-xl max-w-[80%] shadow-md backdrop-blur-md relative group animate-in fade-in-0 slide-in-from-bottom-2 duration-400",
                msg.role === "assistant"
                  ? "bg-white/10 text-white self-start"
                  : "bg-white/30 text-black font-semibold self-end"
              )}
            >
              <div className="flex items-start gap-2">
                {msg.role === "assistant" ? (
                  <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />
                ) : (
                  <User className="w-4 h-4 mt-0.5 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.mode === "admin" && msg.sql_query && (
                    <SQLDisplay sqlQuery={msg.sql_query} />
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0"
                  onClick={() => copyToClipboard(msg.content, `msg-${i}`)}
                >
                  {copiedMessageId === `msg-${i}` ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <Copy className="w-3 h-3" />
                  )}
                </Button>
              </div>
            </div>
          ))}

          {/* AI Typing Indicator */}
          {isLoading && (
            <div className="flex items-center gap-1 px-3 py-2 rounded-xl max-w-[30%] bg-white/10 self-start animate-pulse">
              <Bot className="w-4 h-4" />
              <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>
              <span className="w-2 h-2 rounded-full bg-white animate-pulse delay-200"></span>
              <span className="w-2 h-2 rounded-full bg-white animate-pulse delay-400"></span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex items-center gap-2 p-3 border-t border-white/10 relative z-10">
          <input
            className="flex-1 px-3 py-2 text-sm bg-black/50 rounded-lg border border-white/10 text-white focus:outline-none focus:ring-1 focus:ring-white/50 placeholder-white/50"
            placeholder={
              mode === "admin" 
                ? "Задайте вопрос о статистике..." 
                : "Введите сообщение..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors disabled:opacity-50"
            size="sm"
          >
            <Send className="w-4 h-4 text-white" />
          </Button>
        </div>
      </div>
    </div>
  );
}
