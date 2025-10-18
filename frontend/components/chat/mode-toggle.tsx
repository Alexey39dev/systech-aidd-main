"use client";

import { Database, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { ChatMode } from "@/types/api";

interface ModeToggleProps {
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  className?: string;
}

export function ModeToggle({ mode, onModeChange, className }: ModeToggleProps) {
  return (
    <div className={cn("flex items-center gap-1 bg-black/20 rounded-lg p-1", className)}>
      <Button
        variant={mode === "normal" ? "default" : "ghost"}
        size="sm"
        onClick={() => onModeChange("normal")}
        className={cn(
          "h-8 px-3 text-xs transition-all",
          mode === "normal"
            ? "bg-white/20 text-white shadow-sm"
            : "text-white/60 hover:text-white hover:bg-white/10"
        )}
      >
        <MessageCircle className="w-3 h-3 mr-1" />
        Обычный
      </Button>
      <Button
        variant={mode === "admin" ? "default" : "ghost"}
        size="sm"
        onClick={() => onModeChange("admin")}
        className={cn(
          "h-8 px-3 text-xs transition-all",
          mode === "admin"
            ? "bg-white/20 text-white shadow-sm"
            : "text-white/60 hover:text-white hover:bg-white/10"
        )}
      >
        <Database className="w-3 h-3 mr-1" />
        Админ
      </Button>
    </div>
  );
}
