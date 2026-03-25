create table if not exists repo_tree_snapshots (
    id uuid primary key default gen_random_uuid(),
    repo_id uuid not null references repos(id) on delete cascade,
    source text not null default 'github',
    ref text,
    depth integer not null default 2,
    root_path text not null,
    tree_json jsonb not null,
    tree_text text not null,
    structural_hash text,
    analysis_status text not null default 'queued',
    detected_frameworks_json jsonb not null default '[]'::jsonb,
    detected_repo_types_json jsonb not null default '[]'::jsonb,
    risk_flags_json jsonb not null default '[]'::jsonb,
    recommendations_json jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_repo_tree_snapshots_repo_id on repo_tree_snapshots(repo_id);
create index if not exists idx_repo_tree_snapshots_analysis_status on repo_tree_snapshots(analysis_status);

create or replace trigger trg_repo_tree_snapshots_updated_at
before update on repo_tree_snapshots
for each row execute function set_updated_at();
