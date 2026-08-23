import React from 'react';
import type {Asset, SemanticEvidenceBinding} from '../../types';

type EvidenceRecommendationPanelProps = {
  binding: SemanticEvidenceBinding | null;
  assets: Asset[];
  accepted: boolean;
  onJump: (frame: number) => void;
  onAccept: (binding: SemanticEvidenceBinding) => void;
};

const scoreRationale = (binding: SemanticEvidenceBinding): string[] => {
  const top = binding.eligible_candidates[0];
  if (!top) return [];
  return Object.entries(top.score_breakdown)
    .filter(([, value]) => value.points !== 0)
    .sort((left, right) => Math.abs(right[1].points) - Math.abs(left[1].points))
    .slice(0, 4)
    .map(([key, value]) => `${key.replaceAll('_', ' ')} ${value.points > 0 ? '+' : ''}${value.points}`);
};

export function EvidenceRecommendationPanel({binding, assets, accepted, onJump, onAccept}: EvidenceRecommendationPanelProps) {
  if (!binding) {
    return (
      <aside className="evidence-recommendation" data-state="idle">
        <div><span className="eyebrow">Semantic evidence</span><strong>No cue recommendation at this frame</strong></div>
        <small>Move the playhead to a reviewed world-plate cue.</small>
      </aside>
    );
  }

  const proposed = binding.proposed_binding;
  const top = binding.eligible_candidates[0];
  const asset = proposed ? assets.find((candidate) => candidate.asset_id === proposed.asset_id) : undefined;
  const rationale = scoreRationale(binding);
  const jumpFrame = proposed?.frame_range.start_frame ?? 0;

  return (
    <aside className="evidence-recommendation" data-state={binding.recommendation_state}>
      <div className="evidence-recommendation__heading">
        <div><span className="eyebrow">Semantic evidence · {binding.cue_id}</span><strong>{asset?.label ?? top?.asset_id ?? 'No safe automatic match'}</strong></div>
        <span className="recommendation-state">{binding.recommendation_state.replace('_', ' ')}</span>
      </div>
      {proposed && top ? (
        <div className="evidence-recommendation__details">
          <span>{top.deck_id}{top.slide_number ? ` · slide ${top.slide_number}` : ''}</span>
          <span>Score {top.total_score} · lead {top.lead_margin}</span>
          <span>Slot {proposed.slot_id}</span>
          {rationale.length ? <span>{rationale.join(' · ')}</span> : null}
        </div>
      ) : <small>{binding.recommendation_reason}</small>}
      <div className="evidence-recommendation__actions">
        <button type="button" onClick={() => onJump(jumpFrame)}>Jump to cue</button>
        {proposed ? <button type="button" className="primary-action" disabled={accepted} onClick={() => onAccept(binding)}>{accepted ? 'Accepted on timeline' : 'Accept evidence'}</button> : null}
      </div>
    </aside>
  );
}
