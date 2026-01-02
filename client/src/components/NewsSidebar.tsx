import { useState, useEffect, useRef } from 'react';
import { NewsEvent, CATEGORY_CONFIG, EventCategory, FilterState } from '../types';
import { formatRelativeTime, formatCurrentTime, isRecentEvent } from '../utils/time';
import { 
  Radio, 
  Clock, 
  ExternalLink, 
  MapPin, 
  Filter,
  ChevronDown,
  AlertCircle,
  Zap,
  Building,
  Landmark,
  Newspaper,
  X,
  RefreshCw
} from 'lucide-react';

interface NewsSidebarProps {
  events: NewsEvent[];
  loading: boolean;
  error: string | null;
  total: number;
  filters: FilterState;
  onFilterChange: (filters: Partial<FilterState>) => void;
  onEventClick?: (event: NewsEvent) => void;
  lastUpdated: Date | null;
  onRefresh: () => void;
}

function CategoryIcon({ category, size = 16 }: { category: EventCategory; size?: number }) {
  const iconProps = { size, className: 'flex-shrink-0' };
  
  switch (category) {
    case 'military':
      return <Zap {...iconProps} />;
    case 'political':
      return <Landmark {...iconProps} />;
    case 'casualties':
      return <AlertCircle {...iconProps} />;
    case 'infrastructure':
      return <Building {...iconProps} />;
    default:
      return <Newspaper {...iconProps} />;
  }
}

function NewsItem({ event, onClick }: { event: NewsEvent; onClick?: () => void }) {
  const config = CATEGORY_CONFIG[event.category];
  const isRecent = isRecentEvent(event.timestamp_detected);
  const [showOriginal, setShowOriginal] = useState(false);
  
  return (
    <article 
      className="news-item p-4 border-l-2 border-transparent hover:border-l-blue-500 transition-all animate-slide-up"
      style={{ borderLeftColor: isRecent ? config.color : undefined }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2" dir="rtl">
        <div className="flex items-center gap-2">
          <span 
            className={`category-badge ${event.category}`}
            style={{ color: config.color }}
          >
            <CategoryIcon category={event.category} size={12} />
            <span>{config.labelHe}</span>
          </span>
          {isRecent && (
            <span className="live-indicator flex items-center gap-1 text-[10px] font-bold text-green-400 uppercase tracking-wider">
              <span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
              חי
            </span>
          )}
        </div>
      </div>

      {/* Title (Hebrew translated) */}
      {event.original_title && (
        <h3 className="text-base font-semibold text-white mb-2 leading-snug" dir="rtl">
          {event.original_title}
        </h3>
      )}

      {/* Summary (AI-generated context) */}
      <p className="text-sm text-gray-300 leading-relaxed mb-3" dir="rtl">
        {event.summary_text}
      </p>

      {/* Original Text Drawer Toggle */}
      {event.original_text && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowOriginal(!showOriginal);
          }}
          className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors mb-2"
          dir="rtl"
        >
          <ChevronDown 
            size={14} 
            className={`transition-transform ${showOriginal ? 'rotate-180' : ''}`}
          />
          <span>{showOriginal ? 'הסתר טקסט מקורי' : 'הצג טקסט מקורי'}</span>
        </button>
      )}

      {/* Original Text Drawer */}
      {showOriginal && event.original_text && (
        <div 
          className="mb-3 p-3 bg-geo-dark/50 rounded-lg border border-geo-border animate-slide-up"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
            <Newspaper size={12} />
            <span>טקסט מקורי מ{event.source_name}:</span>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap" dir="rtl">
            {event.original_text}
          </p>
        </div>
      )}

      {/* Image thumbnail if available */}
      {event.image_url && (
        <div className="mb-3 rounded-lg overflow-hidden bg-geo-dark">
          <img 
            src={event.image_url} 
            alt="" 
            className="w-full h-24 object-cover opacity-80 hover:opacity-100 transition-opacity"
            loading="lazy"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        </div>
      )}

      {/* Meta info */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-3">
          {event.location_name && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (event.latitude && event.longitude) {
                  onClick?.();
                }
              }}
              className={`flex items-center gap-1 transition-all ${
                event.latitude && event.longitude
                  ? 'hover:text-blue-400 hover:bg-blue-500/10 px-2 py-1 -mx-2 -my-1 rounded-md cursor-pointer'
                  : ''
              }`}
              disabled={!event.latitude || !event.longitude}
            >
              <MapPin size={12} className={event.latitude && event.longitude ? 'group-hover:text-blue-400' : ''} />
              <span dir="rtl">{event.location_name}</span>
            </button>
          )}
          <span className="flex items-center gap-1">
            <Clock size={12} />
            {formatRelativeTime(event.timestamp_detected)}
          </span>
        </div>
        {event.original_url && (
          <a 
            href={event.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-blue-400 hover:text-blue-300 transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            <span dir="rtl">{event.source_name}</span>
            <ExternalLink size={10} />
          </a>
        )}
      </div>
    </article>
  );
}

