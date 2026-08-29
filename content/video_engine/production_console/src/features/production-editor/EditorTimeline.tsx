import React, {useEffect, useMemo, useRef, useState} from 'react';
import type {FrameRange, TimelineDocument, TimelineItem} from '../../editor/types';

type DragState = {
  itemId: string;
  mode: 'move' | 'trim-start' | 'trim-end';
  startClientX: number;
  initial: FrameRange;
};

type Props = {
  document: TimelineDocument;
  currentFrame: number;
  selectedIds: string[];
  zoom: number;
  waveformPeaks?: number[];
  onZoom: (zoom: number) => void;
  onSeek: (frame: number) => void;
  onSelect: (itemId: string, additive: boolean) => void;
  onCommitRange: (itemId: string, range: FrameRange, disableSnap: boolean) => void;
};

const TRACK_HEIGHT = 38;
const LABEL_WIDTH = 142;
const MIN_ITEM_FRAMES = 2;

const itemClass = (item: TimelineItem) => `timeline-item timeline-item--${item.kind}`;

const clampRange = (range: FrameRange, duration: number): FrameRange => {
  const startFrame = Math.max(0, Math.min(duration - MIN_ITEM_FRAMES, Math.round(range.startFrame)));
  const endFrame = Math.max(startFrame + MIN_ITEM_FRAMES, Math.min(duration, Math.round(range.endFrame)));
  return {startFrame, endFrame};
};

