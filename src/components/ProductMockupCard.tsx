import styles from './ProductMockupCard.module.css';

interface Props {
  title: string;
  orbColor?: 'violet' | 'pink' | 'amber';
  children: React.ReactNode;
  floatDelay?: string;
}

export default function ProductMockupCard({ title, orbColor = 'violet', children, floatDelay = '0s' }: Props) {
  return (
    <div className={`${styles.wrapper} animate-float`} style={{ animationDelay: floatDelay }}>
      {/* Gradient orb behind the card */}
      <div className={`${styles.orb} ${styles[`orb--${orbColor}`]}`} aria-hidden />

      <div className={styles.card}>
        {/* macOS traffic-light dots */}
        <div className={styles.dots} aria-hidden>
          <span className={`${styles.dot} ${styles.dotRed}`} />
          <span className={`${styles.dot} ${styles.dotAmber}`} />
          <span className={`${styles.dot} ${styles.dotGreen}`} />
        </div>

        {/* Title bar */}
        <div className={styles.titleBar}>
          <span className={styles.portalLabel}>{title}</span>
        </div>

        {/* Content */}
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>
  );
}
