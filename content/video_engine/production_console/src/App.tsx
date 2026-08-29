import React, {useCallback, useEffect, useMemo, useReducer, useRef, useState} from 'react';
import {Player, type PlayerRef} from '@remotion/player';
import {ProductionTimelineComposition} from '../../editor/src/ProductionTimelineComposition';
import {saveEditorialRevision, validateEditorialRevision} from './api';
import {
  buildSnapPoints,
  canRedo,
  canUndo,
  createEditorState,
  editorReducer,
  findTimelineItem,
  isTransformableItem,
  loadDraft,
  saveDraft,
  setKeyframe,
  snapRange,
  type AnimatableProperty,
  type EditorCommand,
  type FrameRange,
  type TimelineItem,
  type TimelineDocument,
  type TransformableTimelineItem,
  type VisualTransform,
} from './editor';
import {ComponentPalette} from './features/production-editor/ComponentPalette';
import {EditorCanvasOverlay} from './features/production-editor/EditorCanvasOverlay';
import {EditorInspector} from './features/production-editor/EditorInspector';
import {EditorTimeline} from './features/production-editor/EditorTimeline';
import {EvidenceRecommendationPanel} from './features/production-editor/EvidenceRecommendationPanel';
import {buildEditorialRevision, downloadJson} from './features/production-editor/revision';
import {snapshotToTimelineDocument, timelineDocumentToComposition} from './features/production-editor/snapshotDocument';
import type {PlateLayoutProfile, SemanticEvidenceBinding, SnapshotV2} from './types';
import {useConsoleData} from './useConsoleData';

const shortHash = (value: string) => `${value.slice(0, 8)}…${value.slice(-6)}`;
const itemId = (prefix: string) => `${prefix}-${crypto.randomUUID()}`;
const DRAFT_PREFIX = 'outreach-production-editor';

export const staleDraftExportPayload = (raw: string): unknown => {
  try {
    return JSON.parse(raw) as unknown;
  } catch {
    return {schema_version: 'production_console_corrupt_draft.v1', status: 'invalid_json', raw};
  }
};

export type EvidenceSlot = {x: number; y: number; width: number; height: number; name: string};

const fallbackEvidenceSlot: EvidenceSlot = {x: .29, y: -.21, width: .3, height: .23, name: 'off-center field note'};

const slotFromProfile = (profile: PlateLayoutProfile, index: number): EvidenceSlot | null => {
  const slots = [...profile.evidence_slots].filter((slot) => slot.safe).sort((left, right) => left.order - right.order);
  const selected = slots[index % Math.max(1, slots.length)];
  if (!selected) return null;
  const {rect} = selected;
  return {
    x: rect.x + rect.width / 2 - .5,
    y: rect.y + rect.height / 2 - .5,
    width: rect.width,
    height: rect.height,
    name: selected.label,
  };
};

export const evidenceSlotForDocument = (document: TimelineDocument, frame: number, profileCollection?: SnapshotV2['plate_layout_profiles']): EvidenceSlot => {
  const world = document.items.find((item) => item.kind === 'world_plate' && item.range.startFrame <= frame && frame < item.range.endFrame);
  if (!profileCollection) return fallbackEvidenceSlot;
  const profile = profileCollection.profiles.find((candidate) => candidate.world_asset_id && world?.kind === 'world_plate' && candidate.world_asset_id === world.assetId)
    ?? profileCollection.profiles.find((candidate) => candidate.profile_id === profileCollection.default_profile_id);
  if (!profile) return fallbackEvidenceSlot;
  const used = document.items.filter((item) => item.kind === 'evidence' && item.range.endFrame <= frame).length;
  return slotFromProfile(profile, used) ?? fallbackEvidenceSlot;
};

const isTyping = (target: EventTarget | null) => target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement;

