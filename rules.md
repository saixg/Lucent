# Lucent — Agent Rules

These are binding constraints for whichever agent (Antigravity or otherwise) builds Lucent. Read `memory.md` for context, then follow these rules while executing `phases.md`.

## 1. Source-of-truth hierarchy
When docs conflict: `prd.md` (what to build) > `architecture.md` (how) > `rules.md` (constraints) > `phases.md` (order) > `memory.md` (running notes). If code and docs disagree, the docs win — update code, or flag the conflict to the user and update the doc, but never silently drift.

## 2. Product integrity rules (non-negotiable)
- Never emit a verdict (`True`/`False`/`Misleading`/etc.) without at least one cited source attached. If evidence is insufficient, the verdict must be `Unverifiable` — this is a success case, not a failure to hide.
- Never fabricate a source URL, title, or quote. If the LLM step proposes a source, it must be validated against an actual retrieved evidence item before being shown to the user.
- Never let the system state a confidence level without a one-line reason for that confidence (e.g. "High — corroborated by 3 independent primary sources" vs "Low — only one secondary source available").
- Keep verdict language neutral on contested value judgments. Lucent evaluates evidence, not opinions. If a claim is a matter of opinion rather than fact, say so explicitly instead of forcing a verdict.
- Follow-up answers (chat turns after the initial verdict) must be grounded in the same evidence set gathered for that verification — don't silently re-run a fresh, ungrounded LLM call with no evidence context.

## 3. Security & credentials
- All API keys/secrets live in environment variables / secret manager only. Never hardcode a key in source, never log a full key, never echo one into a commit, PR description, or chat output.
- Before reusing any credential carried over from the old build: confirm it isn't exposed client-side anywhere in the new frontend bundle. Server-side calls only for any key that grants paid/rate-limited access.
- Any new third-party integration (search API, forensics API, LLM provider) needs its key added to `.env.example` (with placeholder, not real value) and documented in `architecture.md` §6.
- Rate-limit and cost-cap every external call path (see §4) so a bug or abuse pattern can't run up an unbounded bill.

## 4. Cost & performance discipline
- Cap external calls per verification request: define a max number of search queries and max number of LLM calls per verification (tune the number in `architecture.md`, but there must always be a hard ceiling, not an open loop).
- Prefer cheaper/faster checks first (cached fact-check DB lookup, simple metadata checks) before falling back to expensive steps (full web search fan-out, heavy media forensics).
- If a pipeline step times out or fails, degrade gracefully: return a partial verdict with confidence explicitly lowered and a note on what couldn't be checked. Never silently retry in an unbounded loop.

## 5. Code & repo hygiene
- Don't port over old build's file structure by default — this rebuild exists specifically because the old structure became unmanageable. Follow `architecture.md`'s proposed structure unless the user says otherwise.
- Every new module gets a short header comment stating its single responsibility. If a file's responsibility can't be stated in one sentence, it's doing too much — split it.
- No dead code, no commented-out blocks left in commits. Delete or don't commit.
- Write the smallest working version of each phase milestone before adding polish — see `phases.md` for exit criteria per phase. Don't gold-plate phase 1 while phase 2 features are unbuilt.

## 6. Working with the user
- If a requirement in `prd.md` is ambiguous for implementation, make the most reasonable call, note the assumption in `memory.md`, and keep moving — don't block on every ambiguity.
- If a requirement would require an architecture change (new external dependency, new data store, breaking the verdict contract in `prd.md` §6), stop and flag it before proceeding — that's a real fork, not a minor ambiguity.
- Keep `memory.md` current. It is the mechanism by which context survives resets — treat updating it as part of finishing a task, not an optional extra.

## 7. Testing & validation minimum bar
- Every verification pipeline change needs at least one test case per verdict type it can produce (`True`, `False`, `Misleading`, `Missing Context`, `Altered/Manipulated`, `AI-Generated`, `Unverifiable`).
- Before marking a phase complete (`phases.md` exit criteria), manually run at least 3 real-world examples end-to-end (not mocked) and confirm the output matches the verdict contract in `prd.md` §6.