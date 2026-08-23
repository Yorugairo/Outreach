import React from 'react';
import '@testing-library/jest-dom/vitest';
import {cleanup, fireEvent, render, screen, waitFor, within} from '@testing-library/react';
import {afterEach, describe, expect, it, vi} from 'vitest';
import App, {staleDraftExportPayload} from './App';
import {snapshotToTimelineDocument} from './features/production-editor/snapshotDocument';
import type {SnapshotV2} from './types';

vi.mock('@remotion/player', () => ({Player: React.forwardRef(function MockPlayer(_props: unknown, _ref: unknown) {return <div data-testid="player">player</div>;})}));

const digest = 'a'.repeat(64);
const tracks = [
  ['track-scenes', 'scenes', false, [{item_id: 'scene-item-1', item_type: 'scene', start_frame: 0, end_frame: 120, locked: false, locked_fields: [], scene_id: 'scene-1'}]],
  ['track-cues', 'cues', false, [{item_id: 'cue-item-1', item_type: 'cue', start_frame: 0, end_frame: 120, locked: false, locked_fields: [], cue_id: 'cue-1', scene_id: 'scene-1'}]],
  ['track-captions', 'captions', true, [{item_id: 'caption-1', item_type: 'caption', start_frame: 0, end_frame: 120, locked: false, locked_fields: ['text', 'word_timing'], text: 'Market', start_word: 0, end_word: 0}]],
  ['track-overlays', 'overlays', true, []],
  ['track-teacher_stamp', 'teacher_stamp', false, []],
  ['track-evidence', 'evidence', true, []],
  ['track-world_plates', 'world_plates', true, [{item_id: 'world-1', item_type: 'world_plate', start_frame: 0, end_frame: 120, locked: true, locked_fields: [], asset_id: 'memory-skepticism-v2'}]],
  ['track-narration', 'narration', false, [{item_id: 'narration-canonical', item_type: 'narration', start_frame: 0, end_frame: 120, locked: true, locked_fields: ['audio_source', 'word_timing'], asset_id: 'canonical-narration', sha256: digest}]],
].map(([track_id, kind, editable, items], order) => ({track_id, kind, label: String(kind), order, editable, items}));

const asset = {asset_id: 'visual-1', label: 'Bubble comparison', sha256: digest, source_kind: 'production_visual', approval_scope: 'production_visuals', evidence_eligible: true, rights_state: 'operator_authorized', context_status: 'operator_verified', deck_id: 'deck', slide_number: 1, width: 1376, height: 768, what_it_is: 'A comparison plate.', claim_refs: [], cue_refs: []};
const worldAsset = {asset_id: 'memory-skepticism-v2', label: 'Memory skepticism world', sha256: digest, source_kind: 'project_asset', approval_scope: 'none', evidence_eligible: false, rights_state: 'operator_authorized', context_status: 'operator_verified', deck_id: null, slide_number: null, width: 1920, height: 1080, what_it_is: 'hero_plate', claim_refs: [], cue_refs: []};
const catalog = {schema_version: 'editor_component_catalog.v1', catalog_id: 'catalog', catalog_version: '1.0.0', remotion_version: '4.0.502', components: [{component_id: 'fade-in', label: 'Fade In', kind: 'remotion_bit', adapter_id: 'fade-in', source: 'remotion_bits', version: '0.2.0', deterministic: true, allowed_prop_keys: ['text'], preset_ids: ['fade-in-default']}], presets: [{preset_id: 'fade-in-default', component_id: 'fade-in', label: 'Fade In default', props: {style_id: 'default'}}], catalog_hash: digest, artifact_hash: digest};
const semanticBinding = {
  schema_version: 'semantic_evidence_binding.v1', binding_id: 'binding-cue-1', cue_id: 'cue-1', claim_refs: [],
  world_plate: {asset_id: 'memory-skepticism-v2', sha256: digest, profile_id: 'memory-skepticism-v2', profile_status: 'reviewed'},
  eligible_candidates: [{asset_id: asset.asset_id, deck_id: 'deck', slide_number: 1, rank: 1, total_score: 31, lead_margin: 8, score_breakdown: {topic_overlap: {points: 12, matched: ['valuation'], details: 'Matched cue concept.'}}}],
  rejected_candidates: [], recommendation_state: 'recommended', recommendation_reason: 'One reviewed candidate cleared the score and lead thresholds.',
  proposed_binding: {asset_id: asset.asset_id, asset_sha256: digest, slot_id: 'teal-callout', slot_rect: {x: .05, y: .7, width: .25, height: .18}, caption_zone: {region_id: 'upper-caption', rect: {x: .1, y: .05, width: .8, height: .14}}, annotation_anchor: {x: .3, y: .7}, source_marker: {placement: 'bottom-right', inset: .02}, frame_range: {start_frame: 0, end_frame: 90}}, artifact_hash: digest,
};
const snapshot = {
  schema_version: 'production_console_snapshot.v2', snapshot_id: 'fixture-v2', project_id: 'fixture', composition_id: 'ProductionTimeline',
  project_profile: {profile_id: 'landscape', fps: 30, width: 1920, height: 1080, duration_s: 4, duration_frames: 120, audio: {audio_id: 'canonical-narration', sha256: digest, duration_s: 4, status: 'available'}, audio_trim: {start_s: 0, end_s: 4, start_frame: 0, end_frame: 120}},
  base_artifact_hashes: {flow: digest}, artifact_hash: digest, degraded_inputs: [], reviews: [],
  scenes: [{scene_id: 'scene-1', title: 'Valuation paradox', start_s: 0, end_s: 4, start_frame: 0, end_frame: 120, cue_refs: ['cue-1'], claim_refs: [], asset_ids: [], review_state: 'unreviewed'}],
  cues: [{cue_id: 'cue-1', start_word: 0, end_word: 0, start_s: 0, end_s: 4, start_frame: 0, end_frame: 120, excerpt: 'Market', state_type: 'hook', visual_world: 'whiteboard'}],
  words: [{word_id: 'word-1', text: 'Market', start_s: 0, end_s: .2, start_frame: 0, end_frame: 6}], tracks,
  assets: [asset, worldAsset], approved_assets: [asset], locks: {narration: true}, waveform: {audio_sha256: digest, cache_key: digest, sample_count: 2, peaks: [.2, .8], status: 'derived'}, component_catalog: catalog, component_catalog_hash: digest,
  plate_layout_profiles: {schema_version: 'plate_layout_profiles.v1', default_profile_id: 'generic-manual-only', profiles: [{profile_id: 'memory-skepticism-v2', world_asset_id: 'memory-skepticism-v2', status: 'reviewed', evidence_slots: [{slot_id: 'teal-callout', order: 1, label: 'Teal lower evidence card', rect: {x: .05, y: .7, width: .25, height: .18}, safe: true}]}], artifact_hash: digest}, semantic_evidence_bindings: [semanticBinding],
};

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
  localStorage.clear();
});

