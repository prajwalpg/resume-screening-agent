import React, { useState } from 'react';
import { 
  Upload, FileText, Files, Sparkles, AlertCircle, Trash2, CheckCircle2, Sliders, ArrowRight 
} from 'lucide-react';

interface NewScreeningViewProps {
  onStartCustomScreening: (jdFile: File | null, resumeFiles: File[]) => void;
  onRunDemo: () => void;
  isProcessing: boolean;
}

export const NewScreeningView: React.FC<NewScreeningViewProps> = ({
  onStartCustomScreening,
  onRunDemo,
  isProcessing,
}) => {
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [resumeFiles, setResumeFiles] = useState<File[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleJdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setJdFile(e.target.files[0]);
      setErrorMsg(null);
    }
  };

  const handleResumesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const added = Array.from(e.target.files);
      setResumeFiles((prev) => [...prev, ...added]);
      setErrorMsg(null);
    }
  };

  const removeResume = (index: number) => {
    setResumeFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (resumeFiles.length === 0) {
      setErrorMsg('Please attach at least one candidate resume file (PDF, DOCX, or TXT).');
      return;
    }
    onStartCustomScreening(jdFile, resumeFiles);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight">
          CREATE NEW AI SCREENING
        </h1>
        <p className="text-slate-400 text-sm max-w-xl mx-auto">
          Upload a Job Description and candidate resumes to execute candidate skill extraction, experience calculation, sentence embedding similarity, and explainable ranking.
        </p>
      </div>

      {/* Preset Banner */}
      <div className="glass-panel p-4 rounded-2xl border border-indigo-500/30 bg-indigo-950/20 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-semibold text-slate-100 text-sm">Want to test instantly without uploading files?</h4>
            <p className="text-xs text-slate-400">Run our bundled QA Engineer JD + 12 sample candidate dataset.</p>
          </div>
        </div>

        <button
          type="button"
          onClick={onRunDemo}
          disabled={isProcessing}
          className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/30 whitespace-nowrap"
        >
          Load 12 Sample Resumes Preset →
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Job Description */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-lg text-slate-100 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-400" />
              1. Job Description (JD)
            </h2>
            <span className="text-xs text-slate-400">PDF • DOCX • TXT (Optional if using default)</span>
          </div>

          <div className="relative border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-2xl p-6 text-center transition-all bg-slate-900/40">
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleJdChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            {jdFile ? (
              <div className="flex items-center justify-center gap-3 text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
                <span className="font-semibold text-sm">{jdFile.name}</span>
                <span className="text-xs text-slate-400 font-mono">({(jdFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            ) : (
              <div className="space-y-2">
                <Upload className="w-8 h-8 text-indigo-400 mx-auto" />
                <p className="text-sm font-medium text-slate-200">
                  Drop Job Description here or <span className="text-indigo-400 underline">browse</span>
                </p>
                <p className="text-xs text-slate-500">
                  If left empty, default <code className="bg-slate-800 px-1 py-0.5 rounded text-indigo-300">software_test_engineer.txt</code> will be used.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Resume Files */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-lg text-slate-100 flex items-center gap-2">
              <Files className="w-5 h-5 text-purple-400" />
              2. Candidate Resumes
            </h2>
            <span className="text-xs text-slate-400">Drop 1+ resumes (PDF / DOCX / TXT)</span>
          </div>

          <div className="relative border-2 border-dashed border-slate-700 hover:border-purple-500/60 rounded-2xl p-8 text-center transition-all bg-slate-900/40">
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              onChange={handleResumesChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <div className="space-y-2">
              <Upload className="w-8 h-8 text-purple-400 mx-auto" />
              <p className="text-sm font-medium text-slate-200">
                Drop candidate resumes here or <span className="text-purple-400 underline">select files</span>
              </p>
              <p className="text-xs text-slate-500">
                Select multiple files at once. PyMuPDF & python-docx extract text automatically.
              </p>
            </div>
          </div>

          {/* Attached files list */}
          {resumeFiles.length > 0 && (
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                <span>Attached Files ({resumeFiles.length})</span>
                <button
                  type="button"
                  onClick={() => setResumeFiles([])}
                  className="text-rose-400 hover:underline"
                >
                  Clear All
                </button>
              </div>

              <div className="max-h-48 overflow-y-auto space-y-1.5 pr-2">
                {resumeFiles.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300"
                  >
                    <div className="flex items-center gap-2 truncate">
                      <FileText className="w-4 h-4 text-purple-400 flex-shrink-0" />
                      <span className="font-medium truncate">{file.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-slate-500 text-[10px]">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                      <button
                        type="button"
                        onClick={() => removeResume(idx)}
                        className="text-slate-500 hover:text-rose-400 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Step 3: Configured Scoring Engine Weights */}
        <div className="glass-panel p-6 rounded-3xl border border-slate-800 space-y-3">
          <h3 className="font-bold text-sm text-slate-200 flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            Deterministic Scoring Criteria (Must sum to 100%)
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center text-xs">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-indigo-400 text-base">40%</div>
              <div className="text-slate-400 mt-0.5">Required Skills</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-emerald-400 text-base">25%</div>
              <div className="text-slate-400 mt-0.5">Work Experience</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-purple-400 text-base">15%</div>
              <div className="text-slate-400 mt-0.5">Education</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-cyan-400 text-base">10%</div>
              <div className="text-slate-400 mt-0.5">NLP Semantic</div>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <div className="font-bold text-pink-400 text-base">10%</div>
              <div className="text-slate-400 mt-0.5">Preferred Skills</div>
            </div>
          </div>
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={isProcessing}
          className="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:from-indigo-500 hover:to-pink-500 text-white font-extrabold text-base tracking-wide shadow-xl shadow-indigo-600/30 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
        >
          <Sparkles className="w-5 h-5" />
          START AI SCREENING PIPELINE
          <ArrowRight className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};
