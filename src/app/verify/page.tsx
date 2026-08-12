'use client';
import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import styles from './page.module.css';
import { createInvestigation, uploadFile, pollUntilComplete } from '@/lib/api';

type Tab = 'url' | 'upload' | 'text';

const STATUS_MESSAGES: Record<string, string> = {
  pending: 'Queued for analysis...',
  processing: 'Running verification pipeline...',
  complete: 'Complete!',
  failed: 'Investigation failed',
};

function VerifyContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState<Tab>('url');
  const [url, setUrl] = useState('');
  const [text, setText] = useState('');
  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    const queryParam = searchParams.get('q');
    if (queryParam) {
      if (queryParam.startsWith('http://') || queryParam.startsWith('https://')) {
        setTab('url');
        setUrl(queryParam);
      } else {
        setTab('text');
        setText(queryParam);
      }
    }
  }, [searchParams]);

  const handleVerify = async () => {
    setError('');
    setLoading(true);
    setProgress(5);

    try {
      let inv;

      if (tab === 'upload' && selectedFile) {
        setStatus('Uploading file...');
        inv = await uploadFile(selectedFile);
      } else if (tab === 'url' && url) {
        const platform = url.includes('youtube') ? 'youtube'
          : url.includes('twitter.com') || url.includes('x.com') ? 'x'
          : url.includes('instagram') ? 'instagram'
          : 'web';
        inv = await createInvestigation({
          input_type: `${platform}_url`,
          input_url: url,
          platform,
        });
      } else if (tab === 'text' && text) {
        inv = await createInvestigation({
          input_type: 'text',
          input_text: text,
          platform: 'web',
        });
      } else {
        setError('Please provide a URL, file, or text claim to verify.');
        setLoading(false);
        return;
      }

      setStatus('pending');
      setProgress(10);

      // Poll until complete
      const completed = await pollUntilComplete(
        inv.id,
        (s, p) => {
          setStatus(s);
          setProgress(p ?? 50);
        },
      );

      setProgress(100);
      router.push(`/investigation/${completed.id}`);
    } catch (e: any) {
      setError(e.message || 'Verification failed. Please try again.');
      setLoading(false);
      setStatus('');
      setProgress(0);
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) { setSelectedFile(file); setTab('upload'); }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setSelectedFile(file);
  };

  return (
    <>
      <Navbar />
      <main className={`blueprint-grid-bg ${styles.main}`}>
        <div className={`container ${styles.inner}`}>

          <div className={styles.header}>
            <div style={{ fontFamily: 'var(--font-geistmono)', fontSize: 12, color: 'var(--color-mute-gray)', marginBottom: 8 }}>
              LUCENT // VERIFICATION WORKSPACE v2.4
            </div>
            <h1 className={styles.headline}>
              What do you want to verify today?
            </h1>
            <p className={styles.subtitle}>
              Paste a URL, upload media, or submit a claim. Lucent extracts statements and cross-examines evidence across primary databases.
            </p>
          </div>

          <div className={styles.card}>
            {/* Tab switcher */}
            <div className={styles.tabs} role="tablist">
              {([
                { id: 'url', label: '🔗 URL / Link' },
                { id: 'upload', label: '⬆ Upload Media' },
                { id: 'text', label: '✏ Text Claim' },
              ] as { id: Tab; label: string }[]).map(t => (
                <button
                  key={t.id}
                  role="tab"
                  aria-selected={tab === t.id}
                  id={`tab-${t.id}`}
                  className={`${styles.tab} ${tab === t.id ? styles.tabActive : ''}`}
                  onClick={() => setTab(t.id)}
                  disabled={loading}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* URL Tab */}
            {tab === 'url' && (
              <div className={styles.tabPanel} id="panel-url">
                <div className={styles.inputGroup}>
                  <div className={styles.inputWrap}>
                    <span className={styles.inputIcon}>🔗</span>
                    <input
                      id="url-input"
                      type="url"
                      className={styles.input}
                      placeholder="Paste YouTube, Instagram Reel, X post, or web article URL..."
                      value={url}
                      onChange={e => setUrl(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && handleVerify()}
                      autoFocus
                      disabled={loading}
                    />
                    {url && !loading && (
                      <button className={styles.clearBtn} onClick={() => setUrl('')} aria-label="Clear">✕</button>
                    )}
                  </div>
                  <div className={styles.platformChips}>
                    <span className={styles.platformLabel}>SAMPLE URLS:</span>
                    {[
                      { name: 'YouTube', sample: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' },
                      { name: 'Twitter/X', sample: 'https://x.com/NASA/status/1758203859203958' },
                      { name: 'Instagram', sample: 'https://www.instagram.com/reel/C8X12345678/' },
                      { name: 'News Article', sample: 'https://www.reuters.com/world/' },
                    ].map(p => (
                      <button
                        key={p.name}
                        className={styles.platformChip}
                        onClick={() => { setTab('url'); setUrl(p.sample); }}
                        disabled={loading}
                      >
                        {p.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Upload Tab */}
            {tab === 'upload' && (
              <div className={styles.tabPanel} id="panel-upload">
                <div
                  className={`${styles.dropzone} ${dragging ? styles.dropzoneDragging : ''} ${selectedFile ? styles.dropzoneHasFile : ''}`}
                  onDragOver={e => { e.preventDefault(); setDragging(true); }}
                  onDragLeave={() => setDragging(false)}
                  onDrop={handleFileDrop}
                >
                  {selectedFile ? (
                    <>
                      <div className={styles.dropzoneIcon}>✓</div>
                      <p className={styles.dropzoneTitle}>{selectedFile.name}</p>
                      <p className={styles.dropzoneSubtitle}>{(selectedFile.size / 1024 / 1024).toFixed(1)} MB</p>
                      <button className="btn btn--ghost-outline" style={{ marginTop: 8, height: 36, fontSize: 12 }} onClick={() => setSelectedFile(null)}>
                        Change file
                      </button>
                    </>
                  ) : (
                    <>
                      <div className={styles.dropzoneIcon}>⬆</div>
                      <p className={styles.dropzoneTitle}>Drop media file here</p>
                      <p className={styles.dropzoneSubtitle}>MP4, MOV, MP3, JPG, PNG, WebP — up to 200MB</p>
                      <label htmlFor="file-input" className="btn btn--ghost-outline" style={{ cursor: 'pointer', marginTop: 8, height: 36, fontSize: 12 }}>
                        Browse Files
                      </label>
                      <input id="file-input" type="file" hidden accept="video/*,audio/*,image/*" onChange={handleFileSelect} />
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Text Tab */}
            {tab === 'text' && (
              <div className={styles.tabPanel} id="panel-text">
                <textarea
                  id="text-input"
                  className={styles.textarea}
                  placeholder={'Paste or type a claim to verify...\n\nExample: "The government has banned UPI transactions starting August 15, 2026."'}
                  value={text}
                  onChange={e => setText(e.target.value)}
                  rows={6}
                  autoFocus
                  disabled={loading}
                />
              </div>
            )}

            {/* Progress bar */}
            {loading && (
              <div className={styles.progressWrap}>
                <div className={styles.progressBar} style={{ width: `${progress}%` }} />
                <p className={styles.progressLabel}>
                  {STATUS_MESSAGES[status] || status || 'Analyzing...'}
                </p>
              </div>
            )}

            {/* Error */}
            {error && <div className={styles.errorBox}>{error}</div>}

            {/* Action button */}
            <div className={styles.verifyAction}>
              <button
                id="start-verification-btn"
                className={`btn btn--primary-pill ${styles.verifyBtn}`}
                onClick={handleVerify}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className={styles.spinner} />
                    Processing Pipeline...
                  </>
                ) : (
                  'Start Verification'
                )}
              </button>
              <p className={styles.verifyMeta}>
                Powered by Gemini 3.6 Flash · Tavily Evidence Ranker · Sightengine & Hive Forensics
              </p>
            </div>

          </div>

        </div>
      </main>

      <Footer />
    </>
  );
}

export default function VerifyPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyContent />
    </Suspense>
  );
}