export default function NewsSidebar({
  events,
  loading,
  error,
  total,
  filters,
  onFilterChange,
  onEventClick,
  lastUpdated,
  onRefresh,
}: NewsSidebarProps) {
  const [currentTime, setCurrentTime] = useState(formatCurrentTime());
  const [showFilters, setShowFilters] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  // Update clock every second
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(formatCurrentTime());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const categories: (EventCategory | null)[] = [null, 'military', 'political', 'casualties', 'infrastructure', 'general'];
  const hourOptions = [6, 12, 24, 48, 72, 168];
  
  // Get unique sources from events
  const sources = ['הכל', ...Array.from(new Set(events.map(e => e.source_name)))];

  return (
    <aside className="flex flex-col h-full bg-geo-panel border-l border-geo-border">
      {/* Header */}
      <header className="flex-shrink-0 p-4 border-b border-geo-border bg-geo-darker/50">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="relative">
              <Radio className="text-red-500" size={20} />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-500 rounded-full live-indicator"></span>
            </div>
            <h1 className="text-lg font-semibold text-white font-display" dir="rtl">חדשות בזמן אמת</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onRefresh}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-geo-border/50 rounded-lg transition-colors"
              title="רענן"
            >
              <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            </button>
            <span className="text-sm font-mono text-gray-400">{currentTime}</span>
          </div>
        </div>

        {/* Stats bar */}
        <div className="flex items-center justify-between text-xs text-gray-500" dir="rtl">
          <span>{total} אירועים ב-{filters.hours} שעות אחרונות</span>
          {lastUpdated && (
            <span>עודכן {formatRelativeTime(lastUpdated.toISOString())}</span>
          )}
        </div>

        {/* Filter toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-2 mt-3 w-full px-3 py-2 text-sm text-gray-300 bg-geo-dark/50 hover:bg-geo-dark rounded-lg transition-colors"
          dir="rtl"
        >
          <Filter size={14} />
          <span>סינון</span>
          {(filters.category || filters.source) && (
            <span className="ml-auto px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded-full">
              {filters.category && CATEGORY_CONFIG[filters.category].labelHe}
              {filters.category && filters.source && ' • '}
              {filters.source}
            </span>
          )}
          <ChevronDown size={14} className={`transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>

        {/* Filter panel */}
        {showFilters && (
          <div className="mt-3 p-3 bg-geo-dark/50 rounded-lg space-y-3 animate-slide-up" dir="rtl">
            {/* Time filter */}
            <div>
              <label className="block text-xs text-gray-500 mb-2">טווח זמן</label>
              <div className="flex flex-wrap gap-1.5">
                {hourOptions.map((hours) => (
                  <button
                    key={hours}
                    onClick={() => onFilterChange({ hours })}
                    className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                      filters.hours === hours
                        ? 'bg-blue-500 text-white'
                        : 'bg-geo-border/50 text-gray-400 hover:text-white'
                    }`}
                  >
                    {hours} שעות
                  </button>
                ))}
              </div>
            </div>

            {/* Category filter */}
            <div>
              <label className="block text-xs text-gray-500 mb-2">קטגוריה</label>
              <div className="flex flex-wrap gap-1.5">
                {categories.map((cat) => (
                  <button
                    key={cat || 'all'}
                    onClick={() => onFilterChange({ category: cat })}
                    className={`flex items-center gap-1 px-2.5 py-1 text-xs rounded-md transition-colors ${
                      filters.category === cat
                        ? 'bg-blue-500 text-white'
                        : 'bg-geo-border/50 text-gray-400 hover:text-white'
                    }`}
                  >
                    {cat ? (
                      <>
                        <CategoryIcon category={cat} size={10} />
                        {CATEGORY_CONFIG[cat].labelHe}
                      </>
                    ) : (
                      'הכל'
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Source filter */}
            <div>
              <label className="block text-xs text-gray-500 mb-2">מקור</label>
              <div className="flex flex-wrap gap-1.5">
                {sources.map((source) => (
                  <button
                    key={source}
                    onClick={() => onFilterChange({ source: source === 'הכל' ? null : source })}
                    className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                      (source === 'הכל' && !filters.source) || filters.source === source
                        ? 'bg-blue-500 text-white'
                        : 'bg-geo-border/50 text-gray-400 hover:text-white'
                    }`}
                  >
                    {source}
                  </button>
                ))}
              </div>
            </div>

            {/* Location filter */}
            <div>
              <label className="block text-xs text-gray-500 mb-2">מיקום</label>
              <input
                type="text"
                placeholder="חפש לפי מיקום..."
                value={filters.location || ''}
                onChange={(e) => onFilterChange({ location: e.target.value || null })}
                className="w-full px-3 py-2 text-sm bg-geo-border/50 text-white placeholder-gray-500 rounded-md border border-geo-border focus:border-blue-500 focus:outline-none transition-colors"
                dir="rtl"
              />
            </div>

            {/* Clear filters */}
            {(filters.category || filters.source || filters.location) && (
              <button
                onClick={() => onFilterChange({ category: null, source: null, location: null })}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-white transition-colors"
              >
                <X size={12} />
                נקה סינון
              </button>
            )}
          </div>
        )}
      </header>

      {/* News list */}
      <div 
        ref={listRef}
        className="flex-1 overflow-y-auto divide-y divide-geo-border/50"
      >
        {error ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <AlertCircle className="text-red-400 mb-3" size={32} />
            <p className="text-gray-400 text-sm">{error}</p>
            <button
              onClick={onRefresh}
              className="mt-4 px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : loading && events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8">
            <RefreshCw className="text-blue-400 animate-spin mb-3" size={32} />
            <p className="text-gray-400 text-sm">Loading events...</p>
          </div>
        ) : events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <Newspaper className="text-gray-600 mb-3" size={32} />
            <p className="text-gray-400 text-sm">No events found</p>
            <p className="text-gray-500 text-xs mt-1">Try adjusting your filters</p>
          </div>
        ) : (
          events.map((event) => (
            <NewsItem 
              key={event.id} 
              event={event} 
              onClick={() => onEventClick?.(event)}
            />
          ))
        )}
      </div>
    </aside>
  );
}