function EditorConsole({snapshot, bridgeStatus}: {snapshot: SnapshotV2; bridgeStatus: string}) {
  const baseDocument = useMemo(() => snapshotToTimelineDocument(snapshot), [snapshot]);
  const draftKey = `${DRAFT_PREFIX}:${snapshot.project_id}:${snapshot.artifact_hash}`;
  const latestKey = `${DRAFT_PREFIX}:${snapshot.project_id}:latest`;
  const recovery = useMemo(() => {
    const loaded = loadDraft(localStorage, draftKey);
    const previousKey = localStorage.getItem(latestKey);
    const stale = previousKey && previousKey !== draftKey ? localStorage.getItem(previousKey) : null;
    return {loaded, stale};
  }, [draftKey, latestKey]);
  const [state, dispatch] = useReducer(editorReducer, undefined, () => recovery.loaded.status === 'recovered' ? createEditorState(recovery.loaded.draft.document, recovery.loaded.draft.selection) : createEditorState(baseDocument));
  const [zoom, setZoom] = useState(1);
  const [uiFrame, setUiFrame] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [revisionNote, setRevisionNote] = useState('Current-bubble editorial proof');
  const [saveState, setSaveState] = useState<'idle' | 'validating' | 'saved' | 'error'>('idle');
  const [saveMessage, setSaveMessage] = useState('Unsaved local draft');
  const playerRef = useRef<PlayerRef>(null);
  const playheadFrame = useRef(0);
  const frameRaf = useRef<number | null>(null);

  const compositionProps = useMemo(() => timelineDocumentToComposition(state.document, snapshot), [snapshot, state.document]);
  const selectedItem = useMemo(() => state.selection.primaryItemId ? findTimelineItem(state.document, state.selection.primaryItemId) ?? null : null, [state.document, state.selection.primaryItemId]);
  const currentScene = useMemo(() => state.document.items.find((item) => item.kind === 'scene' && item.range.startFrame <= uiFrame && uiFrame < item.range.endFrame) ?? state.document.items.find((item) => item.kind === 'scene'), [state.document.items, uiFrame]);
  const currentCueId = useMemo(() => snapshot.cues.find((cue) => cue.start_frame <= uiFrame && uiFrame < cue.end_frame)?.cue_id ?? null, [snapshot.cues, uiFrame]);
  const semanticBindings = snapshot.semantic_evidence_bindings ?? [];
  const activeBinding = useMemo(() => semanticBindings.find((binding) => binding.cue_id === currentCueId)
    ?? semanticBindings.find((binding) => binding.recommendation_state === 'recommended')
    ?? null, [currentCueId, semanticBindings]);
  const acceptedBindingIds = useMemo(() => new Set(state.document.items.flatMap((item) => item.kind === 'evidence' && item.binding ? [item.binding.bindingId] : [])), [state.document.items]);

  useEffect(() => {
    saveDraft(localStorage, draftKey, state);
    localStorage.setItem(latestKey, draftKey);
  }, [draftKey, latestKey, state]);

  useEffect(() => {
    const player = playerRef.current;
    if (!player) return;
    const onFrame = ({detail}: {detail: {frame: number}}) => {
      playheadFrame.current = detail.frame;
      if (frameRaf.current === null) frameRaf.current = requestAnimationFrame(() => {
        const marker = document.querySelector<HTMLElement>('[data-editor-playhead]');
        if (marker) marker.style.left = `${142 + playheadFrame.current * Number(marker.dataset.pixelsPerFrame ?? 0)}px`;
        frameRaf.current = null;
      });
    };
    const onSeek = ({detail}: {detail: {frame: number}}) => setUiFrame(detail.frame);
    const onPlay = () => setPlaying(true);
    const onPause = () => {
      setPlaying(false);
      setUiFrame(playheadFrame.current);
    };
    player.addEventListener('frameupdate', onFrame);
    player.addEventListener('seeked', onSeek);
    player.addEventListener('play', onPlay);
    player.addEventListener('pause', onPause);
    return () => {
      player.removeEventListener('frameupdate', onFrame);
      player.removeEventListener('seeked', onSeek);
      player.removeEventListener('play', onPlay);
      player.removeEventListener('pause', onPause);
      if (frameRaf.current !== null) cancelAnimationFrame(frameRaf.current);
    };
  }, []);

  const seek = useCallback((frame: number) => {
    const next = Math.max(0, Math.min(state.document.durationFrames - 1, Math.round(frame)));
    playheadFrame.current = next;
    setUiFrame(next);
    playerRef.current?.seekTo(next);
  }, [state.document.durationFrames]);

  const select = useCallback((selectedId: string, additive: boolean) => dispatch({type: 'select', itemId: selectedId, mode: additive ? 'toggle' : 'replace'}), []);

  const commitRange = useCallback((selectedId: string, range: FrameRange, disableSnap: boolean) => {
    const item = findTimelineItem(state.document, selectedId);
    if (!item) return;
    const next = disableSnap ? range : snapRange(range, buildSnapPoints(state.document, {excludeItemIds: [selectedId]}), {thresholdFrames: Math.max(1, Math.round(state.document.fps / 6)), excludeItemId: selectedId, minFrame: 0, maxFrame: state.document.durationFrames}).range;
    if (item.kind === 'scene') {
      if (next.startFrame !== item.range.startFrame) dispatch({type: 'set-scene-boundary', sceneId: item.sceneId, boundaryFrame: next.startFrame, side: 'start'});
      else if (next.endFrame !== item.range.endFrame) dispatch({type: 'set-scene-boundary', sceneId: item.sceneId, boundaryFrame: next.endFrame, side: 'end'});
      return;
    }
    dispatch(item.kind === 'narration' ? {type: 'trim-narration', itemId: item.id, range: next} : {type: 'set-item-range', itemId: selectedId, range: next});
  }, [state.document]);

  const updateTransform = useCallback((selectedId: string, transform: Omit<Partial<VisualTransform>, 'crop'> & {crop?: Partial<VisualTransform['crop']>}) => dispatch({type: 'update-item', itemId: selectedId, patch: {transform}}), []);
  const duration = Math.max(snapshot.project_profile.fps * 4, Math.round(snapshot.project_profile.fps * 7));
  const insertionRange = useCallback(() => ({startFrame: uiFrame, endFrame: Math.min(state.document.durationFrames, uiFrame + duration)}), [duration, state.document.durationFrames, uiFrame]);
  const trackId = useCallback((kind: string) => state.document.tracks.find((track) => track.kind === kind)?.id ?? `track-${kind}`, [state.document.tracks]);
  const insert = useCallback((item: TimelineItem) => dispatch({type: 'batch', commands: [{type: 'insert-item', item}, {type: 'select', itemId: item.id}]}), []);

  const addAsset = useCallback((assetId: string) => {
    const asset = snapshot.approved_assets.find((candidate) => candidate.asset_id === assetId);
    if (!asset) return;
    const range = insertionRange();
    const slot = evidenceSlotForDocument(state.document, range.startFrame, snapshot.plate_layout_profiles);
    const evidence = {id: itemId('evidence'), kind: 'evidence' as const, trackId: trackId('evidence'), range, label: `${asset.label} · ${slot.name}`, locked: false, assetId, claimRefs: asset.claim_refs, evidenceEligible: asset.evidence_eligible, transform: {x: slot.x, y: slot.y, scaleX: 1, scaleY: 1, rotation: 0, opacity: 1, zIndex: 40, crop: {x: 0, y: 0, width: slot.width, height: slot.height}}, keyframes: {}};
    const commands: EditorCommand[] = state.document.items
      .filter((item) => item.kind === 'evidence' && !item.locked && item.range.startFrame <= range.startFrame && range.startFrame < item.range.endFrame)
      .map((item) => item.range.startFrame < range.startFrame
        ? ({type: 'set-item-range' as const, itemId: item.id, range: {...item.range, endFrame: range.startFrame}})
        : ({type: 'remove-item' as const, itemId: item.id}));
    const activeWorld = state.document.items.find((item) => item.kind === 'world_plate' && item.range.startFrame <= range.startFrame && range.startFrame < item.range.endFrame);
    const activeProfile = activeWorld?.kind === 'world_plate'
      ? snapshot.plate_layout_profiles.profiles.find((profile) => profile.world_asset_id === activeWorld.assetId)
      : null;
    if (activeProfile?.profile_id === 'memory-skepticism-v2') {
      for (const item of state.document.items) {
        const overlapsTime = item.range.startFrame < range.endFrame && range.startFrame < item.range.endFrame;
        if (!overlapsTime || item.locked) continue;
        if (item.kind === 'overlay' && item.transform.y >= .2) {
          if (item.range.startFrame < range.startFrame) commands.push({type: 'set-item-range', itemId: item.id, range: {...item.range, endFrame: range.startFrame}});
          else commands.push({type: 'remove-item', itemId: item.id});
        }
        if (item.kind === 'caption' && item.range.startFrame <= range.startFrame && range.startFrame < item.range.endFrame) {
          commands.push({type: 'update-item', itemId: item.id, patch: {transform: {x: -.3, y: -.37, crop: {width: .36, height: .18}, zIndex: 72}}});
        }
      }
    }
    dispatch({type: 'batch', commands: [...commands, {type: 'insert-item', item: evidence}, {type: 'select', itemId: evidence.id}]});
  }, [insertionRange, snapshot.approved_assets, snapshot.plate_layout_profiles, state.document, trackId]);

  const worldAssets = useMemo(() => snapshot.assets.filter((asset) => asset.source_kind === 'project_asset' && ([...['hero_plate', 'generated_hero', 'world_board', 'mechanism'], 'sentence_native_plate']).some((kind) => (asset.what_it_is ?? '').includes(kind))), [snapshot.assets]);
  const addWorldPlate = useCallback((assetId: string) => {
    const asset = worldAssets.find((candidate) => candidate.asset_id === assetId);
    if (!asset) return;
    const range = insertionRange();
    insert({id: itemId('world'), kind: 'world_plate', trackId: trackId('world_plates'), range, label: asset.label, locked: false, assetId, fit: 'cover', transform: {x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0, opacity: 1, zIndex: 0, crop: {x: 0, y: 0, width: 1, height: 1}}, keyframes: {}});
  }, [insertionRange, insert, trackId, worldAssets]);

  const acceptEvidenceBinding = useCallback((binding: SemanticEvidenceBinding) => {
    const proposed = binding.proposed_binding;
    if (!proposed || binding.recommendation_state !== 'recommended' || acceptedBindingIds.has(binding.binding_id)) return;
    const asset = snapshot.approved_assets.find((candidate) => candidate.asset_id === proposed.asset_id);
    if (!asset || !asset.evidence_eligible) return;
    const range = {startFrame: proposed.frame_range.start_frame, endFrame: proposed.frame_range.end_frame};
    const rect = proposed.slot_rect;
    const evidence = {
      id: itemId('evidence'), kind: 'evidence' as const, trackId: trackId('evidence'), range,
      label: `${asset.label} · ${proposed.slot_id}`, locked: false, assetId: asset.asset_id,
      claimRefs: asset.claim_refs, evidenceEligible: asset.evidence_eligible,
      binding: {bindingId: binding.binding_id, bindingHash: binding.artifact_hash, slotId: proposed.slot_id, worldAssetId: binding.world_plate.asset_id},
      transform: {x: rect.x + rect.width / 2 - .5, y: rect.y + rect.height / 2 - .5, scaleX: 1, scaleY: 1, rotation: 0, opacity: 1, zIndex: 40, crop: {x: 0, y: 0, width: rect.width, height: rect.height}}, keyframes: {},
    };
    const commands: EditorCommand[] = state.document.items
      .filter((item) => item.kind === 'evidence' && !item.locked && item.range.startFrame < range.endFrame && range.startFrame < item.range.endFrame)
      .map((item) => item.range.startFrame < range.startFrame
        ? ({type: 'set-item-range' as const, itemId: item.id, range: {...item.range, endFrame: range.startFrame}})
        : ({type: 'remove-item' as const, itemId: item.id}));
    dispatch({type: 'batch', commands: [...commands, {type: 'insert-item', item: evidence}, {type: 'select', itemId: evidence.id}]});
    seek(range.startFrame);
  }, [acceptedBindingIds, seek, snapshot.approved_assets, state.document.items, trackId]);

  const addText = useCallback(() => insert({id: itemId('text'), kind: 'overlay', overlayKind: 'text', trackId: trackId('overlays'), range: insertionRange(), label: 'New overlay text', text: 'Edit this on-screen text', locked: false, transform: {x: 0, y: -.3, scaleX: 1, scaleY: 1, rotation: 0, opacity: 1, zIndex: 60, crop: {x: 0, y: 0, width: .7, height: .2}}, keyframes: {}}), [insertionRange, insert, trackId]);
  const addAnnotation = useCallback((kind: 'arrow' | 'shape') => {
    const range = insertionRange();
    const activeEvidence = state.document.items.find((item) => item.kind === 'evidence' && item.range.startFrame <= range.startFrame && range.startFrame < item.range.endFrame);
    const evidenceX = activeEvidence?.kind === 'evidence' ? activeEvidence.transform.x : -.24;
    const evidenceY = activeEvidence?.kind === 'evidence' ? activeEvidence.transform.y : .28;
    insert({id: itemId(kind), kind: 'overlay', overlayKind: kind, trackId: trackId('overlays'), range, label: kind === 'arrow' ? 'Evidence leader line' : 'Evidence frame', text: '', locked: false, transform: {x: evidenceX + (evidenceX <= 0 ? .2 : -.2), y: evidenceY - .18, scaleX: 1, scaleY: 1, rotation: evidenceX <= 0 ? 0 : -90, opacity: 1, zIndex: 65, crop: {x: 0, y: 0, width: .18, height: .14}}, keyframes: {}});
  }, [insertionRange, insert, state.document.items, trackId]);
  const addTeacherStamp = useCallback(() => insert({id: itemId('teacher-stamp'), kind: 'teacher_stamp', trackId: trackId('teacher_stamp'), range: insertionRange(), label: 'Teacher stamp', locked: false, assetId: 'teacher-stamp-center-gaze-v4', transform: {x: .36, y: .34, scaleX: .72, scaleY: .87, rotation: 0, opacity: 1, zIndex: 80, crop: {x: 0, y: 0, width: .24, height: .27}}, keyframes: {}}), [insertionRange, insert, trackId]);
  const addBit = useCallback((componentId: string) => insert({id: itemId('bit'), kind: 'remotion_bit', trackId: trackId('overlays'), range: insertionRange(), label: snapshot.component_catalog.components.find((component) => component.component_id === componentId)?.label ?? componentId, locked: false, componentId, presetId: `${componentId}-default`, props: componentId.includes('counter') ? {from: 0, to: 41.18, postfix: '×'} : {text: 'The valuation paradox'}, transform: {x: 0, y: 0, scaleX: 1, scaleY: 1, rotation: 0, opacity: 1, zIndex: 70, crop: {x: 0, y: 0, width: .7, height: .32}}, keyframes: {}} as TimelineItem), [insertionRange, insert, snapshot.component_catalog.components, trackId]);

  const duplicate = useCallback((selectedId: string) => dispatch({type: 'duplicate-item', itemId: selectedId, newItemId: itemId('copy'), offsetFrames: Math.round(state.document.fps / 3)}), [state.document.fps]);
  const remove = useCallback((selectedId: string) => dispatch({type: 'remove-item', itemId: selectedId}), []);
  const addKeyframe = useCallback((selectedId: string, property: AnimatableProperty) => {
    const item = findTimelineItem(state.document, selectedId);
    if (!item || !isTransformableItem(item)) return;
    const value = item.transform[property];
    if (typeof value !== 'number') return;
    dispatch({type: 'set-keyframes', itemId: selectedId, property, keyframes: setKeyframe(item.keyframes[property] ?? [], {frame: uiFrame, value, easing: 'ease_in_out'})});
  }, [state.document, uiFrame]);

  const alignSelection = useCallback((axis: 'x' | 'y') => {
    const items = state.selection.selectedItemIds.map((id) => findTimelineItem(state.document, id)).filter((item): item is TransformableTimelineItem => Boolean(item && isTransformableItem(item)));
    if (items.length < 2) return;
    const value = items.reduce((sum, item) => sum + item.transform[axis], 0) / items.length;
    dispatch({type: 'batch', commands: items.map((item) => ({type: 'update-item' as const, itemId: item.id, patch: {transform: {[axis]: value}}}))});
  }, [state.document, state.selection.selectedItemIds]);

  const distributeSelection = useCallback((axis: 'x' | 'y') => {
    const items = state.selection.selectedItemIds.map((id) => findTimelineItem(state.document, id)).filter((item): item is TransformableTimelineItem => Boolean(item && isTransformableItem(item))).sort((left, right) => left.transform[axis] - right.transform[axis]);
    if (items.length < 3) return;
    const start = items[0].transform[axis];
    const step = (items[items.length - 1].transform[axis] - start) / (items.length - 1);
    dispatch({type: 'batch', commands: items.slice(1, -1).map((item, index) => ({type: 'update-item' as const, itemId: item.id, patch: {transform: {[axis]: start + step * (index + 1)}}}))});
  }, [state.document, state.selection.selectedItemIds]);

  const requestIntake = useCallback(() => downloadJson(`remotion-bit-intake-${Date.now()}.json`, {schema_version: 'editor_component_intake_request.v1', project_id: snapshot.project_id, base_snapshot_hash: snapshot.artifact_hash, catalog_hash: snapshot.component_catalog_hash, requested_at: new Date().toISOString(), status: 'review_required', package: 'remotion-bits', pinned_version: '0.2.0'}), [snapshot]);

  const saveRevision = useCallback(async () => {
    setSaveState('validating');
    setSaveMessage('Validating immutable revision…');
    try {
      const revision = await buildEditorialRevision({snapshot, base: baseDocument, draft: state.document, note: revisionNote, operatorId: 'local-operator'});
      const validation = await validateEditorialRevision(revision);
      if (!validation.valid) throw new Error(validation.errors?.[0]?.message ?? 'Revision validation failed.');
      const saved = await saveEditorialRevision(revision);
      setSaveState('saved');
      setSaveMessage(`Saved ${String(saved.revision_id ?? revision.revision_id)}`);
    } catch (error) {
      setSaveState('error');
      setSaveMessage(error instanceof Error ? error.message : String(error));
    }
  }, [baseDocument, revisionNote, snapshot, state.document]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (isTyping(event.target)) return;
      const modifier = event.ctrlKey || event.metaKey;
      if (modifier && event.key.toLowerCase() === 'z') {event.preventDefault(); dispatch({type: event.shiftKey ? 'redo' : 'undo'}); return;}
      if (modifier && event.key.toLowerCase() === 'y') {event.preventDefault(); dispatch({type: 'redo'}); return;}
      if (modifier && event.key.toLowerCase() === 'd' && selectedItem && !selectedItem.locked) {event.preventDefault(); duplicate(selectedItem.id); return;}
      if (event.key === 'Escape') {event.preventDefault(); dispatch({type: 'clear-selection'}); return;}
      if ((event.key === 'Delete' || event.key === 'Backspace') && selectedItem && !selectedItem.locked) {event.preventDefault(); remove(selectedItem.id); return;}
      if (event.key === ' ') {event.preventDefault(); playerRef.current?.toggle(); return;}
      if (selectedItem && isTransformableItem(selectedItem) && ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
        event.preventDefault();
        const step = (event.shiftKey ? 10 : 1) / state.document.width;
        updateTransform(selectedItem.id, {x: selectedItem.transform.x + (event.key === 'ArrowLeft' ? -step : event.key === 'ArrowRight' ? step : 0), y: selectedItem.transform.y + (event.key === 'ArrowUp' ? -step : event.key === 'ArrowDown' ? step : 0)});
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [duplicate, remove, selectedItem, state.document.width, updateTransform]);

  return (
    <main className="console-shell editor-shell">
      <header className="topbar">
        <div><span className="eyebrow">Outreach video engine</span><h1>Interactive Production Editor</h1></div>
        <div className="topbar__status"><span className="status-dot" /> {bridgeStatus}<span className="hash">{shortHash(snapshot.artifact_hash)}</span><span className="gate-chip">P31 · Explicit evidence acceptance</span></div>
      </header>
      {recovery.stale ? <div className="stale-draft"><b>Stale draft quarantined.</b><span>Its base snapshot changed, so it was not loaded.</span><button onClick={() => downloadJson('stale-production-editor-draft.json', staleDraftExportPayload(recovery.stale!))}>Export JSON</button></div> : null}
      <section className="editor-toolbar">
        <button type="button" onClick={() => playerRef.current?.toggle()}>{playing ? '❚❚ Pause' : '▶ Play'}</button>
        <button type="button" disabled={!canUndo(state)} onClick={() => dispatch({type: 'undo'})}>↶ Undo</button><button type="button" disabled={!canRedo(state)} onClick={() => dispatch({type: 'redo'})}>↷ Redo</button>
        <span className="toolbar-divider" /><button type="button" onClick={() => alignSelection('x')}>Align center X</button><button type="button" onClick={() => alignSelection('y')}>Align center Y</button><button type="button" onClick={() => distributeSelection('x')}>Distribute X</button><button type="button" onClick={() => distributeSelection('y')}>Distribute Y</button>
        <span className="toolbar-spacer" /><span className="frame-readout">{uiFrame.toLocaleString()}f · {(uiFrame / state.document.fps).toFixed(2)}s</span>
      </section>
      <section className="editor-workspace">
        <ComponentPalette assets={snapshot.approved_assets} worldAssets={worldAssets} catalog={snapshot.component_catalog} onAddAsset={addAsset} onAddWorldPlate={addWorldPlate} onAddText={addText} onAddAnnotation={addAnnotation} onAddTeacherStamp={addTeacherStamp} onAddBit={addBit} onRequestIntake={requestIntake} />
        <section className="editor-stage-column">
          <div className="preview-heading"><div><span className="eyebrow">{currentScene?.kind === 'scene' ? currentScene.sceneId : 'episode'}</span><h2>{currentScene?.label ?? snapshot.project_id}</h2></div><span className="timecode">{snapshot.project_profile.width}×{snapshot.project_profile.height} · {state.document.fps} fps</span></div>
          <EvidenceRecommendationPanel binding={activeBinding} assets={snapshot.approved_assets} accepted={Boolean(activeBinding && acceptedBindingIds.has(activeBinding.binding_id))} onJump={seek} onAccept={acceptEvidenceBinding} />
          <div className="player-frame editor-player-frame">
            <Player ref={playerRef} component={ProductionTimelineComposition} inputProps={compositionProps} durationInFrames={state.document.durationFrames} fps={state.document.fps} compositionWidth={state.document.width} compositionHeight={state.document.height} controls={false} style={{width: '100%', aspectRatio: `${state.document.width} / ${state.document.height}`}} />
            <EditorCanvasOverlay document={state.document} currentFrame={uiFrame} selectedIds={state.selection.selectedItemIds} onSelect={select} onTransform={updateTransform} />
          </div>
          <div className="scene-jump-strip">{state.document.items.filter((item) => item.kind === 'scene').map((scene, index) => <button key={scene.id} data-active={scene.id === currentScene?.id} onClick={() => {dispatch({type: 'focus-scene', sceneId: scene.kind === 'scene' ? scene.sceneId : null}); seek(scene.range.startFrame);}}>{String(index + 1).padStart(2, '0')} {scene.label}</button>)}</div>
        </section>
        <EditorInspector item={selectedItem} currentFrame={uiFrame} onTransform={updateTransform} onText={(id, text) => dispatch({type: 'update-item', itemId: id, patch: {text}})} onItemPatch={(id, patch) => dispatch({type: 'update-item', itemId: id, patch})} onNarration={(id, range, level) => dispatch({type: 'batch', commands: [{type: 'trim-narration', itemId: id, range}, {type: 'set-narration-level', itemId: id, level}]})} onAddKeyframe={addKeyframe} onDuplicate={duplicate} onDelete={remove} />
      </section>
      {state.lastError ? <div className="editor-error"><b>Edit rejected</b>{state.lastError}</div> : null}
      <EditorTimeline document={state.document} currentFrame={uiFrame} selectedIds={state.selection.selectedItemIds} zoom={zoom} waveformPeaks={snapshot.waveform.peaks} onZoom={setZoom} onSeek={seek} onSelect={select} onCommitRange={commitRange} />
      <section className="revision-bar panel">
        <div><span className="eyebrow">Immutable revision</span><strong>{saveMessage}</strong><small>Source audio, transcript, evidence status, approvals, hashes, and prior revisions are protected.</small></div>
        <input aria-label="Revision note" value={revisionNote} onChange={(event) => setRevisionNote(event.currentTarget.value)} />
        <button type="button" data-state={saveState} disabled={saveState === 'validating'} onClick={saveRevision}>Save immutable revision</button>
      </section>
      {snapshot.degraded_inputs.length ? <footer className="degraded"><b>Degraded input</b>{snapshot.degraded_inputs.join(' · ')}</footer> : null}
    </main>
  );
}

export default function App() {
  const {snapshot, health, error, loading} = useConsoleData();
  if (loading) return <div className="state-page"><span className="loader" /><h1>Compiling production context</h1><p>Loading the frame-addressable snapshot and component catalog.</p></div>;
  if (error) return <div className="state-page state-page--error"><h1>Editor unavailable</h1><p>{error}</p><code>Verify the P31 loopback bridge is running on 127.0.0.1.</code></div>;
  if (!snapshot) return <div className="state-page"><h1>Snapshot empty</h1><p>No production editor snapshot was returned.</p></div>;
  return <EditorConsole snapshot={snapshot} bridgeStatus={health?.status ?? 'bridge unknown'} />;
}
