import { useEffect, useMemo, useRef } from 'react';
import { MapContainer, TileLayer, ZoomControl, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.markercluster';
import { NewsEvent, CATEGORY_CONFIG, EventCategory } from '../types';
import { formatRelativeTime, isRecentEvent } from '../utils/time';

// Fix Leaflet default marker icon issue
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;

interface NewsMapProps {
  events: NewsEvent[];
  selectedEventId?: number | null;
  onEventSelect?: (event: NewsEvent | null) => void;
  mapCenter?: { lat: number; lng: number; zoom: number } | null;
  onMapCenterChange?: () => void;
  resetView?: boolean;
}

// Custom marker icon creator
function createMarkerIcon(category: EventCategory, isRecent: boolean = false): L.DivIcon {
  const config = CATEGORY_CONFIG[category];
  const pulseClass = isRecent ? 'marker-pulse' : '';
  
  return L.divIcon({
    className: 'custom-div-icon',
    html: `
      <div class="custom-marker ${category} ${pulseClass}" style="background: linear-gradient(135deg, ${config.color}, ${config.color}dd);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
          ${getCategoryIconPath(category)}
        </svg>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -20],
  });
}

function getCategoryIconPath(category: EventCategory): string {
  switch (category) {
    case 'military':
      return '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>';
    case 'political':
      return '<path d="M3 22v-3a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v3"/><path d="M12 2l8 4v6c0 2.5-2 5-8 8-6-3-8-5.5-8-8V6l8-4z"/>';
    case 'casualties':
      return '<line x1="12" y1="2" x2="12" y2="22"/><line x1="4" y1="9" x2="20" y2="9"/>';
    case 'infrastructure':
      return '<rect x="4" y="10" width="16" height="12" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4"/><circle cx="12" cy="16" r="1"/>';
    default:
      return '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>';
  }
}

// Marker cluster group component
function MarkerClusterGroup({ events, onEventSelect }: { events: NewsEvent[]; onEventSelect?: (event: NewsEvent | null) => void }) {
  const map = useMap();
  const clusterGroupRef = useRef<L.MarkerClusterGroup | null>(null);
  const hasInitializedRef = useRef(false);

  useEffect(() => {
    // Create cluster group
    const clusterGroup = L.markerClusterGroup({
      chunkedLoading: true,
      spiderfyOnMaxZoom: true,
      showCoverageOnHover: false,
      zoomToBoundsOnClick: true,
      maxClusterRadius: 50,
      iconCreateFunction: (cluster) => {
        const count = cluster.getChildCount();
        let size = 'small';
        if (count > 10) size = 'medium';
        if (count > 25) size = 'large';
        
        return L.divIcon({
          html: `<div><span>${count}</span></div>`,
          className: `marker-cluster marker-cluster-${size}`,
          iconSize: L.point(40, 40),
        });
      },
    });

    clusterGroupRef.current = clusterGroup;

    // Add markers
    events.forEach((event) => {
      if (event.latitude && event.longitude) {
        const isRecent = isRecentEvent(event.timestamp_detected);
        const marker = L.marker([event.latitude, event.longitude], {
          icon: createMarkerIcon(event.category, isRecent),
        });

        // Create popup content
        const config = CATEGORY_CONFIG[event.category];
        const popupContent = `
          <div class="min-w-[250px] max-w-[300px]" dir="rtl">
            <div class="flex items-center gap-2 mb-2">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium" 
                    style="background: ${config.color}20; color: ${config.color};">
                ${config.labelHe}
              </span>
              ${isRecent ? '<span class="text-xs text-green-400 font-medium">● חי</span>' : ''}
            </div>
            ${event.original_title ? `<h4 class="text-sm font-semibold text-white mb-2 leading-snug">${event.original_title}</h4>` : ''}
            <p class="text-xs text-gray-300 mb-3 leading-relaxed">${event.summary_text}</p>
            <div class="flex items-center justify-between text-xs text-gray-400 border-t border-gray-700 pt-2 mt-2">
              <div class="flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                ${event.location_name || 'מיקום לא ידוע'}
              </div>
              <div class="flex items-center gap-1">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
                </svg>
                ${formatRelativeTime(event.timestamp_detected)}
              </div>
            </div>
            ${event.original_url ? `
              <a href="${event.original_url}" target="_blank" rel="noopener noreferrer" 
                 class="mt-3 inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300">
                <span>צפה במקור (${event.source_name})</span>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
            ` : ''}
          </div>
        `;

        marker.bindPopup(popupContent, {
          maxWidth: 320,
          className: 'custom-popup',
        });

        marker.on('click', () => {
          onEventSelect?.(event);
        });

        clusterGroup.addLayer(marker);
      }
    });

    map.addLayer(clusterGroup);

    // Only fit bounds on FIRST load, not on subsequent updates
    if (!hasInitializedRef.current && events.length > 0) {
      const validEvents = events.filter(e => e.latitude && e.longitude);
      if (validEvents.length > 0) {
        const bounds = L.latLngBounds(
          validEvents.map(e => [e.latitude!, e.longitude!] as [number, number])
        );
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
        hasInitializedRef.current = true;
      }
    }

    return () => {
      map.removeLayer(clusterGroup);
    };
  }, [events, map, onEventSelect]);

  return null;
}

// Component to handle map centering when requested
function MapCenterController({ mapCenter, onMapCenterChange }: { 
  mapCenter: { lat: number; lng: number; zoom: number } | null;
  onMapCenterChange?: () => void;
}) {
  const map = useMap();

  useEffect(() => {
    if (mapCenter) {
      map.setView([mapCenter.lat, mapCenter.lng], mapCenter.zoom, {
        animate: true,
        duration: 1,
      });
      // Clear the center request after applying it
      if (onMapCenterChange) {
        onMapCenterChange();
      }
    }
  }, [mapCenter, map, onMapCenterChange]);

  return null;
}

// Component to reset map view to fit all events
function MapResetController({ resetView, events }: { resetView: boolean; events: NewsEvent[] }) {
  const map = useMap();

  useEffect(() => {
    if (resetView && events.length > 0) {
      const validEvents = events.filter(e => e.latitude && e.longitude);
      if (validEvents.length > 0) {
        const bounds = L.latLngBounds(
          validEvents.map(e => [e.latitude!, e.longitude!] as [number, number])
        );
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 6 });
      }
    }
  }, [resetView, events, map]);

  return null;
}

export default function NewsMap({ events, onEventSelect, mapCenter, onMapCenterChange }: NewsMapProps) {
  // Filter events with valid coordinates
  const mappableEvents = useMemo(() => 
    events.filter(e => e.latitude !== null && e.longitude !== null),
    [events]
  );

  // Default center (Middle East region)
  const defaultCenter: [number, number] = [31.5, 34.8];
  const defaultZoom = 7;

  return (
    <MapContainer
      center={defaultCenter}
      zoom={defaultZoom}
      className="w-full h-full"
      zoomControl={false}
      scrollWheelZoom={true}
    >
      {/* Dark-themed map tiles */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
      />
      
      {/* Zoom control positioned in top-left (below floating menu via CSS) */}
      <ZoomControl position="topleft" />
      
      {/* Marker cluster group */}
      <MarkerClusterGroup events={mappableEvents} onEventSelect={onEventSelect} />
      
      {/* Map center controller */}
      <MapCenterController mapCenter={mapCenter} onMapCenterChange={onMapCenterChange} />
    </MapContainer>
  );
}

