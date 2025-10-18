"use client";

import { useRouter } from "next/navigation";
import { useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { TimelineChart } from "@/components/dashboard/timeline-chart";
import { RecentDialogs } from "@/components/dashboard/recent-dialogs";
import { TopUsers } from "@/components/dashboard/top-users";
import { MetricCard } from "@/components/dashboard/metric-card";
import { PeriodFilter } from "@/components/dashboard/period-filter";
import { FloatingChatButton } from "@/components/chat/floating-chat-button";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useStats } from "@/hooks/use-stats";
import type { Period, StatsResponse, MetricCard as MetricCardType } from "@/types/api";

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      {/* Metrics cards skeleton */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
        <Skeleton className="h-32" />
      </div>

      {/* Chart skeleton */}
      <Skeleton className="h-80" />

      {/* Bottom row skeleton */}
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-64" />
        <Skeleton className="h-64" />
      </div>
    </div>
  );
}

function ErrorState({ error, onRetry }: { error: Error; onRetry: () => void }) {
  return (
    <div className="flex h-full items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Failed to load dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-4">{error.message}</p>
          <Button onClick={onRetry}>Retry</Button>
        </CardContent>
      </Card>
    </div>
  );
}

function DashboardWithParams() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initialPeriod = (searchParams.get('period') || 'day') as Period;
  
  const { data, loading, error, period, setPeriod, refetch } = useStats(initialPeriod);

  // Синхронизация с URL при изменении периода
  useEffect(() => {
    const currentPeriod = searchParams.get('period') || 'day';
    if (currentPeriod !== period) {
      router.push(`/dashboard?period=${period}`);
    }
  }, [period, searchParams, router]);

  const handlePeriodChange = (newPeriod: Period) => {
    setPeriod(newPeriod);
  };

  return <DashboardContent data={data} loading={loading} error={error} period={period} onPeriodChange={handlePeriodChange} onRetry={refetch} />;
}

function DashboardContent({ 
  data, 
  loading, 
  error, 
  period, 
  onPeriodChange, 
  onRetry 
}: { 
  data: StatsResponse | null; 
  loading: boolean; 
  error: Error | null; 
  period: Period; 
  onPeriodChange: (period: Period) => void; 
  onRetry: () => void; 
}) {
  const router = useRouter();

  if (error) {
    return (
      <div className="flex min-h-screen w-full flex-col bg-muted/40">
        <div className="flex flex-col sm:gap-4 sm:py-4">
          <main className="grid flex-1 items-start gap-4 p-4 sm:px-6 sm:py-0 md:gap-8">
            <ErrorState error={error} onRetry={onRetry} />
          </main>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Fixed Sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 hidden w-14 flex-col border-r bg-background sm:flex">
        <nav className="flex flex-col items-center gap-4 px-2 py-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground text-lg font-semibold">
            S
          </div>
          <div className="flex flex-col gap-2 w-full">
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9"
              onClick={() => router.push("/")}
              title="Главная"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9"
              onClick={() => router.push("/dashboard")}
              title="Дашборд"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-9 w-9"
              onClick={() => router.push("/chat")}
              title="Чат"
            >
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </Button>
          </div>
        </nav>
      </aside>
      
      {/* Main Content */}
      <div className="flex flex-col sm:pl-14 w-full">
        <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background px-4 sm:px-6">
          <h1 className="text-lg font-semibold">Dashboard</h1>
        </header>
        <main className="flex flex-1 flex-col">
          <div className="flex flex-1 flex-col gap-4 p-4 md:gap-6 md:p-6 lg:p-8">
            {/* Заголовок и фильтр */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-bold tracking-tight">AI Conversation Metrics</h2>
                <p className="text-muted-foreground">Monitor and analyze your conversations</p>
              </div>
              <PeriodFilter period={period} onPeriodChange={onPeriodChange} />
            </div>

            {/* Контент с обработкой состояний */}
            {loading ? (
              <DashboardSkeleton />
            ) : (
              <div className="space-y-6">
                {/* Метрики - 4 карточки в сетке */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {data?.metrics.map((metric: MetricCardType, index: number) => (
                    <MetricCard 
                      key={index}
                      label={metric.label}
                      value={metric.value}
                      change={metric.change}
                      trend={metric.trend}
                    />
                  ))}
                </div>

                {/* График */}
                <TimelineChart data={data?.timeline || []} period={period} />

                {/* Нижняя часть - Recent Dialogs и Top Users */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                  <div className="lg:col-span-4">
                    <RecentDialogs dialogs={data?.recent_dialogs || []} loading={loading} />
                  </div>
                  <div className="lg:col-span-3">
                    <TopUsers users={data?.top_users || []} loading={loading} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>

      {/* Floating Chat Button */}
      <FloatingChatButton 
        onClick={() => router.push("/chat")}
        showBadge={false}
      />
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <DashboardWithParams />
    </Suspense>
  );
}
