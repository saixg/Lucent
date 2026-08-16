'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      backgroundColor: 'rgba(255, 255, 255, 0.92)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--color-bone)',
      height: 68,
      display: 'flex',
      alignItems: 'center',
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Brand Logo & Tag */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              backgroundColor: 'var(--color-ink-black)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontFamily: 'var(--font-family-display)',
              fontWeight: 800,
              fontSize: 18,
            }}>
              L
            </div>
            <span style={{
              fontFamily: 'var(--font-family-display)',
              fontSize: 20,
              fontWeight: 800,
              letterSpacing: '-0.03em',
              color: 'var(--color-onyx)',
            }}>
              Lucent
            </span>
          </Link>

          <span className="mono-meta" style={{
            backgroundColor: 'var(--color-mist)',
            padding: '3px 8px',
            borderRadius: 9999,
            border: '1px solid var(--color-bone)',
            color: 'var(--color-brand-violet)',
            fontWeight: 600,
          }}>
            VERIFICATION CORE
          </span>
        </div>

        {/* Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Link
            href="/"
            className="btn btn-nav-pill"
            style={{ color: pathname === '/' ? 'var(--color-onyx)' : 'var(--color-slate)' }}
          >
            Overview
          </Link>
          <Link
            href="/verify"
            className="btn btn-nav-pill"
            style={{ color: pathname.startsWith('/verify') ? 'var(--color-onyx)' : 'var(--color-slate)' }}
          >
            Verify Console
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noreferrer"
            className="btn btn-nav-pill"
            style={{ color: 'var(--color-slate)' }}
          >
            Standards
          </a>
        </nav>

        {/* Action Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Link href="/verify" className="btn btn-primary" style={{ padding: '8px 18px', fontSize: 13 }}>
            New Verification &rarr;
          </Link>
        </div>
      </div>
    </header>
  );
}
