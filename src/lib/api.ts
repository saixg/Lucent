// VeriLens API client
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Investigation {
  id: string;
  input_type: string;
  input_url?: string;
  input_text?: string;
  platform?: string;
  status: string;
  verdict?: string;
  confidence?: number;
  claim_credibility?: number;
  media_authenticity?: number;
  context_accuracy?: number;
  evidence_confidence?: number;
  summary?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
  claims: Claim[];
  analysis_results: AnalysisResult[];
  media_assets: MediaAsset[];
}

export interface Claim {
  id: string;
  claim_text: string;
  subject?: string;
  actor?: string;
  event?: string;
  claim_type?: string;
  entities?: string[];
  importance: number;
  verdict?: string;
  verdict_confidence?: number;
  evidence: Evidence[];
}

export interface Evidence {
  id: string;
  source_url: string;
  source_name?: string;
  source_type: string;
  source_tier: number;
  stance?: string;
  relevance_score?: number;
  credibility_score?: number;
  title?: string;
  snippet?: string;
}

export interface AnalysisResult {
  id: string;
  media_authenticity?: number;
  ai_generation_probability?: number;
  manipulation_probability?: number;
  deepfake_probability?: number;
  context_match?: boolean;
  provenance_status?: string;
  original_source_url?: string;
  reasoning?: string;
}

export interface MediaAsset {
  id: string;
  asset_type: string;
  storage_url?: string;
  mime_type?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  created_at: string;
}

// ─── Investigations ───────────────────────────────────────────────────────────

export async function createInvestigation(payload: {
  input_type: string;
  input_url?: string;
  input_text?: string;
  platform?: string;
}): Promise<Investigation> {
  const res = await fetch(`${API_BASE}/investigations/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getInvestigationStatus(id: string): Promise<{
  id: string; status: string; verdict?: string; confidence?: number; summary?: string;
}> {
  const res = await fetch(`${API_BASE}/investigations/${id}/status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getInvestigation(id: string): Promise<Investigation> {
  const res = await fetch(`${API_BASE}/investigations/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function listInvestigations(limit = 10): Promise<Investigation[]> {
  const res = await fetch(`${API_BASE}/investigations/?limit=${limit}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function uploadFile(file: File): Promise<Investigation> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/upload/`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ─── Conversations ────────────────────────────────────────────────────────────

export async function createConversation(investigation_id: string): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE}/conversations/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ investigation_id, platform: 'web' }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function sendMessage(conversation_id: string, content: string): Promise<Message> {
  const res = await fetch(`${API_BASE}/conversations/${conversation_id}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getMessages(conversation_id: string): Promise<Message[]> {
  const res = await fetch(`${API_BASE}/conversations/${conversation_id}/messages`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ─── Polling helper ───────────────────────────────────────────────────────────

export async function pollUntilComplete(
  investigationId: string,
  onUpdate: (status: string, progress?: number) => void,
  maxAttempts = 120,
  initialIntervalMs = 1000,
): Promise<Investigation> {
  // First immediate status check
  try {
    const initStatus = await getInvestigationStatus(investigationId);
    onUpdate(initStatus.status, 10);
    if (initStatus.status === 'complete' || initStatus.status === 'failed') {
      return getInvestigation(investigationId);
    }
  } catch {}

  for (let i = 0; i < maxAttempts; i++) {
    // Progressive backoff: 1s → 1.5s → 2s → ... → 3s max
    const interval = Math.min(3000, initialIntervalMs + i * 50);
    await new Promise(resolve => setTimeout(resolve, interval));
    try {
      const status = await getInvestigationStatus(investigationId);
      const estProgress = Math.min(95, 10 + Math.round((i / maxAttempts) * 90));
      onUpdate(status.status, estProgress);
      if (status.status === 'complete' || status.status === 'failed') {
        return getInvestigation(investigationId);
      }
    } catch (err) {
      // Continue polling through transient network hiccups
    }
  }
  throw new Error('Investigation timed out — the analysis is taking longer than expected. Please check back shortly.');
}
