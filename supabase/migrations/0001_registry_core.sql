create extension if not exists pgcrypto;

create table if not exists ecosystems (
    id uuid primary key default gen_random_uuid(),
    key text not null unique,
    display_name text not null,
    type text not null,
    description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists repos (
    id uuid primary key default gen_random_uuid(),
    ecosystem_id uuid references ecosystems(id) on delete set null,
    full_name text not null unique,
    repo_name text not null,
    visibility text,
    default_branch text,
    html_url text,
    language text,
    role text,
    runtime text,
    status text not null default 'discovered',
    stack_json jsonb not null default '{}'::jsonb,
    common_files_json jsonb not null default '{}'::jsonb,
    recent_commits_json jsonb not null default '[]'::jsonb,
    summary_json jsonb not null default '{}'::jsonb,
    last_scan_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists repo_relations (
    id uuid primary key default gen_random_uuid(),
    source_repo_id uuid not null references repos(id) on delete cascade,
    target_repo_id uuid not null references repos(id) on delete cascade,
    relation_type text not null,
    confidence_score numeric(5,2) not null default 1.00,
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (source_repo_id, target_repo_id, relation_type)
);

create table if not exists risk_flags (
    id uuid primary key default gen_random_uuid(),
    repo_id uuid references repos(id) on delete cascade,
    ecosystem_id uuid references ecosystems(id) on delete cascade,
    flag_key text not null,
    severity text not null default 'medium',
    status text not null default 'open',
    title text,
    description text,
    detected_at timestamptz not null default now(),
    resolved_at timestamptz,
    metadata_json jsonb not null default '{}'::jsonb
);

create table if not exists scans (
    id uuid primary key default gen_random_uuid(),
    scan_type text not null,
    scope text not null,
    success boolean not null default false,
    partial boolean not null default false,
    summary_json jsonb not null default '{}'::jsonb,
    started_at timestamptz not null default now(),
    finished_at timestamptz
);

create table if not exists scan_targets (
    id uuid primary key default gen_random_uuid(),
    scan_id uuid not null references scans(id) on delete cascade,
    repo_id uuid references repos(id) on delete cascade,
    target_key text,
    status text not null default 'pending',
    error_message text,
    payload_json jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists manual_rules (
    id uuid primary key default gen_random_uuid(),
    ecosystem_id uuid references ecosystems(id) on delete cascade,
    rule_key text not null,
    rule_type text not null,
    config_json jsonb not null default '{}'::jsonb,
    is_active boolean not null default true,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_repos_ecosystem_id on repos(ecosystem_id);
create index if not exists idx_repo_relations_source on repo_relations(source_repo_id);
create index if not exists idx_repo_relations_target on repo_relations(target_repo_id);
create index if not exists idx_risk_flags_repo_id on risk_flags(repo_id);
create index if not exists idx_risk_flags_ecosystem_id on risk_flags(ecosystem_id);
create index if not exists idx_scans_scan_type on scans(scan_type);
create index if not exists idx_scan_targets_scan_id on scan_targets(scan_id);
create index if not exists idx_manual_rules_ecosystem_id on manual_rules(ecosystem_id);

create or replace function set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create or replace trigger trg_ecosystems_updated_at
before update on ecosystems
for each row execute function set_updated_at();

create or replace trigger trg_repos_updated_at
before update on repos
for each row execute function set_updated_at();

create or replace trigger trg_repo_relations_updated_at
before update on repo_relations
for each row execute function set_updated_at();

create or replace trigger trg_scan_targets_updated_at
before update on scan_targets
for each row execute function set_updated_at();

create or replace trigger trg_manual_rules_updated_at
before update on manual_rules
for each row execute function set_updated_at();
