# Lucent — Build Phases

Follow in order. Don't start a phase until the previous one's exit criteria are met — see `rules.md` §5 on not gold-plating ahead of sequence. Update `memory.md`'s Status section whenever a phase completes.

---

## Phase 0 — Foundation & credential audit
**Goal**: Clean slate, verified credentials, confirmed stack — before any pipeline code is written.

- Run the credential re-validation checklist in `architecture.md` §7 for every key carried over from the old build.
- Stand up the new repo structure per `architecture.md` (don't copy old file layout).
- Confirm/lock the stack choices in `architecture.md` §4 (or override and update the doc).
- Set up `.env.example` with placeholders for every integration in `architecture.md` §6.
- Wire up bare-bones CI/deploy so every later phase ships to a real, checkable environment.

**Exit criteria**: A deployed "hello world" that can accept a text input and echo it back through the real infra (frontend → backend → DB round trip), with zero hardcoded secrets.

---

## Phase 1 — MVP: text & URL claim verification
**Goal**: The core loop works end-to-end for the simplest content type.

- Build [1] Ingestion for text/URL input only.
- Build [2] Evidence Gathering: web search + fact-check DB lookup only (no media forensics yet).
- Build [3] Synthesis & Verdict Engine enforcing the full 6-part contract (`prd.md` §6), including the `Unverifiable`-when-no-evidence guard from `rules.md` §2.
- Build [4] Response Formatting into a real UI screen (per `design.md` once available).
- Build [5] Conversational follow-up, scoped to stored evidence for that verification.

**Exit criteria**: Per `rules.md` §7 — manually run 3+ real text/URL claims end-to-end, confirm each output matches the verdict contract, confirm follow-up questions work without re-running the full pipeline.

---

## Phase 2 — Image verification
**Goal**: Extend ingestion + evidence gathering to images without breaking the text/URL path.

- Add image upload to [1] Ingestion & Classification.
- Add reverse-image-context search + AI-generation likelihood check to [2] Evidence Gathering.
- Confirm [3] Synthesis Engine handles image-sourced evidence with the same contract (no special-casing the output shape).
- Add async/job-queue handling per `architecture.md` §5 if image checks exceed the sync-response time budget.

**Exit criteria**: 3+ real image examples (at least one genuine, one AI-generated, one miscaptioned-but-real) verified end-to-end with correct verdict labels and non-empty evidence.

---

## Phase 3 — Video & audio verification
**Goal**: Extend to the highest-effort content types.

- Video: frame sampling, reverse-image search on key frames, manipulation-likelihood signals.
- Audio: transcription → claim extraction reusing the Phase 1 text pipeline where possible, plus voice-clone/synthetic-audio likelihood signals.
- Confirm async job handling scales to these longer-running checks; frontend must show real progress, not a spinner with no feedback (design.md should specify this once provided).

**Exit criteria**: 3+ real video and 3+ real audio examples verified end-to-end, including at least one deliberately manipulated example per type to confirm detection isn't just defaulting to `Unverifiable`.

---

## Phase 4 — Conversational depth & history
**Goal**: Make the "understand it, don't just get a label" promise real over multiple turns.

- Persist follow-up conversation history (`FollowUpMessage` table from `architecture.md` §3) if not already done.
- Improve follow-up grounding: confirm the model never drifts from the original evidence set without explicitly flagging "this needs a new check."
- (Optional, per `prd.md` §7) user accounts + saved verification history.

**Exit criteria**: A multi-turn conversation (5+ follow-ups) on a single verification stays grounded and consistent, verified manually.

---

## Phase 5 — Distribution surfaces
**Goal**: Move Lucent to where suspicious content is actually encountered, per `prd.md` §"Real-world usage".

- Browser extension / share-target integration (share-to-Lucent from platforms).
- Public API for third parties (journalists/orgs), with its own rate limiting and auth per `rules.md` §3–4.
- Revisit `prd.md` success metrics with real usage data before committing further scope.

**Exit criteria**: Defined once Phase 4 ships — do not pre-plan implementation details for this phase now, only keep it on the roadmap.

---

## Phase discipline reminders
- Each phase's exit criteria must be manually verified with real (not mocked) examples before moving on — per `rules.md` §7.
- If a phase reveals the verdict contract (`prd.md` §6) needs to change, stop, update `prd.md` first, then propagate the change — don't let implementation silently diverge from the documented contract.
- Log any deviation from this sequence in `memory.md` with a short reason, so future sessions understand why the order changed.