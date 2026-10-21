import React from 'react';
import { Waves, Sparkles, MapPin, Cpu, BookOpen, Sun, Moon } from 'lucide-react';
import { Beach } from '../types';

interface NavbarProps {
  selectedBeach: Beach | null;
  onOpenBeachPicker: () => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  selectedBeach,
  onOpenBeachPicker,
  darkMode,
  onToggleDarkMode
}) => {
  return (
    <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur border-b border-slate-200 px-6 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
          <Waves className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-bold text-lg text-slate-900 tracking-tight">BeachWaste <span className="text-teal-600">AI</span></span>
            <span className="text-[10px] font-semibold bg-teal-50 text-teal-700 border border-teal-200 px-2 py-0.5 rounded-full flex items-center">
              <Sparkles className="w-2.5 h-2.5 mr-1" /> DL Lab Edition
            </span>
          </div>
          <p className="text-xs text-slate-500 hidden sm:block">Deep Learning Coastal Waste Prediction & Cost Estimation</p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Selected beach quick selector */}
        <button
          onClick={onOpenBeachPicker}
          className="flex items-center space-x-2 bg-slate-100 hover:bg-slate-200/80 text-slate-700 px-3.5 py-1.5 rounded-lg border border-slate-200 text-xs font-medium transition-all"
        >
          <MapPin className="w-3.5 h-3.5 text-teal-600" />
          <span className="font-semibold text-slate-900 truncate max-w-[150px] sm:max-w-[200px]">
            {selectedBeach ? selectedBeach.name : 'Select Beach'}
          </span>
          {selectedBeach && (
            <span className="text-[10px] bg-teal-100 text-teal-800 px-1.5 py-0.5 rounded font-bold">
              {selectedBeach.country}
            </span>
          )}
        </button>

        {/* Compute Status indicator */}
        <div className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-xs font-medium">
          <Cpu className="w-3.5 h-3.5 text-emerald-600" />
          <span>PyTorch Ready</span>
        </div>

        {/* Mode toggle */}
        <button
          onClick={onToggleDarkMode}
          className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 border border-slate-200 transition-colors"
          title="Toggle Theme"
        >
          {darkMode ? <Sun className="w-4 h-4 text-amber-500" /> : <Moon className="w-4 h-4 text-slate-600" />}
        </button>
      </div>
    </header>
  );
};
