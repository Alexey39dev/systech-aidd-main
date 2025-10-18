"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SQLDisplayProps {
  sqlQuery: string;
  className?: string;
}

export function SQLDisplay({ sqlQuery, className }: SQLDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(sqlQuery);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy SQL:", err);
    }
  };

  return (
    <div className={cn("mt-2 border border-white/20 rounded-lg overflow-hidden", className)}>
      <div className="flex items-center justify-between px-3 py-2 bg-black/30 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-white/80">SQL Query</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={copyToClipboard}
            className="h-6 w-6 p-0 hover:bg-white/10"
          >
            {copied ? (
              <Check className="w-3 h-3 text-green-400" />
            ) : (
              <Copy className="w-3 h-3 text-white/60" />
            )}
          </Button>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="h-6 w-6 p-0 hover:bg-white/10"
        >
          {isExpanded ? (
            <ChevronUp className="w-3 h-3 text-white/60" />
          ) : (
            <ChevronDown className="w-3 h-3 text-white/60" />
          )}
        </Button>
      </div>
      
      {isExpanded && (
        <div className="p-3 bg-black/50">
          <pre className="text-xs text-green-400 font-mono whitespace-pre-wrap overflow-x-auto">
            {sqlQuery}
          </pre>
        </div>
      )}
    </div>
  );
}
