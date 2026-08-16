'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import VerdictCard from '@/components/VerdictCard';
import FollowUpChat from '@/components/FollowUpChat';
import { getVerification, Verification } from '@/lib/api';

export default function VerificationDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [verification, setVerification] = useState<Verification | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getVerification(id)
      .then((data) => {
        setVerification(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load verification');
        setLoading(false);
      });
  }, [id]);

  return (
    <>
      <Navbar />

      <main style={{ minHeight: 'calc(100vh - 68px)', backgroundColor: 'var(--color-mist)', padding: '48px 0 80px' }}>
        <div className="container" style={{ maxWidth: 900 }}>
          
          <div style={{ marginBottom: 24 }}>
            <Link href="/verify" className="btn btn-ghost-outline" style={{ fontSize: 13, padding: '6px 16px' }}>
              &larr; Back to Verify Console
            </Link>
          </div>

          {loading && (
            <div className="card-flat" style={{ textAlign: 'center', padding: '60px 20px' }}>
              <div style={{
                width: 24,
                height: 24,
                border: '3px solid var(--color-brand-violet)',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'rotateConic 1s linear infinite',
                margin: '0 auto 16px',
              }} />
              <p style={{ color: 'var(--color-slate)', fontSize: 15 }}>Loading verification record {id}...</p>
            </div>
          )}

          {error && (
            <div className="card-flat" style={{ textAlign: 'center', padding: '40px 20px' }}>
              <h2 style={{ color: '#991b1b', marginBottom: 8, fontSize: 20 }}>Verification Not Found</h2>
              <p style={{ color: 'var(--color-slate)', marginBottom: 20 }}>{error}</p>
              <Link href="/verify" className="btn btn-primary">
                Return to Verification Console
              </Link>
            </div>
          )}

          {verification && (
            <div>
              <VerdictCard verification={verification} />

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
