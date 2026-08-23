import {cloneTimelineItem, findNarrationItem, findTimelineItem, isRemotionBitProps, isTransformableItem, mergeVisualTransform, replaceTimelineItem, trackKindForItem} from './document';
import {normalizeKeyframes, validateKeyframes} from './keyframes';
import {clearSelection, createSelection, focusScene, selectItem, setSelection} from './selection';
import {validateCueContainment, validateSceneContiguity, validateWordGapTrim} from './validation';
import {
  MAX_HISTORY_ENTRIES,
  type EditorCommand,
  type EditorState,
  type CueTimelineItem,
  type FrameRange,
  type NarrationTimelineItem,
  type RemotionBitTimelineItem,
  type SceneTimelineItem,
  type SelectionState,
  type TimelineDocument,
  type TimelineItem,
  type VisualTransform,
} from './types';

type CoreResult = {
  document: TimelineDocument;
  selection: SelectionState;
  error: string | null;
};

export function createEditorState(
  document: TimelineDocument,
  selection: Partial<SelectionState> = {},
  historyLimit = MAX_HISTORY_ENTRIES,
): EditorState {
  const limit = Number.isFinite(historyLimit) ? Math.max(1, Math.min(MAX_HISTORY_ENTRIES, Math.trunc(historyLimit))) : MAX_HISTORY_ENTRIES;
  const initialSelection = setSelection(createSelection(selection), selection.selectedItemIds ?? [], selection.primaryItemId);
  return {
    document,
    selection: normalizeSelection(document, initialSelection),
    history: {past: [], future: [], limit},
    lastError: null,
  };
}

export function reduceEditorCommand(state: EditorState, command: EditorCommand): EditorState {
  if (command.type === 'undo') return undo(state);
  if (command.type === 'redo') return redo(state);
  if (command.type === 'batch') return reduceBatch(state, command.commands);

  const result = applyCore(state, command);
  if (result.error) return {...state, lastError: result.error};
  if (result.document === state.document) return {...state, selection: result.selection, lastError: null};
  return commit(state, result.document, result.selection);
}

export const editorReducer = reduceEditorCommand;
export const reducer = reduceEditorCommand;
export const applyEditorCommand = reduceEditorCommand;

export function undo(state: EditorState): EditorState {
  const previous = state.history.past[state.history.past.length - 1];
  if (!previous) return {...state, lastError: null};
  return {
    ...state,
    document: previous,
    selection: normalizeSelection(previous, state.selection),
    history: {
      ...state.history,
      past: state.history.past.slice(0, -1),
      future: [state.document, ...state.history.future].slice(0, state.history.limit),
    },
    lastError: null,
  };
}

export function redo(state: EditorState): EditorState {
  const next = state.history.future[0];
  if (!next) return {...state, lastError: null};
  return {
    ...state,
    document: next,
    selection: normalizeSelection(next, state.selection),
    history: {
      ...state.history,
      past: [...state.history.past, state.document].slice(-state.history.limit),
      future: state.history.future.slice(1),
    },
    lastError: null,
  };
}

export const canUndo = (state: EditorState): boolean => state.history.past.length > 0;
export const canRedo = (state: EditorState): boolean => state.history.future.length > 0;

function reduceBatch(state: EditorState, commands: readonly EditorCommand[]): EditorState {
  let working: EditorState = {...state, lastError: null};
  for (const command of commands) {
    if (command.type === 'undo' || command.type === 'redo' || command.type === 'batch') return {...state, lastError: 'nested history commands are not allowed in a batch'};
    const result = applyCore(working, command);
    if (result.error) return {...state, lastError: result.error};
    working = {...working, document: result.document, selection: result.selection};
  }
  if (working.document === state.document) return {...state, selection: working.selection, lastError: null};
  return commit(state, working.document, working.selection);
}

