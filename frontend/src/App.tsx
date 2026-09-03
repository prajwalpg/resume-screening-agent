import { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardView } from './components/DashboardView';
import { NewScreeningView } from './components/NewScreeningView';
import { ProcessingView } from './components/ProcessingView';
import { ResultsView } from './components/ResultsView';
import { CandidateModal } from './components/CandidateModal';
import { CompareView } from './components/CompareView';
import type { 
  CandidateRecord, HealthStatus, ScreeningData 
} from './types';
import { 
  fetchHealth, fetchScreening, fetchScreenings, runCustomScreening, runDemoScreening 
} from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'new-screening' | 'results' | 'compare'>('dashboard');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [screenings, setScreenings] = useState<ScreeningData[]>([]);
  const [activeScreening, setActiveScreening] = useState<ScreeningData | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateRecord | null>(null);
  const [comparedCandidates, setComparedCandidates] = useState<CandidateRecord[]>([]);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [errorToast, setErrorToast] = useState<string | null>(null);

  // Load initial system status and past runs
  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err) => console.warn('Health check failed:', err));

    loadScreeningsList();
  }, []);

  const loadScreeningsList = async () => {
    try {
      const list = await fetchScreenings();
      setScreenings(list);
      if (list.length > 0 && !activeScreening) {
        // Load full details for latest screening
        const latest = await fetchScreening(list[0].id);
        setActiveScreening(latest);
      }
    } catch (err) {
      console.warn('Failed to load screenings list:', err);
    }
  };

  const handleSelectScreening = async (id: string) => {
    try {
      const details = await fetchScreening(id);
      setActiveScreening(details);
      setCurrentTab('results');
    } catch (err) {
      setErrorToast('Could not load screening details');
    }
  };

  const handleRunDemo = async () => {
    setIsProcessing(true);
    setErrorToast(null);

    try {
      const res = await runDemoScreening();
      setActiveScreening(res);
      await loadScreeningsList();
      // Delay slightly to show processing completion
      setTimeout(() => {
        setIsProcessing(false);
        setCurrentTab('results');
      }, 3500);
    } catch (err: any) {
      setIsProcessing(false);
      setErrorToast(err.message || 'Demo screening failed');
    }
  };

  const handleStartCustomScreening = async (jdFile: File | null, resumeFiles: File[]) => {
    setIsProcessing(true);
    setErrorToast(null);

    try {
      const res = await runCustomScreening(jdFile, resumeFiles);
      setActiveScreening(res);
      await loadScreeningsList();
      setTimeout(() => {
        setIsProcessing(false);
        setCurrentTab('results');
      }, 3500);
    } catch (err: any) {
      setIsProcessing(false);
      setErrorToast(err.message || 'Screening execution failed');
    }
  };

  const handleToggleCompare = (cand: CandidateRecord) => {
    setComparedCandidates((prev) => {
      const exists = prev.some((c) => c.id === cand.id);
      if (exists) return prev.filter((c) => c.id !== cand.id);
      if (prev.length >= 4) {
        setErrorToast('Maximum 4 candidates can be compared at once.');
        return prev;
      }
      return [...prev, cand];
    });
  };

  const handleRemoveCompare = (id: string) => {
    setComparedCandidates((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      {/* Navigation Bar */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        health={health}
        selectedCandidateCount={comparedCandidates.length}
        hasActiveScreening={Boolean(activeScreening)}
        onRunDemo={handleRunDemo}
        isProcessing={isProcessing}
      />

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-8">
        {errorToast && (
          <div className="mb-6 p-4 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-200 text-sm flex items-center justify-between shadow-lg">
            <span>{errorToast}</span>
            <button onClick={() => setErrorToast(null)} className="text-xs underline font-bold">
              Dismiss
            </button>
          </div>
        )}

        {isProcessing ? (
          <ProcessingView />
        ) : (
          <>
            {currentTab === 'dashboard' && (
              <DashboardView
                screenings={screenings}
                onSelectScreening={handleSelectScreening}
                onNewScreening={() => setCurrentTab('new-screening')}
                onRunDemo={handleRunDemo}
                isProcessing={isProcessing}
              />
            )}

            {currentTab === 'new-screening' && (
              <NewScreeningView
                onStartCustomScreening={handleStartCustomScreening}
                onRunDemo={handleRunDemo}
                isProcessing={isProcessing}
              />
            )}

            {currentTab === 'results' && activeScreening && (
              <ResultsView
                screening={activeScreening}
                onSelectCandidate={setSelectedCandidate}
                onToggleCompare={handleToggleCompare}
                comparedIds={comparedCandidates.map((c) => c.id)}
                onOpenCompareView={() => setCurrentTab('compare')}
              />
            )}

            {currentTab === 'compare' && (
              <CompareView
                candidates={comparedCandidates}
                onRemoveCandidate={handleRemoveCompare}
                onClearAll={() => setComparedCandidates([])}
                onOpenNewScreening={() => setCurrentTab('new-screening')}
              />
            )}
          </>
        )}
      </main>

      {/* Candidate Details Modal Drawer */}
      {selectedCandidate && (
        <CandidateModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
          onSelectForCompare={handleToggleCompare}
          isCompared={comparedCandidates.some((c) => c.id === selectedCandidate.id)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-400 bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-2">
          <div>
            AI RECRUITER — Resume Screening & Candidate Intelligence Agent
          </div>
          <div>
            Powered by PyMuPDF • Sentence Transformers • Pydantic • FastAPI • Next.js
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
