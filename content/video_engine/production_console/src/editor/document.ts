import {
  DEFAULT_TRACK_ORDER,
  TIMELINE_SCHEMA_VERSION,
  type CueTimelineItem,
  type FrameRange,
  type NarrationTimelineItem,
  type SceneTimelineItem,
  type TimelineDocument,
  type TimelineItem,
  type TimelineTrack,
  type TimelineTrackKind,
  type TransformableTimelineItem,
  type VisualTransform,
  type RemotionBitId,
} from './types';

export type TimelineDocumentInput = Omit<TimelineDocument, 'schemaVersion' | 'tracks' | 'items'> & {
  tracks?: TimelineTrack[];
  items?: TimelineItem[];
};

const TRACK_LABELS: Record<TimelineTrackKind, string> = {
  scenes: 'Scenes',
  cues: 'Cues',
  captions: 'Captions',
  overlays: 'Overlays / annotations',
  teacher_stamp: 'Teacher stamp',
  evidence: 'Evidence',
  world_plates: 'World plates',
  narration: 'Narration',
};

export function trackIdForKind(kind: TimelineTrackKind): string {
  return `track-${kind}`;
}

export function createDefaultTracks(): TimelineTrack[] {
  return DEFAULT_TRACK_ORDER.map((kind) => ({
    id: trackIdForKind(kind),
    kind,
    label: TRACK_LABELS[kind],
    locked: kind === 'narration',
    visible: true,
    itemIds: [],
  }));
}

export function createTimelineDocument(input: TimelineDocumentInput): TimelineDocument {
  const tracksWereProvided = input.tracks !== undefined;
  const tracks = (input.tracks ?? createDefaultTracks()).map((track) => ({
    ...track,
    itemIds: [...track.itemIds],
  }));
  const items = (input.items ?? []).map(cloneTimelineItem);
  const document: TimelineDocument = {
    schemaVersion: TIMELINE_SCHEMA_VERSION,
    documentId: input.documentId,
    projectId: input.projectId,
    snapshotId: input.snapshotId,
    baseSnapshotHash: input.baseSnapshotHash,
    compositionId: input.compositionId,
    fps: input.fps,
    width: input.width,
    height: input.height,
    durationFrames: input.durationFrames,
    tracks,
    items,
  };
  return tracksWereProvided ? document : updateTrackItemIds(document);
}

export function cloneTimelineDocument(document: TimelineDocument): TimelineDocument {
  return JSON.parse(JSON.stringify(document)) as TimelineDocument;
}

export function cloneTimelineItem(item: TimelineItem): TimelineItem {
  return JSON.parse(JSON.stringify(item)) as TimelineItem;
}

export function findTimelineItem(document: TimelineDocument, itemId: string): TimelineItem | undefined {
  return document.items.find((item) => item.id === itemId);
}

export function findSceneItem(document: TimelineDocument, sceneId: string): SceneTimelineItem | undefined {
  return document.items.find((item): item is SceneTimelineItem => item.kind === 'scene' && item.sceneId === sceneId);
}

export function findCueItem(document: TimelineDocument, cueId: string): CueTimelineItem | undefined {
  return document.items.find((item): item is CueTimelineItem => item.kind === 'cue' && item.cueId === cueId);
}

export function findNarrationItem(document: TimelineDocument, itemId?: string): NarrationTimelineItem | undefined {
  return document.items.find(
    (item): item is NarrationTimelineItem => item.kind === 'narration' && (itemId === undefined || item.id === itemId),
  );
}

export function isTransformableItem(item: TimelineItem): item is TransformableTimelineItem {
  return item.kind === 'caption' || item.kind === 'overlay' || item.kind === 'teacher_stamp' || item.kind === 'evidence' || item.kind === 'world_plate' || item.kind === 'remotion_bit';
}

