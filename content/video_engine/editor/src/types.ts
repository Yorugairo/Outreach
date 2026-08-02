export type Aspect = "landscape" | "vertical";

export type TransitionKind =
  | "continuous"
  | "crossfade"
  | "match_cut"
  | "hard_cut";

export type EditClip = {
  id: string;
  src: string;
  duration_in_frames: number;
  transition?: TransitionKind;
  transition_frames?: number;
  scene_id?: string | number;
  scene_ids?: Array<string | number>;
  motif?: string;
  function?: string;
};

export type CaptionLayer = {
  id: string;
  text: string;
  from: number;
  duration_in_frames: number;
  style?: Record<string, string | number>;
};

export type OverlayLayer = {
  id: string;
  kind: "text" | "image" | "box" | "line" | "arrow";
  from: number;
  duration_in_frames: number;
  text?: string;
  src?: string;
  style?: Record<string, string | number>;
};

export type EditManifest = {
  schema_version: "edit_manifest.v1";
  aspect: Aspect;
  fps: number;
  width: number;
  height: number;
  duration_in_frames: number;
  clips: EditClip[];
  /** Optional canonical narration track owned by the local editor. */
  audio?: {
    src: string;
    from?: number;
    duration_in_frames?: number;
    volume?: number;
  };
  captions: CaptionLayer[];
  overlays: OverlayLayer[];
  segments?: Array<{
    scene_id?: string | number;
    clip_id?: string;
    path?: string;
    duration_in_frames?: number;
  }>;
  metadata?: Record<string, unknown>;
};

export type EditorialProps = EditManifest | { manifest: EditManifest };

export type TimelineClip = EditClip & {
  from: number;
};

export type DocumentaryFunction =
  | "artifact_cold_open"
  | "archival_portrait"
  | "illustrated_reconstruction"
  | "document_quote_closeup"
  | "migration_map_timeline"
  | "lineage_graph"
  | "concept_mechanics_cutaway"
  | "chapter_cta";

export type MotionRecipe =
  | "parallax_push"
  | "detail_punch"
  | "masked_reveal"
  | "evidence_highlight"
  | "map_trace"
  | "comic_pop"
  | "split_compare"
  | "type_build"
  | "paper_transition";

export type DocumentaryVisualBeat = {
  coverage_slot_id: string;
  narration_excerpt: string;
  parent_offset_s: number;
  duration_s: number;
  semantic_purpose: string;
  visual_source: string;
  asset_ids: string[];
  motion_recipe: MotionRecipe;
  micro_events: Array<{ at_s: number; action: string; recipe: MotionRecipe }>;
  transition: TransitionKind;
  character_layers?: DocumentaryCharacterLayer[];
};

export type DocumentaryCharacterMotion =
  | "enter_from_left"
  | "enter_from_right"
  | "rise"
  | "pop"
  | "settle"
  | "float";

/**
 * A reviewed character plate placed over a documentary shot.  The editor only
 * receives an approved asset id resolved through the local asset map; it never
 * receives a provider URL or a character-generation prompt.
 */
export type DocumentaryCharacterLayer = {
  id: string;
  asset_id: string;
  from_s: number;
  duration_s: number;
  x: number;
  y: number;
  width: number;
  height: number;
  motion?: DocumentaryCharacterMotion;
  label?: string;
  z_index?: number;
};

export type DocumentaryShot = {
  shot_id: string | number;
  treatment_id: string;
  function: DocumentaryFunction;
  visual_type?: DocumentaryFunction;
  purpose?: string;
  composition?: string;
  scene_class?: "DocumentaryScene";
  duration_s?: number;
  duration_in_frames?: number;
  asset_ids?: string[];
  citations?: Array<string | { citation_id: string; label?: string }>;
  credit_ids?: string[];
  illustration_label?: string;
  camera?: {
    framing?: string;
    anchor?: string;
    move?: string;
    safe_zone?: string;
  };
  parameters?: Record<string, unknown> & {
    visual_beats?: DocumentaryVisualBeat[];
  };
  signature?: string;
  uniqueness_signature?: string;
  phash?: string;
  character_layers?: DocumentaryCharacterLayer[];
};

