import { useState, useEffect, useCallback } from 'react';
import { NewsEvent, NewsEventsResponse, FilterState } from '../types';

const API_BASE = '/api';

interface UseNewsEventsReturn {
  events: NewsEvent[];
  loading: boolean;
  error: string | null;
  total: number;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
}

export function useNewsEvents(filters: FilterState): UseNewsEventsReturn {
  const [events, setEvents] = useState<NewsEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query params
      const params = new URLSearchParams();
      params.set('hours', filters.hours.toString());
      params.set('limit', '200');
      
      if (filters.category) {
        params.set('category', filters.category);
      }
      if (filters.source) {
        params.set('source', filters.source);
      }

      const response = await fetch(`${API_BASE}/events?${params}`);
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: NewsEventsResponse = await response.json();
      
      // Apply client-side location filter if specified
      let filteredEvents = data.events;
      if (filters.location) {
        filteredEvents = data.events.filter(event => 
          event.location_name?.toLowerCase().includes(filters.location!.toLowerCase())
        );
      }
      
      setEvents(filteredEvents);
      setTotal(filteredEvents.length);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Failed to fetch events:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch events');
    } finally {
      setLoading(false);
    }
  }, [filters.hours, filters.category, filters.source, filters.location]);

  // Initial fetch and polling
  useEffect(() => {
    fetchEvents();

    // Poll every 30 seconds
    const interval = setInterval(fetchEvents, 30000);
    return () => clearInterval(interval);
  }, [fetchEvents]);

  return {
    events,
    loading,
    error,
    total,
    refetch: fetchEvents,
    lastUpdated,
  };
}

// Hook for stats
export function useStats() {
  const [stats, setStats] = useState<{
    total_events: number;
    events_last_24h: number;
    events_by_category: Record<string, number>;
  } | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_BASE}/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  return stats;
}

