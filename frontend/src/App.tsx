import React, { useState, useEffect } from 'react';
import { Beach, ForecastResponse } from './types';
import { fetchBeaches, fetchBeachDetail, generateForecast, toggleFavorite } from './services/api';
import { Navbar } from './components/Navbar';
import { Sidebar, TabType } from './components/Sidebar';
import { BeachSelectorModal } from './components/BeachSelectorModal';

import { OverviewPage } from './pages/OverviewPage';
import { ExplorerPage } from './pages/ExplorerPage';
import { ForecastingPage } from './pages/ForecastingPage';
import { CompositionPage } from './pages/CompositionPage';
import { CostsPage } from './pages/CostsPage';
import { ComparisonPage } from './pages/ComparisonPage';
import { TrainingPage } from './pages/TrainingPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { DatasetsPage } from './pages/DatasetsPage';
import { ReportsPage } from './pages/ReportsPage';
import { AboutPage } from './pages/AboutPage';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [beaches, setBeaches] = useState<Beach[]>([]);
  const [selectedBeach, setSelectedBeach] = useState<Beach | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [comparisonList, setComparisonList] = useState<string[]>([]);
  const [currency, setCurrency] = useState('USD');
  const [isBeachModalOpen, setIsBeachModalOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(true);

  // Load beaches on startup
  useEffect(() => {
    fetchBeaches()
      .then((data) => {
        setBeaches(data);
        if (data.length > 0) {
          // Select South Beach, Miami or first beach as default
          const initial = data.find((b) => b.id === 'beach_miami_south') || data[0];
          handleSelectBeach(initial);
          // Set initial comparison list to first 3 beaches
          setComparisonList(data.slice(0, 3).map((b) => b.id));
        }
      })
      .catch((err) => console.error('Failed to load beaches:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectBeach = async (beach: Beach) => {
    try {
      const detailed = await fetchBeachDetail(beach.id);
      setSelectedBeach(detailed);
      // Automatically generate initial forecast
      const fc = await generateForecast({
        beach_id: beach.id,
        model_type: 'lstm',
        horizon_months: 6,
        currency: currency
      });
      setForecast(fc);
    } catch (err) {
      console.error('Failed to load beach details/forecast:', err);
      setSelectedBeach(beach);
    }
  };

  const handleToggleFavorite = async (beachId: string) => {
    try {
      const updated = await toggleFavorite(beachId);
      setBeaches((prev) =>
        prev.map((b) => (b.id === beachId ? { ...b, is_favorite: updated.is_favorite } : b))
      );
      if (selectedBeach?.id === beachId) {
        setSelectedBeach({ ...selectedBeach, is_favorite: updated.is_favorite });
      }
    } catch (err) {
      console.error('Favorite toggle failed', err);
    }
  };

  const handleToggleComparison = (beachId: string) => {
    setComparisonList((prev) => {
      if (prev.includes(beachId)) {
        return prev.filter((id) => id !== beachId);
      } else {
        if (prev.length >= 5) return prev;
        return [...prev, beachId];
      }
    });
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    if (!darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'dark bg-slate-950 text-slate-100' : 'bg-slate-50 text-slate-800'}`}>
      <Navbar
        selectedBeach={selectedBeach}
        onOpenBeachPicker={() => setIsBeachModalOpen(true)}
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {activeTab === 'overview' && (
            <OverviewPage
              beach={selectedBeach}
              forecast={forecast}
              onNavigate={setActiveTab}
            />
          )}

          {activeTab === 'explorer' && (
            <ExplorerPage
              beaches={beaches}
              selectedBeach={selectedBeach}
              onSelectBeach={handleSelectBeach}
              onToggleFavorite={handleToggleFavorite}
              onNavigate={setActiveTab}
              comparisonList={comparisonList}
              onToggleComparison={handleToggleComparison}
            />
          )}

          {activeTab === 'forecasting' && (
            <ForecastingPage
              beach={selectedBeach}
              forecast={forecast}
              onUpdateForecast={setForecast}
              currency={currency}
            />
          )}

          {activeTab === 'composition' && (
            <CompositionPage
              beach={selectedBeach}
              forecast={forecast}
            />
          )}

          {activeTab === 'costs' && (
            <CostsPage
              beach={selectedBeach}
              forecast={forecast}
              currency={currency}
              onCurrencyChange={setCurrency}
            />
          )}

          {activeTab === 'comparison' && (
            <ComparisonPage
              beaches={beaches}
              comparisonList={comparisonList}
              onToggleComparison={handleToggleComparison}
              currency={currency}
            />
          )}

          {activeTab === 'training' && <TrainingPage />}

          {activeTab === 'evaluation' && <EvaluationPage />}

          {activeTab === 'datasets' && <DatasetsPage />}

          {activeTab === 'reports' && (
            <ReportsPage
              beach={selectedBeach}
              forecast={forecast}
              currency={currency}
            />
          )}

          {activeTab === 'about' && <AboutPage />}
        </main>
      </div>

      <BeachSelectorModal
        isOpen={isBeachModalOpen}
        onClose={() => setIsBeachModalOpen(false)}
        beaches={beaches}
        selectedBeach={selectedBeach}
        onSelectBeach={handleSelectBeach}
        onToggleFavorite={handleToggleFavorite}
      />
    </div>
  );
};

export default App;
