'use client';

import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const SAMPLE_CLAIMS = [
  'The Eiffel Tower is located in Paris, France.',
  'NASA discovered liquid water oceans on Jupiter’s moon Europa.',
  'Scientists created a hybrid grain crop providing 80% higher yield.',
];

export default function HomePage() {
  return (
    <>
      <Navbar />

      <main style={{ minHeight: 'calc(100vh - 68px)', display: 'flex', flexDirection: 'column' }}>
        
        {/* ─── Hero Section (2-Column Split per Design.md) ────────────────── */}
        <section className="section" style={{ paddingTop: '64px', paddingBottom: '72px' }}>
          <div className="container" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: 48,
            alignItems: 'center',
          }}>
            {/* Left Column: Copy, CTAs, Tags */}
            <div>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
                <span className="mono-meta" style={{
                  backgroundColor: 'var(--color-mist)',
                  border: '1px solid var(--color-bone)',
                  padding: '4px 10px',
                  borderRadius: 9999,
                  color: 'var(--color-brand-violet)',
                  fontWeight: 600,
                }}>
                  ● INDEPENDENT VERIFICATION LAYER
                </span>
              </div>

              <h1 className="display-headline" style={{ marginBottom: 24 }}>
                See beyond the feed.<br />
                Know what&apos;s true.
              </h1>

              <p className="subheading" style={{ marginBottom: 28, maxWidth: 500 }}>
                Lucent evaluates suspicious claims, cross-examines primary news records and fact-checking databases, and synthesizes clear, evidence-backed verdicts.
              </p>

              {/* Benefit Checkmarks */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 36 }}>
                <div className="benefit-item">
                  <span className="benefit-check">✓</span>
                  <span><strong className="benefit-strong">100% Sourced Citations</strong> — Every verdict is backed by traceable primary sources.</span>
                </div>
                <div className="benefit-item">
                  <span className="benefit-check">✓</span>
                  <span><strong className="benefit-strong">Unverifiable Guard</strong> — Never asserts certainty when public evidence is insufficient.</span>
                </div>
                <div className="benefit-item">
                  <span className="benefit-check">✓</span>
                  <span><strong className="benefit-strong">Conversational Context</strong> — Ask follow-up questions without re-running searches.</span>
                </div>
              </div>

              {/* CTA Row with Rotating Conic Gradient Border */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 32 }}>
                <div className="conic-border-wrapper">
                  <div className="conic-border-inner">
                    <Link
                      href="/verify"
                      className="btn btn-primary"
                      style={{ padding: '14px 28px', fontSize: 15 }}
                    >
                      Start Free Verification &rarr;
                    </Link>
                  </div>
                </div>

                <Link
                  href="/verify"
                  className="btn btn-ghost-outline"
                  style={{ padding: '14px 24px', fontSize: 15 }}
                >
                  Explore Samples
                </Link>
              </div>

              {/* Feature Tags Row */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {['Text Claims', 'News URLs', 'Evidence Mapping', 'Tavily Search', 'Gemini Structured Output'].map((tag) => (
                  <span key={tag} className="tag-pill" style={{ cursor: 'default' }}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Right Column: Interactive Product Card Preview */}
            <div>
              <div className="card-flat" style={{
                padding: '32px',
                border: '1px solid var(--color-bone)',
                borderRadius: 'var(--radius-largecards)',
                boxShadow: 'var(--shadow-xl)',
                backgroundColor: 'var(--color-signal-white)',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                  <span className="mono-meta">LIVE VERIFICATION PREVIEW</span>
                  <span className="status-pill status-true">● TRUE · HIGH CONFIDENCE</span>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <span className="mono-meta" style={{ display: 'block', marginBottom: 4 }}>Claim Under Review</span>
                  <p style={{
                    fontFamily: 'var(--font-family-display)',
                    fontSize: 18,
                    fontWeight: 700,
                    color: 'var(--color-onyx)',
                    lineHeight: 1.3,
                  }}>
                    &quot;The James Webb Space Telescope detected atmospheric water vapor on exoplanet WASP-96b.&quot;
                  </p>
                </div>

                <div style={{
                  backgroundColor: 'var(--color-mist)',
                  borderRadius: 'var(--radius-inputs)',
                  padding: '16px',
                  border: '1px solid var(--color-bone)',
                  marginBottom: 20,
                  fontSize: 14,
                  lineHeight: 1.5,
                  color: 'var(--color-carbon)',
                }}>
                  NASA confirmed spectrographic signatures of water vapor in the atmosphere of WASP-96b during JWST&apos;s initial science observations in July 2022.
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                    <span className="mono-meta">PRIMARY EVIDENCE (2 SOURCES)</span>
                    <span className="mono-meta" style={{ color: 'var(--color-emerald)' }}>✓ 100% CITED</span>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{
                      padding: '10px 14px',
                      backgroundColor: '#ffffff',
                      border: '1px solid var(--color-bone)',
                      borderRadius: 8,
                      fontSize: 13,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-onyx)' }}>NASA Goddard Space Flight Center</span>
                      <span className="status-pill status-true" style={{ fontSize: 10, padding: '2px 8px' }}>SUPPORTS</span>
                    </div>

                    <div style={{
                      padding: '10px 14px',
                      backgroundColor: '#ffffff',
                      border: '1px solid var(--color-bone)',
                      borderRadius: 8,
                      fontSize: 13,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-onyx)' }}>European Space Agency (ESA) Science</span>
                      <span className="status-pill status-true" style={{ fontSize: 10, padding: '2px 8px' }}>SUPPORTS</span>
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--color-bone)' }}>
                  <Link
                    href="/verify"
                    className="btn btn-primary"
                    style={{ width: '100%', padding: '10px', fontSize: 14 }}
                  >
                    Test Your Own Claim &rarr;
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Social Proof & Trust Strip ─────────────────────────────────── */}
        <section style={{
          backgroundColor: 'var(--color-mist)',
          borderTop: '1px solid var(--color-bone)',
          borderBottom: '1px solid var(--color-bone)',
          padding: '40px 0',
        }}>
          <div className="container" style={{ textAlign: 'center' }}>
            <span className="mono-meta" style={{ display: 'block', marginBottom: 20, color: 'var(--color-ash)' }}>
              TRUSTED FOR RAPID VERIFICATION INTELLIGENCE
            </span>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: 40,
              color: 'var(--color-slate)',
              fontFamily: 'var(--font-family-display)',
              fontWeight: 700,
              fontSize: 16,
              letterSpacing: '-0.02em',
            }}>
              <span>REUTERS FACT CHECK</span>
              <span>ASSOCIATED PRESS</span>
              <span>POYNTER INSTITUTE</span>
              <span>BBC VERIFY</span>
              <span>IFCN STANDARDS</span>
            </div>
          </div>
        </section>

        {/* ─── The 3-Step Verification Architecture ───────────────────────── */}
        <section className="section">
          <div className="container">
            <div style={{ textAlign: 'center', maxWidth: 640, margin: '0 auto 56px' }}>
              <span className="mono-meta" style={{ color: 'var(--color-brand-violet)' }}>HOW LUCENT WORKS</span>
              <h2 className="section-headline" style={{ marginTop: 8, marginBottom: 16 }}>
                The Verification Pipeline
              </h2>
              <p className="subheading">
                Engineered for speed, evidence traceability, and absolute neutrality.
              </p>
            </div>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: 24,
            }}>
              <div className="card-flat" style={{ padding: '32px 28px' }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  backgroundColor: 'var(--color-mist)',
                  border: '1px solid var(--color-bone)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontFamily: 'var(--font-family-mono)',
                  fontWeight: 700,
                  fontSize: 16,
                  marginBottom: 20,
                  color: 'var(--color-brand-violet)',
                }}>
                  01
                </div>
                <h3 style={{
                  fontFamily: 'var(--font-family-display)',
                  fontSize: 18,
                  fontWeight: 700,
                  marginBottom: 10,
                  color: 'var(--color-onyx)',
                }}>
                  Ingestion & Claim Isolation
                </h3>
                <p style={{ fontSize: 14, color: 'var(--color-slate)', lineHeight: 1.6 }}>
                  Submits a text claim or URL. Lucent normalizes page articles and extracts atomic, checkable factual claims using Gemini reasoning.
                </p>
              </div>

              <div className="card-flat" style={{ padding: '32px 28px' }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  backgroundColor: 'var(--color-mist)',
                  border: '1px solid var(--color-bone)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontFamily: 'var(--font-family-mono)',
                  fontWeight: 700,
                  fontSize: 16,
                  marginBottom: 20,
                  color: 'var(--color-signal-blue)',
                }}>
                  02
                </div>
                <h3 style={{
                  fontFamily: 'var(--font-family-display)',
                  fontSize: 18,
                  fontWeight: 700,
                  marginBottom: 10,
                  color: 'var(--color-onyx)',
                }}>
                  Multi-Index Evidence Search
                </h3>
                <p style={{ fontSize: 14, color: 'var(--color-slate)', lineHeight: 1.6 }}>
                  Queries real-time news repositories and authoritative databases via Tavily API with strict query caps and source deduplication.
                </p>
              </div>

              <div className="card-flat" style={{ padding: '32px 28px' }}>
                <div style={{
                  width: 40,
                  height: 40,
                  borderRadius: 10,
                  backgroundColor: 'var(--color-mist)',
                  border: '1px solid var(--color-bone)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontFamily: 'var(--font-family-mono)',
                  fontWeight: 700,
                  fontSize: 16,
                  marginBottom: 20,
                  color: 'var(--color-emerald)',
                }}>
                  03
                </div>
                <h3 style={{
                  fontFamily: 'var(--font-family-display)',
                  fontSize: 18,
                  fontWeight: 700,
                  marginBottom: 10,
                  color: 'var(--color-onyx)',
                }}>
                  6-Part Verdict Synthesis
                </h3>
                <p style={{ fontSize: 14, color: 'var(--color-slate)', lineHeight: 1.6 }}>
                  Enforces the strict verdict contract: label, confidence rating, explanation, and mapped citations with code-enforced Unverifiable guards.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Bottom Dark Panel CTA ───────────────────────────────────────── */}
        <section className="section section-dark" style={{ textAlign: 'center' }}>
          <div className="container" style={{ maxWidth: 700 }}>
            <span className="mono-meta" style={{ color: 'var(--color-brand-violet)', display: 'block', marginBottom: 12 }}>
              READY TO INVESTIGATE?
            </span>
            <h2 className="section-headline" style={{ color: '#ffffff', marginBottom: 20 }}>
              Verify any claim in under 20 seconds.
            </h2>
            <p style={{ color: '#b3b3b3', fontSize: 16, marginBottom: 32 }}>
              Experience evidence-grounded truth without subjective bias or hallucinations.
            </p>
            <Link
              href="/verify"
              className="btn"
              style={{
                backgroundColor: '#ffffff',
                color: '#111111',
                padding: '14px 32px',
                fontSize: 15,
                fontWeight: 700,
              }}
            >
              Open Verification Console &rarr;
            </Link>
          </div>
        </section>

      </main>

      <Footer />
    </>
  );
}
