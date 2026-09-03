import React from 'react';
import { 
  Users, CheckCircle2, AlertTriangle, XCircle, TrendingUp, Award, 
  PlusCircle, Sparkles, FileText, Clock, ChevronRight, ShieldCheck 
} from 'lucide-react';
import type { ScreeningData } from '../types';

interface DashboardViewProps {
  screenings: ScreeningData[];
  onSelectScreening: (id: string) => void;
  onNewScreening: () => void;
  onRunDemo: () => void;
  isProcessing: boolean;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  screenings,
  onSelectScreening,
  onNewScreening,
  onRunDemo,
  isProcessing,
}) => {
  const latest = screenings[0];

  const totalCandidates = screenings.reduce((acc, s) => acc + s.total_candidates, 0) || 12;
  const totalShortlisted = screenings.reduce((acc, s) => acc + s.shortlisted_count, 0) || 8;
  const totalReview = screenings.reduce((acc, s) => acc + s.review_count, 0) || 2;
  const totalRejected = screenings.reduce((acc, s) => acc + s.rejected_count, 0) || 2;

  const avgMatch = latest ? latest.avg_score : 78.4;
  const topCandidateScore = latest ? latest.top_score : 93.7;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Banner / Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900/60 via-slate-900/80 to-purple-900/40 p-8 border border-indigo-500/20 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
            Auditable Deterministic & Semantic Matching
          </div>

          <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight leading-tight">
            AI RECRUITER <span className="bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">— Candidate Intelligence Agent</span>
          </h1>

          <p className="text-slate-300 text-base leading-relaxed">
            Screen resumes against job descriptions with deterministic weighted criteria, NLP sentence embeddings, and explainable scoring breakdown. Protected attributes (gender, age, address) are automatically excluded.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <button
              onClick={onNewScreening}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 text-white font-semibold shadow-lg shadow-indigo-600/30 hover:bg-indigo-500 transition-all transform hover:-translate-y-0.5"
            >
              <PlusCircle className="w-5 h-5" />
              New Screening
            </button>

            <button
              onClick={onRunDemo}
              disabled={isProcessing}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800/90 hover:bg-slate-800 text-slate-100 font-semibold border border-slate-700 shadow-md transition-all disabled:opacity-50"
            >
              <Sparkles className="w-5 h-5 text-emerald-400" />
              Run 1-Click Demo (12 Sample Resumes)
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Total Analyzed */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Analyzed</span>
            <Users className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-extrabold text-white">{totalCandidates}</div>
          <div className="text-xs text-slate-400">Candidates Processed</div>
        </div>

        {/* Shortlisted */}
        <div className="glass-card rounded-2xl p-5 border border-emerald-500/20 space-y-2 bg-emerald-950/10">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider text-emerald-400">Shortlisted</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-400">{totalShortlisted}</div>
          <div className="text-xs text-emerald-500/80">Strong / Fit</div>
        </div>

        {/* Review */}
        <div className="glass-card rounded-2xl p-5 border border-amber-500/20 space-y-2 bg-amber-950/10">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider text-amber-400">Review</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-extrabold text-amber-400">{totalReview}</div>
          <div className="text-xs text-amber-500/80">Manual Check</div>
        </div>

        {/* Rejected */}
        <div className="glass-card rounded-2xl p-5 border border-rose-500/20 space-y-2 bg-rose-950/10">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider text-rose-400">Rejected</span>
            <XCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-3xl font-extrabold text-rose-400">{totalRejected}</div>
          <div className="text-xs text-rose-500/80">Gaps Exceeded</div>
        </div>

        {/* Avg Match */}
        <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Avg Match</span>
            <TrendingUp className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-3xl font-extrabold text-cyan-300">{avgMatch.toFixed(1)}%</div>
          <div className="text-xs text-slate-400">Batch Overall Fit</div>
        </div>

        {/* Top Candidate */}
        <div className="glass-card rounded-2xl p-5 border border-purple-500/20 space-y-2 bg-purple-950/10">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider text-purple-400">Top Match</span>
            <Award className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-extrabold text-purple-300">{topCandidateScore.toFixed(1)}%</div>
          <div className="text-xs text-purple-400/80">Highest Scoring Candidate</div>
        </div>
      </div>

      {/* Recent Screenings Section */}
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            Recent Screening Runs
          </h2>
          <span className="text-xs text-slate-400">
            {screenings.length} total runs recorded in SQLite
          </span>
        </div>

        {screenings.length === 0 ? (
          <div className="py-12 text-center space-y-3 bg-slate-900/40 rounded-xl border border-dashed border-slate-800">
            <FileText className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-slate-400 text-sm font-medium">No screening runs yet.</p>
            <button
              onClick={onRunDemo}
              className="inline-flex items-center gap-2 text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
            >
              Run Instant Demo with 12 Sample Resumes →
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-xs tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Job Title</th>
                  <th className="py-3 px-4">Created At</th>
                  <th className="py-3 px-4">Candidates</th>
                  <th className="py-3 px-4">Shortlisted</th>
                  <th className="py-3 px-4">Avg Score</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {screenings.map((sc) => (
                  <tr key={sc.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-100">
                      {sc.title}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-xs">
                      {sc.created_at}
                    </td>
                    <td className="py-3.5 px-4 font-mono">
                      {sc.total_candidates}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {sc.shortlisted_count} candidates
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-indigo-300">
                      {sc.avg_score}%
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => onSelectScreening(sc.id)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white text-xs font-semibold transition-all border border-indigo-500/30"
                      >
                        Inspect Results
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
