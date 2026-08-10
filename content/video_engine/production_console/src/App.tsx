import React, {useMemo, useReducer} from 'react';
import {Player} from '@remotion/player';
import {mediaUrl} from './api';
import {ProductionEvidenceComposition} from '../../editor/src/ProductionEvidenceComposition';
import type {Asset, ConsoleState, Scene, Snapshot} from './types';
import {useConsoleData} from './useConsoleData';
import {VirtualAssetList} from './VirtualAssetList';

type Action =
  | {type: 'scene'; id: string; assetId: string}
  | {type: 'asset'; id: string}
  | {type: 'query'; value: string};

const reducer = (state: ConsoleState, action: Action): ConsoleState => {
  if (action.type === 'scene') return {...state, selectedSceneId: action.id, selectedAssetId: action.assetId};
  if (action.type === 'asset') return {...state, selectedAssetId: action.id};
  return {...state, assetQuery: action.value};
};

const shortHash = (value: string) => `${value.slice(0, 8)}…${value.slice(-6)}`;

function Console({snapshot, bridgeStatus}: {snapshot: Snapshot; bridgeStatus: string}) {
  const productionAssets = useMemo(() => snapshot.assets.filter((asset) => asset.source_kind === 'production_visual'), [snapshot.assets]);
  const [state, dispatch] = useReducer(reducer, {
    selectedSceneId: snapshot.scenes[0]?.scene_id ?? '',
    selectedAssetId: productionAssets[0]?.asset_id ?? '',
    assetQuery: '',
  });
  const selectedScene = useMemo(() => snapshot.scenes.find((scene) => scene.scene_id === state.selectedSceneId) ?? snapshot.scenes[0], [snapshot.scenes, state.selectedSceneId]);
  const selectedAsset = useMemo(() => productionAssets.find((asset) => asset.asset_id === state.selectedAssetId) ?? productionAssets[0], [productionAssets, state.selectedAssetId]);
  const filteredAssets = useMemo(() => {
    const query = state.assetQuery.trim().toLowerCase();
    return query ? productionAssets.filter((asset) => `${asset.label} ${asset.deck_id ?? ''} ${asset.what_it_is ?? ''}`.toLowerCase().includes(query)) : productionAssets;
  }, [productionAssets, state.assetQuery]);
  const sceneWords = useMemo(() => snapshot.words.filter((word) => word.end_s >= selectedScene.start_s && word.start_s <= selectedScene.end_s), [snapshot.words, selectedScene]);
  const duration = Math.max(90, Math.round((selectedScene.end_s - selectedScene.start_s) * 30));

  if (!selectedAsset) return <div className="state-page"><h1>No production visuals</h1><p>The approved visual catalog is empty.</p></div>;

  const chooseScene = (scene: Scene, index: number) => dispatch({type: 'scene', id: scene.scene_id, assetId: productionAssets[index % productionAssets.length]?.asset_id ?? state.selectedAssetId});

  return (
    <main className="console-shell">
      <header className="topbar">
        <div><span className="eyebrow">Outreach video engine</span><h1>Production Console</h1></div>
        <div className="topbar__status"><span className="status-dot" /> {bridgeStatus}<span className="hash">Snapshot {shortHash(snapshot.artifact_hash)}</span><span className="gate-chip">Gate A · Read only</span></div>
      </header>

      <section className="workspace">
        <aside className="panel scene-panel" aria-label="Scene queue">
          <div className="panel-heading"><span>Scene queue</span><b>{snapshot.scenes.length}</b></div>
          <div className="scene-list">
            {snapshot.scenes.map((scene, index) => (
              <button key={scene.scene_id} className="scene-row" data-active={scene.scene_id === selectedScene.scene_id} onClick={() => chooseScene(scene, index)}>
                <span className="scene-index">{String(index + 1).padStart(2, '0')}</span>
                <span><strong>{scene.title}</strong><small>{scene.start_s.toFixed(1)}–{scene.end_s.toFixed(1)}s · {scene.review_state.replace('_', ' ')}</small></span>
              </button>
            ))}
          </div>
        </aside>

        <section className="preview-column">
          <div className="preview-heading"><div><span className="eyebrow">Active scene</span><h2>{selectedScene.title}</h2></div><span className="timecode">{selectedScene.start_s.toFixed(2)} → {selectedScene.end_s.toFixed(2)}</span></div>
          <div className="player-frame">
            <Player component={ProductionEvidenceComposition} inputProps={{assetUrl: mediaUrl(selectedAsset.asset_id), sceneTitle: selectedScene.title, assetLabel: selectedAsset.label, approvalLabel: 'Production visual'}} durationInFrames={duration} fps={30} compositionWidth={1376} compositionHeight={768} initialFrame={18} controls loop style={{width: '100%', aspectRatio: '1376 / 768'}} />
          </div>
          <div className="validation-strip"><span className="status-dot" /> Browser-safe shared composition <span>·</span> asset hash verified by bridge <span>·</span> mutation disabled</div>
        </section>

        <aside className="panel inspector-panel" aria-label="Read-only inspector">
          <div className="panel-heading"><span>Inspector</span><span className="lock">Locked</span></div>
          <fieldset disabled>
            <label>Scale <output>100%</output><input type="range" value="100" readOnly /></label>
            <div className="field-grid"><label>X <input value="0" readOnly /></label><label>Y <input value="0" readOnly /></label></div>
            <label>Motion recipe<select value="evidence-focus" disabled><option>evidence-focus</option></select></label>
            <label>Review note<textarea placeholder="Enabled after Gate A approval" /></label>
            <button>Save immutable revision</button>
          </fieldset>
          <div className="boundary-note"><b>Protected</b><span>Script, claims, timings, evidence status, source media and prior approvals cannot be changed here.</span></div>
        </aside>
      </section>

      <section className="lower-deck">
        <div className="timeline panel">
          <div className="panel-heading"><span>Narration / cue context</span><small>{sceneWords.length} words · {selectedScene.cue_refs.length} cues</small></div>
          <div className="word-strip">{sceneWords.map((word) => <span key={word.word_id} title={`${word.start_s.toFixed(2)}s`}>{word.text}</span>)}</div>
          <div className="cue-strip">{selectedScene.cue_refs.length ? selectedScene.cue_refs.map((cue) => <span key={cue}>{cue}</span>) : <em>No cue refs mapped for this scene.</em>}</div>
        </div>

        <div className="asset-drawer panel">
          <div className="panel-heading"><span>Approved production visuals</span><small>{filteredAssets.length} / {productionAssets.length}</small></div>
          <input className="asset-search" aria-label="Search production visuals" placeholder="Filter by topic or deck…" value={state.assetQuery} onChange={(event) => dispatch({type: 'query', value: event.target.value})} />
          <VirtualAssetList assets={filteredAssets} selectedId={selectedAsset.asset_id} onSelect={(id) => dispatch({type: 'asset', id})} />
        </div>

        <div className="evidence panel">
          <div className="panel-heading"><span>Provenance</span><small>{selectedAsset.deck_id}</small></div>
          <h3>{selectedAsset.label}</h3>
          <p>{selectedAsset.what_it_is}</p>
          <dl><div><dt>Source</dt><dd>{selectedAsset.deck_id} · slide {selectedAsset.slide_number}</dd></div><div><dt>Asset hash</dt><dd className="mono">{shortHash(selectedAsset.sha256)}</dd></div><div><dt>Rights</dt><dd>{selectedAsset.rights_state.replace('_', ' ')}</dd></div></dl>
          <div className="scope-grid"><div className="scope-ok"><b>Production use</b><span>Approved visual</span></div><div className={selectedAsset.evidence_eligible ? 'scope-ok' : 'scope-no'}><b>Claim support</b><span>{selectedAsset.evidence_eligible ? 'Approved factual content' : 'Not granted'}</span></div></div>
          <p className="scope-explainer">{selectedAsset.evidence_eligible ? 'The operator approved this deck’s factual contents for claim-support use.' : 'The visual may appear in the edit, but its factual contents are not approved as claim support.'}</p>
        </div>
      </section>

      {snapshot.degraded_inputs.length > 0 && <footer className="degraded"><b>Degraded input</b>{snapshot.degraded_inputs.join(' · ')}</footer>}
    </main>
  );
}

export default function App() {
  const {snapshot, health, error, loading} = useConsoleData();
  if (loading) return <div className="state-page"><span className="loader" /><h1>Compiling production context</h1><p>Loading the deterministic snapshot and bridge state.</p></div>;
  if (error) return <div className="state-page state-page--error"><h1>Console unavailable</h1><p>{error}</p><code>Verify the loopback bridge is running on 127.0.0.1.</code></div>;
  if (!snapshot) return <div className="state-page"><h1>Snapshot empty</h1><p>No canonical project snapshot was returned.</p></div>;
  return <Console snapshot={snapshot} bridgeStatus={health?.status ?? 'bridge unknown'} />;
}