function setSceneBoundary(state: EditorState, sceneId: string, boundaryFrame: number, side?: 'start' | 'end'): CoreResult {
  if (!Number.isInteger(boundaryFrame)) return unchanged(state, 'scene boundary must be an integer frame');
  const scenes = state.document.items
    .filter((item): item is SceneTimelineItem => item.kind === 'scene')
    .slice()
    .sort((left, right) => left.range.startFrame - right.range.startFrame || left.id.localeCompare(right.id));
  const targetIndex = scenes.findIndex((scene) => scene.sceneId === sceneId || scene.id === sceneId);
  if (targetIndex < 0) return unchanged(state, `unknown scene: ${sceneId}`);
  const resolvedSide = side ?? inferBoundarySide(scenes, targetIndex, boundaryFrame);
  if (!resolvedSide) return unchanged(state, 'scene boundary has no valid adjacent scene');
  const leftIndex = resolvedSide === 'start' ? targetIndex - 1 : targetIndex;
  const rightIndex = resolvedSide === 'start' ? targetIndex : targetIndex + 1;
  const left = scenes[leftIndex];
  const right = scenes[rightIndex];
  if (!left || !right) return unchanged(state, 'scene boundary has no adjacent scene');
  if (left.locked || right.locked) return unchanged(state, 'scene boundary is locked');
  if (boundaryFrame <= left.range.startFrame || boundaryFrame >= right.range.endFrame || boundaryFrame < 0 || boundaryFrame > state.document.durationFrames) return unchanged(state, 'scene boundary would create an invalid adjacent range');
  if (left.range.endFrame === boundaryFrame && right.range.startFrame === boundaryFrame) return {document: state.document, selection: state.selection, error: null};

  const previousBoundary = left.range.endFrame;
  let document = replaceTimelineItem(state.document, {...left, range: {startFrame: left.range.startFrame, endFrame: boundaryFrame}});
  document = replaceTimelineItem(document, {...right, range: {startFrame: boundaryFrame, endFrame: right.range.endFrame}});
  // Scene-edge cues move with the shared boundary as one command. This keeps a
  // contiguous narration-derived cue sheet editable even when there is no gap
  // between the final cue of the left scene and first cue of the right scene.
  for (const cue of document.items.filter((item): item is CueTimelineItem => item.kind === 'cue')) {
    if (cue.sceneId === left.sceneId && cue.range.endFrame === previousBoundary) {
      if (boundaryFrame <= cue.range.startFrame) return unchanged(state, 'scene boundary would collapse the adjacent cue');
      document = replaceTimelineItem(document, {...cue, range: {...cue.range, endFrame: boundaryFrame}});
    } else if (cue.sceneId === right.sceneId && cue.range.startFrame === previousBoundary) {
      if (boundaryFrame >= cue.range.endFrame) return unchanged(state, 'scene boundary would collapse the adjacent cue');
      document = replaceTimelineItem(document, {...cue, range: {...cue.range, startFrame: boundaryFrame}});
    }
  }
  const sceneResult = validateSceneContiguity(document.items.filter((item) => item.kind === 'scene'), document.durationFrames);
  if (!sceneResult.valid) return unchanged(state, `scene ranges are not contiguous: ${sceneResult.issues[0].code}`);
  const cueResult = validateCueContainment(document.items.filter((item) => item.kind === 'cue'), document.items.filter((item) => item.kind === 'scene'));
  if (!cueResult.valid) return unchanged(state, `cue is outside its scene: ${cueResult.issues[0].code}`);
  return {document, selection: state.selection, error: null};
}

function inferBoundarySide(scenes: readonly SceneTimelineItem[], targetIndex: number, boundaryFrame: number): 'start' | 'end' | undefined {
  const target = scenes[targetIndex];
  const previous = scenes[targetIndex - 1];
  const next = scenes[targetIndex + 1];
  const canMoveStart = !!previous && boundaryFrame > previous.range.startFrame && boundaryFrame < target.range.endFrame;
  const canMoveEnd = !!next && boundaryFrame > target.range.startFrame && boundaryFrame < next.range.endFrame;
  if (canMoveStart && canMoveEnd) {
    return Math.abs(boundaryFrame - target.range.startFrame) <= Math.abs(boundaryFrame - target.range.endFrame) ? 'start' : 'end';
  }
  if (canMoveStart) return 'start';
  if (canMoveEnd) return 'end';
  return undefined;
}

