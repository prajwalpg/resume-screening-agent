import React, { useEffect, useState } from 'react';
import { Bot, CheckCircle2, Loader2, Sparkles, Cpu, Terminal } from 'lucide-react';

interface ProcessingStep {
  id: string;
  label: string;
  detail: string;
}

const STEPS: ProcessingStep[] = [
  { id: 'jd', label: 'Reading job description', detail: 'Parsing text with PyMuPDF/docx & scrubbing PII' },
  { id: 'reqs', label: 'Extracting requirements', detail: 'Identified required skills & min experience' },
  { id: 'resumes', label: 'Processing candidate resumes', detail: 'Parsing documents and section splitting' },
  { id: 'skills', label: 'Extracting candidate skills', detail: 'Matching against curated canonical taxonomy & alias maps' },
  { id: 'exp', label: 'Comparing experience', detail: 'Checking date range spans & experience declarations' },
  { id: 'embeddings', label: 'Generating embeddings', detail: 'Sentence Transformer all-MiniLM-L6-v2 / TF-IDF' },
  { id: 'scores', label: 'Calculating candidate scores', detail: 'Applying weighted formula (40/25/15/10/10)' },
  { id: 'reasons', label: 'Generating explanations', detail: 'Synthesizing strengths, gaps, and decision rationales' },
  { id: 'rank', label: 'Ranking candidates', detail: 'Sorting by score with stable tie-breaking' },
];

export const ProcessingView: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev < STEPS.length - 1) {
          const next = prev + 1;
          setLogs((l) => [
            ...l,
            `[AGENT LOG ${new Date().toLocaleTimeString()}] ${STEPS[next].label} -> ${STEPS[next].detail}`,
          ]);
          return next;
        }
        return prev;
      });
    }, 900);

    return () => clearInterval(timer);
  }, []);

  const progressPercent = Math.round(((currentStepIndex + 1) / STEPS.length) * 100);

  return (
    <div className="max-w-3xl mx-auto space-y-8 py-8 animate-fadeIn">
      {/* Header */}
      <div className="glass-panel p-8 rounded-3xl border border-indigo-500/30 text-center space-y-4 shadow-2xl relative overflow-hidden">
        <div className="absolute -top-12 -left-12 w-48 h-48 bg-indigo-500/20 rounded-full blur-2xl" />
        
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 to-pink-500 p-0.5 mx-auto shadow-lg shadow-indigo-500/30 animate-pulse">
          <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
            <Bot className="w-8 h-8 text-indigo-400" />
          </div>
        </div>

        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold text-white tracking-tight flex items-center justify-center gap-2">
            AI AGENT IS WORKING...
            <Sparkles className="w-5 h-5 text-emerald-400 animate-spin" />
          </h2>
          <p className="text-slate-400 text-sm">
            Autonomous recruitment agent analyzing candidate resumes against job criteria
          </p>
        </div>

        {/* Progress bar */}
        <div className="space-y-2 pt-2 max-w-md mx-auto">
          <div className="flex justify-between text-xs font-bold text-slate-300">
            <span>Progress</span>
            <span className="text-indigo-400 font-mono">{progressPercent}%</span>
          </div>
          <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Checklist Grid */}
      <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-indigo-400" />
          Agent Pipeline Execution
        </h3>

        <div className="space-y-2">
          {STEPS.map((step, idx) => {
            const isCompleted = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;
            const isPending = idx > currentStepIndex;

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                  isCompleted
                    ? 'bg-slate-900/60 border-slate-800 text-slate-200'
                    : isCurrent
                    ? 'bg-indigo-950/40 border-indigo-500/40 text-indigo-200 shadow-md shadow-indigo-500/10 scale-[1.01]'
                    : 'bg-slate-950/40 border-slate-900/60 text-slate-600'
                }`}
              >
                <div className="flex items-center gap-3">
                  {isCompleted && <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />}
                  {isCurrent && <Loader2 className="w-5 h-5 text-indigo-400 animate-spin flex-shrink-0" />}
                  {isPending && <div className="w-5 h-5 rounded-full border-2 border-slate-800 flex-shrink-0" />}

                  <div>
                    <div className={`font-semibold text-sm ${isCurrent ? 'text-indigo-300' : ''}`}>
                      {step.label}
                    </div>
                    <div className="text-xs text-slate-400 font-mono">{step.detail}</div>
                  </div>
                </div>

                <div className="text-xs font-mono">
                  {isCompleted && <span className="text-emerald-400 font-bold">DONE</span>}
                  {isCurrent && <span className="text-indigo-400 font-bold animate-pulse">RUNNING</span>}
                  {isPending && <span className="text-slate-600">WAITING</span>}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Agent Log Console */}
      <div className="glass-panel rounded-2xl p-4 border border-slate-800 font-mono text-xs text-slate-300 space-y-2">
        <div className="flex items-center gap-2 text-slate-400 border-b border-slate-800 pb-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span>Live Agent stdout</span>
        </div>

        <div className="max-h-36 overflow-y-auto space-y-1 text-[11px] text-slate-400">
          <p className="text-slate-500">[AGENT ENGINE] Initializing deterministic scoring weights: 40/25/15/10/10</p>
          {logs.map((log, i) => (
            <p key={i} className="text-emerald-300/90">{log}</p>
          ))}
        </div>
      </div>
    </div>
  );
};
