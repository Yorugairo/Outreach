import {findTimelineItem} from './document';
import {EMPTY_SELECTION, type FrameRange, type SelectionMode, type SelectionState, type TimelineDocument, type TimelineItem} from './types';

export function createSelection(input: Partial<SelectionState> = {}): SelectionState {
  const selectedItemIds = uniqueIds(input.selectedItemIds ?? []);
  const primaryItemId = input.primaryItemId && selectedItemIds.includes(input.primaryItemId) ? input.primaryItemId : selectedItemIds[0] ?? null;
  return {
    selectedItemIds,
    primaryItemId,
    focusedSceneId: input.focusedSceneId ?? null,
  };
}

export function clearSelection(selection: SelectionState = EMPTY_SELECTION): SelectionState {
  return {selectedItemIds: [], primaryItemId: null, focusedSceneId: selection.focusedSceneId};
}

export function setSelection(selection: SelectionState, itemIds: readonly string[], primaryItemId?: string | null): SelectionState {
  const selectedItemIds = uniqueIds(itemIds);
  const primary = primaryItemId === undefined ? selection.primaryItemId : primaryItemId;
  return {
    selectedItemIds,
    primaryItemId: primary && selectedItemIds.includes(primary) ? primary : selectedItemIds[0] ?? null,
    focusedSceneId: selection.focusedSceneId,
  };
}

export function selectItem(selection: SelectionState, itemId: string, mode: SelectionMode = 'replace'): SelectionState {
  if (!itemId.trim()) return selection;
  if (mode === 'replace') return {...selection, selectedItemIds: [itemId], primaryItemId: itemId};
  if (mode === 'add') {
    if (selection.selectedItemIds.includes(itemId)) return {...selection, primaryItemId: itemId};
    return {...selection, selectedItemIds: [...selection.selectedItemIds, itemId], primaryItemId: itemId};
  }
  if (selection.selectedItemIds.includes(itemId)) {
    const selectedItemIds = selection.selectedItemIds.filter((selectedId) => selectedId !== itemId);
    return {...selection, selectedItemIds, primaryItemId: selection.primaryItemId === itemId ? selectedItemIds[0] ?? null : selection.primaryItemId};
  }
  return {...selection, selectedItemIds: [...selection.selectedItemIds, itemId], primaryItemId: itemId};
}

export function focusScene(selection: SelectionState, sceneId: string | null): SelectionState {
  return {...selection, focusedSceneId: sceneId};
}

export function isSelected(selection: SelectionState, itemId: string): boolean {
  return selection.selectedItemIds.includes(itemId);
}

export function selectedItems(document: TimelineDocument, selection: SelectionState): TimelineItem[] {
  const byId = new Map(document.items.map((item) => [item.id, item]));
  return selection.selectedItemIds.flatMap((itemId) => {
    const item = byId.get(itemId);
    return item ? [item] : [];
  });
}

export function selectionBounds(document: TimelineDocument, selection: SelectionState): FrameRange | null {
  const items = selectedItems(document, selection);
  if (items.length === 0) return null;
  return {
    startFrame: Math.min(...items.map((item) => item.range.startFrame)),
    endFrame: Math.max(...items.map((item) => item.range.endFrame)),
  };
}

export function selectItemsInRange(
  document: TimelineDocument,
  range: FrameRange,
  selection: SelectionState = createSelection(),
  mode: SelectionMode = 'replace',
): SelectionState {
  if (range.endFrame <= range.startFrame) return selection;
  const ids = document.items
    .filter((item) => item.range.startFrame < range.endFrame && item.range.endFrame > range.startFrame)
    .map((item) => item.id);
  if (mode === 'replace') return setSelection(selection, ids, ids[0] ?? null);
  let next = selection;
  for (const id of ids) next = selectItem(next, id, mode);
  return next;
}

export function selectOnlyIfPresent(document: TimelineDocument, selection: SelectionState, itemId: string, mode: SelectionMode = 'replace'): SelectionState {
  return findTimelineItem(document, itemId) ? selectItem(selection, itemId, mode) : selection;
}

function uniqueIds(ids: readonly string[]): string[] {
  return [...new Set(ids.filter((id) => id.trim().length > 0))];
}