export function replaceTimelineItem(document: TimelineDocument, replacement: TimelineItem): TimelineDocument {
  const index = document.items.findIndex((item) => item.id === replacement.id);
  if (index < 0) return document;
  const items = document.items.slice();
  items[index] = cloneTimelineItem(replacement);
  return {...document, items};
}

export function updateTrackItemIds(document: TimelineDocument): TimelineDocument {
  const itemsByTrack = new Map<string, string[]>();
  for (const item of document.items) {
    const ids = itemsByTrack.get(item.trackId) ?? [];
    ids.push(item.id);
    itemsByTrack.set(item.trackId, ids);
  }
  return {
    ...document,
    tracks: document.tracks.map((track) => ({...track, itemIds: [...(itemsByTrack.get(track.id) ?? [])]})),
  };
}

export function isFrameRange(value: unknown): value is FrameRange {
  if (!isRecord(value)) return false;
  return isInteger(value.startFrame) && isInteger(value.endFrame) && value.startFrame >= 0 && value.endFrame > value.startFrame;
}

export function isRangeInsideDocument(range: FrameRange, document: TimelineDocument): boolean {
  return isFrameRange(range) && range.endFrame <= document.durationFrames;
}

export function isValidVisualTransform(value: unknown): value is VisualTransform {
  if (!isRecord(value) || !isRecord(value.crop)) return false;
  const numericKeys = ['x', 'y', 'scaleX', 'scaleY', 'rotation', 'opacity', 'zIndex'] as const;
  if (!numericKeys.every((key) => isFiniteNumber(value[key]))) return false;
  return (
    isFiniteNumber(value.crop.x) &&
    isFiniteNumber(value.crop.y) &&
    isFiniteNumber(value.crop.width) &&
    isFiniteNumber(value.crop.height) &&
    value.crop.width > 0 &&
    value.crop.height > 0
  );
}

export function mergeVisualTransform(item: TransformableTimelineItem, patch: Omit<Partial<VisualTransform>, 'crop'> & {crop?: Partial<VisualTransform['crop']>}): TransformableTimelineItem {
  const nextCrop = patch.crop ? {...item.transform.crop, ...patch.crop} : item.transform.crop;
  return {
    ...item,
    transform: {...item.transform, ...patch, crop: nextCrop},
  } as TransformableTimelineItem;
}

export function isTimelineDocument(value: unknown): value is TimelineDocument {
  if (!isRecord(value)) return false;
  if (
    value.schemaVersion !== TIMELINE_SCHEMA_VERSION ||
    !isNonEmptyString(value.documentId) ||
    !isNonEmptyString(value.projectId) ||
    !isNonEmptyString(value.snapshotId) ||
    !isNonEmptyString(value.baseSnapshotHash) ||
    !isNonEmptyString(value.compositionId) ||
    !isFiniteNumber(value.fps) ||
    value.fps <= 0 ||
    !isPositiveInteger(value.width) ||
    !isPositiveInteger(value.height) ||
    !isPositiveInteger(value.durationFrames) ||
    !Array.isArray(value.tracks) ||
    !Array.isArray(value.items)
  ) return false;

  const trackIds = new Set<string>();
  const trackKinds = new Set<TimelineTrackKind>();
  for (const rawTrack of value.tracks) {
    if (!isRecord(rawTrack) || !isNonEmptyString(rawTrack.id) || !isTrackKind(rawTrack.kind) || trackIds.has(rawTrack.id) || trackKinds.has(rawTrack.kind)) return false;
    if (typeof rawTrack.label !== 'string' || typeof rawTrack.locked !== 'boolean' || typeof rawTrack.visible !== 'boolean' || !isStringArray(rawTrack.itemIds)) return false;
    trackIds.add(rawTrack.id);
    trackKinds.add(rawTrack.kind);
  }
  if (trackKinds.size !== DEFAULT_TRACK_ORDER.length || DEFAULT_TRACK_ORDER.some((kind) => !trackKinds.has(kind))) return false;

  const itemIds = new Set<string>();
  for (const rawItem of value.items) {
    if (!isTimelineItem(rawItem) || itemIds.has(rawItem.id) || !trackIds.has(rawItem.trackId)) return false;
    if (!isRangeInsideDocument(rawItem.range, value as TimelineDocument)) return false;
    const track = (value.tracks as TimelineTrack[]).find((candidate) => candidate.id === rawItem.trackId);
    if (!track || track.kind !== trackKindForItem(rawItem)) return false;
    itemIds.add(rawItem.id);
  }
  const listedItemIds = new Set<string>();
  for (const track of value.tracks as TimelineTrack[]) {
    for (const itemId of track.itemIds) {
      if (listedItemIds.has(itemId) || !itemIds.has(itemId)) return false;
      listedItemIds.add(itemId);
    }
  }
  return listedItemIds.size === itemIds.size && value.items.every((rawItem) => {
    const item = rawItem as TimelineItem;
    const track = (value.tracks as TimelineTrack[]).find((candidate) => candidate.id === item.trackId);
    return track?.itemIds.includes(item.id) ?? false;
  });
}

