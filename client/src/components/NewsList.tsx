import { useState } from 'react';
import { NewsEvent, CATEGORY_CONFIG, EventCategory, FilterState } from '../types';
import { formatRelativeTime, formatFullTime } from '../utils/time';
import {
  Calendar,
  MapPin,
  ExternalLink,
  Filter,
  ChevronDown,
  X,
  Clock,
  Newspaper,
  AlertCircle,
  Zap,
  Building,
  Landmark,
} from 'lucide-react';

interface NewsListProps {
  events: NewsEvent[];
  loading: boolean;
  error: string | null;
  total: number;
  filters: FilterState;
  onFilterChange: (filters: Partial<FilterState>) => void;
  onEventClick?: (event: NewsEvent) => void;
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

function NewsListItem({ event, onClick }: { event: NewsEvent; onClick?: () => void }) {
  const config = CATEGORY_CONFIG[event.category];
  const [showOriginal, setShowOriginal] = useState(false);
  const hasLocation = event.latitude && event.longitude;

  return (
    <article
      className="bg-geo-panel border border-geo-border rounded-xl p-5 hover:border-blue-500/50 transition-all"
      dir="rtl"
    >
      {/* Header with category and time */}
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex items-center gap-2">
          <span
            className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium"
            style={{ background: `${config.color}20`, color: config.color }}
          >
            <CategoryIcon category={event.category} size={12} />
            {config.labelHe}
          </span>
          <span className="text-xs text-gray-500">{event.source_name}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Clock size={12} />
          {formatRelativeTime(event.timestamp_detected)}
        </div>
      </div>

      {/* Title */}
      {event.original_title && (
        <h3 className="text-lg font-semibold text-white mb-2 leading-snug">
          {event.original_title}
        </h3>
      )}

      {/* Summary */}
      <p className="text-sm text-gray-300 leading-relaxed mb-3">
        {event.summary_text}
      </p>

      {/* Location - Clickable */}
      {event.location_name && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (hasLocation) onClick?.();
          }}
          disabled={!hasLocation}
          className={`flex items-center gap-2 text-sm mb-3 transition-all ${
            hasLocation
              ? 'text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 px-2 py-1.5 -mx-2 rounded-lg cursor-pointer'
              : 'text-gray-500 cursor-default'
          }`}
        >
          <MapPin size={14} />
          <span>{event.location_name}</span>
        </button>
      )}

      {/* Original text toggle */}
      {event.original_text && (
        <>
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowOriginal(!showOriginal);
            }}
            className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 mb-2"
          >
            <ChevronDown
              size={14}
              className={`transition-transform ${showOriginal ? 'rotate-180' : ''}`}
            />
            {showOriginal ? 'הסתר טקסט מקורי' : 'הצג טקסט מקורי'}
          </button>

          {showOriginal && (
            <div className="mt-2 p-3 bg-geo-dark/50 rounded-lg border border-geo-border">
              <p className="text-xs text-gray-400 mb-2">
                טקסט מקורי מ-{event.source_name}
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">
                {event.original_text}
              </p>
            </div>
          )}
        </>
      )}

      {/* Footer with link */}
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-geo-border">
        <div className="text-xs text-gray-500">
          {event.timestamp_original
            ? formatFullTime(event.timestamp_original)
            : formatFullTime(event.timestamp_detected)}
        </div>
        {event.original_url && (
          <a
            href={event.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
            onClick={(e) => e.stopPropagation()}
          >
            <span>קרא עוד</span>
            <ExternalLink size={12} />
          </a>
        )}
      </div>
    </article>
  );
}

