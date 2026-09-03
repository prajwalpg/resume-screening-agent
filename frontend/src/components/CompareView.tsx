import React from 'react';
import { Scale, X } from 'lucide-react';
import type { CandidateRecord } from '../types';

interface CompareViewProps {
  candidates: CandidateRecord[];
  onRemoveCandidate: (id: string) => void;
  onClearAll: () => void;
  onOpenNewScreening: () => void;
}

export const CompareView: React.FC<CompareViewProps> = ({
  candidates,
  onRemoveCandidate,
  onClearAll,
}) => {
  if (candidates.length === 0) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center space-y-4 glass-panel rounded-3xl border border-slate-800 p-8">
        <Scale className="w-12 h-12 text-slate-600 mx-auto" />
        <h2 className="text-xl font-bold text-slate-200">No Candidates Selected for Comparison</h2>
        <p className="text-slate-400 text-sm">
          Select 2 to 4 candidates from the Results Dashboard by clicking "+ Compare" to view side-by-side score breakdowns, skill matches, and hiring recommendations.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <Scale className="w-6 h-6 text-indigo-400" />
            CANDIDATE COMPARISON MATRIX
          </h1>
          <p className="text-xs text-slate-400">Comparing {candidates.length} candidates side-by-side</p>
        </div>

        <button
          onClick={onClearAll}
          className="text-xs text-rose-400 hover:underline font-semibold"
        >
          Clear Matrix
        </button>
      </div>

      {/* Comparison Table */}
      <div className="glass-panel rounded-3xl border border-slate-800 overflow-x-auto shadow-2xl">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-4 px-6 font-bold text-xs uppercase tracking-wider text-indigo-400 w-48">
                Metric / Candidate
              </th>
              {candidates.map((cand) => (
                <th key={cand.id} className="py-4 px-6 text-slate-100 font-bold text-base min-w-[200px]">
                  <div className="flex items-center justify-between">
                    <div>
                      <div>{cand.name}</div>
                      <div className="text-xs font-mono text-slate-400 font-normal">Rank #{cand.rank}</div>
                    </div>
                    <button
                      onClick={() => onRemoveCandidate(cand.id)}
                      className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-slate-800 transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/80">
            {/* Final Overall Score */}
            <tr className="bg-indigo-950/20">
              <td className="py-4 px-6 font-bold text-slate-200">Overall Score</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6">
                  <div className="text-2xl font-extrabold text-indigo-300">
                    {cand.score.toFixed(1)}%
                  </div>
                </td>
              ))}
            </tr>

            {/* Recommendation */}
            <tr>
              <td className="py-4 px-6 font-semibold text-slate-300">Recommendation</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6">
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                    {cand.recommendation}
                  </span>
                </td>
              ))}
            </tr>

            {/* Required Skills Score */}
            <tr>
              <td className="py-4 px-6 font-semibold text-slate-300">Required Skills %</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6 font-mono font-bold text-emerald-400">
                  {(cand.result.breakdown.required_skills * 100).toFixed(0)}%
                </td>
              ))}
            </tr>

            {/* Work Experience */}
            <tr>
              <td className="py-4 px-6 font-semibold text-slate-300">Experience Years</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6">
                  <span className="font-semibold text-slate-100">{cand.result.experience_years} yrs</span>
                  <span className="text-xs text-slate-400 block">
                    (Req: {cand.result.required_experience} yrs)
                  </span>
                </td>
              ))}
            </tr>

            {/* Education Score */}
            <tr>
              <td className="py-4 px-6 font-semibold text-slate-300">Education Score</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6 font-mono text-purple-300">
                  {(cand.result.breakdown.education * 100).toFixed(0)}%
                </td>
              ))}
            </tr>

            {/* NLP Semantic Similarity */}
            <tr>
              <td className="py-4 px-6 font-semibold text-slate-300">Semantic Similarity</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6 font-mono text-cyan-300">
                  {(cand.result.semantic_similarity * 100).toFixed(0)}%
                </td>
              ))}
            </tr>

            {/* Missing Skills */}
            <tr>
              <td className="py-4 px-6 font-semibold text-slate-300">Skill Gaps</td>
              {candidates.map((cand) => (
                <td key={cand.id} className="py-4 px-6">
                  {cand.result.missing_required.length > 0 ? (
                    <div className="flex flex-wrap gap-1">
                      {cand.result.missing_required.map((sk, i) => (
                        <span key={i} className="px-2 py-0.5 rounded text-[11px] bg-rose-500/10 text-rose-300 border border-rose-500/20">
                          {sk}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <span className="text-xs text-emerald-400 font-semibold">None ✓</span>
                  )}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};