function isTimelineItem(value: unknown): value is TimelineItem {
  if (!isRecord(value) || !isNonEmptyString(value.id) || !isNonEmptyString(value.trackId) || !isFrameRange(value.range) || typeof value.label !== 'string' || typeof value.locked !== 'boolean') return false;
  switch (value.kind) {
    case 'scene':
      return isNonEmptyString(value.sceneId) && typeof value.title === 'string' && isStringArray(value.cueIds) && isReviewState(value.reviewState);
    case 'cue':
      return isNonEmptyString(value.cueId) && isNonEmptyString(value.sceneId);
    case 'caption':
      return typeof value.text === 'string' && isStringArray(value.wordIds) && (value.styleId === undefined || typeof value.styleId === 'string') && (value.groupId === undefined || typeof value.groupId === 'string') && (value.lineBreaks === undefined || isNonNegativeIntegerArray(value.lineBreaks)) && isValidVisualTransform(value.transform) && isKeyframeTracks(value.keyframes);
    case 'overlay':
      return isOverlayKind(value.overlayKind) && (value.text === undefined || typeof value.text === 'string') && (value.assetId === undefined || isNonEmptyString(value.assetId)) && isValidVisualTransform(value.transform) && isKeyframeTracks(value.keyframes);
    case 'teacher_stamp':
      return isNonEmptyString(value.assetId) && isValidVisualTransform(value.transform) && isKeyframeTracks(value.keyframes);
    case 'evidence':
      return isNonEmptyString(value.assetId) && isStringArray(value.claimRefs) && typeof value.evidenceEligible === 'boolean' && isValidVisualTransform(value.transform) && isKeyframeTracks(value.keyframes);
    case 'world_plate':
      return isNonEmptyString(value.assetId) && (value.fit === 'contain' || value.fit === 'cover') && isValidVisualTransform(value.transform) && isKeyframeTracks(value.keyframes);
    case 'remotion_bit':
      return isRemotionBitId(value.componentId) && isNonEmptyString(value.presetId) && isRemotionBitProps(value.componentId, value.props) && isValidVisualTransform(value.transform) && isKeyframeTracks(value.keyframes);
    case 'narration':
      return value.locked === true && isNonEmptyString(value.sourceAssetId) && isNonEmptyString(value.sourceSha256) && isFiniteNumber(value.level) && value.level >= 0 && value.level <= 1 && Array.isArray(value.words) && value.words.every(isNarrationWord);
    default:
      return false;
  }
}

function isNarrationWord(value: unknown): boolean {
  return isRecord(value) && isNonEmptyString(value.wordId) && typeof value.text === 'string' && isInteger(value.startFrame) && isInteger(value.endFrame) && value.startFrame >= 0 && value.endFrame > value.startFrame;
}

function isTrackKind(value: unknown): value is TimelineTrackKind {
  return typeof value === 'string' && (DEFAULT_TRACK_ORDER as readonly string[]).includes(value);
}

