import { useState, useEffect, useCallback } from 'react';
import { fetchStats } from '@/lib/api';
import type { StatsResponse, Period } from '@/types/api';

interface UseStatsReturn {
  data: StatsResponse | null;
  loading: boolean;
  error: Error | null;
  period: Period;
  setPeriod: (period: Period) => void;
  refetch: () => Promise<void>;
}

export function useStats(initialPeriod: Period = 'day'): UseStatsReturn {
  const [period, setPeriod] = useState<Period>(initialPeriod);
  const [data, setData] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetchStats(period);
      setData(response);
    } catch (err) {
      console.error('[useStats] Error loading data:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch stats'));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSetPeriod = useCallback((newPeriod: Period) => {
    setPeriod(newPeriod);
  }, []);

  const refetch = useCallback(async () => {
    await loadData();
  }, [loadData]);

  return {
    data,
    loading,
    error,
    period,
    setPeriod: handleSetPeriod,
    refetch,
  };
}
