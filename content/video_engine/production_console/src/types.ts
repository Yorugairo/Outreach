export type Scene = {
  scene_id: string;
  title: string;
  start_s: number;
  end_s: number;
  cue_refs: string[];
  claim_refs: string[];
  asset_ids: string[];
  review_state: 'unreviewed' | 'review_only' | 'revision_required' | 'approved';
};

export type Word = {word_id: string; text: string; start_s: number; end_s: number};

export type Asset = {
  asset_id: string;
  label: string;
  sha256: string;
  source_kind: 'project_asset' | 'deck_source' | 'production_visual' | 'evidence_surface';
  approval_scope: 'none' | 'review_only' | 'production_visuals' | 'evidence';
  evidence_eligible: boolean;
  rights_state: string;
  context_status: string;
  deck_id: string | null;
  slide_number: number | null;
  width: number | null;
  height: number | null;
  what_it_is: string | null;
  claim_refs: string[];
  cue_refs: string[];
};

export type Snapshot = {
  schema_version: 'production_console_snapshot.v1';
  snapshot_id: string;
  project_id: string;
  composition_id: string;
  base_artifact_hashes: Record<string, string>;
  artifact_hash: string;
  scenes: Scene[];
  words: Word[];
  assets: Asset[];
  reviews: Array<{review_id: string; scope: string; state: string; sha256: string}>;
  degraded_inputs: string[];
};

export type Health = {status: string; snapshot_hash?: string; queue?: string};

export type ConsoleState = {
  selectedSceneId: string;
  selectedAssetId: string;
  assetQuery: string;
};
