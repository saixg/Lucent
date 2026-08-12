import styles from './Footer.module.css';
import Link from 'next/link';

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.inner}`}>
        <div className={styles.brand}>
          <Link href="/" className="badge-white" style={{ textDecoration: 'none', marginBottom: 24, display: 'inline-flex' }}>
            <span className={styles.logoSquare} aria-hidden />
            <span>LUCENT</span>
          </Link>
          <p className={styles.tagline}>
            A modern developer console for social media claim verification, multimodal media forensics, and evidence retrieval.
          </p>
        </div>

        <div className={styles.cols}>
          <div className={styles.col}>
            <h4 className={styles.colTitle}>Product</h4>
            <Link href="/verify" className={styles.footerLink}>Intelligence</Link>
            <Link href="/#platform" className={styles.footerLink}>Lead Generation</Link>
            <Link href="/#verification" className={styles.footerLink}>Engagement</Link>
            <Link href="/#forensics" className={styles.footerLink}>Deliverability</Link>
          </div>
          <div className={styles.col}>
            <h4 className={styles.colTitle}>Company</h4>
            <span className={styles.footerLink}>About Us</span>
            <span className={styles.footerLink}>Careers</span>
            <span className={styles.footerLink}>Security</span>
            <span className={styles.footerLink}>Terms of Service</span>
          </div>
          <div className={styles.col}>
            <h4 className={styles.colTitle}>Resources</h4>
            <span className={styles.footerLink}>Blog</span>
            <span className={styles.footerLink}>Help Center</span>
            <span className={styles.footerLink}>Customer Stories</span>
            <span className={styles.footerLink}>System Status</span>
          </div>
        </div>
      </div>

      <div className={`container ${styles.bottom}`}>
        <p className={styles.copy}>© 2026 Lucent Inc. All rights reserved.</p>
        <p className={styles.copy}>Sunlit Workspace · Amplemarket Design System</p>
      </div>
    </footer>
  );
}
