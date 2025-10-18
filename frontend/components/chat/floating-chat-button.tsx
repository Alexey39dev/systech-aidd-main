"use client";

import { useState, useEffect } from "react";
import { MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FloatingChatButtonProps {
  className?: string;
  onClick?: () => void;
  showBadge?: boolean;
  badgeCount?: number;
}

export function FloatingChatButton({
  className,
  onClick,
  showBadge = false,
  badgeCount = 0,
}: FloatingChatButtonProps) {
  const [isVisible, setIsVisible] = useState(false);

  // Показываем кнопку после небольшой задержки
  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        "fixed bottom-6 right-6 z-50 animate-in fade-in-0 zoom-in-95 duration-500",
        className
      )}
    >
      <Button
        onClick={onClick}
        className="relative h-14 w-14 rounded-full bg-primary hover:bg-primary/90 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
        size="icon"
      >
        <MessageCircle className="w-6 h-6" />
        
        {/* Badge */}
        {showBadge && badgeCount > 0 && (
          <div className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-red-500 text-white text-xs font-bold flex items-center justify-center animate-in zoom-in-95 duration-300">
            {badgeCount > 99 ? "99+" : badgeCount}
          </div>
        )}

        {/* Pulse animation using CSS */}
        <div className="absolute inset-0 rounded-full bg-primary/30 animate-ping" />
      </Button>
    </div>
  );
}
