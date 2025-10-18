"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Period } from "@/types/api";

interface PeriodFilterProps {
  period: Period;
  onPeriodChange: (period: Period) => void;
  className?: string;
}

export function PeriodFilter({ period, onPeriodChange, className }: PeriodFilterProps) {
  const handleValueChange = (value: string) => {
    // Type assertion is safe here because we control the possible values
    onPeriodChange(value as Period);
  };

  return (
    <Tabs value={period} onValueChange={handleValueChange} className={className}>
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="day">Day</TabsTrigger>
        <TabsTrigger value="week">Week</TabsTrigger>
        <TabsTrigger value="month">Month</TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
