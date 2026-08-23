import React, {useEffect, useMemo, useRef, useState} from 'react';
import {isTransformableItem} from '../../editor/document';
import type {TimelineDocument, TransformableTimelineItem, VisualTransform} from '../../editor/types';

type Props = {
  document: TimelineDocument;
  currentFrame: number;
  selectedIds: string[];
  onSelect: (itemId: string, additive: boolean) => void;
  onTransform: (itemId: string, transform: Partial<VisualTransform>) => void;
};

type Gesture = {itemId: string; mode: 'move' | 'resize' | 'rotate'; startX: number; startY: number; transform: VisualTransform};
type PreviewTransform = {itemId: string; transform: VisualTransform};

export function EditorCanvasOverlay({document, currentFrame, selectedIds, onSelect, onTransform}: Props) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [gesture, setGesture] = useState<Gesture | null>(null);
  const [preview, setPreview] = useState<PreviewTransform | null>(null);
  const visible = useMemo(() => document.items.filter((item): item is TransformableTimelineItem => item.range.startFrame <= currentFrame && currentFrame < item.range.endFrame && isTransformableItem(item)), [currentFrame, document.items]);

  useEffect(() => {
    if (!gesture) return;
    const move = (event: PointerEvent) => {
      const rect = rootRef.current?.getBoundingClientRect();
      if (!rect) return;
      const dx = (event.clientX - gesture.startX) / rect.width;
      const dy = (event.clientY - gesture.startY) / rect.height;
      const transform = gesture.mode === 'move'
        ? {...gesture.transform, x: gesture.transform.x + dx, y: gesture.transform.y + dy}
        : gesture.mode === 'resize'
          ? {...gesture.transform, scaleX: Math.max(.05, gesture.transform.scaleX + dx * 2), scaleY: Math.max(.05, gesture.transform.scaleY + dy * 2)}
          : {...gesture.transform, rotation: gesture.transform.rotation + dx * 360};
      setPreview({itemId: gesture.itemId, transform});
    };
    const up = () => {
      if (preview?.itemId === gesture.itemId) onTransform(gesture.itemId, preview.transform);
      setGesture(null);
      setPreview(null);
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up, {once: true});
    return () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
    };
  }, [gesture, onTransform, preview]);

  return (
    <div className="canvas-editor-overlay" ref={rootRef} aria-label="Direct canvas controls">
      <span className="canvas-guide canvas-guide--x" />
      <span className="canvas-guide canvas-guide--y" />
      <span className="canvas-safe-area" />
      {visible.map((item) => {
        const selected = selectedIds.includes(item.id);
        const displayTransform = preview?.itemId === item.id ? preview.transform : item.transform;
        const width = item.kind === 'world_plate' ? 100 * displayTransform.scaleX : Math.max(8, displayTransform.crop.width * 72 * displayTransform.scaleX);
        const height = item.kind === 'world_plate' ? 100 * displayTransform.scaleY : Math.max(8, displayTransform.crop.height * 66 * displayTransform.scaleY);
        return (
          <button
            type="button"
            key={item.id}
            className="canvas-selection"
            data-selected={selected}
            aria-label={`Select ${item.label}`}
            style={{
              left: `${50 + displayTransform.x * 100}%`,
              top: `${50 + displayTransform.y * 100}%`,
              width: `${width}%`,
              height: `${height}%`,
              opacity: selected ? 1 : 0,
              transform: `translate(-50%, -50%) rotate(${displayTransform.rotation}deg)`,
              zIndex: 100 + displayTransform.zIndex,
            }}
            onClick={(event) => {event.stopPropagation(); onSelect(item.id, event.shiftKey);}}
            onPointerDown={(event) => {
              if (!selected) onSelect(item.id, event.shiftKey);
              setGesture({itemId: item.id, mode: 'move', startX: event.clientX, startY: event.clientY, transform: item.transform});
            }}
          >
            <span className="canvas-selection__label">{item.label}</span>
            <i className="canvas-handle canvas-handle--nw" /><i className="canvas-handle canvas-handle--ne" />
            <i className="canvas-handle canvas-handle--sw" /><i className="canvas-handle canvas-handle--se" onPointerDown={(event) => {event.stopPropagation(); setGesture({itemId: item.id, mode: 'resize', startX: event.clientX, startY: event.clientY, transform: item.transform});}} />
            <i className="canvas-rotate-handle" onPointerDown={(event) => {event.stopPropagation(); setGesture({itemId: item.id, mode: 'rotate', startX: event.clientX, startY: event.clientY, transform: item.transform});}} />
          </button>
        );
      })}
    </div>
  );
}
