import {cloneTimelineDocument, isTimelineDocument} from './document';
import {createSelection} from './selection';
import {DRAFT_SCHEMA_VERSION, type DraftRecoveryResult, type DraftStorage, type EditorState, type SelectionState, type TimelineDocument, type TimelineDraft} from './types';

export type DraftWriteResult = {ok: true} | {ok: false; error: string};

export function createTimelineDraft(document: TimelineDocument, selection: SelectionState = createSelection()): TimelineDraft {
  return {
    schemaVersion: DRAFT_SCHEMA_VERSION,
    document: cloneTimelineDocument(document),
    selection: normalizeDraftSelection(selection),
  };
}

export function draftFromEditorState(state: EditorState): TimelineDraft {
  return createTimelineDraft(state.document, state.selection);
}

export function serializeDraft(draftOrState: TimelineDraft | EditorState | TimelineDocument): string {
  const draft = isEditorState(draftOrState)
    ? draftFromEditorState(draftOrState)
    : isTimelineDocument(draftOrState)
      ? createTimelineDraft(draftOrState)
      : createTimelineDraft(draftOrState.document, draftOrState.selection);
  return stableStringify(draft);
}

export function deserializeDraft(serialized: string): TimelineDraft {
  if (typeof serialized !== 'string' || serialized.trim().length === 0) throw new Error('draft is empty');
  let value: unknown;
  try {
    value = JSON.parse(serialized) as unknown;
  } catch {
    throw new Error('draft is not valid JSON');
  }
  if (!isTimelineDraft(value)) throw new Error('draft does not match the local draft contract');
  return {
    schemaVersion: DRAFT_SCHEMA_VERSION,
    document: cloneTimelineDocument(value.document),
    selection: normalizeDraftSelection(value.selection),
  };
}

export const serializeLocalDraft = serializeDraft;
export const deserializeLocalDraft = deserializeDraft;

export function saveDraft(storage: DraftStorage, key: string, draftOrState: TimelineDraft | EditorState | TimelineDocument): DraftWriteResult {
  if (!key.trim()) return {ok: false, error: 'draft key is empty'};
  try {
    storage.setItem(key, serializeDraft(draftOrState));
    return {ok: true};
  } catch (error) {
    return {ok: false, error: error instanceof Error ? error.message : String(error)};
  }
}

export const saveDraftToLocalStorage = saveDraft;

export function loadDraft(storage: DraftStorage, key: string): DraftRecoveryResult {
  if (!key.trim()) return {status: 'invalid', draft: null, error: 'draft key is empty'};
  let serialized: string | null;
  try {
    serialized = storage.getItem(key);
  } catch (error) {
    return {status: 'invalid', draft: null, error: error instanceof Error ? error.message : String(error)};
  }
  if (serialized === null) return {status: 'missing', draft: null};
  try {
    return {status: 'recovered', draft: deserializeDraft(serialized)};
  } catch (error) {
    return {status: 'invalid', draft: null, error: error instanceof Error ? error.message : String(error)};
  }
}

export const loadDraftFromLocalStorage = loadDraft;

export function recoverDraft(storage: DraftStorage, key: string, fallback?: TimelineDraft | null): TimelineDraft | null {
  const result = loadDraft(storage, key);
  return result.status === 'recovered' ? result.draft : fallback ?? null;
}

export const recoverLocalDraft = recoverDraft;
export const recoverDraftResult = loadDraft;

export function removeDraft(storage: DraftStorage, key: string): DraftWriteResult {
  try {
    storage.removeItem(key);
    return {ok: true};
  } catch (error) {
    return {ok: false, error: error instanceof Error ? error.message : String(error)};
  }
}

export function createMemoryDraftStorage(initial: Record<string, string> = {}): DraftStorage {
  const values = new Map(Object.entries(initial));
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => void values.set(key, value),
    removeItem: (key) => void values.delete(key),
  };
}

export function isTimelineDraft(value: unknown): value is TimelineDraft {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as {schemaVersion?: unknown; document?: unknown; selection?: unknown};
  return candidate.schemaVersion === DRAFT_SCHEMA_VERSION && isTimelineDocument(candidate.document) && isSelection(candidate.selection);
}

function isEditorState(value: TimelineDraft | EditorState | TimelineDocument): value is EditorState {
  return typeof value === 'object' && value !== null && 'history' in value && 'lastError' in value && 'selection' in value && 'document' in value;
}

function isSelection(value: unknown): value is SelectionState {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as {selectedItemIds?: unknown; primaryItemId?: unknown; focusedSceneId?: unknown};
  return Array.isArray(candidate.selectedItemIds) && candidate.selectedItemIds.every((id) => typeof id === 'string') && (typeof candidate.primaryItemId === 'string' || candidate.primaryItemId === null) && (typeof candidate.focusedSceneId === 'string' || candidate.focusedSceneId === null);
}

function normalizeDraftSelection(selection: SelectionState): SelectionState {
  const selectedItemIds = [...new Set(selection.selectedItemIds)];
  const primaryItemId = selection.primaryItemId && selectedItemIds.includes(selection.primaryItemId) ? selection.primaryItemId : selectedItemIds[0] ?? null;
  return {selectedItemIds, primaryItemId, focusedSceneId: selection.focusedSceneId ?? null};
}

function stableStringify(value: unknown): string {
  return JSON.stringify(sortJson(value));
}

function sortJson(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortJson);
  if (value && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    return Object.fromEntries(Object.keys(record).sort().map((key) => [key, sortJson(record[key])]));
  }
  return value;
}
