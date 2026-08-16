'use client';

import { useState, useRef } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import VerdictCard from '@/components/VerdictCard';
import FollowUpChat from '@/components/FollowUpChat';
import { verifyClaim, verifyImage, Verification } from '@/lib/api';

const QUICK_SAMPLES = [
  { label: 'Eiffel Tower Location', type: 'text' as const, text: 'The Eiffel Tower is located in Paris, France.' },
  { label: 'Liquid Water on Europa', type: 'text' as const, text: 'NASA confirmed subsurface liquid oceans on Jupiter’s moon Europa.' },
  { label: 'Synthetic Beef Rice', type: 'text' as const, text: 'Scientists in South Korea created hybrid beef rice with 80% higher protein.' },
  { label: 'Submarine Tunnel Myth', type: 'text' as const, text: 'Secret submarine tunnels connect Lake Michigan directly to the Atlantic Ocean.' },
];

export default function VerifyPage() {
  const [activeTab, setActiveTab] = useState<'text' | 'url' | 'image'>('text');
  const [inputContent, setInputContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusStep, setStatusStep] = useState<string>('');
  const [verification, setVerification] = useState<Verification | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File | null) => {
    if (!file) return;
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (loading) return;

    if (activeTab === 'image' && !selectedFile) {
      setError('Please select or drop an image file to verify.');
      return;
    }

    if (activeTab !== 'image' && !inputContent.trim()) {
      setError('Please enter a claim or article URL to verify.');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      if (activeTab === 'image' && selectedFile) {
        setStatusStep('Extracting visual claims & transcribing text with Gemini Vision...');
        const t1 = setTimeout(() => {
          setStatusStep('Evaluating Sightengine AI forensics & digital manipulation signals...');
        }, 1500);
        const t2 = setTimeout(() => {
          setStatusStep('Querying Tavily for reverse context, origins, and debunk records...');
        }, 3500);

        const result = await verifyImage(selectedFile);
        clearTimeout(t1);
        clearTimeout(t2);
        setVerification(result);
      } else {
        setStatusStep('Extracting checkable factual claims...');
        const t1 = setTimeout(() => {
          setStatusStep('Searching Tavily for authoritative evidence & fact-checks...');
        }, 1200);
        const t2 = setTimeout(() => {
          setStatusStep('Synthesizing structured 6-part verdict with integrity guards...');
        }, 3500);

        const result = await verifyClaim({
          content: inputContent.trim(),
          content_type: activeTab,
        });
        clearTimeout(t1);
        clearTimeout(t2);
        setVerification(result);
      }
    } catch (err: any) {
      setError(err.message || 'Verification pipeline encountered an error. Please try again.');
    } finally {
      setLoading(false);
      setStatusStep('');
    }
  };

  const handleSelectSample = (sampleText: string) => {
    setInputContent(sampleText);
    setActiveTab(sampleText.startsWith('http') ? 'url' : 'text');
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  const handleReset = () => {
    setVerification(null);
    setInputContent('');
    setSelectedFile(null);
    setPreviewUrl(null);
    setError(null);
  };

  return (
    <>
      <Navbar />

      <main style={{ minHeight: 'calc(100vh - 68px)', backgroundColor: 'var(--color-mist)', padding: '48px 0 80px' }}>
        <div className="container" style={{ maxWidth: 900 }}>
          
          {/* Header */}
          <div style={{ marginBottom: 32, textAlign: 'center' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <span className="mono-meta" style={{
                backgroundColor: 'var(--color-signal-white)',
                border: '1px solid var(--color-bone)',
                padding: '4px 12px',
                borderRadius: 9999,
                color: 'var(--color-brand-violet)',
              }}>
                LUCENT // MULTIMODAL VERIFICATION CONSOLE
              </span>
            </div>
            <h1 className="section-headline" style={{ marginBottom: 8 }}>
              What do you want to verify today?
            </h1>
            <p style={{ color: 'var(--color-slate)', fontSize: 16 }}>
              Submit a factual claim, article URL, or upload an image to inspect evidence and forensics.
            </p>
          </div>

          {/* ─── Verification Input Form (When no verification active) ────── */}
          {!verification && (
            <div className="card-flat" style={{ padding: '36px', marginBottom: 32 }}>
              
              {/* Tab Selector */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 24, flexWrap: 'wrap' }}>
                <button
                  type="button"
                  className={`tag-pill ${activeTab === 'text' ? 'tag-pill-active' : ''}`}
                  onClick={() => setActiveTab('text')}
                  disabled={loading}
                >
                  ✏️ Text Claim
                </button>
                <button
                  type="button"
                  className={`tag-pill ${activeTab === 'url' ? 'tag-pill-active' : ''}`}
                  onClick={() => setActiveTab('url')}
                  disabled={loading}
                >
                  🔗 News / Article URL
                </button>
                <button
                  type="button"
                  className={`tag-pill ${activeTab === 'image' ? 'tag-pill-active' : ''}`}
                  onClick={() => setActiveTab('image')}
                  disabled={loading}
                >
                  🖼️ Image / Media Forensics
                </button>
              </div>

              {/* Form Input */}
              <form onSubmit={handleVerify}>
                
                {/* Text & URL Inputs */}
                {activeTab !== 'image' && (
                  <div style={{ marginBottom: 20 }}>
                    <textarea
                      className="input-text"
                      rows={activeTab === 'text' ? 4 : 2}
                      placeholder={
                        activeTab === 'text'
                          ? 'Paste or type a claim to verify...\nExample: "Scientists in South Korea created hybrid beef rice with 80% higher protein."'
                          : 'Paste an article URL (e.g. https://www.reuters.com/world/...)'
                      }
                      value={inputContent}
                      onChange={(e) => setInputContent(e.target.value)}
                      disabled={loading}
                      autoFocus
                      style={{ fontSize: 15, lineHeight: 1.5 }}
                    />
                  </div>
                )}

                {/* Image Upload Input */}
                {activeTab === 'image' && (
                  <div style={{ marginBottom: 24 }}>
                    <input
                      type="file"
                      ref={fileInputRef}
                      style={{ display: 'none' }}
                      accept="image/png, image/jpeg, image/webp"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          handleFileChange(e.target.files[0]);
                        }
                      }}
                    />

                    {!previewUrl ? (
                      <div
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        style={{
                          border: '2px dashed var(--color-cloud)',
                          borderRadius: 'var(--radius-cards)',
                          padding: '40px 20px',
                          textAlign: 'center',
                          cursor: 'pointer',
                          backgroundColor: 'var(--color-mist)',
                          transition: 'border-color 0.15s ease',
                        }}
                      >
                        <div style={{ fontSize: 36, marginBottom: 12 }}>🖼️</div>
                        <h3 style={{ fontFamily: 'var(--font-family-display)', fontSize: 16, fontWeight: 700, marginBottom: 4 }}>
                          Click to upload or drag and drop an image
                        </h3>
                        <p style={{ fontSize: 13, color: 'var(--color-slate)' }}>
                          Supports PNG, JPG, JPEG, and WebP (Forensics, AI-detection & claim verification)
                        </p>
                      </div>
                    ) : (
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 20,
                        padding: 16,
                        border: '1px solid var(--color-bone)',
                        borderRadius: 'var(--radius-cards)',
                        backgroundColor: 'var(--color-mist)',
                      }}>
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={previewUrl}
                          alt="Upload preview"
                          style={{ width: 90, height: 90, objectFit: 'cover', borderRadius: 8, border: '1px solid var(--color-bone)' }}
                        />
                        <div style={{ flex: 1 }}>
                          <h4 style={{ fontFamily: 'var(--font-family-display)', fontSize: 15, fontWeight: 700 }}>
                            {selectedFile?.name}
                          </h4>
                          <p style={{ fontSize: 13, color: 'var(--color-slate)', marginTop: 2 }}>
                            {selectedFile ? `${(selectedFile.size / 1024).toFixed(1)} KB` : ''} · Ready for Multimodal Forensics
                          </p>
                        </div>
                        <button
                          type="button"
                          className="btn btn-ghost-outline"
                          onClick={() => {
                            setSelectedFile(null);
                            setPreviewUrl(null);
                          }}
                          style={{ fontSize: 12, padding: '6px 14px' }}
                        >
                          Change File
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Quick Sample Chips for Text */}
                {activeTab !== 'image' && (
                  <div style={{ marginBottom: 24 }}>
                    <span className="mono-meta" style={{ display: 'block', marginBottom: 8, color: 'var(--color-ash)' }}>
                      TRY A SAMPLE CLAIM:
                    </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {QUICK_SAMPLES.map((sample) => (
                        <button
                          key={sample.label}
                          type="button"
                          className="tag-pill"
                          style={{ fontSize: 12, padding: '4px 12px' }}
                          onClick={() => handleSelectSample(sample.text)}
                          disabled={loading}
                        >
                          {sample.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Loading Status Bar */}
                {loading && (
                  <div style={{
                    padding: '16px 20px',
                    backgroundColor: '#eff6ff',
                    border: '1px solid #bfdbfe',
                    borderRadius: 'var(--radius-inputs)',
                    marginBottom: 20,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                  }}>
                    <div style={{
                      width: 16,
                      height: 16,
                      border: '2px solid #3b82f6',
                      borderTopColor: 'transparent',
                      borderRadius: '50%',
                      animation: 'rotateConic 1s linear infinite',
                    }} />
                    <span style={{ fontSize: 14, color: '#1e40af', fontWeight: 600 }}>
                      {statusStep || 'Processing verification pipeline...'}
                    </span>
                  </div>
                )}

                {/* Error Box */}
                {error && (
                  <div style={{
                    padding: '14px 18px',
                    backgroundColor: '#fef2f2',
                    border: '1px solid #fecaca',
                    borderRadius: 'var(--radius-inputs)',
                    color: '#991b1b',
                    fontSize: 14,
                    marginBottom: 20,
                  }}>
                    <strong>Error:</strong> {error}
                  </div>
                )}

                {/* Action CTA */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading || (activeTab === 'image' ? !selectedFile : !inputContent.trim())}
                    style={{ padding: '12px 32px', fontSize: 15 }}
                  >
                    {loading ? 'Analyzing Evidence...' : 'Run Verification &rarr;'}
                  </button>

                  <span className="mono-meta">
                    {activeTab === 'image' ? 'MULTIMODAL + SIGHTENGINE FORENSICS' : 'TARGET TIME: < 20S'}
                  </span>
                </div>
              </form>
            </div>
          )}

          {/* ─── Verification Result View (When verification completed) ──── */}
          {verification && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <button
                  type="button"
                  onClick={handleReset}
                  className="btn btn-ghost-outline"
                  style={{ fontSize: 13, padding: '6px 16px' }}
                >
                  &larr; Start Another Verification
                </button>

                <span className="mono-meta">
                  TYPE: {verification.content_type.toUpperCase()} · ID: {verification.id.slice(0, 8)}...
                </span>
              </div>

              {/* 6-Part Verdict Contract Card */}
              <VerdictCard verification={verification} />

              {/* Grounded Conversational Follow-Up Section */}
              <div style={{ marginTop: 32 }}>
                <FollowUpChat
                  verification={verification}
                  onUpdateVerification={(updated) => setVerification(updated)}
                />
              </div>
            </div>
          )}

        </div>
      </main>

      <Footer />
    </>
  );
}
