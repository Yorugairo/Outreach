import {mediaUrl} from '../../api';
import {
  DEFAULT_VISUAL_TRANSFORM,
  createTimelineDocument,
  updateTrackItemIds,
  type TimelineDocument,
  type TimelineItem,
  type TimelineTrack,
  type TimelineTrackKind,
  type VisualTransform,
} from '../../editor';
import type {FrameTrackItem, SnapshotV2} from '../../types';
import type {ProductionTimelineCompositionProps, ProductionTimelineItem} from '../../../../editor/src/ProductionTimelineComposition';

const transform = (zIndex = 0): VisualTransform => ({
  ...DEFAULT_VISUAL_TRANSFORM,
  crop: {...DEFAULT_VISUAL_TRANSFORM.crop},
  zIndex,
});

const transformFromLayout = (raw: FrameTrackItem, zIndex: number, fallback?: Partial<VisualTransform>): VisualTransform => ({
  ...transform(zIndex),
  ...fallback,
  x: raw.layout?.x ?? fallback?.x ?? 0,
  y: raw.layout?.y ?? fallback?.y ?? 0,
  crop: {
    ...DEFAULT_VISUAL_TRANSFORM.crop,
    width: raw.layout?.width ?? fallback?.crop?.width ?? 1,
    height: raw.layout?.height ?? fallback?.crop?.height ?? 1,
  },
});

const itemLabel = (snapshot: SnapshotV2, item: FrameTrackItem): string => {
  if (item.item_type === 'scene') return snapshot.scenes.find((scene) => scene.scene_id === item.scene_id)?.title ?? item.scene_id ?? item.item_id;
  if (item.item_type === 'cue') return snapshot.cues.find((cue) => cue.cue_id === item.cue_id)?.excerpt ?? item.cue_id ?? item.item_id;
  if (item.asset_id) return snapshot.assets.find((asset) => asset.asset_id === item.asset_id)?.label ?? item.asset_id;
  return item.text ?? item.excerpt ?? item.component_id ?? item.item_id;
};

const timelineItem = (snapshot: SnapshotV2, trackId: string, raw: FrameTrackItem): TimelineItem | null => {
  const base = {
    id: raw.item_id,
    trackId,
    range: {startFrame: raw.start_frame, endFrame: raw.end_frame},
    label: itemLabel(snapshot, raw),
    locked: raw.locked,
  };
  if (raw.item_type === 'scene') {
    const scene = snapshot.scenes.find((candidate) => candidate.scene_id === raw.scene_id);
    return {...base, kind: 'scene', sceneId: raw.scene_id ?? raw.item_id, title: scene?.title ?? base.label, cueIds: scene?.cue_refs ?? [], reviewState: scene?.review_state ?? 'unreviewed'};
  }
  if (raw.item_type === 'cue') return {...base, kind: 'cue', cueId: raw.cue_id ?? raw.item_id, sceneId: raw.scene_id ?? snapshot.scenes.find((scene) => scene.start_frame <= raw.start_frame && scene.end_frame >= raw.end_frame)?.scene_id ?? snapshot.scenes[0]?.scene_id ?? 'scene-unknown'};
  if (raw.item_type === 'caption') {
    const start = raw.start_word ?? 0;
    const end = raw.end_word ?? start;
    return {...base, kind: 'caption', text: raw.text ?? raw.excerpt ?? '', wordIds: snapshot.words.slice(start, end + 1).map((word) => word.word_id), styleId: raw.caption_preset ?? raw.style_id ?? 'compact', transform: transformFromLayout(raw, 50, {y: 0.3, crop: {...DEFAULT_VISUAL_TRANSFORM.crop, height: 0.2}}), keyframes: {}};
  }
  if (raw.item_type === 'overlay') return {...base, kind: 'overlay', overlayKind: raw.overlay_kind ?? (raw.asset_id ? 'shape' : 'text'), text: raw.display_text, assetId: raw.asset_id, transform: transformFromLayout(raw, 60), keyframes: {}};
  if (raw.item_type === 'teacher_stamp' && raw.asset_id) return {...base, kind: 'teacher_stamp', assetId: raw.asset_id, transform: transform(80), keyframes: {}};
  if (raw.item_type === 'evidence' && raw.asset_id) return {...base, kind: 'evidence', assetId: raw.asset_id, claimRefs: [], evidenceEligible: Boolean(raw.evidence_eligible), binding: raw.binding, transform: transformFromLayout(raw, 40), keyframes: {}};
  if (raw.item_type === 'world_plate' && raw.asset_id) return {...base, kind: 'world_plate', assetId: raw.asset_id, fit: 'cover', transform: transform(0), keyframes: {}};
  if (raw.item_type === 'remotion_bit') return {...base, kind: 'remotion_bit', componentId: raw.component_id ?? 'fade-in', presetId: raw.preset_id, props: {}, transform: transform(70), keyframes: {}} as TimelineItem;
  if (raw.item_type === 'narration') return {...base, kind: 'narration', sourceAssetId: raw.asset_id ?? snapshot.project_profile.audio.audio_id, sourceSha256: raw.sha256 ?? snapshot.project_profile.audio.sha256, words: snapshot.words.map((word) => ({wordId: word.word_id, text: word.text, startFrame: word.start_frame, endFrame: word.end_frame})), level: 1, locked: true};
  return null;
};

