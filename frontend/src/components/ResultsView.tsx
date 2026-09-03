import React, { useState } from 'react';
import { 
  Award, CheckCircle2, AlertTriangle, XCircle, Search, 
  FileSpreadsheet, FileJson, FileText, Sparkles 
} from 'lucide-react';
import type { CandidateRecord, ScreeningData } from '../types';
import { getExportUrl } from '../services/api';

interface ResultsViewProps {
  screening: ScreeningData;
  onSelectCandidate: (candidate: CandidateRecord) => void;
  onToggleCompare: (candidate: CandidateRecord) => void;
  comparedIds: string[];
  onOpenCompareView: () => void;
}

export const ResultsView: React.FC<ResultsViewProps> = ({
  screening,
  onSelectCandidate,
  onToggleCompare,
  comparedIds,
}) => {
  const [filterRec, setFilterRec] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortBy, setSortBy] = useState<'score' | 'name' | 'exp'>('score');

  const candidates = screening.candidates || [];

  const strongCount = candidates.filter((c) => c.recommendation === 'STRONG SHORTLIST').length;
  const shortlistCount = candidates.filter((c) => c.recommendation === 'SHORTLIST').length;
  const reviewCount = candidates.filter((c) => c.recommendation === 'REVIEW').length;
  const rejectCount = candidates.filter((c) => c.recommendation === 'REJECT').length;

  // Filtering
  let filtered = candidates.filter((c) => {
    if (filterRec !== 'ALL' && c.recommendation !== filterRec) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        c.name.toLowerCase().includes(q) ||
        (c.result.skills && c.result.skills.some((s) => s.toLowerCase().includes(q)))
      );
    }
    return true;
  });

  // Sorting
  filtered = [...filtered].sort((a, b) => {
    if (sortBy === 'score') return b.score - a.score;
    if (sortBy === 'name') return a.name.localeCompare(b.name);
    if (sortBy === 'exp') return b.result.experience_years - a.result.experience_years;
    return 0;
  });

  const getRankBadge = (rank: number) => {
    if (rank === 1) return <span className="text-xl">🥇</span>;
    if (rank === 2) return <span className="text-xl">🥈</span>;
    if (rank === 3) return <span className="text-xl">🥉</span>;
    return <span className="font-mono text-slate-400 font-bold text-sm">#{rank}</span>;
  };

  const getRecBadgeClass = (rec: string) => {
    switch (rec) {
      case 'STRONG SHORTLIST':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'SHORTLIST':
        return 'bg-teal-500/10 text-teal-300 border-teal-500/30';
      case 'REVIEW':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'REJECT':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header & Job Details Card */}
      <div className="glass-panel rounded-3xl p-6 border border-slate-800 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs text-indigo-400 font-semibold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" />
              AI Candidate Ranking & Intelligence
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              {screening.title}
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Screened {screening.total_candidates} resumes against role requirements • Similarity Backend:{' '}
              <span className="text-emerald-400 font-mono">{screening.similarity_backend}</span>
            </p>
          </div>

          {/* Export Report Actions */}
          <div className="flex flex-wrap items-center gap-2">
            <a
              href={getExportUrl(screening.id, 'csv')}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              Export CSV
            </a>

            <a
              href={getExportUrl(screening.id, 'json')}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-semibold transition-all"
            >
              <FileJson className="w-4 h-4 text-amber-400" />
              Export JSON
            </a>

            <a
              href={getExportUrl(screening.id, 'report')}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/30"
            >
              <FileText className="w-4 h-4" />
              Download Report (.md)
            </a>
          </div>
        </div>

        {/* Breakdown Stats Pill Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
          <div className="p-3 rounded-2xl bg-emerald-950/20 border border-emerald-500/20 flex items-center justify-between">
            <div>
              <div className="text-xs text-emerald-400/80 font-medium">Strong Shortlist</div>
              <div className="text-xl font-extrabold text-emerald-400">{strongCount}</div>
            </div>
            <Award className="w-5 h-5 text-emerald-400" />
          </div>

          <div className="p-3 rounded-2xl bg-teal-950/20 border border-teal-500/20 flex items-center justify-between">
            <div>
              <div className="text-xs text-teal-400/80 font-medium">Shortlist Fit</div>
              <div className="text-xl font-extrabold text-teal-300">{shortlistCount}</div>
            </div>
            <CheckCircle2 className="w-5 h-5 text-teal-400" />
          </div>

          <div className="p-3 rounded-2xl bg-amber-950/20 border border-amber-500/20 flex items-center justify-between">
            <div>
              <div className="text-xs text-amber-400/80 font-medium">Review</div>
              <div className="text-xl font-extrabold text-amber-400">{reviewCount}</div>
            </div>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>

          <div className="p-3 rounded-2xl bg-rose-950/20 border border-rose-500/20 flex items-center justify-between">
            <div>
              <div className="text-xs text-rose-400/80 font-medium">Rejected</div>
              <div className="text-xl font-extrabold text-rose-400">{rejectCount}</div>
            </div>
            <XCircle className="w-5 h-5 text-rose-400" />
          </div>
        </div>
      </div>

      {/* Controls Bar: Filters & Search */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Recommendation Filter Tabs */}
        <div className="flex flex-wrap items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-xs font-medium w-full md:w-auto">
          {[
            { id: 'ALL', label: 'All Candidates', count: candidates.length },
            { id: 'STRONG SHORTLIST', label: 'Strong', count: strongCount },
            { id: 'SHORTLIST', label: 'Shortlist', count: shortlistCount },
            { id: 'REVIEW', label: 'Review', count: reviewCount },
            { id: 'REJECT', label: 'Rejected', count: rejectCount },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterRec(tab.id)}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                filterRec === tab.id
                  ? 'bg-indigo-600 text-white font-bold shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {tab.label} <span className="opacity-70 font-mono">({tab.count})</span>
            </button>
          ))}
        </div>

        {/* Search & Sort */}
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-48">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search candidate or skill..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={sortBy}
            onChange={(e: any) => setSortBy(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
          >
            <option value="score">Sort by Score ▼</option>
            <option value="name">Sort by Name A-Z</option>
            <option value="exp">Sort by Experience</option>
          </select>
        </div>
      </div>

      {/* Candidate Ranking Table */}
      <div className="glass-panel rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 uppercase text-xs tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-4 px-4 text-center w-14">Rank</th>
                <th className="py-4 px-4">Candidate</th>
                <th className="py-4 px-4">Score</th>
                <th className="py-4 px-4">Decision</th>
                <th className="py-4 px-4">Confidence</th>
                <th className="py-4 px-4">Matched Skills</th>
                <th className="py-4 px-4">Exp</th>
                <th className="py-4 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((cand) => {
                const res = cand.result;
                const isCompared = comparedIds.includes(cand.id);

                return (
                  <tr
                    key={cand.id}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => onSelectCandidate(cand)}
                  >
                    {/* Rank */}
                    <td className="py-4 px-4 text-center">
                      {getRankBadge(cand.rank)}
                    </td>

                    {/* Candidate Name */}
                    <td className="py-4 px-4">
                      <div className="font-bold text-slate-100 group-hover:text-indigo-300 transition-colors">
                        {cand.name}
                      </div>
                      <div className="text-[11px] text-slate-500 font-mono truncate max-w-[180px]">
                        {cand.source_file}
                      </div>
                    </td>

                    {/* Score */}
                    <td className="py-4 px-4">
                      <div className="inline-flex items-center gap-1 font-extrabold text-base bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">
                        {cand.score.toFixed(1)}%
                      </div>
                    </td>

                    {/* Decision */}
                    <td className="py-4 px-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${getRecBadgeClass(cand.recommendation)}`}>
                        {cand.recommendation}
                      </span>
                    </td>

                    {/* Confidence */}
                    <td className="py-4 px-4">
                      <span className="px-2 py-0.5 rounded text-xs font-mono bg-slate-900 text-slate-400 border border-slate-800">
                        {cand.confidence}
                      </span>
                    </td>

                    {/* Matched skills count */}
                    <td className="py-4 px-4">
                      <div className="text-xs text-slate-300">
                        <span className="text-emerald-400 font-bold">{res.matched_required.length}</span> matched
                        {res.missing_required.length > 0 && (
                          <span className="text-rose-400 font-medium ml-1">
                            ({res.missing_required.length} gap)
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Experience */}
                    <td className="py-4 px-4 text-xs font-mono text-slate-300">
                      {res.experience_years} yrs
                    </td>

                    {/* Actions */}
                    <td className="py-4 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => onToggleCompare(cand)}
                          className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition-all ${
                            isCompared
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                              : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-700'
                          }`}
                        >
                          {isCompared ? 'Compared ✓' : '+ Compare'}
                        </button>

                        <button
                          onClick={() => onSelectCandidate(cand)}
                          className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-sm"
                        >
                          Details →
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