export type DocumentaryTreatment = {
  schema_version: "visual_treatment.v2";
  source_kind: "documentary";
  art_bible_id: string;
  art_bible_hash: string;
  shot_plan_hash: string;
  research_hash: string;
  asset_manifest_hash: string;
  coverage_plan_hash?: string;
  asset_selection_hash?: string;
  episode_id?: string;
  duration_s: number;
  shots: DocumentaryShot[];
  credits?: Record<string, unknown> | Array<Record<string, unknown>>;
  artifact_hash?: string;
};

export type DocumentaryProps =
  | (DocumentaryTreatment & { asset_map?: Record<string, string> })
  | { treatment: DocumentaryTreatment; asset_map?: Record<string, string> };

/** A renderer-facing SHA-256 identifier from an approved content artifact. */
export type EditorialMotionHash = string;

export type EditorialMotionPurpose =
  | "hook"
  | "establish"
  | "reveal"
  | "explain"
  | "detail"
  | "reaction"
  | "payoff"
  | "chapter_reset";

export type EditorialMotionShotScale =
  | "wide"
  | "medium"
  | "medium_detail"
  | "close"
  | "insert";

export type EditorialMotionLayerRole =
  | "world"
  | "depth"
  | "character"
  | "prop"
  | "ambient"
  | "diagram";

export type EditorialMotionCameraKind =
  | "locked"
  | "push_settle"
  | "pull_settle"
  | "lateral_reveal"
  | "foreground_parallax"
  | "cut_on_motion";

export type EditorialMotionCamera = {
  kind: EditorialMotionCameraKind;
  amount: number;
  easing: "smoothstep" | "ease_in_out" | "linear";
  hold_in_s: number;
  move_s: number;
  hold_out_s: number;
  direction?: "left" | "right" | "up" | "down" | "toward_focal_point";
};

export type EditorialMotionTransitionKind =
  | "hard_cut"
  | "match_cut"
  | "paper_wipe"
  | "chapter_fade"
  | "crossfade";

export type EditorialMotionTransition = {
  kind: EditorialMotionTransitionKind;
  reason: string;
  motif_id?: string;
  duration_s?: number;
  time_or_place_change?: boolean;
};

export type EditorialMotionLayer = {
  asset_id: string;
  role: EditorialMotionLayerRole;
  z_index?: number;
  action?: string;
  mask_asset_id?: string;
  timing?: {
    exit_at_s: number;
    exit_duration_s: number;
    exit_effect_duration_s?: number;
    exit_effect: "none" | "smoke_puff";
  };
  placement?: {
    support_plane: EditorialMotionPlacementRegion;
    foot_anchor: EditorialMotionFocalPoint;
    exclusion_zones: EditorialMotionPlacementRegion[];
  };
  layout?: {
    x: number;
    y: number;
    width: number;
    height: number;
    fit?: "contain" | "cover";
  };
};

export type EditorialMotionWordRange = {
  start_index: number;
  end_index: number;
};

export type EditorialMotionFocalPoint = {
  x: number;
  y: number;
};

/** An authored ground/deck/mat plane or a named region a layer must avoid. */
export type EditorialMotionPlacementRegion = {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
};

/** A short, local sound cue; canonical narration remains the master audio. */
export type EditorialMotionSoundEffect = {
  id: string;
  at_s: number;
  duration_s: number;
  volume: number;
  sha256: string;
};

export type EditorialMotionProvider = {
  requirement: "none" | "preferred" | "required";
  fallback: "local_layer_motion" | "locked_hold" | "omit_shot";
  candidate_asset_id?: string;
};

export type EditorialMotionInformationSurface = {
  mode: "floating_label" | "surface_ink" | "none";
  x: number;
  y: number;
  width: number;
  height: number;
  text_align?: "left" | "center" | "right";
  surface_asset_id?: string;
};

