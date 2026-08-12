-- ============================================================
-- VeriLens — Supabase SQL Schema
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- Enable UUID extension
create extension if not exists "pgcrypto";

-- ──────────────────────────────────────────────────────────────────────────────
-- investigations
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists investigations (
  id                  uuid primary key default gen_random_uuid(),
  user_id             text,

  -- input
  input_type          text not null,  -- youtube_url | x_url | ig_url | image | video | audio | text | screenshot
  input_url           text,
  input_text          text,
  platform            text,           -- youtube | x | instagram | web

  -- status
  status              text not null default 'pending',  -- pending | processing | complete | failed

  -- verdict
  verdict             text,           -- VERIFIED | FALSE | MISLEADING | OUT_OF_CONTEXT | MANIPULATED | UNVERIFIED
  confidence          numeric(4,3),

  -- scores (0.0 – 1.0)
  claim_credibility   numeric(4,3),
  media_authenticity  numeric(4,3),
  context_accuracy    numeric(4,3),
  evidence_confidence numeric(4,3),

  summary             text,
  error_message       text,

  created_at          timestamptz not null default now(),
  completed_at        timestamptz
);

create index if not exists idx_investigations_user_id  on investigations(user_id);
create index if not exists idx_investigations_status   on investigations(status);
create index if not exists idx_investigations_verdict  on investigations(verdict);

-- ──────────────────────────────────────────────────────────────────────────────
-- media_assets
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists media_assets (
  id               uuid primary key default gen_random_uuid(),
  investigation_id uuid not null references investigations(id) on delete cascade,

  asset_type       text not null,  -- video | audio | image | frame | transcript | screenshot
  storage_url      text,
  local_path       text,
  duration_seconds numeric(10,3),
  file_hash        text,           -- SHA-256
  file_size_bytes  bigint,
  mime_type        text,
  metadata         jsonb,

  created_at       timestamptz not null default now()
);

create index if not exists idx_media_assets_investigation_id on media_assets(investigation_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- claims
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists claims (
  id               uuid primary key default gen_random_uuid(),
  investigation_id uuid not null references investigations(id) on delete cascade,

  claim_text          text not null,
  subject             text,
  actor               text,
  event               text,
  claim_type          text,            -- policy | health | event | statistic | quote

  entities            jsonb,           -- array of named entities
  time_reference      text,
  location            text,
  importance          integer not null default 1,  -- 1 (low) – 5 (critical)

  -- per-claim verdict
  verdict             text,
  verdict_confidence  numeric(4,3)
);

create index if not exists idx_claims_investigation_id on claims(investigation_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- evidence
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists evidence (
  id               uuid primary key default gen_random_uuid(),
  claim_id         uuid not null references claims(id) on delete cascade,

  source_url       text not null,
  source_name      text,
  source_type      text not null,  -- government | regulator | science | news | factcheck | social | other
  source_tier      integer not null default 4,  -- 1 (primary) – 4 (low-authority)

  published_at     timestamptz,
  retrieved_at     timestamptz not null default now(),

  stance           text,            -- supports | refutes | neutral | unrelated
  relevance_score  numeric(4,3),
  credibility_score numeric(4,3),

  title            text,
  snippet          text
);

create index if not exists idx_evidence_claim_id    on evidence(claim_id);
create index if not exists idx_evidence_source_tier on evidence(source_tier);

-- ──────────────────────────────────────────────────────────────────────────────
-- analysis_results  (media forensics)
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists analysis_results (
  id               uuid primary key default gen_random_uuid(),
  investigation_id uuid not null references investigations(id) on delete cascade,

  -- media signals (0.0 – 1.0)
  media_authenticity          numeric(4,3),
  ai_generation_probability   numeric(4,3),
  manipulation_probability    numeric(4,3),
  deepfake_probability        numeric(4,3),
  voice_clone_probability     numeric(4,3),

  -- context
  context_match               boolean,
  provenance_status           text,     -- original | edited | reposted | unknown
  original_source_url         text,
  original_date               timestamptz,
  original_location           text,
  original_caption            text,

  provenance_timeline         jsonb,    -- [{date, url, change_description}]
  manipulation_regions        jsonb,    -- frame → region → score heatmap

  reasoning                   text,
  raw_forensics               jsonb,

  created_at                  timestamptz not null default now()
);

create index if not exists idx_analysis_results_investigation_id on analysis_results(investigation_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- conversations
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists conversations (
  id                 uuid primary key default gen_random_uuid(),
  investigation_id   uuid not null references investigations(id) on delete cascade,

  platform           text not null default 'web',  -- web | youtube | x | instagram
  platform_user_id   text,
  platform_thread_id text,

  created_at         timestamptz not null default now()
);

create index if not exists idx_conversations_investigation_id on conversations(investigation_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- messages
-- ──────────────────────────────────────────────────────────────────────────────
create table if not exists messages (
  id                   uuid primary key default gen_random_uuid(),
  conversation_id      uuid not null references conversations(id) on delete cascade,

  role                 text not null,  -- user | assistant | system
  content              text not null,
  cited_evidence_ids   jsonb,          -- array of evidence UUIDs

  created_at           timestamptz not null default now()
);

create index if not exists idx_messages_conversation_id on messages(conversation_id);

-- ──────────────────────────────────────────────────────────────────────────────
-- Row Level Security  (enable after confirming schema works)
-- ──────────────────────────────────────────────────────────────────────────────
-- alter table investigations enable row level security;
-- alter table media_assets    enable row level security;
-- alter table claims          enable row level security;
-- alter table evidence        enable row level security;
-- alter table analysis_results enable row level security;
-- alter table conversations   enable row level security;
-- alter table messages        enable row level security;
