import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string | number;
  change: string;
  trend: "up" | "down" | "neutral";
}

export function MetricCard({ label, value, change, trend }: MetricCardProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case "up":
        return "↗";
      case "down":
        return "↘";
      default:
        return "→";
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case "up":
        return "text-green-600 dark:text-green-500";
      case "down":
        return "text-red-600 dark:text-red-500";
      default:
        return "text-muted-foreground";
    }
  };

  const formatValue = (val: string | number) => {
    if (typeof val === 'number') {
      return val.toLocaleString();
    }
    return val;
  };

  return (
    <Card className="hover:bg-accent/50 transition-colors">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {label}
        </CardTitle>
        <div className={cn("flex items-center gap-0.5 text-xs font-medium", getTrendColor())}>
          <span className="text-base leading-none">{getTrendIcon()}</span>
          <span>{change}</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold tracking-tight">
          {formatValue(value)}
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          {trend === "up" && "Trending up this month"}
          {trend === "down" && "Acquisition needs attention"}
          {trend === "neutral" && "Steady performance"}
        </p>
      </CardContent>
    </Card>
  );
}