/** A pre-render planning requirement; it is not a generic text overlay. */
export type EditorialMotionVisualAction = {
  kind: "map_cut_in" | "list_item_popout" | "object_cutaway" | "character_action" | "scenic_cutaway";
  subject: string;
};

export type EditorialMotionShot = {
  shot_id: string;
  parent_beat_ids: string[];
  parent_scene_bundle_id: string;
  start_s: number;
  duration_s: number;
  word_range: EditorialMotionWordRange;
  narration_excerpt: string;
  visual_intent?: "academic" | "martial" | "scenic" | "journey" | "evidence" | "explanation" | "humor" | "transition";
  required_visual_actions?: EditorialMotionVisualAction[];
  purpose: EditorialMotionPurpose;
  shot_scale: EditorialMotionShotScale;
  focal_point: EditorialMotionFocalPoint;
  layers: EditorialMotionLayer[];
  subject_action: string;
  ambient_actions: string[];
  sound_effects?: EditorialMotionSoundEffect[];
  information_reveal: string;
  information_surface?: EditorialMotionInformationSurface;
  camera: EditorialMotionCamera;
  transition_in: EditorialMotionTransition;
  transition_out: EditorialMotionTransition;
  audio_bridge: "continuous_narration" | "none" | "j_cut" | "l_cut";
  provider_motion: EditorialMotionProvider;
  overlay_ids: string[];
  uniqueness_signature: string;
};

/** The versioned, hash-bound contract compiled by the editorial-motion service. */
export type EditorialMotionPlan = {
  schema_version: "editorial_motion_plan.v1";
  source_storyboard_hash: EditorialMotionHash;
  source_beat_plan_hash: EditorialMotionHash;
  scene_bundle_hashes: EditorialMotionHash[];
  scene_flow_graph_hash: EditorialMotionHash;
  asset_map_hash: EditorialMotionHash;
  audio_manifest_hash: EditorialMotionHash;
  pacing_recipe_hash: EditorialMotionHash;
  duration_s: number;
  source_start_s?: number;
  shots: EditorialMotionShot[];
  provider_calls: 0;
  revision_only: true;
  artifact_hash: EditorialMotionHash;
};

export type EditorialMotionPlanV1 = EditorialMotionPlan;

/** Text and evidence surfaces are resolved from this job-local map only. */
export type EditorialMotionOverlay = {
  kind?: "caption" | "citation" | "text" | "image" | "box" | "line" | "arrow";
  text?: string;
  label?: string;
  citation_id?: string;
  src?: string;
  from_s?: number;
  duration_s?: number;
  style?: Record<string, string | number>;
  position?: "top" | "center" | "bottom" | "rail";
};

export type EditorialMotionAudio = {
  path: string;
  start_s?: number;
  volume?: number;
};

/** Optional low-resolution proof profile used by fixture renders. */
export type EditorialMotionRenderProfile = {
  width: number;
  height: number;
  fps?: number;
  label?: string;
  enabled?: boolean;
  scale?: number;
  codec?: string;
  metadata?: Record<string, string | number | boolean>;
};

export type EditorialMotionProps = {
  plan: EditorialMotionPlan;
  /** Asset IDs are approved by the compiler; values are relative to editor/public. */
  asset_map: Record<string, string>;
  canonical_audio: EditorialMotionAudio;
  /** Render-service-resolved local SFX only; no remote paths reach the editor. */
  sound_effect_map?: Record<string, string>;
  overlay_map: Record<string, EditorialMotionOverlay>;
  /** Platform captions are the default; burn-in is opt-in for exports that require it. */
  caption_policy?: "platform" | "burned_in";
  /** Claim citations remain bound to the shot but normally resolve in credits/description. */
  citation_policy?: "on_screen" | "credits_only";
  diagnostic?: boolean;
  render_profile?: EditorialMotionRenderProfile;
  /** Alias accepted for low-resolution fixture callers. */
  low_res?: EditorialMotionRenderProfile;
};

export type EditorialMotionPlanProps = EditorialMotionProps;
