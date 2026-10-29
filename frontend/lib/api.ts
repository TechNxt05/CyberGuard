export const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

type Token = string | null | undefined;

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  token?: Token;
  signal?: AbortSignal;
}

/** Single place for backend calls: base URL, JSON, auth header and readable errors. */
export async function apiFetch<T>(path: string, { method = 'GET', body, token, signal }: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = typeof err.detail === 'string' ? err.detail : `Request failed (${res.status})`;
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export interface ProgressStep {
  step: string;
  label: string;
}

/**
 * POSTs to a Server-Sent Events endpoint, calling onProgress for each finished step,
 * and resolves with the final `result` event (rejects on an `error` event).
 */
export async function apiStream<T>(path: string, body: unknown, onProgress: (p: ProgressStep) => void): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify(body),
  });
  if (!res.ok || !res.body) {
    const err = await res.json().catch(() => ({}));
    throw new ApiError(res.status, typeof err.detail === 'string' ? err.detail : `Request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let boundary;
    while ((boundary = buffer.indexOf('\n\n')) !== -1) {
      const chunk = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const event = /^event: (.*)$/m.exec(chunk)?.[1];
      const data = /^data: (.*)$/m.exec(chunk)?.[1];
      if (!event || !data) continue;
      const payload = JSON.parse(data);
      if (event === 'progress') onProgress(payload);
      else if (event === 'result') return payload as T;
      else if (event === 'error') throw new ApiError(500, payload.detail || 'Analysis failed');
    }
  }
  throw new ApiError(500, 'The connection closed before the analysis finished.');
}

/** Downloads a binary response (e.g. PDF) and triggers a browser save. */
export async function apiDownload(path: string, body: unknown, token: Token, filename: string): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new ApiError(res.status, `Download failed (${res.status})`);
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export const checkHealth = async (): Promise<boolean> => {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(8000) });
    return res.ok;
  } catch {
    return false;
  }
};

/** Reads a File as base64 (without the data: prefix). */
export const fileToBase64 = (file: File): Promise<string> =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve((reader.result as string).split(',')[1]);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });

export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

// ---------- Types ----------

export type EntityMap = Record<string, string[]>;

export interface KnownThreat {
  entity_type: string;
  entity_value: string;
  occurrence_count: number;
  first_seen: string;
  last_seen: string;
  crime_types: string[];
  risk_score: number;
  is_confirmed_threat: boolean;
  case_count: number;
}

export interface InvestigationResponse {
  sessionId: string;
  extracted_entities: EntityMap;
  image_text?: string | null;
  known_threats: KnownThreat[];
}

export interface ConfidenceData {
  scamLikelihood: number;
  attackSophistication: string;
  sophisticationScore: number;
  recoveryProbability: number;
  urgencyLevel: string;
  urgencyReason: string;
  timeToAct: string;
  priorityActions: { action: string; deadline: string; impact: string }[];
  riskFactors: string[];
  mitigatingFactors: string[];
}

export interface TimelineEventData {
  id: string;
  timestamp: string;
  eventType: string;
  description: string;
  impact?: string;
  relativeTime?: string;
}

export interface GraphData {
  nodes: { id: string; type: string; label: string; metadata?: Record<string, unknown> }[];
  edges: { id: string; source: string; target: string; label: string; type?: string }[];
}

export interface ResolutionStepData {
  step_id: string;
  phase: string;
  action: string;
  description: string;
}

export interface CaseStateData {
  incident_id: string;
  dimensions: { summary: string; attack_type: string; urgency: string; prevention_tips: string[]; incident_logic: string };
  strategy: { lifecycle_plan: ResolutionStepData[]; estimated_timeline: string };
}

export interface ScamResult {
  scout_report: {
    verdict: 'SAFE' | 'SUSPICIOUS' | 'SCAM';
    risk_score: number;
    severity: string;
    scam_logic: string;
    consequences: string;
    recommendation: string;
    extracted_entities: Record<string, unknown>;
    analysis_status: 'ok' | 'failed';
    url_checks?: { url: string; domain: string; verdict: string; signals: string[]; domain_age_days?: number; impersonates?: string }[];
    analysis?: string;
  };
  explanation: { simple_explanation: string; trust_score: number };
  action_plan: { steps: string[]; blocking_instructions?: string | null };
}

export interface AnalysisRequest {
  message?: string;
  image_base64?: string;
  image_mime_type?: string;
  source?: string;
  language?: 'en' | 'hi';
}

export interface IncidentRequest {
  description: string;
  user_context?: Record<string, string>;
}

// ---------- Endpoints ----------

export const runInvestigation = (
  req: { message: string; sessionId: string; imageBase64?: string; imageMimeType?: string },
  token: Token,
) => apiFetch<InvestigationResponse>('/api/investigate', { method: 'POST', body: req, token });

export const checkKnownEntities = (entities: EntityMap) =>
  apiFetch<KnownThreat[]>('/api/memory/check', { method: 'POST', body: { entities } });

export const getConfidence = (incidentDescription: string, extractedEntities: EntityMap, token: Token) =>
  apiFetch<ConfidenceData>('/api/analysis/confidence', { method: 'POST', body: { incidentDescription, extractedEntities }, token });

export const getTimeline = (incidentDescription: string, token: Token) =>
  apiFetch<{ events: TimelineEventData[] }>('/api/analysis/timeline', { method: 'POST', body: { incidentDescription }, token });

export const getGraph = (incidentDescription: string, extractedEntities: EntityMap, token: Token) =>
  apiFetch<GraphData>('/api/analysis/graph', { method: 'POST', body: { incidentDescription, extractedEntities }, token });

export const checkScam = (data: AnalysisRequest, onProgress: (p: ProgressStep) => void = () => {}) =>
  apiStream<ScamResult>('/analyze-message/stream', data, onProgress);

export const resolveIncident = (data: IncidentRequest, onProgress: (p: ProgressStep) => void = () => {}) =>
  apiStream<{ case_state: CaseStateData; guide: string | null }>('/resolve-incident/stream', data, onProgress);

export const solveDoubt = (question: string, context: string, language: 'en' | 'hi' = 'en') =>
  apiFetch<{ answer: string }>('/case/doubt', { method: 'POST', body: { question, context, language } });

export const assistForm = (actionItem: string, context: string, language: 'en' | 'hi' = 'en') =>
  apiFetch<{ guidance: string; checklist: string[] }>('/case/form-assist', { method: 'POST', body: { action_item: actionItem, context, language } });