function isReviewState(value: unknown): value is SceneTimelineItem['reviewState'] {
  return value === 'unreviewed' || value === 'review_only' || value === 'revision_required' || value === 'approved';
}

function isOverlayKind(value: unknown): boolean {
  return value === 'text' || value === 'annotation' || value === 'shape' || value === 'arrow';
}

export function trackKindForItem(item: TimelineItem): TimelineTrackKind {
  switch (item.kind) {
    case 'scene': return 'scenes';
    case 'cue': return 'cues';
    case 'caption': return 'captions';
    case 'overlay': return 'overlays';
    case 'teacher_stamp': return 'teacher_stamp';
    case 'evidence': return 'evidence';
    case 'world_plate': return 'world_plates';
    case 'remotion_bit': return 'overlays';
    case 'narration': return 'narration';
  }
}

function isRemotionBitId(value: unknown): value is RemotionBitId {
  return value === 'fade-in' || value === 'blur-in' || value === 'word-by-word' || value === 'slide-from-left' || value === 'basic-typewriter' || value === 'basic-counter' || value === 'list-reveal' || value === 'grid-stagger' || value === 'mosaic-reframe' || value === '3d-card-stack' || value === 'ken-burns-effect';
}

export function isRemotionBitProps(componentId: RemotionBitId, value: unknown): boolean {
  if (!isRecord(value)) return false;
  const common = ['durationInFrames', 'color', 'backgroundColor', 'fontSize', 'styleId'];
  const specific: Record<RemotionBitId, readonly string[]> = {
    'fade-in': ['text'],
    'blur-in': ['text', 'blurAmount'],
    'word-by-word': ['text', 'staggerFrames'],
    'slide-from-left': ['text', 'distance'],
    'basic-typewriter': ['text', 'typeSpeedFrames', 'showCursor'],
    'basic-counter': ['from', 'to', 'prefix', 'postfix', 'decimals'],
    'list-reveal': ['items', 'staggerFrames'],
    'grid-stagger': ['items', 'columns', 'staggerFrames'],
    'mosaic-reframe': ['images', 'tileCount'],
    '3d-card-stack': ['cards', 'staggerFrames'],
    'ken-burns-effect': ['images', 'scaleFrom', 'scaleTo', 'direction'],
  };
  const allowed = new Set([...common, ...specific[componentId]]);
  return Object.entries(value).every(([key, prop]) => allowed.has(key) && isRemotionBitPropValue(prop));
}

function isRemotionBitPropValue(value: unknown): boolean {
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') return Number.isFinite(value as number) || typeof value !== 'number';
  return Array.isArray(value) && value.every((entry) => typeof entry === 'string');
}

function isKeyframeTracks(value: unknown): boolean {
  if (!isRecord(value)) return false;
  const properties = ['x', 'y', 'scaleX', 'scaleY', 'rotation', 'opacity', 'zIndex'];
  return Object.entries(value).every(([property, keyframes]) => {
    if (!properties.includes(property) || !Array.isArray(keyframes)) return false;
    return keyframes.every((keyframe) => {
      if (!isRecord(keyframe) || !isInteger(keyframe.frame) || keyframe.frame < 0 || !isFiniteNumber(keyframe.value)) return false;
      return (keyframe.easing === undefined || keyframe.easing === 'linear' || keyframe.easing === 'smoothstep' || keyframe.easing === 'ease_in' || keyframe.easing === 'ease_out' || keyframe.easing === 'ease_in_out') && (keyframe.springPreset === undefined || keyframe.springPreset === 'gentle' || keyframe.springPreset === 'snappy' || keyframe.springPreset === 'bouncy');
    });
  });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((entry) => typeof entry === 'string');
}

function isNonNegativeIntegerArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.every((entry) => isInteger(entry) && entry >= 0);
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}

function isInteger(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value);
}

function isPositiveInteger(value: unknown): value is number {
  return isInteger(value) && value > 0;
}
