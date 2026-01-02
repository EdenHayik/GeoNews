import { useState, useEffect } from 'react';
import { 
  FileText, 
  Sparkles, 
  Calendar, 
  ChevronDown, 
  Loader2, 
  Clock,
  AlertCircle,
  TrendingUp
} from 'lucide-react';

const API_BASE = '/api';

interface RecapSource {
  source_name: string;
  event_count: number;
  latest_event: string | null;
}

interface RecapSection {
  heading: string;
  items: string[];
}

interface DailyRecapData {
  source_name: string;
  hours: number;
  title: string;
  executive_summary: string;
  sections: RecapSection[];
  insights: string | null;
  total_events: number;
  time_range: string;
  generated_at: string;
}

interface DailyRecapProps {
  onClose: () => void;
}

export default function DailyRecap({ onClose }: DailyRecapProps) {
  const [sources, setSources] = useState<RecapSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingFor, setGeneratingFor] = useState<string | null>(null);
  const [recaps, setRecaps] = useState<Map<string, DailyRecapData>>(new Map());
  const [expandedRecap, setExpandedRecap] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/recap/sources`);
      const data = await response.json();
      setSources(data.sources || []);
    } catch (err) {
      console.error('Error fetching sources:', err);
      setError('שגיאה בטעינת רשימת המקורות');
    } finally {
      setLoading(false);
    }
  };

  const generateRecap = async (sourceName: string, hours: number = 24) => {
    try {
      setGeneratingFor(sourceName);
      setError(null);
      
      const response = await fetch(
        `${API_BASE}/recap/generate?source_name=${encodeURIComponent(sourceName)}&hours=${hours}`,
        { method: 'POST' }
      );
      
      const data = await response.json();
      
      if (data.success && data.recap) {
        setRecaps(prev => new Map(prev).set(sourceName, data.recap));
        setExpandedRecap(sourceName);
      } else {
        setError(`שגיאה ביצירת הסיכום עבור ${sourceName}`);
      }
    } catch (err) {
      console.error('Error generating recap:', err);
      setError(`שגיאה ביצירת הסיכום עבור ${sourceName}`);
    } finally {
      setGeneratingFor(null);
    }
  };

  const toggleRecap = (sourceName: string) => {
    setExpandedRecap(expandedRecap === sourceName ? null : sourceName);
  };

  return (
    <div className="h-full w-full bg-geo-darker overflow-hidden flex flex-col animate-slide-up">
      {/* Header */}
      <div className="bg-geo-panel border-b border-geo-border px-4 md:px-6 py-3 md:py-4 flex-shrink-0 md:ml-[220px]">
        <div className="flex items-center justify-between" dir="rtl">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <FileText className="text-blue-400" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                סיכום יומי
                <Sparkles className="text-yellow-400" size={20} />
              </h1>
              <p className="text-sm text-gray-400">
                יצירת סיכומים מבוססי AI לפי מקור
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-geo-dark-light hover:bg-geo-border text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <span>חזרה למפה</span>
          </button>
        </div>
      </div>

      {/* Error display */}
      {error && (
        <div className="mx-6 mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400" dir="rtl">
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 md:px-6 py-4 md:py-6 pb-20 md:pb-6 md:ml-[220px]">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="animate-spin text-blue-400" size={48} />
          </div>
        ) : sources.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500" dir="rtl">
            <Calendar size={64} className="mb-4 opacity-50" />
            <p className="text-lg">לא נמצאו מקורות עם אירועים ב-24 השעות האחרונות</p>
          </div>
        ) : (
          <div className="space-y-4 max-w-5xl mx-auto">
            {sources.map((source) => {
              const existingRecap = recaps.get(source.source_name);
              const isExpanded = expandedRecap === source.source_name;
              const isGenerating = generatingFor === source.source_name;

              return (
                <div
                  key={source.source_name}
                  className="bg-geo-panel border border-geo-border rounded-xl overflow-hidden transition-all hover:border-blue-500/30"
                >
                  {/* Source Header */}
                  <div className="p-5 border-b border-geo-border">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4" dir="rtl">
                        <div className="p-3 bg-blue-500/10 rounded-lg">
                          <FileText className="text-blue-400" size={24} />
                        </div>
                        <div>
                          <h3 className="text-xl font-semibold text-white">
                            {source.source_name}
                          </h3>
                          <p className="text-sm text-gray-400 flex items-center gap-2 mt-1">
                            <Calendar size={14} />
                            {source.event_count} אירועים ב-24 השעות האחרונות
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {existingRecap && (
                          <button
                            onClick={() => toggleRecap(source.source_name)}
                            className="px-4 py-2 bg-geo-dark-light hover:bg-geo-border text-gray-300 hover:text-white rounded-lg transition-colors flex items-center gap-2"
                          >
                            <span>{isExpanded ? 'הסתר' : 'הצג'}</span>
                            <ChevronDown
                              size={16}
                              className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                            />
                          </button>
                        )}
                        <button
                          onClick={() => generateRecap(source.source_name)}
                          disabled={isGenerating}
                          className="px-5 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2 font-medium"
                        >
                          {isGenerating ? (
                            <>
                              <Loader2 className="animate-spin" size={16} />
                              <span>יוצר סיכום...</span>
                            </>
                          ) : (
                            <>
                              <Sparkles size={16} />
                              <span>{existingRecap ? 'צור מחדש' : 'צור סיכום'}</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Recap Content */}
                  {existingRecap && isExpanded && (
                    <div className="p-6 space-y-6 animate-slide-up" dir="rtl">
                      {/* Title */}
                      <div className="border-b border-geo-border pb-4">
                        <h2 className="text-2xl font-bold text-white mb-2">
                          {existingRecap.title}
                        </h2>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span className="flex items-center gap-1">
                            <Clock size={14} />
                            {existingRecap.time_range}
                          </span>
                          <span>•</span>
                          <span>{existingRecap.total_events} אירועים</span>
                        </div>
                      </div>

                      {/* Executive Summary */}
                      <div className="bg-blue-500/5 border border-blue-500/20 rounded-lg p-5">
                        <h3 className="text-lg font-semibold text-blue-400 mb-3 flex items-center gap-2">
                          <Sparkles size={18} />
                          סיכום מנהלים
                        </h3>
                        <p className="text-gray-200 leading-relaxed">
                          {existingRecap.executive_summary}
                        </p>
                      </div>

                      {/* Sections */}
                      {existingRecap.sections && existingRecap.sections.length > 0 && (
                        <div className="space-y-4">
                          <h3 className="text-lg font-semibold text-white">
                            התפתחויות עיקריות
                          </h3>
                          {existingRecap.sections.map((section, idx) => (
                            <div
                              key={idx}
                              className="bg-geo-dark/50 rounded-lg p-5 border border-geo-border"
                            >
                              <h4 className="text-md font-semibold text-blue-300 mb-3">
                                {section.heading}
                              </h4>
                              <ul className="space-y-2">
                                {section.items.map((item, itemIdx) => (
                                  <li
                                    key={itemIdx}
                                    className="text-gray-300 leading-relaxed flex items-start gap-2"
                                  >
                                    <span className="text-blue-400 mt-1">•</span>
                                    <span>{item}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Insights */}
                      {existingRecap.insights && (
                        <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-lg p-5">
                          <h3 className="text-lg font-semibold text-yellow-400 mb-3 flex items-center gap-2">
                            <TrendingUp size={18} />
                            מגמות ותובנות
                          </h3>
                          <p className="text-gray-200 leading-relaxed">
                            {existingRecap.insights}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

