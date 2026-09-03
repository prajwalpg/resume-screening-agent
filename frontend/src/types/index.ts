export interface ScoreBreakdown {
  required_skills: number;
  experience: number;
  education: number;
  semantic_similarity: number;
  preferred_skills: number;
}

export interface CandidateResult {
  candidate: string;
  rank: number;
  score: number;
  recommendation: 'STRONG SHORTLIST' | 'SHORTLIST' | 'REVIEW' | 'REJECT';
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  source_file: string;
  breakdown: ScoreBreakdown;
  matched_required: string[];
  missing_required: string[];
  matched_preferred: string[];
  missing_preferred: string[];
  experience_years: number;
  required_experience: number;
  semantic_similarity: number;
  skills: string[];
  education: string[];
  strengths: string[];
  gaps: string[];
  reason: string;
  flags: string[];
}

export interface CandidateRecord {
  id: string;
  screening_id: string;
  rank: number;
  name: string;
  score: number;
  recommendation: 'STRONG SHORTLIST' | 'SHORTLIST' | 'REVIEW' | 'REJECT';
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  source_file: string;
  result: CandidateResult;
}

export interface JobData {
  title: string;
  required_skills: string[];
  preferred_skills: string[];
  minimum_experience: number;
  education: string[];
  responsibilities: string[];
}

export interface ScreeningData {
  id: string;
  title: string;
  jd_path: string;
  created_at: string;
  total_candidates: number;
  shortlisted_count: number;
  review_count: number;
  rejected_count: number;
  avg_score: number;
  top_score: number;
  similarity_backend: string;
  job_data?: JobData;
  candidates: CandidateRecord[];
}

export interface HealthStatus {
  status: string;
  similarity_backend: string;
  llm_available: boolean;
  weights: Record<string, number>;
}