function insertItem(state: EditorState, item: TimelineItem, index?: number): CoreResult {
  if (findTimelineItem(state.document, item.id)) return unchanged(state, `item already exists: ${item.id}`);
  if (item.kind === 'narration') return unchanged(state, 'narration source cannot be inserted by the editor');
  if (!isValidRange(item.range, state.document.durationFrames)) return unchanged(state, `invalid range for item: ${item.id}`);
  const track = state.document.tracks.find((candidate) => candidate.id === item.trackId);
  if (!track) return unchanged(state, `unknown track: ${item.trackId}`);
  if (track.kind !== trackKindForItem(item)) return unchanged(state, `item kind does not match track: ${item.id}`);
  if (index !== undefined && (!Number.isInteger(index) || index < 0)) return unchanged(state, 'insert index must be a non-negative integer');
  const nextItem = cloneTimelineItem(item);
  const items = [...state.document.items, nextItem];
  const itemIds = track.itemIds.filter((itemId) => itemId !== item.id);
  const insertAt = Math.min(index ?? itemIds.length, itemIds.length);
  itemIds.splice(insertAt, 0, item.id);
  const document = {...state.document, items, tracks: replaceTrackItemIds(state.document, track.id, itemIds)};
  const semanticError = item.kind === 'scene' || item.kind === 'cue' ? validateSemanticRanges(document, item) : null;
  if (semanticError) return unchanged(state, semanticError);
  return {document, selection: state.selection, error: null};
}

function removeItem(state: EditorState, itemId: string): CoreResult {
  const item = findTimelineItem(state.document, itemId);
  if (!item) return unchanged(state, `unknown item: ${itemId}`);
  if (item.locked || item.kind === 'scene' || item.kind === 'cue') return unchanged(state, `protected item cannot be removed: ${item.id}`);
  const document = {
    ...state.document,
    items: state.document.items.filter((candidate) => candidate.id !== item.id),
    tracks: state.document.tracks.map((track) => ({...track, itemIds: track.itemIds.filter((candidateId) => candidateId !== item.id)})),
  };
  return {document, selection: state.selection, error: null};
}

function duplicateItem(state: EditorState, itemId: string, newItemId: string, offsetFrames: number): CoreResult {
  const item = findTimelineItem(state.document, itemId);
  if (!item) return unchanged(state, `unknown item: ${itemId}`);
  if (item.locked || item.kind === 'scene' || item.kind === 'cue') return unchanged(state, `protected item cannot be duplicated: ${item.id}`);
  if (!newItemId.trim()) return unchanged(state, 'duplicate item id is empty');
  if (findTimelineItem(state.document, newItemId)) return unchanged(state, `item already exists: ${newItemId}`);
  if (!Number.isInteger(offsetFrames)) return unchanged(state, 'duplicate offset must be an integer');
  const range = {startFrame: item.range.startFrame + offsetFrames, endFrame: item.range.endFrame + offsetFrames};
  if (!isValidRange(range, state.document.durationFrames)) return unchanged(state, 'duplicate would leave the document');
  const copy = cloneTimelineItem({...item, id: newItemId, label: `${item.label} copy`, range} as TimelineItem);
  const sourceTrack = state.document.tracks.find((track) => track.id === item.trackId);
  if (!sourceTrack) return unchanged(state, `unknown track: ${item.trackId}`);
  const sourceIndex = sourceTrack.itemIds.indexOf(item.id);
  const itemIds = sourceTrack.itemIds.slice();
  itemIds.splice(sourceIndex < 0 ? itemIds.length : sourceIndex + 1, 0, copy.id);
  const document = {...state.document, items: [...state.document.items, copy], tracks: replaceTrackItemIds(state.document, sourceTrack.id, itemIds)};
  return {document, selection: state.selection, error: null};
}