describe('Interactive Production Editor', () => {
  it('preserves hash-bound evidence provenance when hydrating a snapshot', () => {
    const boundSnapshot = structuredClone(snapshot) as unknown as SnapshotV2;
    boundSnapshot.tracks.find((track) => track.kind === 'evidence')!.items.push({
      item_id: 'bound-evidence', item_type: 'evidence', start_frame: 0, end_frame: 90, locked: false, locked_fields: [], asset_id: asset.asset_id, evidence_eligible: true,
      binding: {bindingId: semanticBinding.binding_id, bindingHash: digest, slotId: 'teal-callout', worldAssetId: 'memory-skepticism-v2'},
    });
    const item = snapshotToTimelineDocument(boundSnapshot).items.find((candidate) => candidate.id === 'bound-evidence');
    expect(item?.kind).toBe('evidence');
    expect(item?.kind === 'evidence' ? item.binding : null).toEqual({bindingId: semanticBinding.binding_id, bindingHash: digest, slotId: 'teal-callout', worldAssetId: 'memory-skepticism-v2'});
  });

  it('exports malformed stale drafts without throwing', () => {
    expect(staleDraftExportPayload('{not-json')).toEqual({schema_version: 'production_console_corrupt_draft.v1', status: 'invalid_json', raw: '{not-json'});
    expect(staleDraftExportPayload('{"ok":true}')).toEqual({ok: true});
  });
  it('loads the typed timeline and can add an approved evidence visual', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve({ok: true, json: () => Promise.resolve(url.includes('/api/editor/snapshot') ? snapshot : {status: 'ready'})})));
    render(<App />);
    await waitFor(() => expect(screen.getByText('Interactive Production Editor')).toBeInTheDocument());
    expect(screen.getByText('Episode timeline')).toBeInTheDocument();
    expect(screen.getAllByText('Bubble comparison')).not.toHaveLength(0);
    fireEvent.click(screen.getByRole('button', {name: /Bubble comparison/}));
    await waitFor(() => expect(screen.getByText('evidence', {selector: '.inspector-identity span'})).toBeInTheDocument());
    expect(screen.getByLabelText('X')).toHaveValue(-0.325);
    expect(screen.getByLabelText('Crop width')).toHaveValue(0.25);
    expect(screen.getByRole('button', {name: 'Save immutable revision'})).toBeEnabled();
  });

  it('exposes mapped world plates separately from factual evidence', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve({ok: true, json: () => Promise.resolve(url.includes('/api/editor/snapshot') ? snapshot : {status: 'ready'})})));
    render(<App />);
    await waitFor(() => expect(screen.getByText('Interactive Production Editor')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', {name: 'World plates'}));
    fireEvent.click(within(screen.getByLabelText('Asset and component palette')).getByRole('button', {name: /Memory skepticism world/}));
    await waitFor(() => expect(screen.getByText('world plate', {selector: '.inspector-identity span'})).toBeInTheDocument());
  });

  it('shows a recommendation without inserting it until the operator accepts', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve({ok: true, json: () => Promise.resolve(url.includes('/api/editor/snapshot') ? snapshot : {status: 'ready'})})));
    render(<App />);
    await waitFor(() => expect(screen.getByText('Accept evidence')).toBeInTheDocument());
    expect(screen.queryByText('Accepted on timeline')).not.toBeInTheDocument();
    fireEvent.click(screen.getByText('Accept evidence'));
    await waitFor(() => expect(screen.getByText('Accepted on timeline')).toBeDisabled());
    expect(screen.getByLabelText('X')).toHaveValue(-0.325);
    expect(screen.getByLabelText('Crop width')).toHaveValue(0.25);
  });

  it('renders an explicit bridge failure state', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('loopback offline'))));
    render(<App />);
    await waitFor(() => expect(screen.getByText('Editor unavailable')).toBeInTheDocument());
    expect(screen.getByText('loopback offline')).toBeInTheDocument();
  });
});
