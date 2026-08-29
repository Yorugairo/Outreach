import {describe, expect, it} from 'vitest';
import {createTimelineDocument, DEFAULT_VISUAL_TRANSFORM, type TimelineDocument} from '../../editor';
import {diffTimelineDocuments} from './revision';

const baseDocument = (): TimelineDocument => createTimelineDocument({
  documentId: 'document-1',
  projectId: 'project-1',
  snapshotId: 'snapshot-1',
  baseSnapshotHash: 'a'.repeat(64),
  compositionId: 'ProductionTimeline',
  fps: 30,
  width: 1920,
  height: 1080,
  durationFrames: 300,
  items: [{
    id: 'overlay-1', trackId: 'track-overlays', kind: 'overlay', overlayKind: 'text', text: 'Existing', label: 'Existing', locked: false,
    range: {startFrame: 0, endFrame: 90}, transform: structuredClone(DEFAULT_VISUAL_TRANSFORM), keyframes: {},
  }],
});

describe('editorial revision diff', () => {
  it('does not misclassify appended inserts as a manual reorder', () => {
    const base = baseDocument();
    const inserted = {
      id: 'overlay-2', trackId: 'track-overlays', kind: 'overlay' as const, overlayKind: 'arrow' as const, label: 'Arrow', locked: false,
      range: {startFrame: 20, endFrame: 100}, transform: structuredClone(DEFAULT_VISUAL_TRANSFORM), keyframes: {},
    };
    const draft = {...base, items: [...base.items, inserted], tracks: base.tracks.map((track) => track.id === inserted.trackId ? {...track, itemIds: [...track.itemIds, inserted.id]} : track)};
    expect(diffTimelineDocuments(base, draft).map((operation) => operation.op)).toEqual(['insert_item']);
  });

  it('emits reorder only when layer order actually changes', () => {
    const base = baseDocument();
    const second = {
      id: 'overlay-2', trackId: 'track-overlays', kind: 'overlay' as const, overlayKind: 'arrow' as const, label: 'Arrow', locked: false,
      range: {startFrame: 20, endFrame: 100}, transform: structuredClone(DEFAULT_VISUAL_TRANSFORM), keyframes: {},
    };
    const draft = {...base, items: [...base.items, second], tracks: base.tracks.map((track) => track.id === second.trackId ? {...track, itemIds: [second.id, ...track.itemIds]} : track)};
    expect(diffTimelineDocuments(base, draft).map((operation) => operation.op)).toEqual(['insert_item', 'reorder_item']);
  });
});
