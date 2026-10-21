import React, { useState } from 'react';
import { Beach } from '../types';
import { Search, MapPin, Check, Star, Filter, X } from 'lucide-react';

interface BeachSelectorModalProps {
  isOpen: boolean;
  onClose: () => void;
  beaches: Beach[];
  selectedBeach: Beach | null;
  onSelectBeach: (beach: Beach) => void;
  onToggleFavorite: (beachId: string) => void;
}

export const BeachSelectorModal: React.FC<BeachSelectorModalProps> = ({
  isOpen,
  onClose,
  beaches,
  selectedBeach,
  onSelectBeach,
  onToggleFavorite
}) => {
  const [search, setSearch] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('All');

  if (!isOpen) return null;

  const regions = ['All', ...Array.from(new Set(beaches.map((b) => b.region)))];

  const filtered = beaches.filter((b) => {
    const matchSearch =
      b.name.toLowerCase().includes(search.toLowerCase()) ||
      b.country.toLowerCase().includes(search.toLowerCase());
    const matchRegion = selectedRegion === 'All' || b.region === selectedRegion;
    return matchSearch && matchRegion;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-teal-50 border border-teal-200 flex items-center justify-center text-teal-600">
              <MapPin className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Select Global Beach</h3>
              <p className="text-xs text-slate-500">Explore historical data & generate deep learning waste forecasts</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Search & Region Filter */}
        <div className="p-4 border-b border-slate-100 bg-slate-50/50 space-y-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search beach name or country (e.g., Bondi, Brazil, Nice)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/30 focus:border-teal-500 transition-all placeholder:text-slate-400"
              autoFocus
            />
          </div>

          <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400 mr-1 shrink-0" />
            {regions.map((reg) => (
              <button
                key={reg}
                onClick={() => setSelectedRegion(reg)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedRegion === reg
                    ? 'bg-teal-600 text-white shadow-sm'
                    : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                {reg}
              </button>
            ))}
          </div>
        </div>

        {/* Beach List */}
        <div className="overflow-y-auto p-4 space-y-2 divide-y divide-slate-100">
          {filtered.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">
              No beaches found matching "{search}".
            </div>
          ) : (
            filtered.map((beach) => {
              const isSelected = selectedBeach?.id === beach.id;
              return (
                <div
                  key={beach.id}
                  onClick={() => {
                    onSelectBeach(beach);
                    onClose();
                  }}
                  className={`pt-2.5 first:pt-0 flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-teal-50/70 border border-teal-200'
                      : 'hover:bg-slate-50 border border-transparent'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-slate-900 text-xs">{beach.name}</span>
                      <span className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full border border-slate-200">
                        {beach.country}
                      </span>
                      {beach.sufficient_data_for_forecasting && (
                        <span className="text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 px-1.5 py-0.5 rounded">
                          DL Ready ({beach.total_observations} mos)
                        </span>
                      )}
                    </div>
                    <div className="flex items-center space-x-3 text-[11px] text-slate-500">
                      <span>{beach.region}</span>
                      <span>•</span>
                      <span>{beach.coastal_type}</span>
                      <span>•</span>
                      <span>
                        {beach.latitude.toFixed(2)}°, {beach.longitude.toFixed(2)}°
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggleFavorite(beach.id);
                      }}
                      className={`p-1.5 rounded-lg border transition-colors ${
                        beach.is_favorite
                          ? 'bg-amber-50 border-amber-200 text-amber-500'
                          : 'border-slate-200 text-slate-300 hover:text-slate-500'
                      }`}
                    >
                      <Star className="w-3.5 h-3.5 fill-current" />
                    </button>
                    {isSelected && (
                      <div className="w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center">
                        <Check className="w-3.5 h-3.5" />
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