export default function NewsList({
  events,
  loading,
  error,
  total,
  filters,
  onFilterChange,
  onEventClick,
}: NewsListProps) {
  const [showFilters, setShowFilters] = useState(false);

  const categories: (EventCategory | null)[] = [
    null,
    'military',
    'political',
    'casualties',
    'infrastructure',
    'general',
  ];
  const hourOptions = [6, 12, 24, 48, 72, 168];

  // Get unique sources
  const sources = ['הכל', ...Array.from(new Set(events.map((e) => e.source_name)))];

  return (
    <div className="h-full w-full bg-geo-darker overflow-hidden flex flex-col">
      {/* Header */}
      <div className="bg-geo-panel border-b border-geo-border px-4 md:px-6 py-3 md:py-4 flex-shrink-0">
        <div className="md:ml-[220px]"> {/* Only add left margin on desktop */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3" dir="rtl">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Newspaper className="text-blue-400" size={24} />
              </div>
              <div>
                <h1 className="text-xl md:text-2xl font-bold text-white">רשימת חדשות</h1>
                <p className="text-xs md:text-sm text-gray-400">{total} אירועים ב-{filters.hours} שעות אחרונות</p>
              </div>
            </div>

            {/* Filter toggle button */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-3 md:px-4 py-2 bg-geo-dark-light hover:bg-geo-border text-gray-300 hover:text-white rounded-lg transition-colors text-sm md:text-base flex-shrink-0"
            >
              <Filter size={16} />
              <span>סינון</span>
              {(filters.category || filters.source) && (
                <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded-full">
                  {[filters.category && CATEGORY_CONFIG[filters.category].labelHe, filters.source]
                    .filter(Boolean)
                    .join(' • ')}
                </span>
              )}
              <ChevronDown
                size={14}
                className={`transition-transform ${showFilters ? 'rotate-180' : ''}`}
              />
            </button>
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-geo-dark/50 rounded-lg space-y-4 animate-slide-up" dir="rtl">
            {/* Time filter */}
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-2">טווח זמן</label>
              <div className="flex flex-wrap gap-2">
                {hourOptions.map((hours) => (
                  <button
                    key={hours}
                    onClick={() => onFilterChange({ hours })}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
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
              <label className="block text-sm font-medium text-gray-400 mb-2">קטגוריה</label>
              <div className="flex flex-wrap gap-2">
                {categories.map((cat) => (
                  <button
                    key={cat || 'all'}
                    onClick={() => onFilterChange({ category: cat })}
                    className={`flex items-center gap-1 px-3 py-1.5 text-sm rounded-lg transition-colors ${
                      filters.category === cat
                        ? 'bg-blue-500 text-white'
                        : 'bg-geo-border/50 text-gray-400 hover:text-white'
                    }`}
                  >
                    {cat ? (
                      <>
                        <CategoryIcon category={cat} size={12} />
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
              <label className="block text-sm font-medium text-gray-400 mb-2">מקור</label>
              <div className="flex flex-wrap gap-2">
                {sources.map((source) => (
                  <button
                    key={source}
                    onClick={() =>
                      onFilterChange({ source: source === 'הכל' ? null : source })
                    }
                    className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
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
              <label className="block text-sm font-medium text-gray-400 mb-2">מיקום</label>
              <input
                type="text"
                placeholder="חפש לפי מיקום..."
                value={filters.location || ''}
                onChange={(e) => onFilterChange({ location: e.target.value || null })}
                className="w-full px-4 py-2 text-sm bg-geo-border/50 text-white placeholder-gray-500 rounded-lg border border-geo-border focus:border-blue-500 focus:outline-none transition-colors"
                dir="rtl"
              />
            </div>

            {/* Clear filters */}
            {(filters.category || filters.source || filters.location) && (
              <button
                onClick={() => onFilterChange({ category: null, source: null, location: null })}
                className="flex items-center gap-1 text-sm text-gray-400 hover:text-white transition-colors"
              >
                <X size={14} />
                נקה סינון
              </button>
            )}
          </div>
        )}
        </div> {/* Close wrapper div for md:ml-[220px] */}
      </div>

      {/* Error display */}
      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400" dir="rtl">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* News List */}
      <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 md:py-6 pb-20 md:pb-6 md:ml-[220px]">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-gray-400">טוען...</div>
          </div>
        ) : events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500" dir="rtl">
            <Calendar size={64} className="mb-4 opacity-50" />
            <p className="text-lg">לא נמצאו אירועים</p>
          </div>
        ) : (
          <div className="space-y-4 max-w-5xl mx-auto">
            {events.map((event) => (
              <NewsListItem
                key={event.id}
                event={event}
                onClick={() => onEventClick?.(event)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