export const snapshotToTimelineDocument = (snapshot: SnapshotV2): TimelineDocument => {
  const tracks: TimelineTrack[] = snapshot.tracks.map((track) => ({
    id: track.track_id,
    kind: track.kind as TimelineTrackKind,
    label: track.label,
    locked: !track.editable,
    visible: true,
    itemIds: [],
  }));
  const items = snapshot.tracks.flatMap((track) => track.items.map((item) => timelineItem(snapshot, track.track_id, item)).filter((item): item is TimelineItem => Boolean(item)));
  return updateTrackItemIds(createTimelineDocument({
    documentId: `${snapshot.snapshot_id}-draft`,
    projectId: snapshot.project_id,
    snapshotId: snapshot.snapshot_id,
    baseSnapshotHash: snapshot.artifact_hash,
    compositionId: 'ProductionTimeline',
    fps: snapshot.project_profile.fps,
    width: snapshot.project_profile.width,
    height: snapshot.project_profile.height,
    durationFrames: snapshot.project_profile.duration_frames,
    tracks,
    items,
  }));
};

export const timelineDocumentToComposition = (document: TimelineDocument, snapshot: SnapshotV2): ProductionTimelineCompositionProps => {
  const assetMap = Object.fromEntries(snapshot.assets.map((asset) => [asset.asset_id, mediaUrl(asset.asset_id)]));
  assetMap[snapshot.project_profile.audio.audio_id] = mediaUrl(snapshot.project_profile.audio.audio_id);
  const items = document.items.flatMap((item): ProductionTimelineItem[] => {
    const durationInFrames = item.range.endFrame - item.range.startFrame;
    const base = {id: item.id, from: item.range.startFrame, durationInFrames, zIndex: 'transform' in item ? item.transform.zIndex : 0};
    const layout = 'transform' in item ? {x: item.transform.x, y: item.transform.y, width: item.transform.crop.width, height: item.transform.crop.height, scaleX: item.transform.scaleX, scaleY: item.transform.scaleY, rotate: item.transform.rotation} : undefined;
    const opacity = 'transform' in item ? item.transform.opacity : 1;
    if (item.kind === 'scene' || item.kind === 'cue') return [];
    if (item.kind === 'caption') {
      const wordsById = new Map(snapshot.words.map((word) => [word.word_id, word]));
      const wordTokens = item.wordIds.flatMap((wordId) => {
        const word = wordsById.get(wordId);
        return word ? [{text: word.text, startFrame: word.start_frame - item.range.startFrame, endFrame: word.end_frame - item.range.startFrame}] : [];
      });
      return [{...base, type: 'caption', text: item.text, caption_preset: item.styleId === 'word_by_word' ? 'word_by_word' : 'compact', word_tokens: wordTokens, layout, opacity}];
    }
    if (item.kind === 'overlay') return [{...base, type: item.overlayKind === 'text' ? 'overlay' : 'annotation', overlayKind: item.overlayKind, display_text: item.text, assetId: item.assetId, layout, opacity} as ProductionTimelineItem];
    if (item.kind === 'teacher_stamp') return [{...base, type: 'teacher_stamp', assetId: item.assetId, text: item.label, layout, opacity}];
    if (item.kind === 'evidence') return [{...base, type: 'evidence', assetId: item.assetId, label: item.label, layout, opacity}];
    if (item.kind === 'world_plate') return [{...base, type: 'world_plate', assetId: item.assetId, label: item.label, layout: {...layout, fit: item.fit}, opacity}];
    if (item.kind === 'remotion_bit') return [{...base, type: 'remotion_bit', bit_id: item.componentId, bit_props: item.props, layout, opacity} as ProductionTimelineItem];
    if (item.kind === 'narration') return [{...base, type: 'narration', assetId: item.sourceAssetId, volume: item.level}];
    return [];
  });
  return {
    schema_version: 'production_console_snapshot.v2',
    width: document.width,
    height: document.height,
    fps: document.fps,
    durationInFrames: document.durationFrames,
    items,
    assetMap,
    backgroundColor: '#0b1015',
  };
};
