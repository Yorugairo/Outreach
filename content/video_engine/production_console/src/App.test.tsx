import React from 'react';
import '@testing-library/jest-dom/vitest';
import {render, screen, waitFor} from '@testing-library/react';
import {afterEach, describe, expect, it, vi} from 'vitest';
import App from './App';

vi.mock('@remotion/player', () => ({Player: () => <div data-testid="player">player</div>}));

const snapshot = {
  schema_version: 'production_console_snapshot.v1', snapshot_id: 'fixture-v1', project_id: 'fixture', composition_id: 'ProductionEvidence',
  base_artifact_hashes: {flow: 'a'.repeat(64)}, artifact_hash: 'b'.repeat(64), degraded_inputs: [], reviews: [],
  scenes: [{scene_id: 'scene-1', title: 'Valuation paradox', start_s: 0, end_s: 4, cue_refs: ['cue-1'], claim_refs: [], asset_ids: [], review_state: 'unreviewed'}],
  words: [{word_id: 'word-1', text: 'Market', start_s: 0, end_s: .2}],
  assets: [{asset_id: 'visual-1', label: 'Bubble comparison', sha256: 'c'.repeat(64), source_kind: 'production_visual', approval_scope: 'production_visuals', evidence_eligible: false, rights_state: 'operator_authorized', context_status: 'review_only', deck_id: 'deck', slide_number: 1, width: 1376, height: 768, what_it_is: 'A comparison plate.', claim_refs: [], cue_refs: []}],
};

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe('Production Console read-only gate', () => {
  it('shows production approval separately from evidence eligibility', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => Promise.resolve({ok: true, json: () => Promise.resolve(url.includes('snapshot') ? snapshot : {status: 'ready'})})));
    render(<App />);
    await waitFor(() => expect(screen.getByText('Production Console')).toBeInTheDocument());
    expect(screen.getByText('Approved visual')).toBeInTheDocument();
    expect(screen.getByText('Not granted')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Save immutable revision'})).toBeDisabled();
  });

  it('renders an explicit bridge failure state', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('loopback offline'))));
    render(<App />);
    await waitFor(() => expect(screen.getByText('Console unavailable')).toBeInTheDocument());
    expect(screen.getByText('loopback offline')).toBeInTheDocument();
  });
});
