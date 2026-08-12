'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import styles from './Navbar.module.css';

export default function Navbar() {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <header className={`${styles.navHeader} ${scrolled ? styles.scrolled : ''}`}>
        <div className={styles.inner}>
          {/* Left: Logo mark (White Pill Badge style) */}
          <Link href="/" className="badge-white" style={{ textDecoration: 'none' }}>
            <span className={styles.logoSquare} aria-hidden />
            <span>LUCENT</span>
          </Link>

          {/* Center: Search & Nav Links */}
          <div className={styles.centerSection}>
            <nav className={styles.links}>
              <Link href="/#product" className={styles.link}>Product</Link>
              <Link href="/#why-us" className={styles.link}>Why us</Link>
              <Link href="/#resources" className={styles.link}>Resources</Link>
              <Link href="/#customers" className={styles.link}>Customers</Link>
              <Link href="/#pricing" className={styles.link}>Pricing</Link>
            </nav>
          </div>

          {/* Right: Dual-action cluster (ghost + filled) */}
          <div className={styles.actions}>
            <Link href="/verify" className="btn btn--ghost">
              Open app
            </Link>
            <Link href="/verify" className="btn btn--primary">
              Get started
            </Link>
          </div>
        </div>
      </header>
    </>
  );
}
