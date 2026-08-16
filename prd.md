# Lucent — Product Requirements Document

## 1. One-liner
Lucent is an independent verification layer that lets anyone bring a piece of suspicious content (text claim, link, image, video, or audio) and get back a clear, evidence-backed explanation of what's actually true — not just a "real/fake" label.

## 2. Problem
People constantly encounter content they can't evaluate: a viral clip, a quote screenshot, an AI-generated image, a "leaked" audio clip. Today they have three bad options:
1. Believe it because everyone else is sharing it.
2. Distrust everything and disengage.
3. Manually search 5+ sites themselves, which almost nobody does.

Existing fact-checking sites are article-based, slow, and require the user to already know what to search for. There is no low-friction "drop content here, get the truth explained to you" experience.

## 3. Target users (v1 priority order)
1. **Everyday social media users** — encounter suspicious content passively, want a fast trustworthy answer.
2. **Students / researchers** — need sourced, citable explanations.
3. **Journalists** — need speed + evidence trail for verification during reporting.
4. **Organizations / community moderators** (later) — need bulk/API verification.

## 4. Core value proposition
Not "Fake News Detector." Lucent is a **verification conversation partner**:
- Takes ambiguous, messy input (screenshot, link, video file, raw claim).
- Produces a structured verdict + explanation + evidence, in plain language.
- Lets the user ask follow-up questions ("why?", "what actually happened?") and get contextual answers without re-submitting the content.

## 5. Core user flow
1. User submits content (paste text/URL, upload image/video/audio, or paste a claim).
2. Lucent classifies the content type and extracts the core checkable claim(s).
3. Lucent gathers evidence (web search, fact-check databases, media forensics as applicable).
4. Lucent synthesizes a verdict with a confidence level and plain-language explanation.
5. User can ask follow-up questions in the same thread; Lucent answers using the same evidence context (no need to resubmit).

## 6. Verdict output structure (contract — do not deviate without updating this doc)
Every verification response must contain:
- **Claim summary** — what is actually being claimed/shown.
- **Verdict label** — one of: `True`, `False`, `Misleading`, `Missing Context`, `Altered/Manipulated`, `AI-Generated`, `Unverifiable`.
- **Confidence** — `High` / `Medium` / `Low`, plus one-line reasoning for the confidence level itself.
- **Explanation** — what's actually going on, in plain language.
- **Evidence** — list of sources with title + link, each mapped to what it supports.
- **Follow-up affordance** — implicit; the system must retain enough context to answer "why?" without redoing the whole pipeline.

## 7. MVP scope (Phase 1 — see phases.md)
In scope:
- Text claim verification (paste a claim or a URL).
- Image verification: reverse-image-style context check + AI-generation likelihood.
- Conversational follow-up on a completed verification (chat-style, scoped to that verification's evidence).
- Source citations rendered as clickable links.

Out of scope for MVP (later phases):
- Video deepfake/lip-sync analysis.
- Audio voice-clone detection.
- Browser extension / platform integrations (share-to-Lucent from Instagram/X/etc).
- Public API for third parties.
- Bulk/batch verification for organizations.
- User accounts, history, saved verifications (nice-to-have, not blocking MVP).

## 8. Non-functional requirements
- **Time to first verdict**: target under 20s for text/URL claims, under 45s for image claims.
- **No unsupported claims**: every verdict must be traceable to at least one cited source, or explicitly marked `Unverifiable` — the system must never assert a verdict with zero evidence backing.
- **Neutral tone**: Lucent explains what evidence shows; it does not editorialize about people's opinions, only about factual/evidentiary claims.
- **Cost control**: every verification has a bounded cost (max N search calls, max M LLM calls) — see rules.md.
- **Graceful degradation**: if forensic/search tools fail, return partial results with an honest confidence downgrade rather than a fabricated verdict.

## 9. Success metrics (post-MVP)
- % of verdicts where user marks the explanation as "helpful/clear" (in-app feedback).
- Median time-to-verdict.
- % of verdicts with 2+ cited sources.
- Follow-up engagement rate (proxy for whether the conversational layer is actually useful vs. a gimmick).

## 10. Explicit non-goals
- Lucent does not tell users what opinions to hold — only what the evidence supports.
- Lucent does not silently "auto-moderate" content on any platform; it is a tool the user invokes.
- Lucent does not claim certainty it doesn't have — `Unverifiable` is a first-class, acceptable outcome.

## 11. Open assumptions (confirm before Phase 2)
- Primary input surface for MVP is a standalone web app (not yet a browser extension or platform integration).
- Existing API keys/credentials from the previous build are being reused as-is (see architecture.md §7 for the checklist to re-validate them before rebuild).