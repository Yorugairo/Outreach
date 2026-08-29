/**
 * Framework-independent contracts for the production console editor.
 *
 * Frames are integer, zero-based, and use half-open ranges: [startFrame,
 * endFrame).  The source narration and its word timing are represented in the
 * document, but the command layer only exposes the explicitly approved
 * narration edits.
 */

export const TIMELINE_SCHEMA_VERSION = 'editorial_timeline_document.v1' as const;
export const DRAFT_SCHEMA_VERSION = 'production_console_local_draft.v1' as const;
export const MAX_HISTORY_ENTRIES = 100 as const;

export type Frame = number;

export type FrameRange = {
  startFrame: Frame;
  endFrame: Frame;
};

/** Closed easing vocabulary accepted by the editor kernel. */
export type ApprovedEasing = 'linear' | 'smoothstep' | 'ease_in' | 'ease_out' | 'ease_in_out';

/** Closed spring labels; the renderer may map these to deterministic configs. */
export type ApprovedSpringPreset = 'gentle' | 'snappy' | 'bouncy';
export type SpringPresetId = ApprovedSpringPreset;

export type NumericKeyframe = {
  frame: Frame;
  value: number;
  /** Easing from this keyframe to the following keyframe. */
  easing?: ApprovedEasing;
  /** Optional approved spring preset for the segment to the next keyframe. */
  springPreset?: ApprovedSpringPreset;
};

export type AnimatableProperty =
  | 'x'
  | 'y'
  | 'scaleX'
  | 'scaleY'
  | 'rotation'
  | 'opacity'
  | 'zIndex';

export type KeyframeTracks = Partial<Record<AnimatableProperty, NumericKeyframe[]>>;

export type CropRect = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export type VisualTransform = {
  x: number;
  y: number;
  scaleX: number;
  scaleY: number;
  rotation: number;
  opacity: number;
  zIndex: number;
  crop: CropRect;
};

export const DEFAULT_VISUAL_TRANSFORM: VisualTransform = {
  x: 0,
  y: 0,
  scaleX: 1,
  scaleY: 1,
  rotation: 0,
  opacity: 1,
  zIndex: 0,
  crop: {x: 0, y: 0, width: 1, height: 1},
};

export type TimelineTrackKind =
  | 'scenes'
  | 'cues'
  | 'captions'
  | 'overlays'
  | 'teacher_stamp'
  | 'evidence'
  | 'world_plates'
  | 'narration';

export const DEFAULT_TRACK_ORDER: readonly TimelineTrackKind[] = [
  'scenes',
  'cues',
  'captions',
  'overlays',
  'teacher_stamp',
  'evidence',
  'world_plates',
  'narration',
];

export type TimelineTrack = {
  id: string;
  kind: TimelineTrackKind;
  label: string;
  locked: boolean;
  visible: boolean;
  itemIds: string[];
};

export type TimelineItemBase = {
  id: string;
  trackId: string;
  range: FrameRange;
  label: string;
  /** A locked item cannot be changed by generic visual commands. */
  locked: boolean;
};

export type SceneTimelineItem = TimelineItemBase & {
  kind: 'scene';
  sceneId: string;
  title: string;
  cueIds: string[];
  reviewState: 'unreviewed' | 'review_only' | 'revision_required' | 'approved';
};

export type CueTimelineItem = TimelineItemBase & {
  kind: 'cue';
  cueId: string;
  sceneId: string;
  cueType?: string;
};

export type CaptionTimelineItem = TimelineItemBase & {
  kind: 'caption';
  text: string;
  /** Word IDs are source provenance and are not editable through this kernel. */
  wordIds: string[];
  styleId?: string;
  groupId?: string;
  lineBreaks?: number[];
  transform: VisualTransform;
  keyframes: KeyframeTracks;
};

export type OverlayKind = 'text' | 'annotation' | 'shape' | 'arrow';

export type OverlayTimelineItem = TimelineItemBase & {
  kind: 'overlay';
  overlayKind: OverlayKind;
  text?: string;
  assetId?: string;
  transform: VisualTransform;
  keyframes: KeyframeTracks;
};

export type TeacherStampTimelineItem = TimelineItemBase & {
  kind: 'teacher_stamp';
  assetId: string;
  transform: VisualTransform;
  keyframes: KeyframeTracks;
};

export type EvidenceTimelineItem = TimelineItemBase & {
  kind: 'evidence';
  assetId: string;
  claimRefs: string[];
  evidenceEligible: boolean;
  binding?: {
    bindingId: string;
    bindingHash: string;
    slotId: string;
    worldAssetId: string;
  };
  transform: VisualTransform;
  keyframes: KeyframeTracks;
};

export type WorldPlateTimelineItem = TimelineItemBase & {
  kind: 'world_plate';
  assetId: string;
  fit: 'contain' | 'cover';
  transform: VisualTransform;
  keyframes: KeyframeTracks;
};

export type RemotionBitCommonProps = {
  durationInFrames?: number;
  color?: string;
  backgroundColor?: string;
  fontSize?: number;
  styleId?: string;
};

