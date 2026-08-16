# Lucent — Agent Memory

> Read this file first, every session, before touching code. Keep it updated as you go — this is the project's long-term memory across context resets. When you learn something durable (a decision, a gotcha, a "we tried X and it failed"), write it here immediately, don't wait to be asked.

## Project identity
- **Name**: Lucent
- **What it is**: Content verification assistant. User submits suspicious content (text/URL/image/video/audio) → Lucent returns a structured verdict + plain-language explanation + cited evidence, and supports follow-up questions in the same thread.
- **Full spec**: see `prd.md` (product), `architecture.md` (system design), `rules.md` (how the agent should build), `phases.md` (build order), `design.md` (UI/UX — provided separately by the user).

## Status
- **Current phase**: Phase 2 Complete & Verified (2026-08-16). Ready for Phase 3 — Video verification.
- **Confirmed Stack**: Next.js (Frontend) + FastAPI / Python 3.13 (Backend) + PostgreSQL (`DATABASE_URL`) + Google Gemini (`gemini-flash-latest` Primary LLM) + OpenAI (Transcription/Fallback) + Tavily (Web Search Evidence) + Sightengine (Media Forensics).
- **Phase 2 Deliverables (Image Verification & Forensics)**:
  - Ingestion: Image file upload handler (`POST /api/v1/verifications/verify-image`).
  - Forensics: Sightengine digital forensics service (`check_image_forensics`) analyzing AI-generation likelihood and image anomalies.
  - Multimodal Vision: Gemini vision analysis (`analyze_image_with_vision`) extracting scene descriptions, visible text, and checkable visual claims.
  - Reverse Context Evidence: Tavily evidence gathering mapped with forensic cards into the 6-part verdict contract.
  - Frontend: Drag-and-Drop image dropzone, file thumbnail preview, and multimodal forensics indicators on `/verify`.
  - Verification: 100% pass on 5 pytest automated tests and manual image validation cases.

## Standing decisions (do not re-litigate without flagging to the user)
- Stack is confirmed & locked (Next.js + FastAPI + Postgres + Gemini + OpenAI + Tavily + Sightengine).
- Verdict output must always follow the 6-part contract in `prd.md` §6 (claim summary, verdict label, confidence + reasoning, explanation, evidence, follow-up context).
- `Unverifiable` is a valid, expected verdict — never force a True/False when evidence is thin.
- Every verdict must cite at least one source or be marked `Unverifiable`. No exceptions, no "trust me" outputs.
- Tone is neutral/evidentiary, never opinionated about contested value judgments — see rules.md §2.
- MVP surface = web app only. No browser extension, no platform integrations, no public API yet (see phases.md).
- UI/UX spec (`design.md`) will be provided before building screens. Frontend is minimally stubbed for Phase 0 round-trip.

## Known gotchas / things to remember
- **Credential audit (2026-08-16)**:
  - `GEMINI_API_KEY`: Active (200 OK) — Primary LLM reasoning & extraction.
  - `OPENAI_API_KEY`: Active (200 OK) — Whisper transcription & fallback LLM.
  - `TAVILY_API_KEY`: Active (200 OK) — Web search & evidence retrieval.
  - `DATABASE_URL` (PostgreSQL): Active & Connected (`SELECT 1` succeeded).
  - `SIGHTENGINE`: Active (credentials recognized) — Media forensics & manipulation detection.
  - `SERPER_API_KEY`: **Failed (HTTP 403 Unauthorized)** — Replaced by Tavily.
  - `HIVE_API_KEY`: **Failed (HTTP 403 Invalid Auth Token)** — Replaced by Sightengine.
  - Client-side leak check: Passed (zero keys in frontend bundle).

## File map (update as the rebuild produces real paths)
- `/prd.md` — product requirements (source of truth for *what*)
- `/architecture.md` — system design (source of truth for *how*)
- `/rules.md` — agent operating rules (source of truth for *constraints*)
- `/phases.md` — build sequencing (source of truth for *order*)
- `/design.md` — UI/UX spec (to be provided)
- `/backend` — FastAPI service (app/, models/, routes/, pipeline/)
- `/frontend` — Next.js client application

## Open questions for the user (don't guess silently on these — ask or flag)
- None currently blocking Phase 0.

## Update protocol
Every time you (the agent) make a non-trivial decision, finish a phase milestone, or discover a constraint the human should know about, append it under the relevant section above with a date. Keep entries short — this file is for orientation, not a changelog of every commit.