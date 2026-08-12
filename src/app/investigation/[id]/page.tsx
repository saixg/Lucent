'use client';
import { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import VerdictBadge from '@/components/VerdictBadge';
import styles from './page.module.css';
import Link from 'next/link';
import {
  getInvestigation,
  createConversation,
  sendMessage,
  getMessages,
  type Investigation,
  type Message,
} from '@/lib/api';

type Verdict = 'VERIFIED' | 'FALSE' | 'MISLEADING' | 'OUT_OF_CONTEXT' | 'MANIPULATED' | 'UNVERIFIED';

export default function InvestigationPage() {
  const params = useParams();
  const id = params.id as string;

  const [inv, setInv] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Conversation
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);

  // Load investigation
  useEffect(() => {
    if (!id || id === 'demo') {
      // Demo mode — load mock data
      setInv(DEMO_INV);
      setLoading(false);
      return;
    }
    getInvestigation(id)
      .then(data => { setInv(data); setLoading(false); })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [id]);

  // Create conversation when investigation loads
  useEffect(() => {
    if (!inv || id === 'demo') return;
    createConversation(inv.id)
      .then(c => {
        setConversationId(c.id);
        // Add welcome message
        setMessages([{
          id: 'welcome',
          conversation_id: c.id,
          role: 'assistant',
          content: `Investigation complete. Verdict: **${inv.verdict}** (${Math.round((inv.confidence || 0) * 100)}% confidence). ${inv.summary || ''} What would you like to know?`,
          created_at: new Date().toISOString(),
        }]);
      })
      .catch(() => {
        // Fail silently — chat just won't work
      });
  }, [inv?.id]);

  const send = useCallback(async () => {
    if (!input.trim() || !conversationId || sending) return;
    const userText = input.trim();
    setInput('');
    setSending(true);

    // Optimistic user message
    const tmpUserMsg: Message = {
      id: `tmp-${Date.now()}`,
      conversation_id: conversationId,
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tmpUserMsg]);

    try {
      const aiMsg = await sendMessage(conversationId, userText);
      setMessages(prev => [...prev, aiMsg]);
    } catch (e: any) {
      setMessages(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          conversation_id: conversationId,
          role: 'assistant',
          content: 'Sorry, I had trouble responding. Please try again.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setSending(false);
    }
  }, [input, conversationId, sending]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState error={error} />;
  if (!inv) return <ErrorState error="Investigation not found" />;

  const forensics = inv.analysis_results[0];
  const confidence = Math.round((inv.confidence || 0) * 100);

  return (
    <>
      <Navbar />
      <main className={styles.main}>
        <div className={`container ${styles.layout}`}>

          {/* ─── LEFT: Investigation Report ─────────────────────────── */}
          <div className={styles.report} id="investigation-report">
            <div className={styles.breadcrumb}>
              <Link href="/verify" className={styles.breadcrumbLink}>← Verifications</Link>
              <span className={styles.breadcrumbSep}>/</span>
              <span className={styles.breadcrumbId}>{inv.id.slice(0, 8).toUpperCase()}</span>
            </div>

            {/* Verdict */}
            <div className={styles.verdictHeader}>
              <VerdictBadge verdict={(inv.verdict || 'UNVERIFIED') as Verdict} size="lg" />
              {confidence > 0 && <span className={styles.confidence}>{confidence}% confidence</span>}
            </div>

            <h1 className={styles.claimText}>
              {inv.claims[0]?.claim_text || inv.input_url || inv.input_text?.slice(0, 120) || 'Investigation'}
            </h1>
            <p className={styles.contentSource}>
              {inv.input_type.replace('_', ' ')} · {inv.input_url || inv.platform || 'web'}
            </p>

            {inv.summary && (
              <div className={styles.summaryBox}>
                <p className={styles.summaryText}>{inv.summary}</p>
              </div>
            )}

            {/* Score bars */}
            {(inv.claim_credibility || inv.media_authenticity || inv.context_accuracy || inv.evidence_confidence) && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Investigation Scores</h2>
                <div className={styles.scores}>
                  {[
                    { label: 'Claim Credibility', value: inv.claim_credibility, color: _scoreColor(inv.claim_credibility) },
                    { label: 'Media Authenticity', value: inv.media_authenticity, color: _scoreColor(inv.media_authenticity) },
                    { label: 'Context Accuracy', value: inv.context_accuracy, color: _scoreColor(inv.context_accuracy) },
                    { label: 'Evidence Confidence', value: inv.evidence_confidence, color: _scoreColor(inv.evidence_confidence) },
                  ].filter(s => s.value != null).map(s => (
                    <div key={s.label} className={styles.scoreRow}>
                      <div className={styles.scoreMeta}>
                        <span className={styles.scoreLabel}>{s.label}</span>
                        <span className={styles.scoreValue} style={{ color: s.color }}>{Math.round((s.value!) * 100)}%</span>
                      </div>
                      <div className={styles.scoreTrack}>
                        <div className={styles.scoreFill} style={{ width: `${Math.round((s.value!) * 100)}%`, background: s.color }} />
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Claim decomposition */}
            {inv.claims.length > 0 && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Claim Decomposition ({inv.claims.length})</h2>
                <div className={styles.claimsGrid}>
                  {inv.claims.map(c => (
                    <div key={c.id} className={styles.claimItem}>
                      {c.verdict && <VerdictBadge verdict={c.verdict as Verdict} size="sm" />}
                      <span className={styles.claimItemText}>{c.claim_text}</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Media forensics */}
            {forensics && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Media Forensics</h2>
                <div className={styles.forensicsGrid}>
                  {[
                    { label: 'AI Generated', value: forensics.ai_generation_probability },
                    { label: 'Manipulation', value: forensics.manipulation_probability },
                    { label: 'Deepfake', value: forensics.deepfake_probability },
                    { label: 'Media Authentic', value: forensics.media_authenticity },
                  ].filter(m => m.value != null).map(m => {
                    const pct = Math.round((m.value!) * 100);
                    const color = m.label === 'Media Authentic'
                      ? _scoreColor(m.value)
                      : _riskColor(m.value);
                    return (
                      <div key={m.label} className={styles.forensicsCard}>
                        <div className={styles.forensicsGauge}>
                          <svg viewBox="0 0 60 60" width="64" height="64">
                            <circle cx="30" cy="30" r="24" fill="none" stroke={`${color}20`} strokeWidth="6" />
                            <circle cx="30" cy="30" r="24" fill="none" stroke={color} strokeWidth="6"
                              strokeDasharray={`${pct * 1.508} 150.8`} strokeLinecap="round"
                              transform="rotate(-90 30 30)" />
                          </svg>
                          <span className={styles.forensicsVal} style={{ color }}>{pct}%</span>
                        </div>
                        <span className={styles.forensicsLabel}>{m.label}</span>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* Evidence */}
            {inv.claims.some(c => c.evidence.length > 0) && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>
                  Evidence ({inv.claims.reduce((acc, c) => acc + c.evidence.length, 0)} sources)
                </h2>
                <div className={styles.evidenceList}>
                  {inv.claims.flatMap(c => c.evidence).slice(0, 10).map(e => (
                    <div key={e.id} className={styles.evidenceItem}>
                      <div className={styles.evidenceHeader}>
                        <span className={styles.tierBadge}>T{e.source_tier}</span>
                        <a href={e.source_url} target="_blank" rel="noopener noreferrer" className={styles.evidenceSource}>
                          {e.source_name || e.source_url}
                        </a>
                        {e.stance && (
                          <span className={styles.evidenceStance} style={{ color: _stanceColor(e.stance) }}>
                            {e.stance}
                          </span>
                        )}
                        {e.credibility_score && (
                          <span className={styles.credScore}>{Math.round(e.credibility_score * 100)}% credibility</span>
                        )}
                      </div>
                      {e.snippet && <p className={styles.evidenceSnippet}>"{e.snippet}"</p>}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Share */}
            <div className={styles.shareRow}>
              <span className={styles.shareLabel}>Share investigation:</span>
              <button className={styles.shareBtn} id="share-link"
                onClick={() => navigator.clipboard?.writeText(window.location.href)}>
                🔗 Copy link
              </button>
            </div>
          </div>

          {/* ─── RIGHT: Chat Panel ──────────────────────────────────── */}
          <aside className={styles.chatPanel} id="conversation-panel">
            <div className={styles.chatHeader}>
              <span className={styles.chatLogo}>✦</span>
              <div>
                <h3 className={styles.chatTitle}>Ask VeriLens</h3>
                <p className={styles.chatSubtitle}>Ask anything about this investigation</p>
              </div>
            </div>

            <div className={styles.chatMessages}>
              {messages.map((m, i) => (
                <div key={m.id || i} className={`${styles.chatMsg} ${m.role === 'user' ? styles.chatUser : styles.chatAi}`}>
                  {m.role === 'assistant' && <span className={styles.chatAiDot}>✦</span>}
                  <span style={{ whiteSpace: 'pre-wrap' }}>{m.content.replace(/\*\*/g, '')}</span>
                </div>
              ))}
              {sending && (
                <div className={`${styles.chatMsg} ${styles.chatAi}`}>
                  <span className={styles.chatAiDot}>✦</span>
                  <span className={styles.thinkingDots}>Thinking<span>.</span><span>.</span><span>.</span></span>
                </div>
              )}
            </div>

            <div className={styles.quickPrompts}>
              {['"Why is this verdict?"', '"Show me evidence"', '"Find the original source"'].map(q => (
                <button key={q} className={styles.quickPrompt}
                  onClick={() => { setInput(q.replace(/"/g, '')); }}>
                  {q}
                </button>
              ))}
            </div>

            <div className={styles.chatInputWrap}>
              <input
                id="chat-input"
                type="text"
                className={styles.chatInput}
                placeholder="Ask anything about this content..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && send()}
                disabled={sending || !conversationId}
              />
              <button className={styles.chatSend} onClick={send} id="chat-send"
                disabled={sending || !conversationId} aria-label="Send">
                ↑
              </button>
            </div>
          </aside>
        </div>
      </main>
      <Footer />
    </>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function _scoreColor(v?: number | null): string {
  if (v == null) return '#6b7589';
  if (v >= 0.7) return '#10b981';
  if (v >= 0.4) return '#f59e0b';
  return '#ef4444';
}

function _riskColor(v?: number | null): string {
  if (v == null) return '#6b7589';
  if (v >= 0.7) return '#ef4444';
  if (v >= 0.4) return '#f59e0b';
  return '#10b981';
}

function _stanceColor(stance: string): string {
  if (stance === 'refutes') return '#ef4444';
  if (stance === 'supports') return '#10b981';
  return '#6b7589';
}

// ─── State components ─────────────────────────────────────────────────────────

function LoadingState() {
  return (
    <>
      <Navbar />
      <main style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', paddingTop: 80 }}>
        <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
          <div style={{ width: 40, height: 40, border: '3px solid #ebdafd', borderTopColor: '#862fe7', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
          <p style={{ fontFamily: 'Inter, sans-serif', color: '#6b7589' }}>Loading investigation...</p>
        </div>
      </main>
      <Footer />
    </>
  );
}

function ErrorState({ error }: { error: string }) {
  return (
    <>
      <Navbar />
      <main style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', paddingTop: 80 }}>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontFamily: 'Inter, sans-serif', color: '#ef4444', marginBottom: 16 }}>{error}</p>
          <Link href="/verify" style={{ color: '#862fe7', fontFamily: 'Inter, sans-serif' }}>← Back to verify</Link>
        </div>
      </main>
      <Footer />
    </>
  );
}

// ─── Demo investigation data ──────────────────────────────────────────────────

const DEMO_INV: Investigation = {
  id: 'demo',
  input_type: 'youtube_url',
  input_url: 'https://youtube.com/example',
  status: 'complete',
  verdict: 'MISLEADING',
  confidence: 0.91,
  claim_credibility: 0.14,
  media_authenticity: 0.72,
  context_accuracy: 0.21,
  evidence_confidence: 0.94,
  summary: 'The video contains a real RBI spokesperson clip from 2024, re-edited to suggest an August 2026 UPI ban. No such ban exists. Three Tier-1 sources directly contradict this claim.',
  created_at: new Date().toISOString(),
  claims: [
    {
      id: '1', claim_text: 'Government has banned UPI from August 15, 2026',
      importance: 5, verdict: 'FALSE', verdict_confidence: 0.95,
      evidence: [
        { id: 'e1', source_url: 'https://rbi.org.in', source_name: 'Reserve Bank of India', source_type: 'government', source_tier: 1, stance: 'refutes', credibility_score: 0.98, snippet: 'RBI has issued no directives regarding UPI suspension.' },
        { id: 'e2', source_url: 'https://reuters.com', source_name: 'Reuters Fact Check', source_type: 'factcheck', source_tier: 3, stance: 'refutes', credibility_score: 0.92, snippet: 'Claim rated FALSE. Original clip is from 2024 RBI press conference.' },
      ],
    },
    { id: '2', claim_text: 'RBI spokesperson statement is authentic', importance: 3, verdict: 'VERIFIED', verdict_confidence: 0.88, evidence: [] },
    { id: '3', claim_text: 'Video is from current events', importance: 4, verdict: 'FALSE', verdict_confidence: 0.91, evidence: [] },
  ],
  analysis_results: [
    { id: 'a1', media_authenticity: 0.72, ai_generation_probability: 0.08, manipulation_probability: 0.63, deepfake_probability: 0.15, provenance_status: 'reposted' },
  ],
  media_assets: [],
};
