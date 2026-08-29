import type {TimelineDocument, TimelineItem} from '../../editor';
import type {SnapshotV2} from '../../types';

export type EditorialOperation = Record<string, unknown> & {op: string};

const comparable = (value: unknown): string => JSON.stringify(value);

const propsFor = (item: TimelineItem) => {
  if ('transform' in item) return {label: item.label, transform: item.transform, ...(item.kind === 'overlay' ? {text: item.text} : {}), ...(item.kind === 'remotion_bit' ? {props: item.props} : {})};
  if (item.kind === 'narration') return {level: item.level};
  return {label: item.label};
};

export const diffTimelineDocuments = (base: TimelineDocument, draft: TimelineDocument): EditorialOperation[] => {
  const operations: EditorialOperation[] = [];
  const baseById = new Map(base.items.map((item) => [item.id, item]));
  const draftById = new Map(draft.items.map((item) => [item.id, item]));
  for (const item of base.items) {
    if (!draftById.has(item.id)) operations.push({op: 'remove_item', item_id: item.id});
  }
  for (const item of draft.items) {
    const previous = baseById.get(item.id);
    if (!previous) {
      operations.push({op: 'insert_item', item});
      continue;
    }
    if (item.kind === 'scene' && previous.kind === 'scene' && comparable(item.range) !== comparable(previous.range)) operations.push({op: 'set_scene_boundary', scene_id: item.sceneId, start_frame: item.range.startFrame, end_frame: item.range.endFrame});
    else if (item.kind === 'cue' && previous.kind === 'cue' && comparable(item.range) !== comparable(previous.range)) operations.push({op: 'set_cue_range', cue_id: item.cueId, start_frame: item.range.startFrame, end_frame: item.range.endFrame});
    else if (item.kind === 'narration' && previous.kind === 'narration') {
      if (comparable(item.range) !== comparable(previous.range) || item.level !== previous.level) operations.push({op: 'set_narration_trim_volume', item_id: item.id, start_frame: item.range.startFrame, end_frame: item.range.endFrame, volume: item.level});
    } else if (comparable(item.range) !== comparable(previous.range)) operations.push({op: 'move_trim_item', item_id: item.id, start_frame: item.range.startFrame, end_frame: item.range.endFrame});
    if (comparable(propsFor(item)) !== comparable(propsFor(previous))) operations.push({op: 'set_item_props', item_id: item.id, props: propsFor(item)});
    if (item.kind === 'caption' && previous.kind === 'caption' && (item.styleId !== previous.styleId || comparable(item.lineBreaks) !== comparable(previous.lineBreaks) || item.groupId !== previous.groupId)) operations.push({op: 'set_caption_layout', item_id: item.id, style_id: item.styleId ?? 'default', line_breaks: item.lineBreaks ?? [], group_id: item.groupId ?? null});
    if ('keyframes' in item && 'keyframes' in previous && comparable(item.keyframes) !== comparable(previous.keyframes)) operations.push({op: 'set_item_keyframes', item_id: item.id, keyframes: item.keyframes});
  }
  for (const track of draft.tracks) {
    const previous = base.tracks.find((candidate) => candidate.id === track.id);
    if (!previous || comparable(track.itemIds) === comparable(previous.itemIds)) continue;
    // remove_item deletes membership first and insert_item appends new items in
    // draft item order. Only emit reorder_item when the requested order differs
    // from that deterministic replay result; membership changes are not a layer
    // reorder by themselves.
    const replayOrder = previous.itemIds.filter((itemId) => draftById.has(itemId));
    for (const item of draft.items) {
      if (!baseById.has(item.id) && item.trackId === track.id) replayOrder.push(item.id);
    }
    if (comparable(track.itemIds) !== comparable(replayOrder)) operations.push({op: 'reorder_item', track_id: track.id, item_ids: track.itemIds});
  }
  return operations;
};

const stable = (value: unknown): string => JSON.stringify(sortJson(value));

const sortJson = (value: unknown): unknown => {
  if (Array.isArray(value)) return value.map(sortJson);
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return Object.fromEntries(Object.keys(record).sort().map((key) => [key, sortJson(record[key])]));
  }
  return value;
};

const sha256 = async (value: string): Promise<string> => {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, '0')).join('');
};

export const buildEditorialRevision = async ({snapshot, base, draft, note, operatorId}: {snapshot: SnapshotV2; base: TimelineDocument; draft: TimelineDocument; note: string; operatorId: string}) => {
  const createdAt = new Date().toISOString();
  const operations = diffTimelineDocuments(base, draft);
  if (!operations.length) throw new Error('No editorial changes to save.');
  const idSeed = await sha256(stable({base_snapshot_hash: snapshot.artifact_hash, operations, created_at: createdAt}));
  const core = {
    schema_version: 'editorial_timeline_revision.v1',
    revision_id: `revision-${idSeed.slice(0, 16)}`,
    revision_only: true,
    base_snapshot_hash: snapshot.artifact_hash,
    base_artifact_hashes: snapshot.base_artifact_hashes,
    source_artifact_hashes: snapshot.base_artifact_hashes,
    operator: {operator_id: operatorId, created_at: createdAt},
    operations,
    note: note.trim() || null,
  };
  return {...core, artifact_hash: await sha256(stable(core))};
};

export const downloadJson = (filename: string, payload: unknown) => {
  const url = URL.createObjectURL(new Blob([`${JSON.stringify(payload, null, 2)}\n`], {type: 'application/json'}));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
};
