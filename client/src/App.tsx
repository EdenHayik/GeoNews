import { useState, useCallback } from 'react';
import NewsMap from './components/NewsMap';
import NewsSidebar from './components/NewsSidebar';
import DailyRecap from './components/DailyRecap';
import NewsList from './components/NewsList';
import { useNewsEvents } from './hooks/useNewsEvents';
import { NewsEvent, FilterState } from './types';
import { Globe, AlertTriangle, FileText, Map, List } from 'lucide-react';

type ViewMode = 'map' | 'recap' | 'list';

function App() {
  // View mode state
  const [viewMode, setViewMode] = useState<ViewMode>('map');

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    hours: 24,
    category: null,
    source: null,
    location: null,
  });

  // Selected event (for map-sidebar sync)
  const [selectedEventId, setSelectedEventId] = useState<number | null>(null);
  
  // Map center state (for zooming to specific locations)
  const [mapCenter, setMapCenter] = useState<{ lat: number; lng: number; zoom: number } | null>(null);
  const [resetMapView, setResetMapView] = useState(false);

  // Fetch events
  const { events, loading, error, total, refetch, lastUpdated } = useNewsEvents(filters);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilters: Partial<FilterState>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  // Handle event selection
  const handleEventSelect = useCallback((event: NewsEvent | null) => {
    setSelectedEventId(event?.id ?? null);
  }, []);

  // Handle sidebar event click - show on map
  const handleSidebarEventClick = useCallback((event: NewsEvent) => {
    setSelectedEventId(event.id);
    if (event.latitude && event.longitude) {
      setMapCenter({ lat: event.latitude, lng: event.longitude, zoom: 6 });
      setViewMode('map');
    }
  }, []);

  // Handle home button click - reset map to default view
  const handleHomeClick = useCallback(() => {
    setViewMode('map');
    setSelectedEventId(null);
    setMapCenter(null);
    setResetMapView(true);
    setTimeout(() => setResetMapView(false), 100);
  }, []);

  return (
    <div className="h-screen w-screen flex flex-col bg-geo-darker overflow-hidden relative">
      {/* Desktop Navigation - Hidden on Mobile */}
      <div className="hidden md:flex absolute top-4 left-4 z-[1001] flex-col gap-2">
        {/* Logo/Brand - Clickable to reset map */}
        <button
          onClick={handleHomeClick}
          className="flex items-center gap-2 px-3 py-2 bg-geo-panel/90 backdrop-blur-sm rounded-xl border border-geo-border shadow-lg hover:bg-geo-dark-light transition-colors"
        >
          <Globe className="text-blue-400" size={22} />
          <span className="text-lg font-semibold text-white font-display tracking-tight">
            GeoNews
          </span>
        </button>

        {/* Navigation Buttons */}
        <div className="flex flex-col gap-1 bg-geo-panel/90 backdrop-blur-sm rounded-xl border border-geo-border shadow-lg p-2">
          <button
            onClick={() => setViewMode('map')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              viewMode === 'map'
                ? 'bg-blue-500 text-white shadow-md'
                : 'text-gray-300 hover:text-white hover:bg-geo-dark-light'
            }`}
            title="מפה"
          >
            <Map size={18} />
            <span className="text-sm font-medium">מפה</span>
          </button>
          
          <button
            onClick={() => setViewMode('list')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              viewMode === 'list'
                ? 'bg-blue-500 text-white shadow-md'
                : 'text-gray-300 hover:text-white hover:bg-geo-dark-light'
            }`}
            title="רשימת חדשות"
          >
            <List size={18} />
            <span className="text-sm font-medium">רשימת חדשות</span>
          </button>
          
          <button
            onClick={() => setViewMode('recap')}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
              viewMode === 'recap'
                ? 'bg-blue-500 text-white shadow-md'
                : 'text-gray-300 hover:text-white hover:bg-geo-dark-light'
            }`}
            title="סיכום יומי"
          >
            <FileText size={18} />
            <span className="text-sm font-medium">סיכום יומי</span>
          </button>
        </div>
      </div>

      {/* Mobile Header - Only visible on mobile */}
      <div className="md:hidden flex-shrink-0 flex items-center justify-between px-4 py-3 bg-geo-panel border-b border-geo-border safe-top">
        <button
          onClick={handleHomeClick}
          className="flex items-center gap-2"
        >
          <Globe className="text-blue-400" size={20} />
          <span className="text-base font-semibold text-white font-display">GeoNews</span>
        </button>
        <span className="text-xs text-gray-400">{total} אירועים</span>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 relative overflow-hidden">
        {/* Map View */}
        <div
          className={`absolute inset-0 flex flex-col transition-all duration-300 ${
            viewMode === 'map'
              ? 'opacity-100 translate-x-0'
              : 'opacity-0 translate-x-full pointer-events-none'
          }`}
        >
          {/* Mobile: Full map, Desktop: Map + Sidebar */}
          <div className="flex-1 flex flex-col md:flex-row h-full">
            {/* Map section */}
            <main className="relative flex-1 h-full md:w-[70%]">
              {/* Connection error overlay */}
              {error && (
                <div className="absolute top-4 left-1/2 -translate-x-1/2 z-[1000] flex items-center gap-2 px-3 py-2 bg-red-500/90 backdrop-blur-sm rounded-xl text-white text-xs">
                  <AlertTriangle size={14} />
                  <span>בעיית חיבור</span>
                </div>
              )}

              {/* Map */}
              <NewsMap 
                events={events}
                selectedEventId={selectedEventId}
                onEventSelect={handleEventSelect}
                mapCenter={mapCenter}
                onMapCenterChange={() => setMapCenter(null)}
                resetView={resetMapView}
              />

              {/* Stats overlay - Hidden on mobile */}
              <div className="hidden md:flex absolute bottom-4 left-4 z-[1000] items-center gap-4 text-xs text-gray-400">
                <span className="px-2 py-1 bg-geo-panel/80 backdrop-blur-sm rounded-md border border-geo-border">
                  {events.filter(e => e.latitude && e.longitude).length} מיקומים במפה
                </span>
              </div>
            </main>

            {/* Sidebar - Desktop only (mobile uses bottom sheet or list view) */}
            <aside className="hidden md:block md:w-[30%] md:min-w-[360px] md:max-w-[480px] h-full">
              <NewsSidebar
                events={events}
                loading={loading}
                error={error}
                total={total}
                filters={filters}
                onFilterChange={handleFilterChange}
                onEventClick={handleSidebarEventClick}
                lastUpdated={lastUpdated}
                onRefresh={refetch}
              />
            </aside>
          </div>
        </div>

        {/* Recap View */}
        <div
          className={`absolute inset-0 transition-all duration-300 ${
            viewMode === 'recap'
              ? 'opacity-100 translate-x-0'
              : 'opacity-0 -translate-x-full pointer-events-none'
          }`}
        >
          {viewMode === 'recap' && <DailyRecap onClose={() => setViewMode('map')} />}
        </div>

        {/* List View */}
        <div
          className={`absolute inset-0 transition-all duration-300 ${
            viewMode === 'list'
              ? 'opacity-100 translate-y-0'
              : 'opacity-0 translate-y-full pointer-events-none'
          }`}
        >
          {viewMode === 'list' && (
            <NewsList
              events={events}
              loading={loading}
              error={error}
              total={total}
              filters={filters}
              onFilterChange={handleFilterChange}
              onEventClick={handleSidebarEventClick}
            />
          )}
        </div>
      </div>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden flex-shrink-0 flex items-center justify-around bg-geo-panel border-t border-geo-border safe-bottom px-2 py-1">
        <button
          onClick={() => setViewMode('map')}
          className={`flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all ${
            viewMode === 'map'
              ? 'text-blue-400 bg-blue-500/10'
              : 'text-gray-400'
          }`}
        >
          <Map size={22} />
          <span className="text-[10px] font-medium">מפה</span>
        </button>
        
        <button
          onClick={() => setViewMode('list')}
          className={`flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all ${
            viewMode === 'list'
              ? 'text-blue-400 bg-blue-500/10'
              : 'text-gray-400'
          }`}
        >
          <List size={22} />
          <span className="text-[10px] font-medium">חדשות</span>
        </button>
        
        <button
          onClick={() => setViewMode('recap')}
          className={`flex flex-col items-center gap-1 px-4 py-2 rounded-xl transition-all ${
            viewMode === 'recap'
              ? 'text-blue-400 bg-blue-500/10'
              : 'text-gray-400'
          }`}
        >
          <FileText size={22} />
          <span className="text-[10px] font-medium">סיכום</span>
        </button>
      </nav>
    </div>
  );
}

export default App;