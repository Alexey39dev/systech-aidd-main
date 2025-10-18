"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatCard } from "@/components/chat/chat-card";
import { useChat } from "@/hooks/use-chat";
import { isChatApiAvailable } from "@/lib/chat-api";
import { useEffect, useState } from "react";

export default function ChatPage() {
  const router = useRouter();
  const [apiAvailable, setApiAvailable] = useState<boolean | null>(null);
  
  const {
    messages,
    mode,
    isLoading,
    error,
    sendMessage,
    setMode,
    clearHistory,
    retry,
  } = useChat({
    initialMode: "normal",
    autoLoadHistory: true,
  });

  // Проверяем доступность API
  useEffect(() => {
    const checkApi = async () => {
      try {
        const available = await isChatApiAvailable();
        setApiAvailable(available);
      } catch {
        setApiAvailable(false);
      }
    };
    checkApi();
  }, []);

  const handleBackToDashboard = () => {
    router.push("/dashboard");
  };

  const handleClearHistory = async () => {
    if (confirm("Вы уверены, что хотите очистить историю диалога?")) {
      await clearHistory();
    }
  };

  // Показываем загрузку пока проверяем API
  if (apiAvailable === null) {
    return (
      <div className="flex min-h-screen w-full items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Проверка доступности чата...</p>
        </div>
      </div>
    );
  }

  // Показываем ошибку если API недоступен
  if (apiAvailable === false) {
    return (
      <div className="flex min-h-screen w-full items-center justify-center bg-background">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ArrowLeft className="w-8 h-8 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2">Чат недоступен</h1>
          <p className="text-muted-foreground mb-6">
            Сервис чата временно недоступен. Пожалуйста, попробуйте позже.
          </p>
          <Button onClick={handleBackToDashboard} variant="outline">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Вернуться к дашборду
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Header */}
      <div className="fixed top-0 left-0 right-0 z-40 bg-background/80 backdrop-blur-sm border-b">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBackToDashboard}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="w-4 h-4" />
              Дашборд
            </Button>
            <div>
              <h1 className="text-lg font-semibold">AI Чат</h1>
              <p className="text-sm text-muted-foreground">
                {mode === "admin" 
                  ? "Режим администратора - вопросы о статистике" 
                  : "Обычный режим - общение с ассистентом"
                }
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearHistory}
                className="text-muted-foreground hover:text-foreground"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Очистить
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 pt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <ChatCard
              mode={mode}
              onModeChange={setMode}
              onSendMessage={sendMessage}
              messages={messages}
              isLoading={isLoading}
              error={error}
              className="h-[600px]"
            />
            
            {/* Error retry button */}
            {error && (
              <div className="mt-4 text-center">
                <Button onClick={retry} variant="outline">
                  Попробовать снова
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
