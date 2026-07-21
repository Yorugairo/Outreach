-- SEO insights platform schema v2
-- Run-centric refactor for Outreach Program

create extension if not exists pgcrypto;

create table if not exists business_entities (
  id uuid primary key default gen_random_uuid(),
  canonical_name text not null,
  primary_domain text,
  primary_phone text,
  trade_category text,
  subcategory text,
  city text,
  state_code text,
  country_code text not null default 'US',
  status text not null default 'active',
  confidence numeric(5,2),
  source_system text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists entity_aliases (
  id uuid primary key default gen_random_uuid(),
  business_entity_id uuid not null references business_entities(id) on delete cascade,
  alias_name text not null,
  alias_type text,
  confidence numeric(5,2),
  created_at timestamptz not null default now()
);

create table if not exists entity_domains (
  id uuid primary key default gen_random_uuid(),
  business_entity_id uuid not null references business_entities(id) on delete cascade,
  domain text not null,
  is_primary boolean not null default false,
  confidence numeric(5,2),
  source_url text,
  last_seen_at timestamptz,
  created_at timestamptz not null default now(),
  unique (business_entity_id, domain)
);

create table if not exists seo_targets (
  id uuid primary key default gen_random_uuid(),
  business_entity_id uuid references business_entities(id) on delete set null,
  target_type text not null default 'domain',
  input_url text not null,
  normalized_url text not null,
  normalized_domain text not null,
  display_name text,
  canonical_domain text,
  default_location_code integer,
  default_language_code text default 'en',
  country_code text not null default 'US',
  status text not null default 'active',
  source_system text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (normalized_url),
  unique (normalized_domain)
);

create index if not exists idx_seo_targets_business_entity on seo_targets (business_entity_id);
create index if not exists idx_seo_targets_domain on seo_targets (normalized_domain);

create table if not exists insight_runs (
  id uuid primary key default gen_random_uuid(),
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  business_entity_id uuid references business_entities(id) on delete set null,
  trigger_source text not null default 'manual',
  mode text not null default 'standard',
  requested_url text not null,
  requested_domain text not null,
  location_code integer,
  language_code text default 'en',
  device text default 'desktop',
  status text not null default 'queued',
  current_stage text not null default 'queued',
  requested_by text,
  attempt_count integer not null default 1,
  input_payload jsonb not null default '{}'::jsonb,
  config_snapshot jsonb not null default '{}'::jsonb,
  summary jsonb not null default '{}'::jsonb,
  error_text text,
  queued_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_insight_runs_target on insight_runs (seo_target_id, created_at desc);
create index if not exists idx_insight_runs_status on insight_runs (status, current_stage);
create index if not exists idx_insight_runs_business_entity on insight_runs (business_entity_id);

create table if not exists run_stage_events (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  stage_name text not null,
  stage_order integer,
  status text not null,
  message text,
  started_at timestamptz,
  completed_at timestamptz,
  duration_ms integer,
  retry_count integer not null default 0,
  input_payload jsonb not null default '{}'::jsonb,
  output_summary jsonb not null default '{}'::jsonb,
  error_text text,
  created_at timestamptz not null default now()
);

create index if not exists idx_run_stage_events_run on run_stage_events (insight_run_id, created_at);
create index if not exists idx_run_stage_events_stage on run_stage_events (insight_run_id, stage_name, status);

create table if not exists run_artifacts (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  artifact_type text not null,
  stage_name text,
  storage_kind text not null default 'local_path',
  storage_path text,
  public_url text,
  mime_type text,
  checksum_sha256 text,
  byte_size bigint,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_run_artifacts_run on run_artifacts (insight_run_id, artifact_type);

create table if not exists discovered_assets (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  asset_type text not null,
  url text not null,
  parent_url text,
  http_status integer,
  content_type text,
  discovered_from text,
  depth integer,
  is_primary boolean not null default false,
  metadata jsonb not null default '{}'::jsonb,
  discovered_at timestamptz not null default now(),
  unique (insight_run_id, asset_type, url)
);

create index if not exists idx_discovered_assets_run on discovered_assets (insight_run_id, asset_type);

create table if not exists page_records (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  discovered_asset_id uuid references discovered_assets(id) on delete set null,
  url text not null,
  canonical_url text,
  normalized_path text,
  page_class text,
  fetch_status text,
  http_status integer,
  content_type text,
  title text,
  meta_description text,
  h1 text,
  robots_meta text,
  canonical_status text,
  indexable boolean,
  word_count integer,
  schema_types jsonb not null default '[]'::jsonb,
  internal_links jsonb not null default '[]'::jsonb,
  image_assets jsonb not null default '[]'::jsonb,
  fetch_metadata jsonb not null default '{}'::jsonb,
  duplicate_cluster_key text,
  fetched_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (insight_run_id, url)
);

create index if not exists idx_page_records_run on page_records (insight_run_id, page_class);
create index if not exists idx_page_records_target on page_records (seo_target_id, created_at desc);
create index if not exists idx_page_records_indexable on page_records (insight_run_id, indexable);

create table if not exists page_evidence (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  page_record_id uuid not null references page_records(id) on delete cascade,
  evidence_type text not null,
  field_name text not null,
  field_value text,
  evidence_snippet text,
  source_selector text,
  source_url text,
  confidence numeric(5,2),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_page_evidence_page on page_evidence (page_record_id, field_name);
create index if not exists idx_page_evidence_run on page_evidence (insight_run_id, evidence_type);

create table if not exists keyword_clusters (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  cluster_label text not null,
  intent_type text not null,
  geo_scope text,
  service_slug text,
  location_slug text,
  primary_keyword text not null,
  supporting_keywords jsonb not null default '[]'::jsonb,
  mapped_page_record_id uuid references page_records(id) on delete set null,
  recommended_page_type text,
  search_volume_est integer,
  priority_score numeric(8,2),
  status text not null default 'candidate',
  source_payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_keyword_clusters_run on keyword_clusters (insight_run_id, status);
create index if not exists idx_keyword_clusters_target on keyword_clusters (seo_target_id, primary_keyword);

create table if not exists serp_snapshots (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  keyword_cluster_id uuid references keyword_clusters(id) on delete set null,
  keyword text not null,
  location_code integer,
  language_code text,
  device text,
  snapshot_date date not null,
  rank_position integer,
  ranking_url text,
  serp_features jsonb not null default '[]'::jsonb,
  top_results jsonb not null default '[]'::jsonb,
  raw_response jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_serp_snapshots_run on serp_snapshots (insight_run_id, snapshot_date desc);
create index if not exists idx_serp_snapshots_cluster on serp_snapshots (keyword_cluster_id);

create table if not exists competitor_snapshots (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  competitor_domain text not null,
  competitor_name text,
  observed_keywords jsonb not null default '[]'::jsonb,
  service_page_count integer,
  location_page_count integer,
  service_location_page_count integer,
  blog_page_count integer,
  project_page_count integer,
  notes jsonb not null default '{}'::jsonb,
  snapshot_date date not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_competitor_snapshots_run on competitor_snapshots (insight_run_id, competitor_domain);

create table if not exists coverage_scorecards (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  overall_score numeric(8,2),
  sitemap_quality_score numeric(8,2),
  metadata_quality_score numeric(8,2),
  page_coverage_score numeric(8,2),
  search_visibility_score numeric(8,2),
  low_value_penalty numeric(8,2),
  service_page_count integer,
  location_page_count integer,
  service_location_page_count integer,
  project_page_count integer,
  blog_page_count integer,
  indexable_page_count integer,
  duplicate_or_low_value_count integer,
  metrics jsonb not null default '{}'::jsonb,
  scoring_notes jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (insight_run_id)
);

create table if not exists sitemap_recommendations (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  included_urls jsonb not null default '[]'::jsonb,
  excluded_urls jsonb not null default '[]'::jsonb,
  missing_urls jsonb not null default '[]'::jsonb,
  child_sitemaps jsonb not null default '[]'::jsonb,
  issues jsonb not null default '[]'::jsonb,
  score numeric(8,2),
  created_at timestamptz not null default now(),
  unique (insight_run_id)
);

create table if not exists page_recommendations (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  keyword_cluster_id uuid references keyword_clusters(id) on delete set null,
  source_page_record_id uuid references page_records(id) on delete set null,
  recommended_page_type text not null,
  recommended_slug text,
  target_title text,
  target_h1 text,
  brief jsonb not null default '{}'::jsonb,
  priority_score numeric(8,2),
  status text not null default 'proposed',
  created_at timestamptz not null default now()
);

create index if not exists idx_page_recommendations_run on page_recommendations (insight_run_id, status, priority_score desc);

create table if not exists audit_findings (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  page_record_id uuid references page_records(id) on delete set null,
  finding_type text not null,
  severity text not null,
  summary text not null,
  evidence jsonb not null default '[]'::jsonb,
  business_impact text,
  recommended_fix text,
  created_at timestamptz not null default now()
);

create index if not exists idx_audit_findings_run on audit_findings (insight_run_id, severity, finding_type);

create table if not exists insight_reports (
  id uuid primary key default gen_random_uuid(),
  insight_run_id uuid not null references insight_runs(id) on delete cascade,
  seo_target_id uuid not null references seo_targets(id) on delete cascade,
  report_version text not null default 'v1',
  report_status text not null default 'draft',
  headline text,
  executive_summary text,
  key_actions jsonb not null default '[]'::jsonb,
  report_payload jsonb not null default '{}'::jsonb,
  export_markdown text,
  export_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (insight_run_id, report_version)
);

create index if not exists idx_insight_reports_run on insight_reports (insight_run_id, report_status);
