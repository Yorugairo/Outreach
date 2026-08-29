import {describe, expect, it} from 'vitest';
import {
  DEFAULT_VISUAL_TRANSFORM,
  buildSnapPoints,
  canRedo,
  canUndo,
  createEditorState,
  createTimelineDocument,
  isSelected,
  reduceEditorCommand,
  selectItem,
  selectionBounds,
  snapFrame,
  snapRange,
  undo,
  redo,
  validateCueContainment,
  validateSceneContiguity,
  validateWordGapTrim,
  wordGaps,
  type TimelineDocument,
  type RemotionBitTimelineItemFor,
} from './index';

function makeDocument(): TimelineDocument {
  return createTimelineDocument({
    documentId: 'draft-1',
    projectId: 'project-1',
    snapshotId: 'snapshot-1',
    baseSnapshotHash: 'a'.repeat(64),
    compositionId: 'ProductionTimeline',
    fps: 30,
    width: 1376,
    height: 768,
    durationFrames: 300,
    items: [
      {
        id: 'scene-1', trackId: 'track-scenes', kind: 'scene', sceneId: 'scene-1', label: 'Opening', title: 'Opening',
        range: {startFrame: 0, endFrame: 150}, locked: false, cueIds: ['cue-1'], reviewState: 'approved',
      },
      {
        id: 'scene-2', trackId: 'track-scenes', kind: 'scene', sceneId: 'scene-2', label: 'Mechanism', title: 'Mechanism',
        range: {startFrame: 150, endFrame: 300}, locked: false, cueIds: ['cue-2'], reviewState: 'unreviewed',
      },
      {id: 'cue-1', trackId: 'track-cues', kind: 'cue', cueId: 'cue-1', sceneId: 'scene-1', label: 'Opening cue', range: {startFrame: 20, endFrame: 40}, locked: false},
      {id: 'cue-2', trackId: 'track-cues', kind: 'cue', cueId: 'cue-2', sceneId: 'scene-2', label: 'Mechanism cue', range: {startFrame: 170, endFrame: 200}, locked: false},
      {
        id: 'caption-1', trackId: 'track-captions', kind: 'caption', label: 'Caption', text: 'Editable overlay', wordIds: ['word-1'],
        range: {startFrame: 20, endFrame: 90}, locked: false, transform: {...DEFAULT_VISUAL_TRANSFORM, crop: {...DEFAULT_VISUAL_TRANSFORM.crop}}, keyframes: {},
      },
      {
        id: 'bit-1', trackId: 'track-overlays', kind: 'remotion_bit', label: 'Fade bit', componentId: 'fade-in', presetId: 'fade-in-default', props: {text: 'Bit'},
        range: {startFrame: 60, endFrame: 120}, locked: false, transform: {...DEFAULT_VISUAL_TRANSFORM, crop: {...DEFAULT_VISUAL_TRANSFORM.crop}}, keyframes: {},
      },
      {
        id: 'narration-1', trackId: 'track-narration', kind: 'narration', label: 'Approved narration', sourceAssetId: 'audio-1', sourceSha256: 'b'.repeat(64),
        range: {startFrame: 0, endFrame: 300}, locked: true, level: 1, words: [
          {wordId: 'word-1', text: 'One', startFrame: 10, endFrame: 30},
          {wordId: 'word-2', text: 'approved', startFrame: 50, endFrame: 70},
          {wordId: 'word-3', text: 'source', startFrame: 120, endFrame: 150},
        ],
      },
    ],
  });
}

describe('timeline document and semantic validation', () => {
  it('creates the fixed track set and keeps scene ranges contiguous', () => {
    const document = makeDocument();
    expect(document.tracks.map((track) => track.kind)).toEqual([
      'scenes', 'cues', 'captions', 'overlays', 'teacher_stamp', 'evidence', 'world_plates', 'narration',
    ]);
    expect(document.tracks.find((track) => track.kind === 'narration')?.locked).toBe(true);
    expect(validateSceneContiguity(document.items.filter((item) => item.kind === 'scene'), document.durationFrames).valid).toBe(true);
    expect(validateCueContainment(document.items.filter((item) => item.kind === 'cue'), document.items.filter((item) => item.kind === 'scene')).valid).toBe(true);
  });

  it('reports gaps, overlaps, and cues crossing scene boundaries', () => {
    const document = makeDocument();
    const scenes = document.items.filter((item) => item.kind === 'scene');
    expect(validateSceneContiguity([{range: {startFrame: 0, endFrame: 10}}, {range: {startFrame: 12, endFrame: 20}}], 20).issues[0].code).toBe('gap');
    expect(validateSceneContiguity([{range: {startFrame: 0, endFrame: 11}}, {range: {startFrame: 10, endFrame: 20}}], 20).issues[0].code).toBe('overlap');
    expect(validateCueContainment([{id: 'crossing', cueId: 'crossing', sceneId: 'scene-1', range: {startFrame: 140, endFrame: 160}}], scenes).valid).toBe(false);
  });
});

