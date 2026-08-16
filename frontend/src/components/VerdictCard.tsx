'use client';

import { Verification, VerdictLabel, RelationType } from '@/lib/api';

interface VerdictCardProps {
  verification: Verification;
}

function getVerdictBadgeClass(label?: VerdictLabel | string | null): string {
  switch (label) {
    case 'True':
      return 'status-true';
    case 'False':
      return 'status-false';
    case 'Misleading':
      return 'status-misleading';
    case 'Missing Context':
      return 'status-missing-context';
    case 'Altered/Manipulated':
    case 'AI-Generated':
      return 'status-altered';
    default:
      return 'status-unverifiable';
  }
}

function getRelationBadge(relation: RelationType | string) {
  switch (relation) {
    case 'supports':
      return { label: 'SUPPORTS', color: '#065f46', bg: '#ecfdf5', border: '#a7f3d0' };
    case 'contradicts':
      return { label: 'CONTRADICTS', color: '#991b1b', bg: '#fef2f2', border: '#fecaca' };
    default:
      return { label: 'CONTEXT', color: '#1e40af', bg: '#eff6ff', border: '#bfdbfe' };
  }
}

export default function VerdictCard({ verification }: VerdictCardProps) {
  const badgeClass = getVerdictBadgeClass(verification.verdict_label);
  const isImage = verification.content_type === 'image';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* ─── Main Verdict Banner Card ──────────────────────────────────────── */}
      <div className="card-flat" style={{ borderLeft: '4px solid var(--color-ink-black)', padding: '32px 28px' }}>
        
        {/* Top Header: Verdict Label & Confidence */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 12,
          marginBottom: 20,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span className="mono-meta">VERDICT CLASSIFICATION:</span>
            <span className={`status-pill ${badgeClass}`} style={{ fontSize: 13, padding: '5px 14px' }}>
              ● {verification.verdict_label || 'Unverifiable'}
            </span>
            {isImage && (
              <span className="mono-meta" style={{
                backgroundColor: 'var(--color-mist)',
                border: '1px solid var(--color-bone)',
                padding: '3px 8px',
                borderRadius: 4,
                color: 'var(--color-brand-violet)',
              }}>
                🖼️ MULTIMODAL FORENSICS
              </span>
            )}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, color: 'var(--color-slate)' }}>
            <span>Confidence:</span>
            <strong style={{
              color: verification.confidence_level === 'High' ? '#065f46' : verification.confidence_level === 'Medium' ? '#92400e' : '#374151',
            }}>
              {verification.confidence_level || 'Low'}
            </strong>
          </div>
        </div>

        {/* Confidence Reasoning */}
        {verification.confidence_reason && (
          <div style={{
            fontSize: 13,
            color: 'var(--color-ash)',
            fontStyle: 'italic',
            marginBottom: 20,
            padding: '8px 12px',
            backgroundColor: 'var(--color-mist)',
            borderRadius: 6,
            border: '1px solid var(--color-bone)',
          }}>
            <strong>Reasoning:</strong> {verification.confidence_reason}
          </div>
        )}

        {/* Claim Summary */}
        <div style={{ marginBottom: 20 }}>
          <span className="mono-meta" style={{ display: 'block', marginBottom: 6 }}>
            {isImage ? 'Extracted Visual Claim / Subject' : 'Extracted Claim'}
          </span>
          <h2 style={{
            fontFamily: 'var(--font-family-display)',
            fontSize: 20,
            fontWeight: 700,
            color: 'var(--color-onyx)',
            lineHeight: 1.35,
          }}>
            {verification.extracted_claims?.[0] || verification.raw_input_ref}
          </h2>
        </div>

        {/* Plain Language Explanation */}
        <div>
          <span className="mono-meta" style={{ display: 'block', marginBottom: 6 }}>Plain-Language Explanation</span>
          <p style={{
            fontSize: 16,
            lineHeight: 1.6,
            color: 'var(--color-carbon)',
            backgroundColor: '#ffffff',
            padding: '16px 20px',
            borderRadius: 'var(--radius-inputs)',
            border: '1px solid var(--color-bone)',
          }}>
            {verification.explanation || 'No explanation generated.'}
          </p>
        </div>
      </div>

      {/* ─── Evidence Sources Grid ────────────────────────────────────────── */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h3 style={{
            fontFamily: 'var(--font-family-display)',
            fontSize: 18,
            fontWeight: 700,
            color: 'var(--color-onyx)',
          }}>
            Cited Primary Evidence & Forensics ({verification.evidence_items?.length || 0})
          </h3>
          <span className="mono-meta">100% CITED · SIGHTENGINE FORENSICS</span>
        </div>

        {(!verification.evidence_items || verification.evidence_items.length === 0) ? (
          <div className="card-flat" style={{ textAlign: 'center', padding: '32px 20px', color: 'var(--color-ash)' }}>
            <p>No external primary sources were discovered for this claim. Marked as <strong>Unverifiable</strong> per integrity standards.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
            {verification.evidence_items.map((ev, idx) => {
              const rel = getRelationBadge(ev.relation);
              return (
                <div key={ev.id || idx} className="card-flat" style={{
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: 12,
                  padding: 20,
                }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, marginBottom: 8 }}>
                      <span style={{
                        fontFamily: 'var(--font-family-mono)',
                        fontSize: 10,
                        fontWeight: 700,
                        padding: '2px 8px',
                        borderRadius: 4,
                        color: rel.color,
                        backgroundColor: rel.bg,
                        border: `1px solid ${rel.border}`,
                      }}>
                        {rel.label}
                      </span>
                    </div>

                    <h4 style={{
                      fontFamily: 'var(--font-family-display)',
                      fontSize: 15,
                      fontWeight: 700,
                      color: 'var(--color-onyx)',
                      lineHeight: 1.3,
                      marginBottom: 8,
                    }}>
                      {ev.source_title}
                    </h4>

                    <p style={{
                      fontSize: 13,
                      color: 'var(--color-slate)',
                      lineHeight: 1.5,
                      maxHeight: 110,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}>
                      {ev.snippet}
                    </p>
                  </div>

                  <a
                    href={ev.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 4,
                      fontSize: 13,
                      fontWeight: 600,
                      color: 'var(--color-signal-blue)',
                      wordBreak: 'break-all',
                      paddingTop: 8,
                      borderTop: '1px solid var(--color-bone)',
                    }}
                  >
                    View Source Link &rarr;
                  </a>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