function reorderItem(state: EditorState, itemId: string, toIndex: number): CoreResult {
  const item = findTimelineItem(state.document, itemId);
  if (!item) return unchanged(state, `unknown item: ${itemId}`);
  if (item.locked) return unchanged(state, 'locked track items cannot be reordered');
  if (!Number.isInteger(toIndex) || toIndex < 0) return unchanged(state, 'reorder index must be a non-negative integer');
  const track = state.document.tracks.find((candidate) => candidate.id === item.trackId);
  if (!track || !track.itemIds.includes(item.id)) return unchanged(state, `item is not indexed by its track: ${item.id}`);
  const itemIds = track.itemIds.filter((candidateId) => candidateId !== item.id);
  const insertAt = Math.min(toIndex, itemIds.length);
  itemIds.splice(insertAt, 0, item.id);
  if (itemIds.every((candidateId, index) => candidateId === track.itemIds[index])) return {document: state.document, selection: state.selection, error: null};
  return {document: {...state.document, tracks: replaceTrackItemIds(state.document, track.id, itemIds)}, selection: state.selection, error: null};
}

function replaceTrackItemIds(document: TimelineDocument, trackId: string, itemIds: string[]): TimelineDocument['tracks'] {
  return document.tracks.map((track) => track.id === trackId ? {...track, itemIds: [...itemIds]} : {...track, itemIds: [...track.itemIds]});
}

