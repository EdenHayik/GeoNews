// News Event from API
export interface NewsEvent {
  id: number;
  source_name: string;
  original_url: string | null;
  original_title: string | null;
  original_text: string | null;
  summary_text: string;
  location_name: string | null;
  latitude: number | null;
  longitude: number | null;
  category: EventCategory;
  confidence_score: number | null;
  image_url: string | null;
  timestamp_detected: string;
  timestamp_original: string | null;
}

// Event categories
export type EventCategory = 
  | 'military'
  | 'political'
  | 'casualties'
  | 'infrastructure'
  | 'general';

// API Response types
export interface NewsEventsResponse {
  events: NewsEvent[];
  total: number;
  filtered_hours: number;
}

export interface StatsResponse {
  total_events: number;
  events_last_24h: number;
  events_by_category: Record<string, number>;
  events_by_source: Record<string, number>;
  last_update: string | null;
}

export interface CategoryInfo {
  id: EventCategory;
  name: string;
  color: string;
  icon: string;
}

export interface CategoriesResponse {
  categories: CategoryInfo[];
}

// Map related types
export interface MapMarker {
  id: number;
  position: [number, number];
  event: NewsEvent;
}

// Filter state
export interface FilterState {
  hours: number;
  category: EventCategory | null;
  source: string | null;
  location: string | null;
}

// Category configuration
export const CATEGORY_CONFIG: Record<EventCategory, { color: string; label: string; labelHe: string; bgClass: string }> = {
  military: { color: '#ef4444', label: 'Military Activity', labelHe: 'פעילות צבאית', bgClass: 'bg-red-500' },
  political: { color: '#3b82f6', label: 'Political', labelHe: 'פוליטיקה', bgClass: 'bg-blue-500' },
  casualties: { color: '#dc2626', label: 'Casualties', labelHe: 'נפגעים', bgClass: 'bg-red-600' },
  infrastructure: { color: '#f59e0b', label: 'Infrastructure', labelHe: 'תשתית', bgClass: 'bg-amber-500' },
  general: { color: '#6b7280', label: 'General News', labelHe: 'כללי', bgClass: 'bg-gray-500' },
};

