import React from 'react';
import { Bot, FileText, LayoutDashboard, Sparkles, Scale, Cpu } from 'lucide-react';
import type { HealthStatus } from '../types';

interface NavbarProps {
  currentTab: 'dashboard' | 'new-screening' | 'results' | 'compare';
  setCurrentTab: (tab: 'dashboard' | 'new-screening' | 'results' | 'compare') => void;
  health: HealthStatus | null;
  selectedCandidateCount: number;
  hasActiveScreening: boolean;
  onRunDemo: () => void;
  isProcessing: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  health,
  selectedCandidateCount,
  hasActiveScreening,
  onRunDemo,
  isProcessing,
}) => {
  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-slate-800/80 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo & Brand */}
        <div 
          onClick={() => setCurrentTab('dashboard')}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Bot className="w-5 h-5 text-indigo-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg text-slate-100 tracking-tight flex items-center gap-1.5">
                AI RECRUITER
                <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-medium">
                  AGENT v1.0
                </span>
              </h1>
            </div>
            <p className="text-xs text-slate-400">Resume Screening & Candidate Intelligence</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setCurrentTab('dashboard')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === 'dashboard'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Dashboard
          </button>

          <button
            onClick={() => setCurrentTab('new-screening')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              currentTab === 'new-screening'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <FileText className="w-4 h-4" />
            New Screening
          </button>

          {hasActiveScreening && (
            <button
              onClick={() => setCurrentTab('results')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'results'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Sparkles className="w-4 h-4 text-emerald-400" />
              Results
            </button>
          )}

          <button
            onClick={() => setCurrentTab('compare')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all relative ${
              currentTab === 'compare'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Scale className="w-4 h-4" />
            Compare
            {selectedCandidateCount > 0 && (
              <span className="ml-1 px-1.5 py-0.5 text-xs bg-emerald-500 text-slate-950 font-bold rounded-full">
                {selectedCandidateCount}
              </span>
            )}
          </button>
        </nav>

        {/* Status & Quick Action */}
        <div className="flex items-center gap-3">
          {health && (
            <div className="hidden lg:flex items-center gap-2 text-xs bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 text-slate-300">
              <Cpu className="w-3.5 h-3.5 text-indigo-400" />
              <span>NLP Engine:</span>
              <span className="font-mono text-emerald-400 font-medium">
                {health.similarity_backend.includes('sentence-transformer')
                  ? 'MiniLM Embeddings'
                  : 'TF-IDF Cosine'}
              </span>
            </div>
          )}

          <button
            onClick={onRunDemo}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-slate-950 font-semibold text-sm hover:from-emerald-400 hover:to-teal-500 transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4 fill-slate-950" />
            <span>Instant Demo</span>
          </button>
        </div>
      </div>
    </header>
  );
};
