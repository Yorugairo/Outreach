import React, {useMemo, useState} from 'react';
import type {Asset} from './types';

const ROW_HEIGHT = 58;
const VIEW_HEIGHT = 350;

export const VirtualAssetList: React.FC<{assets: Asset[]; selectedId: string; onSelect: (id: string) => void}> = ({assets, selectedId, onSelect}) => {
  const [scrollTop, setScrollTop] = useState(0);
  const range = useMemo(() => {
    const start = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - 2);
    const count = Math.ceil(VIEW_HEIGHT / ROW_HEIGHT) + 4;
    return {start, end: Math.min(assets.length, start + count)};
  }, [assets.length, scrollTop]);

  return (
    <div className="asset-virtual" style={{height: VIEW_HEIGHT}} onScroll={(event) => setScrollTop(event.currentTarget.scrollTop)}>
      <div style={{height: assets.length * ROW_HEIGHT, position: 'relative'}}>
        {assets.slice(range.start, range.end).map((asset, offset) => (
          <button key={asset.asset_id} className="asset-row" data-active={asset.asset_id === selectedId} style={{transform: `translateY(${(range.start + offset) * ROW_HEIGHT}px)`, height: ROW_HEIGHT}} onClick={() => onSelect(asset.asset_id)}>
            <span className="asset-row__title">{asset.label}</span>
            <span className="asset-row__meta">{asset.deck_id ?? 'project'} · {asset.slide_number ? `slide ${asset.slide_number}` : asset.source_kind}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
