import React from 'react';
import { 
  X, CheckCircle2, XCircle, ShieldAlert, FileText, 
  Check, AlertCircle, Scale, Sparkles 
} from 'lucide-react';
import type { CandidateRecord } from '../types';

interface CandidateModalProps {
  candidate: CandidateRecord;
  onClose: () => void;
  onSelectForCompare: (cand: CandidateRecord) => void;
  isCompared: boolean;
}

export const CandidateModal: React.FC<CandidateModalProps> = ({
  candidate,
  onClose,
  onSelectForCompare,
  isCompared,
}) => {
  const res = candidate.result;
  const bd = res.breakdown;

  const recColors = {
    'STRONG SHORTLIST': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    SHORTLIST: 'bg-teal-500/10 text-teal-300 border-teal-500/30',
    REVIEW: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    REJECT: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
  }[res.recommendation] || 'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel w-full max-w-4xl max-h-[90vh] rounded-3xl border border-slate-700 shadow-2xl flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-900/60">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-extrabold text-white tracking-tight">
                {res.candidate}
              </h2>
              <span className={`px-3 py-1 rounded-full text-xs font-bold border ${recColors}`}>
                {res.recommendation}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                Rank #{res.rank}
              </span>
            </div>

            <p className="text-xs text-slate-400 flex items-center gap-2">
              <FileText className="w-3.5 h-3.5 text-indigo-400" />
              Source File: <code className="text-indigo-300 font-mono">{res.source_file || 'candidate_resume'}</code>
              <span>•</span>
              <span>Confidence: <strong className="text-slate-200">{res.confidence}</strong></span>
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => onSelectForCompare(candidate)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                isCompared
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700'
              }`}
            >
              <Scale className="w-3.5 h-3.5" />
              {isCompared ? 'In Compare Matrix' : '+ Add to Compare'}
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-slate-300 text-sm">
          {/* Explainable Score Header Box */}
          <div className="glass-card p-6 rounded-2xl border border-indigo-500/30 bg-gradient-to-r from-indigo-950/30 via-slate-900/60 to-purple-950/30 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                  🎯 Explainable Candidate Score
                </h3>
                <p className="text-xs text-slate-400">
                  Calculated using transparent deterministic weighted criteria + NLP semantic similarity
                </p>
              </div>

              <div className="text-right">
                <div className="text-4xl font-extrabold bg-gradient-to-r from-indigo-400 to-emerald-400 bg-clip-text text-transparent">
                  {res.score.toFixed(1)}%
                </div>
                <div className="text-[10px] text-slate-500 font-mono">Auditable Score</div>
              </div>
            </div>

            {/* Score Breakdown Bars */}
            <div className="space-y-2.5 pt-2">
              {/* Required Skills 40% */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">Required Skills Match (40% weight)</span>
                  <span className="font-bold text-indigo-400">{(bd.required_skills * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 rounded-full transition-all"
                    style={{ width: `${bd.required_skills * 100}%` }}
                  />
                </div>
              </div>

              {/* Work Experience 25% */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">Work Experience Match (25% weight)</span>
                  <span className="font-bold text-emerald-400">{(bd.experience * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full transition-all"
                    style={{ width: `${bd.experience * 100}%` }}
                  />
                </div>
              </div>

              {/* Education 15% */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">Education Alignment (15% weight)</span>
                  <span className="font-bold text-purple-400">{(bd.education * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-500 rounded-full transition-all"
                    style={{ width: `${bd.education * 100}%` }}
                  />
                </div>
              </div>

              {/* Semantic Similarity 10% */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">NLP Semantic Similarity (10% weight)</span>
                  <span className="font-bold text-cyan-400">{(bd.semantic_similarity * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500 rounded-full transition-all"
                    style={{ width: `${bd.semantic_similarity * 100}%` }}
                  />
                </div>
              </div>

              {/* Preferred Skills 10% */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-medium">
                  <span className="text-slate-300">Preferred Skills Match (10% weight)</span>
                  <span className="font-bold text-pink-400">{(bd.preferred_skills * 100).toFixed(0)}%</span>
                </div>
                <div className="h-2 bg-slate-900 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-pink-500 rounded-full transition-all"
                    style={{ width: `${bd.preferred_skills * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Skills Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Matched Skills */}
            <div className="glass-card p-4 rounded-2xl border border-emerald-500/20 space-y-2">
              <h4 className="font-bold text-xs text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Matched Required Skills ({res.matched_required.length})
              </h4>
              {res.matched_required.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {res.matched_required.map((skill, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                      <Check className="w-3 h-3 text-emerald-400" />
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-500 italic">No required skills matched</p>
              )}
            </div>

            {/* Missing Skills */}
            <div className="glass-card p-4 rounded-2xl border border-rose-500/20 space-y-2">
              <h4 className="font-bold text-xs text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                Missing / Weak Skills ({res.missing_required.length})
              </h4>
              {res.missing_required.length > 0 ? (
                <div className="flex flex-wrap gap-1.5">
                  {res.missing_required.map((skill, i) => (
                    <span key={i} className="px-2.5 py-1 rounded-lg text-xs font-medium bg-rose-500/10 text-rose-300 border border-rose-500/30 flex items-center gap-1">
                      <XCircle className="w-3 h-3 text-rose-400" />
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-emerald-400 font-medium">✓ Zero required skill gaps!</p>
              )}
            </div>
          </div>

          {/* Work Experience Comparison */}
          <div className="glass-card p-4 rounded-2xl border border-slate-800 space-y-2">
            <h4 className="font-bold text-xs text-slate-300 uppercase tracking-wider">
              Work Experience Alignment
            </h4>
            <div className="flex items-center gap-6 text-sm">
              <div>
                <span className="text-xs text-slate-400">Required:</span>{' '}
                <strong className="text-slate-200">{res.required_experience} yr(s)</strong>
              </div>
              <div>
                <span className="text-xs text-slate-400">Candidate:</span>{' '}
                <strong className={res.experience_years >= res.required_experience ? 'text-emerald-400' : 'text-amber-400'}>
                  {res.experience_years} yr(s)
                </strong>
              </div>
              <div className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {res.experience_years >= res.required_experience ? 'Meets Requirement ✓' : 'Below Minimum Bar'}
              </div>
            </div>
          </div>

          {/* AI Assessment & Rationales */}
          <div className="glass-card p-5 rounded-2xl border border-slate-800 space-y-4">
            <h4 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              AI Assessment Rationale
            </h4>

            {/* Strengths */}
            {res.strengths.length > 0 && (
              <div className="space-y-1">
                <span className="text-xs font-bold text-emerald-400">Key Strengths</span>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 pl-1">
                  {res.strengths.map((str, i) => (
                    <li key={i}>{str}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Gaps */}
            {res.gaps.length > 0 && (
              <div className="space-y-1">
                <span className="text-xs font-bold text-amber-400">Skill / Experience Gaps</span>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-300 pl-1">
                  {res.gaps.map((gap, i) => (
                    <li key={i}>{gap}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Full Decision Reason */}
            <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs leading-relaxed">
              <strong className="text-indigo-300 block mb-1">
                {res.recommendation === 'REJECT' || res.recommendation === 'REVIEW'
                  ? 'Why not shortlisted?'
                  : 'Decision Reason'}
              </strong>
              <p className="text-slate-300">{res.reason}</p>
            </div>
          </div>

          {/* Responsible AI Disclaimer */}
          <div className="p-3 rounded-xl bg-slate-900/40 border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-indigo-400 flex-shrink-0" />
            <span>
              <strong>Responsible AI Note:</strong> Contact details are stripped prior to scoring. Gender, age, photograph, address, and protected attributes are strictly excluded from ranking calculations.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
