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

export type FrameTrackItem = {
  item_id: string;
  item_type: 'scene' | 'cue' | 'caption' | 'overlay' | 'teacher_stamp' | 'evidence' | 'world_plate' | 'remotion_bit' | 'narration';
  start_frame: number;
  end_frame: number;
  locked: boolean;
  locked_fields: string[];
  source_ref?: string;
  scene_id?: string;
  cue_id?: string;
  asset_id?: string;
  sha256?: string;
  component_id?: string;
  preset_id?: string;
  start_word?: number;
  end_word?: number;
  text?: string;
  display_text?: string;
  citation_id?: string;
  diagnostic_label?: string;
  caption_preset?: 'compact' | 'word_by_word';
  excerpt?: string;
  style_id?: string;
  overlay_kind?: 'text' | 'annotation' | 'shape' | 'arrow';
  layout?: {x: number; y: number; width: number; height: number};
  evidence_eligible?: boolean;
  binding?: {
    bindingId: string;
    bindingHash: string;
    slotId: string;
    worldAssetId: string;
  };
};

export type SnapshotTrack = {
  track_id: string;
  kind: 'scenes' | 'cues' | 'captions' | 'overlays' | 'teacher_stamp' | 'evidence' | 'world_plates' | 'narration';
  label: string;
  order: number;
  editable: boolean;
  items: FrameTrackItem[];
};

export type EditorComponent = {
  component_id: string;
  label: string;
  kind: string;
  adapter_id: string;
  source: 'builtin' | 'remotion_bits';
  version: string;
  deterministic: true;
  allowed_prop_keys: string[];
  preset_ids: string[];
};

export type EditorComponentCatalog = {
  schema_version: 'editor_component_catalog.v1';
  catalog_id: string;
  catalog_version: string;
  remotion_version: string;
  components: EditorComponent[];
  presets: Array<{preset_id: string; component_id: string; label: string; props: Record<string, unknown>}>;
  catalog_hash: string;
  artifact_hash: string;
};

export type SemanticEvidenceCandidate = {
  asset_id: string;
  deck_id: string;
  slide_number: number | null;
  rank: number;
  total_score: number;
  lead_margin: number;
  score_breakdown: Record<string, {points: number; matched: string[]; details: string}>;
};

export type SemanticEvidenceBinding = {
  schema_version: 'semantic_evidence_binding.v1';
  binding_id: string;
  cue_id: string;
  claim_refs: string[];
  world_plate: {asset_id: string; sha256: string; profile_id: string; profile_status: string};
  eligible_candidates: SemanticEvidenceCandidate[];
  rejected_candidates: Array<{asset_id: string; rejection_reasons: string[]}>;
  recommendation_state: 'recommended' | 'unmatched' | 'manual_only';
  recommendation_reason: string;
  proposed_binding: null | {
    asset_id: string;
    asset_sha256: string;
    slot_id: string;
    slot_rect: {x: number; y: number; width: number; height: number};
    caption_zone: {region_id: string; rect: {x: number; y: number; width: number; height: number}};
    annotation_anchor: {x: number; y: number};
    source_marker: {placement: string; inset: number};
    frame_range: {start_frame: number; end_frame: number};
  };
  artifact_hash: string;
};

export type PlateLayoutRect = {x: number; y: number; width: number; height: number};

export type PlateLayoutProfile = {
  profile_id: string;
  world_asset_id: string | null;
  status: 'reviewed' | 'experimental' | 'manual_only';
  evidence_slots: Array<{
    slot_id: string;
    order: number;
    label: string;
    rect: PlateLayoutRect;
    safe: boolean;
  }>;
};

export type SnapshotV2 = Omit<Snapshot, 'schema_version' | 'composition_id' | 'scenes' | 'words'> & {
  schema_version: 'production_console_snapshot.v2';
  composition_id: string;
  project_profile: {
    profile_id: string;
    fps: number;
    width: number;
    height: number;
    duration_s: number;
    duration_frames: number;
    audio: {audio_id: string; sha256: string; duration_s: number; status: 'available' | 'missing'};
    audio_trim: {start_s: number; end_s: number; start_frame: number; end_frame: number};
  };
  scenes: Array<Scene & {start_frame: number; end_frame: number}>;
  cues: Array<{
    cue_id: string;
    start_word: number;
    end_word: number;
    start_s: number;
    end_s: number;
    start_frame: number;
    end_frame: number;
    excerpt: string;
    state_type: string;
    visual_world: string;
  }>;
  words: Array<Word & {start_frame: number; end_frame: number}>;
  tracks: SnapshotTrack[];
  approved_assets: Asset[];
  locks: Record<string, true>;
  waveform: {audio_sha256: string; cache_key: string; sample_count: number; peaks: number[]; status: 'cached' | 'derived'};
  component_catalog: EditorComponentCatalog;
  component_catalog_hash: string;
  plate_layout_profiles: {schema_version: 'plate_layout_profiles.v1'; default_profile_id: string; profiles: PlateLayoutProfile[]; artifact_hash: string};
  semantic_evidence_bindings: SemanticEvidenceBinding[];
};

export type RevisionValidation = {
  valid: boolean;
  revision_id?: string;
  artifact_hash?: string;
  errors?: Array<{code: string; message: string; path?: string}>;
};

export type ConsoleState = {
  selectedSceneId: string;
  selectedAssetId: string;
  assetQuery: string;
};
