'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import styles from './page.module.css';

export default function Home() {
  const router = useRouter();
  const [email, setEmail] = useState('');

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault();
    router.push('/verify');
  };

  return (
    <>
      <Navbar />

      <main className={styles.main}>
        {/* ─── Hero Section ──────────────────────── */}
        <section className={styles.heroSection}>
          <div className={styles.heroGradientAtmosphere}></div>
          <div className={`container ${styles.heroContainer}`}>
            <h1 className="hero-headline" style={{ marginBottom: 24, maxWidth: 900, textAlign: 'center' }}>
              See beyond the feed.<br />
              Know what&apos;s real.
            </h1>
            <p className={styles.heroSubtitle}>
              Lucent is a modern verification console. Cross-examine claims, inspect multimodal forensics, and query Tier-1 primary sources instantly.
            </p>
            
            <form className="email-capture-row" onSubmit={handleStart}>
              <input 
                type="email" 
                className="input-field" 
                placeholder="Enter your work email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <button type="submit" className="btn btn--primary">
                Get started
              </button>
            </form>
          </div>

          {/* Hero Video Container */}
          <div className={`container ${styles.videoContainerWrapper}`}>
            <div className={styles.heroVideoContainer}>
              <div className={styles.playButton}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Logo Grid Section ──────────────────────── */}
        <section className={`section ${styles.logoSection}`}>
          <div className={`container ${styles.logoGrid}`}>
            <div className="card-logo-grid">
              <span className={styles.socialLogo}>REUTERS VERIFY</span>
              <span className={styles.migrationCaption}>Migrated off legacy tools</span>
            </div>
            <div className="card-logo-grid">
              <span className={styles.socialLogo}>ASSOCIATED PRESS</span>
              <span className={styles.migrationCaption}>Migrated off legacy tools</span>
            </div>
            <div className="card-logo-grid">
              <span className={styles.socialLogo}>BBC VERIFY</span>
              <span className={styles.migrationCaption}>Migrated off legacy tools</span>
            </div>
            <div className="card-logo-grid">
              <span className={styles.socialLogo}>POYNTER</span>
              <span className={styles.migrationCaption}>Migrated off legacy tools</span>
            </div>
          </div>
        </section>

        {/* ─── Pastel Category Cards (Taxonomy) ──────────────────────── */}
        <section className={`section section--cream`}>
          <div className="container">
            <h2 className="section-headline" style={{ textAlign: 'center', marginBottom: 80 }}>
              The complete verification stack
            </h2>
            
            <div className={styles.pastelGrid}>
              <div className="card-pastel card-pastel--pink">
                <h3 className={styles.pastelTitle}>Intelligence</h3>
                <p className={styles.pastelBody}>Converts viral videos, audio tracks, and social posts into atomic factual claims using Gemini 3.6 Flash.</p>
              </div>
              
              <div className="card-pastel card-pastel--green">
                <h3 className={styles.pastelTitle}>Lead Gen</h3>
                <p className={styles.pastelBody}>Cross-examines claims against Tavily search index, academic archives, and Tier-1 primary news sources.</p>
              </div>
              
              <div className="card-pastel card-pastel--yellow">
                <h3 className={styles.pastelTitle}>Engagement</h3>
                <p className={styles.pastelBody}>Analyzes frame authenticity, EXIF metadata, and visual manipulation with Sightengine and Hive APIs.</p>
              </div>
              
              <div className="card-pastel card-pastel--violet">
                <h3 className={styles.pastelTitle}>Deliver</h3>
                <p className={styles.pastelBody}>Grounded conversational assistant providing structured 3-part breakdowns of any investigation.</p>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Light Feature Cards ──────────────────────── */}
        <section className={`section`}>
          <div className="container">
            <div className={styles.lightFeatureGrid}>
              <div className="card-light">
                <h3 className={styles.lightFeatureTitle}>99.9% Uptime</h3>
                <p className={styles.lightFeatureBody}>On primary evidence sources and databases. We ensure maximum reliability for your investigations.</p>
              </div>
              <div className="card-light">
                <h3 className={styles.lightFeatureTitle}>5,000+ Teams</h3>
                <p className={styles.lightFeatureBody}>Verification teams relying on Lucent infrastructure globally to combat misinformation.</p>
              </div>
              <div className="card-light">
                <h3 className={styles.lightFeatureTitle}>&lt; 200ms Latency</h3>
                <p className={styles.lightFeatureBody}>Real-time processing for multimodal forensics and metadata extraction.</p>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Dark Testimonial Section ──────────────────────── */}
        <section className={`section section--dark`}>
          <div className="container">
            <h2 className="section-headline-dark" style={{ textAlign: 'center', marginBottom: 80 }}>
              Loved by verification teams
            </h2>
            
            <div className={styles.testimonialGrid}>
              <div className="card-dark-testimonial">
                <p className={styles.testimonialQuote}>"Lucent transformed how quickly we can verify breaking news videos on social media."</p>
                <div className={styles.testimonialAuthor}>
                  <div className={styles.avatar}></div>
                  <div>
                    <div className={styles.authorName}>Sarah Jenkins</div>
                    <div className={styles.authorRole}>Lead Investigator</div>
                  </div>
                </div>
              </div>
              
              <div className="card-dark-testimonial">
                <p className={styles.testimonialQuote}>"The multimodal forensics alone replaced three different tools in our daily workflow."</p>
                <div className={styles.testimonialAuthor}>
                  <div className={styles.avatar}></div>
                  <div>
                    <div className={styles.authorName}>David Chen</div>
                    <div className={styles.authorRole}>OSINT Analyst</div>
                  </div>
                </div>
              </div>

              <div className="card-dark-testimonial">
                <p className={styles.testimonialQuote}>"Unparalleled accuracy in matching claims with primary sources. It's a game changer."</p>
                <div className={styles.testimonialAuthor}>
                  <div className={styles.avatar}></div>
                  <div>
                    <div className={styles.authorName}>Elena Rodriguez</div>
                    <div className={styles.authorRole}>Fact-Checker</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

      </main>

      <Footer />
    </>
  );
}
