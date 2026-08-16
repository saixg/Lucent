# Lucent — Architecture

> Assumptions flagged with **[ASSUMED]** are defaults chosen to unblock the rebuild — override freely, but update this doc when you do, since `memory.md` and `phases.md` both reference it.

## 1. System overview

```
User Input (text / URL / image / video / audio)
        │
        ▼
 [1] Ingestion & Classification
        │  → detects content type, extracts checkable claim(s)
        ▼
 [2] Evidence Gathering  ──────────────┐
        │  → web search                │  → media forensics
        │  → fact-check DB lookup      │     (reverse image, AI-gen detection,
        │  → source retrieval          │      deepfake/voice-clone — phased in)
        ▼                              ▼
 [3] Synthesis & Verdict Engine (LLM-driven, evidence-grounded)
        │  → produces the 6-part verdict contract (prd.md §6)
        ▼
 [4] Response Formatting
        │  → structured verdict + citations
        ▼
 [5] Conversational Follow-up Layer
        │  → answers "why?" using the SAME evidence context, no re-run of full pipeline
        ▼
      User
```

## 2. Components

### [1] Ingestion & Classification
- Accepts: pasted text/claim, URL, uploaded image, uploaded video, uploaded audio.
- Responsibilities: detect content type, normalize input (e.g. resolve URL → fetch page text, extract frames from video, transcribe audio if needed), extract the core checkable claim(s) as structured text.
- Output: `{ content_type, raw_input_ref, extracted_claims[] }`

### [2] Evidence Gathering
Runs different sub-pipelines depending on content type, but all funnel into a common `Evidence[]` structure: `{ source_title, source_url, snippet, supports | contradicts | context_only }`.

- **Text/claim/URL path**: web search + fact-check database lookups (e.g. existing fact-checker APIs/indexes) for the extracted claim(s).
- **Image path**: reverse-image-style context search (has this image appeared before, in what context) + AI-generation likelihood check.
- **Video path** *(Phase 3+)*: frame sampling + reverse-image search on key frames, deepfake/manipulation likelihood signals.
- **Audio path** *(Phase 3+)*: transcription + claim extraction from transcript, voice-clone/synthetic-audio likelihood signals.

Every sub-pipeline respects the call caps defined in `rules.md` §4.

### [3] Synthesis & Verdict Engine
- LLM call that receives: extracted claim(s) + full `Evidence[]` array (never a summary that drops source attribution).
- Must output the structured 6-part contract from `prd.md` §6.
- Hard constraint: if `Evidence[]` is empty or all items are `context_only` with nothing decisive, output must be `Unverifiable` — this should be enforced in code (a validation/guard step), not left to LLM discretion alone.
- **[ASSUMED]** Structured output enforced via JSON schema / tool-call style output rather than free-form text parsing, to keep the verdict contract machine-reliable for the frontend.

### [4] Response Formatting
- Converts the verdict object into the UI-ready shape (per `design.md`, once provided).
- Attaches evidence as clickable source cards.
- Persists the verdict + evidence bundle keyed by a verification ID, so the follow-up layer can reference it without recomputation.

### [5] Conversational Follow-up Layer
- Takes a user follow-up message + the stored verification ID.
- Loads the original `Evidence[]` + verdict object as context for a scoped LLM call.
- Does **not** re-run the full ingestion/evidence-gathering pipeline unless the user's follow-up introduces genuinely new content to check (in which case it should route back to [1] as a new verification, not pretend to answer from stale context).

## 3. Data model (minimum viable)

- **Verification**
  `id, created_at, content_type, raw_input_ref, extracted_claims[], verdict_label, confidence_level, confidence_reason, explanation, evidence[] (FK), status`
- **Evidence**
  `id, verification_id (FK), source_title, source_url, snippet, relation (supports|contradicts|context_only)`
- **FollowUpMessage** *(if conversational history is persisted — optional for MVP per prd.md §7)*
  `id, verification_id (FK), role (user|assistant), content, created_at`

**[ASSUMED]** Relational store (Postgres) for this data — swap freely if the existing credentials point at a different provider already set up.

## 4. Confirmed Stack
- **Frontend**: Next.js (React / TypeScript).
- **Backend / verification service**: FastAPI / Python 3.13 service, separated from the frontend with clean async orchestration.
- **Database**: PostgreSQL (via `DATABASE_URL`, SQLAlchemy + asyncpg).
- **LLM provider**: Google Gemini (`GEMINI_API_KEY`) as primary reasoning and structured verdict output engine; OpenAI (`OPENAI_API_KEY`) for Whisper transcription and fallback.
- **Search / fact-check evidence provider**: Tavily (`TAVILY_API_KEY`).
- **Media forensics provider**: Sightengine (`SIGHTENGINE_API_USER`, `SIGHTENGINE_API_SECRET`).
- **Structured output enforcement**: Pydantic / JSON schema for guaranteed adherence to the 6-part contract.

## 5. Async/background processing
Text/URL claims run synchronously via FastAPI for MVP (<20s target). Image, video, and audio checks are structured with async job handling for long-running workflows.

## 6. Third-party integrations checklist
For each integration, `rules.md` requires an entry here once wired up:

| Integration | Purpose | Key location (env var name) | Notes |
|---|---|---|---|
| Google Gemini | claim extraction, synthesis, follow-up | `GEMINI_API_KEY` | Primary reasoning engine |
| OpenAI | STT (Whisper), fallback reasoning | `OPENAI_API_KEY` | Whisper-1 transcription |
| Tavily | web search & evidence gathering | `TAVILY_API_KEY` | Evidence retrieval |
| Sightengine | media forensics / manipulation detection | `SIGHTENGINE_API_USER`, `SIGHTENGINE_API_SECRET` | Image/media forensics |
| PostgreSQL | persistence for verifications & evidence | `DATABASE_URL` | Asyncpg connection |

## 7. Credential re-validation checklist (do this before wiring old keys into new code)
- [ ] Key still active / not revoked.
- [ ] Key scopes match what the new architecture needs (not over- or under-scoped).
- [ ] Key was never exposed in old client-side bundles — if it was, rotate it, don't reuse it as-is.
- [ ] Rate limits/cost tier still appropriate for expected new usage.
- [ ] Key added to new `.env.example` as a placeholder and to the table in §6.

## 8. Non-functional constraints carried from prd.md
- Time-to-verdict targets (§8 of prd.md) should shape the async-vs-sync decision in §5 above.
- Every pipeline stage must support graceful partial failure (return what was found, downgrade confidence, never fabricate).