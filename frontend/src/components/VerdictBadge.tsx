import styles from './VerdictBadge.module.css';

type Verdict = 'VERIFIED' | 'FALSE' | 'MISLEADING' | 'OUT_OF_CONTEXT' | 'MANIPULATED' | 'UNVERIFIED';

interface Props {
  verdict: Verdict;
  size?: 'sm' | 'md' | 'lg';
}

const VERDICT_CONFIG: Record<Verdict, { label: string; icon: string; className: string }> = {
  VERIFIED:      { label: 'Verified',       icon: '✓', className: styles.verified },
  FALSE:         { label: 'False',           icon: '✕', className: styles.false_verdict },
  MISLEADING:    { label: 'Misleading',      icon: '⚠', className: styles.misleading },
  OUT_OF_CONTEXT:{ label: 'Out of Context',  icon: '◎', className: styles.outOfContext },
  MANIPULATED:   { label: 'Manipulated',     icon: '⚡', className: styles.manipulated },
  UNVERIFIED:    { label: 'Unverified',      icon: '?', className: styles.unverified },
};

export default function VerdictBadge({ verdict, size = 'md' }: Props) {
  const config = VERDICT_CONFIG[verdict];
  return (
    <span className={`${styles.badge} ${config.className} ${styles[size]}`}>
      <span className={styles.icon}>{config.icon}</span>
      {config.label}
    </span>
  );
}
