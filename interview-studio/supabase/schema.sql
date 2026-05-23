create extension if not exists pgcrypto;

create table if not exists public.interviews (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  storage_bucket text not null default 'interviews',
  storage_path text not null,
  respondent_code text,
  submitted_at timestamptz not null default now(),
  elapsed_ms bigint not null default 0,
  respondent jsonb not null default '{}'::jsonb,
  consent jsonb not null default '{}'::jsonb,
  interviewer text,
  answers jsonb not null default '{}'::jsonb,
  ai jsonb not null default '{}'::jsonb,
  answer_count integer not null default 0,
  ai_message_count integer not null default 0,
  created_at timestamptz not null default now()
);

alter table public.interviews enable row level security;

create index if not exists interviews_submitted_at_idx
  on public.interviews (submitted_at desc);

create index if not exists interviews_respondent_code_idx
  on public.interviews (respondent_code);

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'interviews',
  'interviews',
  false,
  8388608,
  array['text/markdown', 'text/plain', 'application/json']
)
on conflict (id) do nothing;
