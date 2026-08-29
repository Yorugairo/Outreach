import React from 'react';
import '@testing-library/jest-dom/vitest';
import {fireEvent, render, screen} from '@testing-library/react';
import {describe, expect, it, vi} from 'vitest';
import type {SemanticEvidenceBinding} from '../../types';
import {EvidenceRecommendationPanel} from './EvidenceRecommendationPanel';

const digest = 'a'.repeat(64);
const unmatched: SemanticEvidenceBinding = {
  schema_version: 'semantic_evidence_binding.v1', binding_id: 'binding-unmatched', cue_id: 'cue-2', claim_refs: [],
  world_plate: {asset_id: 'world', sha256: digest, profile_id: 'profile', profile_status: 'reviewed'},
  eligible_candidates: [], rejected_candidates: [{asset_id: 'asset-rejected', rejection_reasons: ['ambiguous_lead']}],
  recommendation_state: 'unmatched', recommendation_reason: 'The leading candidates were too close to bind safely.', proposed_binding: null, artifact_hash: digest,
};

describe('EvidenceRecommendationPanel', () => {
  it('keeps ambiguous semantic matches read-only and exposes the reason', () => {
    const accept = vi.fn();
    render(<EvidenceRecommendationPanel binding={unmatched} assets={[]} accepted={false} onJump={vi.fn()} onAccept={accept} />);
    expect(screen.getByText('The leading candidates were too close to bind safely.')).toBeInTheDocument();
    expect(screen.queryByText('Accept evidence')).not.toBeInTheDocument();
    fireEvent.click(screen.getByText('Jump to cue'));
    expect(accept).not.toHaveBeenCalled();
  });
});
