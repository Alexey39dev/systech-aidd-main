"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { TimelinePoint, Period } from "@/types/api";
import { formatTimestamp } from "@/lib/format-utils";

interface TimelineChartProps {
  data: TimelinePoint[];
  period: Period;
}

export function TimelineChart({ data, period }: TimelineChartProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Total Visitors</CardTitle>
          <CardDescription>Total for the last 3 months</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex h-64 items-center justify-center">
            <div className="space-y-2 text-center">
              <div className="text-4xl">📊</div>
              <p className="text-muted-foreground">No data available</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Расчет размеров и масштабирование
  const width = 1000;
  const height = 400;
  const padding = { top: 20, right: 2, bottom: 40, left: 2 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxValue = Math.max(...data.map(d => d.value), 1);
  const minValue = 0;

  // Создание точек для линии и области
  const points = data.map((point, index) => {
    const x = padding.left + (index / (data.length - 1)) * chartWidth;
    const y = padding.top + chartHeight - ((point.value - minValue) / (maxValue - minValue)) * chartHeight;
    return { x, y, value: point.value, timestamp: point.timestamp };
  });

  // Создание плавной кривой Catmull-Rom для более естественного вида
  const createSmoothPath = (pts: typeof points, tension: number = 0.5) => {
    if (pts.length < 2) return '';
    
    let path = `M ${pts[0].x} ${pts[0].y}`;
    
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[Math.max(i - 1, 0)];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = pts[Math.min(i + 2, pts.length - 1)];
      
      const cp1x = p1.x + (p2.x - p0.x) / 6 * tension;
      const cp1y = p1.y + (p2.y - p0.y) / 6 * tension;
      const cp2x = p2.x - (p3.x - p1.x) / 6 * tension;
      const cp2y = p2.y - (p3.y - p1.y) / 6 * tension;
      
      path += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
    }
    
    return path;
  };

  const linePath = createSmoothPath(points);

  // Path для заливки области с плавной линией
  const areaPath = `
    ${linePath}
    L ${points[points.length - 1].x} ${padding.top + chartHeight}
    L ${points[0].x} ${padding.top + chartHeight}
    Z
  `;

  // X-axis метки (показываем каждую 6-ю метку для читаемости)
  const xStep = Math.max(1, Math.floor(data.length / 8));
  const xLabels = data.filter((_, i) => i % xStep === 0 || i === data.length - 1);

  // Форматирование текста для description
  const getDescriptionText = () => {
    switch (period) {
      case 'day':
        return 'Showing hourly data for the last 24 hours';
      case 'week':
        return 'Showing daily data for the last 7 days';
      case 'month':
        return 'Showing daily data for the last 30 days';
      default:
        return 'Total for the last 3 months';
    }
  };

  return (
    <Card>
      <CardHeader className="flex items-center gap-2 space-y-0 border-b py-5 sm:flex-row">
        <div className="grid flex-1 gap-1 text-center sm:text-left">
          <CardTitle>Total Visitors</CardTitle>
          <CardDescription>{getDescriptionText()}</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <div className="w-full h-[350px]">
          <svg 
            viewBox={`0 0 ${width} ${height}`} 
            className="w-full h-full"
            preserveAspectRatio="xMidYMid meet"
          >
            {/* Gradient definitions */}
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.4" />
                <stop offset="50%" stopColor="hsl(var(--primary))" stopOpacity="0.2" />
                <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0.05" />
              </linearGradient>
            </defs>

            {/* Area fill with gradient */}
            <path
              d={areaPath}
              fill="url(#colorGradient)"
              className="transition-all duration-500"
            />

            {/* Line - multiple layers for glow effect */}
            <path
              d={linePath}
              fill="none"
              stroke="hsl(var(--primary))"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="transition-all duration-500"
              opacity="0.3"
            />
            <path
              d={linePath}
              fill="none"
              stroke="hsl(var(--primary))"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="transition-all duration-500"
            />

            {/* X-axis labels */}
            {xLabels.map((point, i) => {
              const index = data.indexOf(point);
              const x = padding.left + (index / (data.length - 1)) * chartWidth;
              return (
                <text
                  key={i}
                  x={x}
                  y={height - padding.bottom + 25}
                  textAnchor="middle"
                  fontSize="11"
                  fill="currentColor"
                  className="fill-muted-foreground"
                >
                  {formatTimestamp(point.timestamp, period)}
                </text>
              );
            })}

            {/* Invisible hover areas for tooltips */}
            {points.map((point, i) => (
              <g key={i}>
                <circle
                  cx={point.x}
                  cy={point.y}
                  r="24"
                  fill="transparent"
                  className="cursor-pointer"
                >
                  <title>{`${formatTimestamp(point.timestamp, period)}: ${point.value} messages`}</title>
                </circle>
              </g>
            ))}
          </svg>
        </div>
      </CardContent>
    </Card>
  );
}
