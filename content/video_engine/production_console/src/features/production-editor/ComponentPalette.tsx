import React, {useMemo, useState} from 'react';
import type {Asset, EditorComponentCatalog} from '../../types';

export type PaletteComponent = {
  id: string;
  label: string;
  category: 'text' | 'motion' | 'layout' | 'camera';
  status: 'enabled' | 'intake_required';
  tags: string[];
};

export const CURATED_BITS: PaletteComponent[] = [
  ['fade-in', 'Fade In', 'text'], ['blur-in', 'Blur In', 'text'], ['word-by-word', 'Word by Word', 'text'],
  ['slide-from-left', 'Slide from Left', 'motion'], ['basic-typewriter', 'Basic Typewriter', 'text'], ['basic-counter', 'Basic Counter', 'text'],
  ['list-reveal', 'List Reveal', 'layout'], ['grid-stagger', 'Grid Stagger', 'layout'], ['mosaic-reframe', 'Mosaic Reframe', 'layout'],
  ['3d-card-stack', '3D Card Stack', 'layout'], ['ken-burns-effect', 'Ken Burns Effect', 'camera'],
].map(([id, label, category]) => ({id, label, category: category as PaletteComponent['category'], status: 'enabled', tags: [category, 'remotion-bits', '0.2.0']}));

type Props = {
  assets: Asset[];
  worldAssets: Asset[];
  catalog: EditorComponentCatalog;
  onAddAsset: (assetId: string) => void;
  onAddWorldPlate: (assetId: string) => void;
  onAddText: () => void;
  onAddAnnotation: (kind: 'arrow' | 'shape') => void;
  onAddTeacherStamp: () => void;
  onAddBit: (componentId: string) => void;
  onRequestIntake: () => void;
};

export function ComponentPalette({assets, worldAssets, catalog, onAddAsset, onAddWorldPlate, onAddText, onAddAnnotation, onAddTeacherStamp, onAddBit, onRequestIntake}: Props) {
  const [tab, setTab] = useState<'assets' | 'worlds' | 'components' | 'bits'>('assets');
  const [query, setQuery] = useState('');
  const filteredAssets = useMemo(() => assets.filter((asset) => `${asset.asset_id} ${asset.label} ${asset.what_it_is ?? ''} ${asset.deck_id ?? ''}`.toLowerCase().includes(query.toLowerCase())), [assets, query]);
  const filteredWorldAssets = useMemo(() => worldAssets.filter((asset) => `${asset.asset_id} ${asset.label} ${asset.what_it_is ?? ''}`.toLowerCase().includes(query.toLowerCase())), [worldAssets, query]);
  const enabledIds = useMemo(() => new Set(catalog.components.filter((component) => component.source === 'remotion_bits').map((component) => component.component_id)), [catalog.components]);
  const filteredBits = useMemo(() => CURATED_BITS.filter((bit) => enabledIds.has(bit.id) && `${bit.label} ${bit.tags.join(' ')}`.toLowerCase().includes(query.toLowerCase())), [enabledIds, query]);
  return (
    <aside className="panel component-palette" aria-label="Asset and component palette">
      <div className="palette-tabs"><button data-active={tab === 'assets'} onClick={() => setTab('assets')}>Evidence</button><button data-active={tab === 'worlds'} onClick={() => setTab('worlds')}>World plates</button><button data-active={tab === 'components'} onClick={() => setTab('components')}>Create</button><button data-active={tab === 'bits'} onClick={() => setTab('bits')}>Bits</button></div>
      <input className="palette-search" aria-label="Search palette" placeholder={`Search ${tab}`} value={query} onChange={(event) => setQuery(event.currentTarget.value)} />
      <div className="palette-scroll">
        {tab === 'assets' ? filteredAssets.slice(0, 120).map((asset) => <button type="button" className="palette-card" key={asset.asset_id} onClick={() => onAddAsset(asset.asset_id)}><span className="palette-card__icon">▧</span><span><strong>{asset.label}</strong><small>{asset.deck_id ?? asset.source_kind} · {asset.evidence_eligible ? 'evidence approved' : 'visual only'}</small></span><i>＋</i></button>) : null}
        {tab === 'worlds' ? filteredWorldAssets.slice(0, 120).map((asset) => <button type="button" className="palette-card" key={asset.asset_id} onClick={() => onAddWorldPlate(asset.asset_id)}><span className="palette-card__icon">▣</span><span><strong>{asset.label}</strong><small>Composition-approved plate · factual evidence separate</small></span><i>＋</i></button>) : null}
        {tab === 'components' ? <><button type="button" className="palette-card" onClick={onAddText}><span className="palette-card__icon">T</span><span><strong>Overlay text</strong><small>Editable authored text</small></span><i>＋</i></button><button type="button" className="palette-card" onClick={() => onAddAnnotation('arrow')}><span className="palette-card__icon">↗</span><span><strong>Arrow</strong><small>Evidence annotation</small></span><i>＋</i></button><button type="button" className="palette-card" onClick={() => onAddAnnotation('shape')}><span className="palette-card__icon">□</span><span><strong>Shape</strong><small>Frame or emphasis</small></span><i>＋</i></button><button type="button" className="palette-card" onClick={onAddTeacherStamp}><span className="palette-card__icon">◎</span><span><strong>Teacher stamp</strong><small>Approved presenter marker</small></span><i>＋</i></button></> : null}
        {tab === 'bits' ? <>{filteredBits.map((bit) => <button type="button" className="palette-card palette-card--bit" key={bit.id} onClick={() => onAddBit(bit.id)}><span className="bit-preview"><i /><i /><i /></span><span><strong>{bit.label}</strong><small>{bit.category} · Remotion Bits 0.2.0</small></span><b>Enabled</b></button>)}<div className="palette-intake"><strong>Remaining catalog available for review</strong><span>An enable request creates a local intake artifact. Browser code cannot install packages or execute live source.</span><button type="button" onClick={onRequestIntake}>Request enable</button></div></> : null}
      </div>
    </aside>
  );
}
