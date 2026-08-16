import styles from './TestimonialCard.module.css';

interface Props {
  avatar: string;
  name: string;
  handle: string;
  quote: string;
  stars?: number;
}

export default function TestimonialCard({ avatar, name, handle, quote, stars = 5 }: Props) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.avatarWrap}>
          <div className={styles.avatar} style={{ background: avatar }}>
            {name.charAt(0)}
          </div>
          <div className={styles.info}>
            <span className={styles.name}>{name}</span>
            <span className={styles.handle}>{handle}</span>
          </div>
        </div>
        <span className={styles.close} aria-hidden>✕</span>
      </div>
      <p className={styles.quote}>{quote}</p>
      <div className={styles.stars}>
        {Array.from({ length: stars }).map((_, i) => (
          <span key={i}>★</span>
        ))}
      </div>
    </div>
  );
}
