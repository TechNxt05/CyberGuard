const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface InvestigationRequest {
  message: string;
  sessionId: string;
  imageBase64?: string;
  imageMimeType?: string;
  isDemoCase?: boolean;
  demoCaseId?: string;
}

export interface InvestigationResponse {
  sessionId: string;
  understanding: any;
  evidence: any;
  confidence: any;
  timeline: any;
  graph: any;
  strategy: any;
  recovery: any;
  authorityMap: any;
  prevention: any;
}

// Health check — used for cold-start detection
export const checkHealth = async (): Promise<boolean> => {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(8000) });
    return res.ok;
  } catch {
    return false;
  }
};

// Main investigation — real AI pipeline
export const runInvestigation = async (
  req: InvestigationRequest
): Promise<InvestigationResponse> => {
  const body = JSON.stringify(req);
  
  const res = await fetch(`${API_BASE}/api/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `Investigation failed: ${res.status}`);
  }

  return res.json();
};

// Individual module endpoints (called in parallel after main investigation)
export const getConfidence = async (sessionId: string, incidentDescription: string) =>
  fetch(`${API_BASE}/api/analysis/confidence`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incidentDescription }),
  }).then(r => r.json());

export const getTimeline = async (sessionId: string, incidentDescription: string) =>
  fetch(`${API_BASE}/api/analysis/timeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incidentDescription }),
  }).then(r => r.json());

export const getGraph = async (sessionId: string, incidentDescription: string) =>
  fetch(`${API_BASE}/api/analysis/graph`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incidentDescription, extractedEntities: {} }),
  }).then(r => r.json());

export interface AnalysisRequest {
  message?: string;
  image_base64?: string;
  source?: string;
}

export interface IncidentRequest {
  description: string;
  user_context?: Record<string, string>;
}

export const checkScam = async (data: AnalysisRequest) => {
  const res = await fetch(`${API_BASE}/analyze-message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
};

export const resolveIncident = async (data: IncidentRequest) => {
  const res = await fetch(`${API_BASE}/resolve-incident`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
};

export const solveDoubt = async (incidentId: string, question: string) => {
  const res = await fetch(`${API_BASE}/case/doubt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incident_id: incidentId, question }),
  });
  return res.json();
};

export const assistForm = async (incidentId: string, actionItem: string) => {
  const res = await fetch(`${API_BASE}/case/form-assist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ incident_id: incidentId, action_item: actionItem }),
  });
  return res.json();
};