export const EditorTimeline = React.memo<Props>(function EditorTimeline({
  document,
  currentFrame,
  selectedIds,
  zoom,
  waveformPeaks = [],
  onZoom,
  onSeek,
  onSelect,
  onCommitRange,
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [previewRange, setPreviewRange] = useState<FrameRange | null>(null);
  const pixelsPerFrame = Math.max(0.018, 0.07 * zoom);
  const contentWidth = Math.max(900, Math.ceil(document.durationFrames * pixelsPerFrame));
  const itemMap = useMemo(() => new Map(document.items.map((item) => [item.id, item])), [document.items]);
  const previewItemId = drag?.itemId ?? null;

  useEffect(() => {
    if (!drag) return;
    const move = (event: PointerEvent) => {
      const deltaFrames = Math.round((event.clientX - drag.startClientX) / pixelsPerFrame);
      const duration = drag.initial.endFrame - drag.initial.startFrame;
      let next: FrameRange;
      if (drag.mode === 'move') {
        const startFrame = Math.max(0, Math.min(document.durationFrames - duration, drag.initial.startFrame + deltaFrames));
        next = {startFrame, endFrame: startFrame + duration};
      } else if (drag.mode === 'trim-start') {
        next = {startFrame: Math.min(drag.initial.endFrame - MIN_ITEM_FRAMES, Math.max(0, drag.initial.startFrame + deltaFrames)), endFrame: drag.initial.endFrame};
      } else {
        next = {startFrame: drag.initial.startFrame, endFrame: Math.max(drag.initial.startFrame + MIN_ITEM_FRAMES, Math.min(document.durationFrames, drag.initial.endFrame + deltaFrames))};
      }
      setPreviewRange(clampRange(next, document.durationFrames));
    };
    const up = (event: PointerEvent) => {
      if (previewRange) onCommitRange(drag.itemId, previewRange, event.altKey);
      setDrag(null);
      setPreviewRange(null);
    };
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up, {once: true});
    return () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
    };
  }, [document.durationFrames, drag, onCommitRange, pixelsPerFrame, previewRange]);

  const seekFromPointer = (event: React.PointerEvent<HTMLElement>) => {
    const scroller = scrollRef.current;
    if (!scroller) return;
    const rect = scroller.getBoundingClientRect();
    const x = event.clientX - rect.left + scroller.scrollLeft - LABEL_WIDTH;
    onSeek(Math.max(0, Math.min(document.durationFrames - 1, Math.round(x / pixelsPerFrame))));
  };

  const beginDrag = (event: React.PointerEvent, item: TimelineItem, mode: DragState['mode']) => {
    if (item.locked) return;
    if (item.kind === 'scene' && mode === 'move') return;
    event.stopPropagation();
    onSelect(item.id, event.shiftKey);
    setDrag({itemId: item.id, mode, startClientX: event.clientX, initial: item.range});
    setPreviewRange(item.range);
  };

  const seconds = document.durationFrames / document.fps;
  const tickSeconds = zoom >= 2.4 ? 5 : zoom >= 1.2 ? 10 : 30;
  const ticks = useMemo(() => {
    const values: number[] = [];
    for (let second = 0; second <= seconds; second += tickSeconds) values.push(second);
    return values;
  }, [seconds, tickSeconds]);

  return (
    <section className="editor-timeline panel" aria-label="Production timeline">
      <div className="timeline-toolbar">
        <div><span className="eyebrow">Episode timeline</span><strong>{document.durationFrames.toLocaleString()} frames · {seconds.toFixed(1)}s</strong></div>
        <label className="timeline-zoom">Zoom<input aria-label="Timeline zoom" type="range" min="0.45" max="4" step="0.05" value={zoom} onChange={(event) => onZoom(Number(event.currentTarget.value))} /><output>{Math.round(zoom * 100)}%</output></label>
      </div>
      <div className="timeline-scroll" ref={scrollRef}>
        <div className="timeline-grid" style={{width: contentWidth + LABEL_WIDTH}}>
          <div className="timeline-ruler-label">Tracks</div>
          <div className="timeline-ruler" style={{left: LABEL_WIDTH, width: contentWidth}} onPointerDown={seekFromPointer}>
            {ticks.map((second) => <span key={second} style={{left: second * document.fps * pixelsPerFrame}}><i />{Math.floor(second / 60)}:{String(second % 60).padStart(2, '0')}</span>)}
          </div>
          <div className="timeline-playhead" data-editor-playhead data-pixels-per-frame={pixelsPerFrame} aria-hidden style={{left: LABEL_WIDTH + currentFrame * pixelsPerFrame, height: document.tracks.length * TRACK_HEIGHT + 32}} />
          {document.tracks.map((track, trackIndex) => (
            <React.Fragment key={track.id}>
              <div className="timeline-track-label" style={{top: 32 + trackIndex * TRACK_HEIGHT, height: TRACK_HEIGHT}}><span className="track-visibility">{track.visible ? '●' : '○'}</span><strong>{track.label}</strong>{track.locked ? <span title="Locked">⌑</span> : null}</div>
              <div className="timeline-track" style={{left: LABEL_WIDTH, top: 32 + trackIndex * TRACK_HEIGHT, width: contentWidth, height: TRACK_HEIGHT}} onPointerDown={seekFromPointer}>
                {track.kind === 'narration' && waveformPeaks.length ? <div className="timeline-waveform" aria-hidden>{waveformPeaks.map((peak, index) => <i key={index} style={{height: `${Math.max(6, peak * 100)}%`}} />)}</div> : null}
                {track.itemIds.map((itemId) => {
                  const item = itemMap.get(itemId);
                  if (!item) return null;
                  const range = previewItemId === item.id && previewRange ? previewRange : item.range;
                  const selected = selectedIds.includes(item.id);
                  return (
                    <button
                      type="button"
                      key={item.id}
                      className={itemClass(item)}
                      data-selected={selected}
                      data-locked={item.locked}
                      style={{left: range.startFrame * pixelsPerFrame, width: Math.max(5, (range.endFrame - range.startFrame) * pixelsPerFrame)}}
                      title={`${item.label} · ${range.startFrame}–${range.endFrame}`}
                      onClick={(event) => {event.stopPropagation(); onSelect(item.id, event.shiftKey);}}
                      onPointerDown={(event) => beginDrag(event, item, 'move')}
                    >
                      {!item.locked ? <span className="trim-handle trim-handle--start" onPointerDown={(event) => beginDrag(event, item, 'trim-start')} /> : null}
                      <span className="timeline-item__label">{item.label}</span>
                      {!item.locked ? <span className="trim-handle trim-handle--end" onPointerDown={(event) => beginDrag(event, item, 'trim-end')} /> : null}
                    </button>
                  );
                })}
              </div>
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
});