describe('selection and snapping', () => {
  it('supports replace/add/toggle selection and computes bounds', () => {
    const document = makeDocument();
    let selection = createEditorState(document).selection;
    selection = selectItem(selection, 'caption-1');
    selection = selectItem(selection, 'cue-1', 'add');
    expect(isSelected(selection, 'caption-1')).toBe(true);
    expect(selectionBounds(document, selection)).toEqual({startFrame: 20, endFrame: 90});
    selection = selectItem(selection, 'caption-1', 'toggle');
    expect(selection.selectedItemIds).toEqual(['cue-1']);
  });

  it('snaps playheads and ranges to deterministic nearest edges', () => {
    const document = makeDocument();
    const points = buildSnapPoints(document, {excludeItemIds: ['caption-1']});
    expect(snapFrame(148, points, 3)).toMatchObject({frame: 150, snapped: true, deltaFrames: 2});
    expect(snapRange({startFrame: 86, endFrame: 146}, points, {thresholdFrames: 5, minFrame: 0, maxFrame: 300})).toMatchObject({deltaFrames: 4, edge: 'end'});
  });
});

describe('editor command reducer', () => {
  it('moves a scene boundary by updating both adjacent scenes atomically', () => {
    const document = makeDocument();
    let state = createEditorState(document);
    state = reduceEditorCommand(state, {type: 'set-scene-boundary', sceneId: 'scene-1', boundaryFrame: 130});
    const sceneOne = state.document.items.find((item) => item.kind === 'scene' && item.sceneId === 'scene-1');
    const sceneTwo = state.document.items.find((item) => item.kind === 'scene' && item.sceneId === 'scene-2');
    expect(sceneOne?.range).toEqual({startFrame: 0, endFrame: 130});
    expect(sceneTwo?.range).toEqual({startFrame: 130, endFrame: 300});
    expect(state.history.past).toHaveLength(1);
    const rejected = reduceEditorCommand(state, {type: 'set-scene-boundary', sceneId: 'scene-1', boundaryFrame: 180});
    expect(rejected.document).toBe(state.document);
    expect(rejected.lastError).toContain('cue');
    const startBoundary = reduceEditorCommand(createEditorState(document), {type: 'set-scene-boundary', sceneId: 'scene-2', boundaryFrame: 130, side: 'start'});
    expect(startBoundary.document.items.find((item) => item.kind === 'scene' && item.sceneId === 'scene-1')?.range.endFrame).toBe(130);
    expect(startBoundary.document.items.find((item) => item.kind === 'scene' && item.sceneId === 'scene-2')?.range.startFrame).toBe(130);

    const contiguousCues = {...document, items: document.items.map((item) => item.id === 'cue-1' ? {...item, range: {startFrame: 20, endFrame: 150}} : item.id === 'cue-2' ? {...item, range: {startFrame: 150, endFrame: 200}} : item)};
    const movedWithCues = reduceEditorCommand(createEditorState(contiguousCues), {type: 'set-scene-boundary', sceneId: 'scene-1', boundaryFrame: 140});
    expect(movedWithCues.document.items.find((item) => item.id === 'cue-1')?.range.endFrame).toBe(140);
    expect(movedWithCues.document.items.find((item) => item.id === 'cue-2')?.range.startFrame).toBe(140);
  });

  it('inserts, duplicates, reorders, and removes items while maintaining track indexes', () => {
    const document = makeDocument();
    let state = createEditorState(document);
    const bit = document.items.find((item) => item.id === 'bit-1') as RemotionBitTimelineItemFor<'fade-in'> | undefined;
    if (!bit) throw new Error('fixture Remotion Bit missing');
    const inserted = {...bit, id: 'bit-2', label: 'Second bit', range: {startFrame: 125, endFrame: 175}, props: {text: 'Second'}};
    state = reduceEditorCommand(state, {type: 'insert-item', item: inserted});
    expect(state.document.tracks.find((track) => track.id === 'track-overlays')?.itemIds).toEqual(['bit-1', 'bit-2']);
    state = reduceEditorCommand(state, {type: 'update-item', itemId: 'bit-2', patch: {props: {text: 'Edited bit'}}});
    expect((state.document.items.find((item) => item.id === 'bit-2') as typeof inserted).props.text).toBe('Edited bit');
    state = reduceEditorCommand(state, {type: 'duplicate-item', itemId: 'bit-2', newItemId: 'bit-3', offsetFrames: 5});
    expect(state.document.tracks.find((track) => track.id === 'track-overlays')?.itemIds).toEqual(['bit-1', 'bit-2', 'bit-3']);
    state = reduceEditorCommand(state, {type: 'reorder-item', itemId: 'bit-3', toIndex: 0});
    expect(state.document.tracks.find((track) => track.id === 'track-overlays')?.itemIds).toEqual(['bit-3', 'bit-1', 'bit-2']);
    state = reduceEditorCommand(state, {type: 'remove-item', itemId: 'bit-1'});
    expect(state.document.tracks.find((track) => track.id === 'track-overlays')?.itemIds).toEqual(['bit-3', 'bit-2']);
  });

  it('records edits, limits history to 100 entries, and supports undo/redo', () => {
    const document = makeDocument();
    let state = createEditorState(document);
    state = reduceEditorCommand(state, {type: 'update-item', itemId: 'caption-1', patch: {text: 'Must remain locked'}});
    expect(state.lastError).toContain('protected');
    state = reduceEditorCommand(state, {type: 'update-item', itemId: 'caption-1', patch: {label: 'Updated'}});
    expect(state.document.items.find((item) => item.id === 'caption-1')?.kind).toBe('caption');
    expect(canUndo(state)).toBe(true);
    state = undo(state);
    expect(state.document.items.find((item) => item.id === 'caption-1')?.kind).toBe('caption');
    expect((state.document.items.find((item) => item.id === 'caption-1') as {label: string}).label).toBe('Caption');
    expect(canRedo(state)).toBe(true);
    state = redo(state);
    expect((state.document.items.find((item) => item.id === 'caption-1') as {label: string}).label).toBe('Updated');

    for (let index = 0; index < 105; index += 1) {
      state = reduceEditorCommand(state, {type: 'update-item', itemId: 'caption-1', patch: {label: `Revision ${index}`} });
    }
    expect(state.history.past).toHaveLength(100);
    state = undo(state);
    state = reduceEditorCommand(state, {type: 'update-item', itemId: 'caption-1', patch: {label: 'New branch'}});
    expect(canRedo(state)).toBe(false);
  });

  it('rejects arbitrary narration mutations but accepts level and word-gap trim commands', () => {
    const document = makeDocument();
    let state = createEditorState(document);
    state = reduceEditorCommand(state, {type: 'update-item', itemId: 'narration-1', patch: {label: 'Changed'}});
    expect(state.lastError).toContain('locked');
    expect((state.document.items.find((item) => item.id === 'narration-1') as {label: string}).label).toBe('Approved narration');
    state = reduceEditorCommand(state, {type: 'set-narration-level', itemId: 'narration-1', level: 0.75});
    expect((state.document.items.find((item) => item.id === 'narration-1') as {level: number}).level).toBe(0.75);
    const invalid = validateWordGapTrim({originalRange: {startFrame: 0, endFrame: 300}, proposedRange: {startFrame: 20, endFrame: 300}, words: (document.items.find((item) => item.kind === 'narration') as Extract<typeof document.items[number], {kind: 'narration'}>).words});
    expect(invalid.valid).toBe(false);
    const valid = validateWordGapTrim({originalRange: {startFrame: 0, endFrame: 300}, proposedRange: {startFrame: 35, endFrame: 110}, words: (document.items.find((item) => item.kind === 'narration') as Extract<typeof document.items[number], {kind: 'narration'}>).words});
    expect(valid.valid).toBe(true);
    expect(wordGaps((document.items.find((item) => item.kind === 'narration') as Extract<typeof document.items[number], {kind: 'narration'}>).words, {startFrame: 0, endFrame: 300})).toEqual([
      {startFrame: 0, endFrame: 10}, {startFrame: 30, endFrame: 50}, {startFrame: 70, endFrame: 120}, {startFrame: 150, endFrame: 300},
    ]);
  });
});