function applyCore(state: EditorState, command: Exclude<EditorCommand, {type: 'undo'} | {type: 'redo'} | {type: 'batch'}>): CoreResult {
  switch (command.type) {
    case 'select': {
      if (!findTimelineItem(state.document, command.itemId)) return unchanged(state, `unknown item: ${command.itemId}`);
      return {document: state.document, selection: selectItem(state.selection, command.itemId, command.mode), error: null};
    }
    case 'set-selection':
      return {document: state.document, selection: normalizeSelection(state.document, command.selection), error: null};
    case 'clear-selection':
      return {document: state.document, selection: clearSelection(state.selection), error: null};
    case 'focus-scene':
      if (command.sceneId && !state.document.items.some((item) => item.kind === 'scene' && item.sceneId === command.sceneId)) return unchanged(state, `unknown scene: ${command.sceneId}`);
      return {document: state.document, selection: focusScene(state.selection, command.sceneId), error: null};
    case 'move-item': {
      const item = findTimelineItem(state.document, command.itemId);
      if (!item) return unchanged(state, `unknown item: ${command.itemId}`);
      if (!Number.isInteger(command.deltaFrames)) return unchanged(state, 'deltaFrames must be an integer');
      return updateRange(state, item, {startFrame: item.range.startFrame + command.deltaFrames, endFrame: item.range.endFrame + command.deltaFrames});
    }
    case 'set-item-range': {
      const item = findTimelineItem(state.document, command.itemId);
      if (!item) return unchanged(state, `unknown item: ${command.itemId}`);
      return updateRange(state, item, command.range);
    }
    case 'set-scene-boundary':
      return setSceneBoundary(state, command.sceneId, command.boundaryFrame, command.side);
    case 'update-item': {
      let item = findTimelineItem(state.document, command.itemId);
      if (!item) return unchanged(state, `unknown item: ${command.itemId}`);
      if (item.locked) return unchanged(state, `item is locked: ${item.id}`);
      if (command.patch.range) {
        const rangeResult = updateRange(state, item, command.patch.range);
        if (rangeResult.error) return rangeResult;
        state = {...state, document: rangeResult.document};
        item = findTimelineItem(state.document, item.id) as TimelineItem;
      }
      let replacement: TimelineItem = {...item, label: command.patch.label ?? item.label} as TimelineItem;
      if (command.patch.text !== undefined) {
        if (replacement.kind !== 'overlay') return unchanged(state, `transcript text is protected for item: ${item.id}`);
        replacement = {...replacement, text: command.patch.text};
      }
      if (command.patch.styleId !== undefined || command.patch.groupId !== undefined || command.patch.lineBreaks !== undefined) {
        if (replacement.kind !== 'caption') return unchanged(state, `caption metadata is not editable for item: ${item.id}`);
        if (command.patch.lineBreaks && command.patch.lineBreaks.some((lineBreak) => !Number.isInteger(lineBreak) || lineBreak < 0)) return unchanged(state, 'caption line breaks must be non-negative integers');
        replacement = {
          ...replacement,
          ...(command.patch.styleId === undefined ? {} : {styleId: command.patch.styleId}),
          ...(command.patch.groupId === undefined ? {} : {groupId: command.patch.groupId}),
          ...(command.patch.lineBreaks === undefined ? {} : {lineBreaks: [...command.patch.lineBreaks]}),
        };
      }
      if (command.patch.props !== undefined) {
        if (replacement.kind !== 'remotion_bit') return unchanged(state, `Remotion Bit props are not editable for item: ${item.id}`);
        const props = {...replacement.props, ...command.patch.props};
        if (!isRemotionBitProps(replacement.componentId, props)) return unchanged(state, `unsupported Remotion Bit prop for item: ${item.id}`);
        replacement = {...replacement, props} as RemotionBitTimelineItem;
      }
      if (command.patch.level !== undefined) return unchanged(state, 'narration level requires set-narration-level');
      if (command.patch.transform !== undefined) {
        if (!isTransformableItem(replacement)) return unchanged(state, `transform is not supported for item: ${item.id}`);
        const transformed = mergeVisualTransform(replacement, command.patch.transform);
        if (!isFiniteTransform(transformed.transform)) return unchanged(state, `invalid transform for item: ${item.id}`);
        replacement = transformed;
      }
      return {document: replaceTimelineItem(state.document, replacement), selection: state.selection, error: null};
    }
    case 'set-keyframes': {
      const item = findTimelineItem(state.document, command.itemId);
      if (!item) return unchanged(state, `unknown item: ${command.itemId}`);
      if (item.locked) return unchanged(state, `item is locked: ${item.id}`);
      if (!isTransformableItem(item)) return unchanged(state, `keyframes are not supported for item: ${item.id}`);
      const validation = validateKeyframes(command.keyframes, item.range);
      if (!validation.valid) return unchanged(state, validation.errors.join('; '));
      return {document: replaceTimelineItem(state.document, {...item, keyframes: {...item.keyframes, [command.property]: normalizeKeyframes(command.keyframes)}}), selection: state.selection, error: null};
    }
    case 'trim-narration': {
      const narration = findNarrationItem(state.document, command.itemId);
      if (!narration) return unchanged(state, command.itemId ? `unknown narration item: ${command.itemId}` : 'narration item is missing');
      return trimNarration(state, narration, command.range);
    }
    case 'set-narration-level': {
      const narration = findNarrationItem(state.document, command.itemId);
      if (!narration) return unchanged(state, command.itemId ? `unknown narration item: ${command.itemId}` : 'narration item is missing');
      if (!Number.isFinite(command.level) || command.level < 0 || command.level > 1) return unchanged(state, 'narration level must be between 0 and 1');
      return {document: replaceTimelineItem(state.document, {...narration, level: command.level}), selection: state.selection, error: null};
    }
    case 'insert-item':
      return insertItem(state, command.item, command.index);
    case 'remove-item':
      return removeItem(state, command.itemId);
    case 'duplicate-item':
      return duplicateItem(state, command.itemId, command.newItemId, command.offsetFrames ?? 0);
    case 'reorder-item':
      return reorderItem(state, command.itemId, command.toIndex);
    default:
      return unchanged(state, 'unsupported editor command');
  }
}

