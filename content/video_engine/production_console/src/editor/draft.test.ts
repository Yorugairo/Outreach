import {describe, expect, it} from 'vitest';
import {createEditorState, createMemoryDraftStorage, createTimelineDocument, deserializeDraft, isTimelineDraft, loadDraft, recoverDraft, saveDraft, serializeDraft} from './index';

const document = createTimelineDocument({
  documentId: 'draft-document', projectId: 'project', snapshotId: 'snapshot', baseSnapshotHash: 'a'.repeat(64), compositionId: 'ProductionTimeline',
  fps: 30, width: 1280, height: 720, durationFrames: 30, items: [],
});

describe('local draft serialization and recovery', () => {
  it('serializes deterministically and round-trips a selection', () => {
    let state = createEditorState(document);
    state = {...state, selection: {selectedItemIds: [], primaryItemId: null, focusedSceneId: null}};
    const serialized = serializeDraft(state);
    expect(serialized).toBe(serializeDraft(state));
    expect(Object.keys(JSON.parse(serialized) as object)).toEqual(['document', 'schemaVersion', 'selection']);
    const draft = deserializeDraft(serialized);
    expect(isTimelineDraft(draft)).toBe(true);
    expect(draft.document).toEqual(document);
  });

  it('recovers valid drafts, reports malformed drafts, and supports a fallback', () => {
    const storage = createMemoryDraftStorage();
    expect(saveDraft(storage, 'editor:draft', document)).toEqual({ok: true});
    expect(loadDraft(storage, 'editor:draft').status).toBe('recovered');
    storage.setItem('broken', '{not json');
    expect(loadDraft(storage, 'broken')).toMatchObject({status: 'invalid'});
    expect(loadDraft(storage, 'missing')).toEqual({status: 'missing', draft: null});
    expect(recoverDraft(storage, 'missing', deserializeDraft(serializeDraft(document)))).toEqual(deserializeDraft(serializeDraft(document)));
  });
});

