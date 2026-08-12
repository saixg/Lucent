'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './Navbar.module.css';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 16);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <nav className={`${styles.nav} ${scrolled ? styles.scrolled : ''}`}>
      <div className={styles.inner}>
        {/* Logo */}
        <Link href="/" className={styles.logo} id="nav-logo">
          <span className={styles.logoIcon} aria-hidden>✦</span>
          <span className={styles.logoText}>VeriLens</span>
        </Link>

        {/* Center links */}
        <div className={styles.links}>
          <Link href="#how-it-works" className={styles.link}>How it works</Link>
          <Link href="#features" className={styles.link}>Features</Link>
          <Link href="#verdicts" className={styles.link}>Verdicts</Link>
          <Link href="/verify" className={styles.link}>Demo</Link>
        </div>

        {/* Right CTA */}
        <div className={styles.actions}>
          <Link href="/verify" className={`btn btn--primary btn--compact ${styles.cta}`} id="nav-cta">
            Try VeriLens
          </Link>
        </div>
      </div>
    </nav>
  );
}