export type RemotionBitPropsById = {
  'fade-in': RemotionBitCommonProps & {text?: string};
  'blur-in': RemotionBitCommonProps & {text?: string; blurAmount?: number};
  'word-by-word': RemotionBitCommonProps & {text?: string; staggerFrames?: number};
  'slide-from-left': RemotionBitCommonProps & {text?: string; distance?: number};
  'basic-typewriter': RemotionBitCommonProps & {text?: string; typeSpeedFrames?: number; showCursor?: boolean};
  'basic-counter': RemotionBitCommonProps & {from?: number; to?: number; prefix?: string; postfix?: string; decimals?: number};
  'list-reveal': RemotionBitCommonProps & {items?: readonly string[]; staggerFrames?: number};
  'grid-stagger': RemotionBitCommonProps & {items?: readonly string[]; columns?: number; staggerFrames?: number};
  'mosaic-reframe': RemotionBitCommonProps & {images?: readonly string[]; tileCount?: number};
  '3d-card-stack': RemotionBitCommonProps & {cards?: readonly string[]; staggerFrames?: number};
  'ken-burns-effect': RemotionBitCommonProps & {images?: readonly string[]; scaleFrom?: number; scaleTo?: number; direction?: 'left' | 'right' | 'up' | 'down'};
};

export type RemotionBitId = keyof RemotionBitPropsById;
export type RemotionBitProps = {[K in RemotionBitId]: Partial<RemotionBitPropsById[K]>}[RemotionBitId];

export type RemotionBitTimelineItemFor<K extends RemotionBitId> = TimelineItemBase & {
  kind: 'remotion_bit';
  componentId: K;
  presetId: string;
  props: Partial<RemotionBitPropsById[K]>;
  transform: VisualTransform;
  keyframes: KeyframeTracks;
};

export type RemotionBitTimelineItem = {[K in RemotionBitId]: RemotionBitTimelineItemFor<K>}[RemotionBitId];

export type NarrationWord = {
  wordId: string;
  text: string;
  startFrame: Frame;
  endFrame: Frame;
};

export type NarrationTimelineItem = TimelineItemBase & {
  kind: 'narration';
  /** The source asset/hash remain immutable; only approved trim and level commands exist. */
  sourceAssetId: string;
  sourceSha256: string;
  words: NarrationWord[];
  level: number;
  locked: true;
};

export type TimelineItem =
  | SceneTimelineItem
  | CueTimelineItem
  | CaptionTimelineItem
  | OverlayTimelineItem
  | TeacherStampTimelineItem
  | EvidenceTimelineItem
  | WorldPlateTimelineItem
  | RemotionBitTimelineItem
  | NarrationTimelineItem;

export type TransformableTimelineItem =
  | CaptionTimelineItem
  | OverlayTimelineItem
  | TeacherStampTimelineItem
  | EvidenceTimelineItem
  | WorldPlateTimelineItem
  | RemotionBitTimelineItem;

export type TimelineDocument = {
  schemaVersion: typeof TIMELINE_SCHEMA_VERSION;
  documentId: string;
  projectId: string;
  snapshotId: string;
  baseSnapshotHash: string;
  compositionId: string;
  fps: number;
  width: number;
  height: number;
  durationFrames: Frame;
  tracks: TimelineTrack[];
  items: TimelineItem[];
};

export type SelectionMode = 'replace' | 'add' | 'toggle';

export type SelectionState = {
  selectedItemIds: string[];
  primaryItemId: string | null;
  focusedSceneId: string | null;
};

export const EMPTY_SELECTION: SelectionState = {
  selectedItemIds: [],
  primaryItemId: null,
  focusedSceneId: null,
};

export type TimelineItemPatch = {
  range?: FrameRange;
  label?: string;
  text?: string;
  styleId?: string;
  groupId?: string;
  lineBreaks?: number[];
  props?: RemotionBitProps;
  level?: number;
  transform?: Omit<Partial<VisualTransform>, 'crop'> & {crop?: Partial<CropRect>};
};

export type EditorCommand =
  | {type: 'select'; itemId: string; mode?: SelectionMode}
  | {type: 'set-selection'; selection: SelectionState}
  | {type: 'clear-selection'}
  | {type: 'focus-scene'; sceneId: string | null}
  | {type: 'move-item'; itemId: string; deltaFrames: number}
  | {type: 'set-item-range'; itemId: string; range: FrameRange}
  | {type: 'set-scene-boundary'; sceneId: string; boundaryFrame: Frame; side?: 'start' | 'end'}
  | {type: 'update-item'; itemId: string; patch: TimelineItemPatch}
  | {type: 'set-keyframes'; itemId: string; property: AnimatableProperty; keyframes: NumericKeyframe[]}
  | {type: 'trim-narration'; itemId?: string; range: FrameRange}
  | {type: 'set-narration-level'; itemId?: string; level: number}
  | {type: 'insert-item'; item: TimelineItem; index?: number}
  | {type: 'remove-item'; itemId: string}
  | {type: 'duplicate-item'; itemId: string; newItemId: string; offsetFrames?: number}
  | {type: 'reorder-item'; itemId: string; toIndex: number}
  | {type: 'batch'; commands: EditorCommand[]}
  | {type: 'undo'}
  | {type: 'redo'};

export type EditorHistory = {
  past: TimelineDocument[];
  future: TimelineDocument[];
  limit: number;
};

export type EditorState = {
  document: TimelineDocument;
  selection: SelectionState;
  history: EditorHistory;
  lastError: string | null;
};

export type TimelineDraft = {
  schemaVersion: typeof DRAFT_SCHEMA_VERSION;
  document: TimelineDocument;
  selection: SelectionState;
};

export type DraftRecoveryResult =
  | {status: 'recovered'; draft: TimelineDraft}
  | {status: 'missing'; draft: null}
  | {status: 'invalid'; draft: null; error: string};

export interface DraftStorage {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}
