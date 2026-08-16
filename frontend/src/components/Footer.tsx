import Link from 'next/link';

export default function Footer() {
  return (
    <footer style={{
      backgroundColor: '#111111',
      color: '#ffffff',
      borderTop: '1px solid #222222',
      padding: '64px 0 40px',
      marginTop: 'auto',
    }}>
      <div className="container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: 48,
          marginBottom: 48,
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <div style={{
                width: 28,
                height: 28,
                borderRadius: 6,
                backgroundColor: '#ffffff',
                color: '#111111',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: 'var(--font-family-display)',
                fontWeight: 800,
                fontSize: 16,
              }}>
                L
              </div>
              <span style={{
                fontFamily: 'var(--font-family-display)',
                fontSize: 18,
                fontWeight: 800,
                color: '#ffffff',
              }}>
                Lucent
              </span>
            </div>
            <p style={{ color: '#888888', fontSize: 14, lineHeight: 1.6, maxWidth: 300 }}>
              An independent verification layer delivering evidence-grounded verdicts and plain-language truth.
            </p>
          </div>

          <div>
            <h4 style={{
              fontFamily: 'var(--font-family-display)',
              fontSize: 14,
              fontWeight: 700,
              color: '#ffffff',
              marginBottom: 16,
            }}>
              Product
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10, fontSize: 14 }}>
              <li>
                <Link href="/verify" style={{ color: '#aaaaaa', transition: 'color 0.15s' }}>
                  Text Claim Verification
                </Link>
              </li>
              <li>
                <Link href="/verify" style={{ color: '#aaaaaa', transition: 'color 0.15s' }}>
                  URL Article Fact-Check
                </Link>
              </li>
              <li>
                <span style={{ color: '#666666' }}>
                  Media Forensics (Phase 2)
                </span>
              </li>
            </ul>
          </div>

          <div>
            <h4 style={{
              fontFamily: 'var(--font-family-display)',
              fontSize: 14,
              fontWeight: 700,
              color: '#ffffff',
              marginBottom: 16,
            }}>
              Core Principles
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 10, fontSize: 14, color: '#aaaaaa' }}>
              <li>100% Sourced Citations</li>
              <li>Zero Opinion Bias</li>
              <li>First-Class Unverifiable Guards</li>
              <li>Grounded Conversational Context</li>
            </ul>
          </div>
        </div>

        <div style={{
          borderTop: '1px solid #222222',
          paddingTop: 24,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 16,
          fontSize: 13,
          color: '#666666',
        }}>
          <p>© {new Date().getFullYear()} Lucent Verification System. Built on primary evidence standards.</p>
          <div style={{ display: 'flex', gap: 20 }}>
            <span>Privacy</span>
            <span>Terms</span>
            <span>Security</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
