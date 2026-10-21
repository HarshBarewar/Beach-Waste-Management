import React, { useState, useEffect, useRef } from 'react';
import { Beach } from '../types';
import {
  MapPin,
  Search,
  Filter,
  Star,
  Check,
  Calendar,
  AlertCircle,
  ExternalLink,
  Layers,
  ChevronRight
} from 'lucide-react';
import L from 'leaflet';

interface ExplorerPageProps {
  beaches: Beach[];
  selectedBeach: Beach | null;
  onSelectBeach: (beach: Beach) => void;
  onToggleFavorite: (beachId: string) => void;
  onNavigate: (tab: any) => void;
  comparisonList: string[];
  onToggleComparison: (beachId: string) => void;
}

export const ExplorerPage: React.FC<ExplorerPageProps> = ({
  beaches,
  selectedBeach,
  onSelectBeach,
  onToggleFavorite,
  onNavigate,
  comparisonList,
  onToggleComparison
}) => {
  const [search, setSearch] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('All');
  const [selectedCountry, setSelectedCountry] = useState('All');
  const [activeBeach, setActiveBeach] = useState<Beach | null>(selectedBeach || beaches[0] || null);

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersRef = useRef<{ [key: string]: L.Marker }>({});

  const regions = ['All', ...Array.from(new Set(beaches.map((b) => b.region)))];
  const countries = ['All', ...Array.from(new Set(beaches.map((b) => b.country)))];

  const filteredBeaches = beaches.filter((b) => {
    const matchSearch =
      b.name.toLowerCase().includes(search.toLowerCase()) ||
      b.country.toLowerCase().includes(search.toLowerCase());
    const matchRegion = selectedRegion === 'All' || b.region === selectedRegion;
    const matchCountry = selectedCountry === 'All' || b.country === selectedCountry;
    return matchSearch && matchRegion && matchCountry;
  });

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return; // Already initialized

    const map = L.map(mapContainerRef.current, {
      center: [20.0, 0.0],
      zoom: 2,
      minZoom: 2,
      maxZoom: 16,
      worldCopyJump: true
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors | BeachWaste AI'
    }).addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Markers
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    // Clear previous markers
    Object.values(markersRef.current).forEach((marker) => marker.remove());
    markersRef.current = {};

    filteredBeaches.forEach((beach) => {
      const isSelected = activeBeach?.id === beach.id;

      // Custom HTML Marker Icon
      const customIcon = L.divIcon({
        className: 'custom-leaflet-marker',
        html: `
          <div style="
            width: ${isSelected ? '26px' : '20px'};
            height: ${isSelected ? '26px' : '20px'};
            background-color: ${isSelected ? '#0f766e' : '#0284c7'};
            border: 2px solid white;
            border-radius: 50%;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            transition: all 0.2s ease;
          ">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
            </svg>
          </div>
        `,
        iconSize: [isSelected ? 26 : 20, isSelected ? 26 : 20],
        iconAnchor: [isSelected ? 13 : 10, isSelected ? 13 : 10]
      });

      const marker = L.marker([beach.latitude, beach.longitude], { icon: customIcon }).addTo(map);
      marker.on('click', () => {
        setActiveBeach(beach);
      });

      marker.bindTooltip(`<b>${beach.name}</b><br/>${beach.country}`, {
        direction: 'top',
        offset: [0, -10]
      });

      markersRef.current[beach.id] = marker;
    });

    if (activeBeach && markersRef.current[activeBeach.id]) {
      map.flyTo([activeBeach.latitude, activeBeach.longitude], 6, { duration: 1.2 });
    }
  }, [filteredBeaches, activeBeach]);

  return (
    <div className="space-y-6">
      {/* Top Controls */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search beaches by name or country..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500"
          />
        </div>

        <div className="flex items-center space-x-2">
          {/* Region filter */}
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:outline-none"
          >
            {regions.map((r) => (
              <option key={r} value={r}>
                Region: {r}
              </option>
            ))}
          </select>

          {/* Country filter */}
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-700 focus:outline-none"
          >
            {countries.map((c) => (
              <option key={c} value={c}>
                Country: {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Grid: Interactive Map + Details Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Panel */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-2 shadow-sm flex flex-col h-[560px] relative overflow-hidden">
          <div ref={mapContainerRef} className="w-full h-full rounded-xl" />

          {/* Map Overlay Badge */}
          <div className="absolute bottom-4 left-4 z-20 bg-white/90 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-200 text-[11px] font-medium text-slate-600 shadow-sm flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-teal-600"></span>
            <span>Displaying {filteredBeaches.length} monitored coastal beaches</span>
          </div>
        </div>

        {/* Selected Beach Details Drawer */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex flex-col justify-between h-[560px] overflow-y-auto">
          {activeBeach ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 border border-teal-200 px-2 py-0.5 rounded-full">
                    {activeBeach.region}
                  </span>
                  <button
                    onClick={() => onToggleFavorite(activeBeach.id)}
                    className={`p-1.5 rounded-lg border transition-colors ${
                      activeBeach.is_favorite
                        ? 'bg-amber-50 border-amber-200 text-amber-500'
                        : 'border-slate-200 text-slate-400 hover:text-slate-600'
                    }`}
                  >
                    <Star className="w-4 h-4 fill-current" />
                  </button>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mt-2">{activeBeach.name}</h3>
                <p className="text-xs text-slate-500 font-medium">{activeBeach.country}</p>
              </div>

              {/* Coordinates & Coast Type */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">Coordinates</span>
                  <span className="font-semibold text-slate-800">
                    {activeBeach.latitude.toFixed(3)}°, {activeBeach.longitude.toFixed(3)}°
                  </span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <span className="text-slate-400 block text-[10px]">Coastal Shore Type</span>
                  <span className="font-semibold text-slate-800">{activeBeach.coastal_type}</span>
                </div>
              </div>

              {/* Data Period & Sufficiency */}
              <div className="p-3 rounded-xl bg-teal-50/50 border border-teal-100 space-y-1.5 text-xs">
                <div className="flex items-center space-x-1.5 text-teal-900 font-semibold">
                  <Calendar className="w-3.5 h-3.5 text-teal-600" />
                  <span>Historical Observation Period</span>
                </div>
                <p className="text-slate-600 text-[11px]">
                  {activeBeach.data_start_date || '2021-01-01'} to {activeBeach.data_end_date || '2025-12-01'} ({activeBeach.total_observations} months)
                </p>
                <div className="flex items-center space-x-1 text-emerald-700 text-[11px] font-medium pt-1">
                  <Check className="w-3.5 h-3.5" />
                  <span>Sufficient data available for deep learning forecasting</span>
                </div>
              </div>

              {/* Notes & Description */}
              <div className="text-xs text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100">
                <p>{activeBeach.notes || 'Calibrated demonstration benchmark with seasonal rainfall and tourism signals.'}</p>
              </div>

              {/* Data Provenance Warning */}
              <div className="text-[11px] text-amber-800 bg-amber-50/70 p-2.5 rounded-xl border border-amber-200/80 flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>
                  Geographic location alone cannot predict waste. Predictions rely on historical time-series observations and seasonal covariates.
                </span>
              </div>
            </div>
          ) : (
            <div className="text-center py-16 text-slate-400 text-xs">
              Select a beach pin on the map to inspect details.
            </div>
          )}

          {/* Action Buttons */}
          {activeBeach && (
            <div className="space-y-2 pt-4 border-t border-slate-100">
              <button
                onClick={() => {
                  onSelectBeach(activeBeach);
                  onNavigate('forecasting');
                }}
                className="w-full bg-teal-600 hover:bg-teal-700 text-white font-bold py-2.5 rounded-xl text-xs transition-all shadow-sm flex items-center justify-center space-x-1.5"
              >
                <span>Select for Waste Forecasting</span>
                <ChevronRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => onToggleComparison(activeBeach.id)}
                className={`w-full py-2 rounded-xl text-xs font-semibold border transition-all ${
                  comparisonList.includes(activeBeach.id)
                    ? 'bg-sky-50 border-sky-300 text-sky-800'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                {comparisonList.includes(activeBeach.id)
                  ? '✓ In Beach Comparison List'
                  : '+ Add to Beach Comparison (up to 5)'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
