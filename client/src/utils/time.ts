import { formatDistanceToNow, format, parseISO } from 'date-fns';

/**
 * Format a timestamp as relative time (e.g., "5 minutes ago")
 */
export function formatRelativeTime(timestamp: string): string {
  try {
    const date = parseISO(timestamp);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return 'Unknown time';
  }
}

/**
 * Format a timestamp for display in popup (e.g., "Jan 15, 2024 at 14:30")
 */
export function formatFullTime(timestamp: string): string {
  try {
    const date = parseISO(timestamp);
    return format(date, "MMM d, yyyy 'at' HH:mm");
  } catch {
    return 'Unknown time';
  }
}

/**
 * Format current time for display
 */
export function formatCurrentTime(): string {
  return format(new Date(), 'HH:mm:ss');
}

/**
 * Check if an event is recent (within last hour)
 */
export function isRecentEvent(timestamp: string): boolean {
  try {
    const date = parseISO(timestamp);
    const hourAgo = new Date(Date.now() - 60 * 60 * 1000);
    return date > hourAgo;
  } catch {
    return false;
  }
}

