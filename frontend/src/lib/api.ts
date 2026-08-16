// Lucent API Client — Phase 2 Multimodal Complete
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export type VerdictLabel =
  | 'True'
  | 'False'
  | 'Misleading'
  | 'Missing Context'
  | 'Altered/Manipulated'
  | 'AI-Generated'
  | 'Unverifiable';

export type ConfidenceLevel = 'High' | 'Medium' | 'Low';

export type RelationType = 'supports' | 'contradicts' | 'context_only';

export interface EvidenceItem {
  id?: string;
  source_title: string;
  source_url: string;
  snippet: string;
  relation: RelationType;
}

export interface FollowUpMessage {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
}

export interface Verification {
  id: string;
  created_at: string;
  content_type: string;
  raw_input_ref: string;
  extracted_claims: string[];
  verdict_label?: VerdictLabel | null;
  confidence_level?: ConfidenceLevel | null;
  confidence_reason?: string | null;
  explanation?: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  evidence_items: EvidenceItem[];
  follow_up_messages: FollowUpMessage[];
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  database: string;
}

// ─── Health Check ─────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<HealthCheckResponse> {
  const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`Health check failed with HTTP ${res.status}`);
  return res.json();
}

// ─── Text & URL Verification ──────────────────────────────────────────────────

export async function verifyClaim(payload: {
  content: string;
  content_type?: string;
}): Promise<Verification> {
  const res = await fetch(`${API_BASE}/verifications/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      content: payload.content,
      content_type: payload.content_type || 'text',
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Verification failed with HTTP ${res.status}`);
  }
  return res.json();
}

// ─── Image Verification (Phase 2) ─────────────────────────────────────────────

export async function verifyImage(file: File): Promise<Verification> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/verifications/verify-image`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Image verification failed with HTTP ${res.status}`);
  }
  return res.json();
}

// ─── Conversational Follow-Up ─────────────────────────────────────────────────

export async function submitFollowUp(
  verificationId: string,
  message: string,
): Promise<Verification> {
  const res = await fetch(`${API_BASE}/verifications/${verificationId}/follow-up`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Follow-up failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function getVerification(id: string): Promise<Verification> {
  const res = await fetch(`${API_BASE}/verifications/${id}`, { cache: 'no-store' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function listVerifications(limit = 10): Promise<Verification[]> {
  const res = await fetch(`${API_BASE}/verifications?limit=${limit}`, { cache: 'no-store' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
