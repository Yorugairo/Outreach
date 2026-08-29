import React from 'react';
import {isTransformableItem} from '../../editor/document';
import type {FrameRange, TimelineItem, TimelineItemPatch, VisualTransform} from '../../editor/types';

type Props = {
  item: TimelineItem | null;
  currentFrame: number;
  onTransform: (itemId: string, patch: Omit<Partial<VisualTransform>, 'crop'> & {crop?: Partial<VisualTransform['crop']>}) => void;
  onText: (itemId: string, text: string) => void;
  onItemPatch: (itemId: string, patch: TimelineItemPatch) => void;
  onNarration: (itemId: string, range: FrameRange, level: number) => void;
  onAddKeyframe: (itemId: string, property: 'x' | 'y' | 'scaleX' | 'scaleY' | 'rotation' | 'opacity') => void;
  onDuplicate: (itemId: string) => void;
  onDelete: (itemId: string) => void;
};

const NumberField = ({label, value, step = 0.01, min, max, onChange}: {label: string; value: number; step?: number; min?: number; max?: number; onChange: (value: number) => void}) => (
  <label>{label}<input type="number" value={Number(value.toFixed(3))} step={step} min={min} max={max} onChange={(event) => onChange(Number(event.currentTarget.value))} /></label>
);

export function EditorInspector({item, currentFrame, onTransform, onText, onItemPatch, onNarration, onAddKeyframe, onDuplicate, onDelete}: Props) {
  if (!item) return <aside className="panel editor-inspector"><div className="panel-heading"><span>Inspector</span><span className="lock">No selection</span></div><div className="inspector-empty">Select a timeline or canvas item to edit it.</div></aside>;
  const transformable = isTransformableItem(item);
  return (
    <aside className="panel editor-inspector" aria-label="Component inspector">
      <div className="panel-heading"><span>Inspector</span><span className={item.locked ? 'lock' : 'scope-ok-text'}>{item.locked ? 'Protected' : 'Editable'}</span></div>
      <div className="inspector-scroll">
        <div className="inspector-identity"><span>{item.kind.replace('_', ' ')}</span><strong>{item.label}</strong><small>{item.range.startFrame}–{item.range.endFrame} · frame {currentFrame}</small></div>
        {item.kind === 'overlay' && item.overlayKind === 'text' ? <label className="inspector-wide">On-screen text<textarea value={item.text ?? ''} onChange={(event) => onText(item.id, event.currentTarget.value)} /></label> : null}
        {item.kind === 'caption' ? <><div className="protected-field"><b>Transcript locked</b><span>{item.text}</span><small>Style, grouping and line breaks remain editable; approved words do not.</small></div><label className="inspector-wide">Caption style<select value={item.styleId ?? 'compact'} onChange={(event) => onItemPatch(item.id, {styleId: event.currentTarget.value})}><option value="compact">Compact</option><option value="word_by_word">Word by Word · canonical timing</option><option value="upper_safe">Upper safe</option><option value="lower_safe">Lower safe</option><option value="emphasis">Emphasis</option></select></label><label className="inspector-wide">Caption group<input value={item.groupId ?? ''} onChange={(event) => onItemPatch(item.id, {groupId: event.currentTarget.value || undefined})} /></label><label className="inspector-wide">Line breaks (word positions)<input value={(item.lineBreaks ?? []).join(', ')} onChange={(event) => onItemPatch(item.id, {lineBreaks: event.currentTarget.value.split(',').map((value) => Number(value.trim())).filter((value) => Number.isInteger(value) && value > 0)})} /></label></> : null}
        {item.kind === 'narration' ? <><div className="protected-field"><b>Canonical narration</b><span>{item.sourceAssetId}</span><small>Only word-gap head/tail trim and volume are editable.</small></div><div className="inspector-grid"><NumberField label="Trim start" value={item.range.startFrame} step={1} min={0} max={item.range.endFrame - 1} onChange={(value) => onNarration(item.id, {startFrame: value, endFrame: item.range.endFrame}, item.level)} /><NumberField label="Trim end" value={item.range.endFrame} step={1} min={item.range.startFrame + 1} onChange={(value) => onNarration(item.id, {startFrame: item.range.startFrame, endFrame: value}, item.level)} /><NumberField label="Volume" value={item.level} min={0} max={1} onChange={(value) => onNarration(item.id, item.range, value)} /></div></> : null}
        {item.kind === 'remotion_bit' ? <div className="protected-field"><b>Curated Remotion Bit</b><span>{item.componentId} · {item.presetId}</span><small>Only allowlisted typed props may be persisted.</small></div> : null}
        {transformable ? (
          <>
            <h4>Transform</h4>
            <div className="inspector-grid">
              <NumberField label="X" value={item.transform.x} onChange={(value) => onTransform(item.id, {x: value})} />
              <NumberField label="Y" value={item.transform.y} onChange={(value) => onTransform(item.id, {y: value})} />
              <NumberField label="Scale X" value={item.transform.scaleX} min={0.05} max={4} onChange={(value) => onTransform(item.id, {scaleX: value})} />
              <NumberField label="Scale Y" value={item.transform.scaleY} min={0.05} max={4} onChange={(value) => onTransform(item.id, {scaleY: value})} />
              <NumberField label="Rotation" value={item.transform.rotation} step={1} onChange={(value) => onTransform(item.id, {rotation: value})} />
              <NumberField label="Opacity" value={item.transform.opacity} min={0} max={1} onChange={(value) => onTransform(item.id, {opacity: value})} />
              <NumberField label="Layer" value={item.transform.zIndex} step={1} min={-100} max={100} onChange={(value) => onTransform(item.id, {zIndex: value})} />
            </div>
            <h4>Crop / focal point</h4>
            <div className="inspector-grid"><NumberField label="Focal X" value={item.transform.crop.x} min={0} max={1} onChange={(value) => onTransform(item.id, {crop: {x: value}})} /><NumberField label="Focal Y" value={item.transform.crop.y} min={0} max={1} onChange={(value) => onTransform(item.id, {crop: {y: value}})} /><NumberField label="Crop width" value={item.transform.crop.width} min={.05} max={1} onChange={(value) => onTransform(item.id, {crop: {width: value}})} /><NumberField label="Crop height" value={item.transform.crop.height} min={.05} max={1} onChange={(value) => onTransform(item.id, {crop: {height: value}})} /></div>
            <h4>Keyframes</h4>
            <div className="keyframe-grid">{(['x', 'y', 'scaleX', 'scaleY', 'rotation', 'opacity'] as const).map((property) => <button type="button" key={property} onClick={() => onAddKeyframe(item.id, property)}>◇ {property}</button>)}</div>
          </>
        ) : null}
        <div className="inspector-actions"><button type="button" disabled={item.locked} onClick={() => onDuplicate(item.id)}>Duplicate</button><button type="button" className="danger-button" disabled={item.locked} onClick={() => onDelete(item.id)}>Delete</button></div>
        <div className="boundary-note"><b>Protected</b><span>Narration words, claim facts, evidence approval, rights, source files and prior revisions remain immutable.</span></div>
      </div>
    </aside>
  );
}