function updateRange(state: EditorState, item: TimelineItem, range: FrameRange): CoreResult {
  if (item.locked) return unchanged(state, `item is locked: ${item.id}`);
  if (!isValidRange(range, state.document.durationFrames)) return unchanged(state, `invalid range for item: ${item.id}`);
  const nextDocument = replaceTimelineItem(state.document, {...item, range} as TimelineItem);
  const semanticError = validateSemanticRanges(nextDocument, item);
  if (semanticError) return unchanged(state, semanticError);
  return {document: nextDocument, selection: state.selection, error: null};
}

function trimNarration(state: EditorState, narration: NarrationTimelineItem, range: FrameRange): CoreResult {
  const validation = validateWordGapTrim({originalRange: narration.range, proposedRange: range, words: narration.words});
  if (!validation.valid) return unchanged(state, validation.errors.join('; '));
  return {document: replaceTimelineItem(state.document, {...narration, range}), selection: state.selection, error: null};
}

function validateSemanticRanges(document: TimelineDocument, changedItem: TimelineItem): string | null {
  if (changedItem.kind === 'scene') {
    const scenes = document.items.filter((item) => item.kind === 'scene');
    const sceneResult = validateSceneContiguity(scenes, document.durationFrames);
    if (!sceneResult.valid) return `scene ranges are not contiguous: ${sceneResult.issues[0].code}`;
    const cues = document.items.filter((item) => item.kind === 'cue');
    const cueResult = validateCueContainment(cues, scenes);
    if (!cueResult.valid) return `cue is outside its scene: ${cueResult.issues[0].code}`;
  }
  if (changedItem.kind === 'cue') {
    const cues = document.items.filter((item) => item.kind === 'cue');
    const scenes = document.items.filter((item) => item.kind === 'scene');
    const cueResult = validateCueContainment(cues, scenes);
    if (!cueResult.valid) return `cue is outside its scene: ${cueResult.issues[0].code}`;
  }
  return null;
}

function commit(state: EditorState, document: TimelineDocument, selection: SelectionState): EditorState {
  return {
    document,
    selection: normalizeSelection(document, selection),
    history: {
      ...state.history,
      past: [...state.history.past, state.document].slice(-state.history.limit),
      future: [],
    },
    lastError: null,
  };
}

function unchanged(state: EditorState, error: string): CoreResult {
  return {document: state.document, selection: state.selection, error};
}

function normalizeSelection(document: TimelineDocument, selection: SelectionState): SelectionState {
  const presentIds = new Set(document.items.map((item) => item.id));
  const selectedItemIds = selection.selectedItemIds.filter((itemId) => presentIds.has(itemId));
  const primaryItemId = selection.primaryItemId && selectedItemIds.includes(selection.primaryItemId) ? selection.primaryItemId : selectedItemIds[0] ?? null;
  const sceneIds = new Set(document.items.flatMap((item) => item.kind === 'scene' ? [item.sceneId] : []));
  return {
    selectedItemIds: [...new Set(selectedItemIds)],
    primaryItemId,
    focusedSceneId: selection.focusedSceneId && sceneIds.has(selection.focusedSceneId) ? selection.focusedSceneId : null,
  };
}

function isValidRange(range: FrameRange, durationFrames: number): boolean {
  return Number.isInteger(range.startFrame) && Number.isInteger(range.endFrame) && range.startFrame >= 0 && range.endFrame > range.startFrame && range.endFrame <= durationFrames;
}

function isFiniteTransform(transform: VisualTransform): boolean {
  if (!transform || typeof transform !== 'object') return false;
  const value = transform as VisualTransform;
  return [value.x, value.y, value.scaleX, value.scaleY, value.rotation, value.opacity, value.zIndex, value.crop?.x, value.crop?.y, value.crop?.width, value.crop?.height].every(Number.isFinite) && value.crop.width > 0 && value.crop.height > 0;
}
