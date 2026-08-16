'use client';

import { useState } from 'react';
import { submitFollowUp, Verification, FollowUpMessage } from '@/lib/api';

interface FollowUpChatProps {
  verification: Verification;
  onUpdateVerification: (updated: Verification) => void;
}

export default function FollowUpChat({ verification, onUpdateVerification }: FollowUpChatProps) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    setError(null);
    setLoading(true);

    try {
      const updated = await submitFollowUp(verification.id, question);
      onUpdateVerification(updated);
    } catch (err: any) {
      setError(err.message || 'Failed to submit follow-up question.');
    } finally {
      setLoading(false);
    }
  };

  const messages = verification.follow_up_messages || [];

  return (
    <div className="card-flat" style={{ padding: '28px' }}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <span className="mono-meta" style={{ color: 'var(--color-brand-violet)' }}>GROUNDED CONVERSATIONAL LAYER</span>
        </div>
        <h3 style={{
          fontFamily: 'var(--font-family-display)',
          fontSize: 18,
          fontWeight: 700,
          color: 'var(--color-onyx)',
        }}>
          Ask Follow-Up Questions
        </h3>
        <p style={{ fontSize: 13, color: 'var(--color-slate)', marginTop: 4 }}>
          Query this verification&apos;s evidence context directly without re-running the full pipeline.
        </p>
      </div>

      {/* Message History */}
      {messages.length > 0 && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
          marginBottom: 24,
          maxHeight: 400,
          overflowY: 'auto',
          paddingRight: 4,
        }}>
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            return (
              <div
                key={msg.id || idx}
                style={{
                  alignSelf: isUser ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  backgroundColor: isUser ? 'var(--color-ink-black)' : 'var(--color-mist)',
                  color: isUser ? '#ffffff' : 'var(--color-ink-black)',
                  padding: '12px 18px',
                  borderRadius: isUser ? '16px 16px 2px 16px' : '16px 16px 16px 2px',
                  border: isUser ? 'none' : '1px solid var(--color-bone)',
                  fontSize: 14,
                  lineHeight: 1.5,
                }}
              >
                <span style={{
                  display: 'block',
                  fontSize: 11,
                  fontWeight: 700,
                  marginBottom: 4,
                  opacity: 0.7,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  {isUser ? 'You' : 'Lucent'}
                </span>
                <div>{msg.content}</div>
              </div>
            );
          })}
        </div>
      )}

      {/* Suggested Follow-up Prompts */}
      {messages.length === 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
          {[
            'Why is this considered misleading?',
            'What do the primary sources say happened?',
            'Are there any conflicting reports?',
          ].map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="tag-pill"
              style={{ fontSize: 12, padding: '4px 12px' }}
              onClick={() => setInput(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {error && (
        <div style={{ padding: '10px 14px', backgroundColor: '#fef2f2', color: '#991b1b', borderRadius: 6, fontSize: 13, marginBottom: 16 }}>
          {error}
        </div>
      )}

      {/* Question Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 10 }}>
        <input
          type="text"
          className="input-text"
          placeholder="Ask a question about this evidence..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
          style={{ flex: 1, borderRadius: 'var(--radius-buttons)', padding: '10px 18px' }}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !input.trim()}
          style={{ padding: '10px 22px' }}
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </form>
    </div>
  );
}
