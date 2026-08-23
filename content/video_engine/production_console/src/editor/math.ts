import type {Frame, FrameRange} from './types';

export type RoundingMode = 'floor' | 'ceil' | 'round' | 'none';

export type TimelineGeometry = {
  /** Content pixels represented by one frame at the current zoom. */
  pixelsPerFrame: number;
  scrollLeft?: number;
  originPx?: number;
};

export type TimelineScale = {
  fps: number;
  pixelsPerSecond: number;
  zoom: number;
};

export type ZoomAnchorInput = TimelineScale & {
  nextZoom: number;
  anchorPixel?: number;
  anchorPx?: number;
  scrollLeft: number;
  originPx?: number;
  minZoom?: number;
  maxZoom?: number;
};

export type ZoomAnchorResult = {
  zoom: number;
  scrollLeft: number;
  anchorFrame: number;
  pixelsPerFrame: number;
};

export function secondsToFrames(seconds: number, fps: number, rounding: RoundingMode = 'round'): number {
  assertFinite(seconds, 'seconds');
  assertPositive(fps, 'fps');
  const frames = seconds * fps;
  return roundValue(frames, rounding);
}

export function framesToSeconds(frames: number, fps: number): number {
  assertFinite(frames, 'frames');
  assertPositive(fps, 'fps');
  return frames / fps;
}

export const frameFromSeconds = secondsToFrames;
export const secondsFromFrame = framesToSeconds;

export function pixelsPerFrame(scale: TimelineScale): number {
  assertPositive(scale.fps, 'fps');
  assertPositive(scale.pixelsPerSecond, 'pixelsPerSecond');
  assertPositive(scale.zoom, 'zoom');
  return (scale.pixelsPerSecond / scale.fps) * scale.zoom;
}

export function framesToPixels(frames: number, pixelsPerFrameValue: number): number {
  assertFinite(frames, 'frames');
  assertPositive(pixelsPerFrameValue, 'pixelsPerFrame');
  return frames * pixelsPerFrameValue;
}

export function pixelsToFrames(pixels: number, pixelsPerFrameValue: number, rounding: RoundingMode = 'none'): number {
  assertFinite(pixels, 'pixels');
  assertPositive(pixelsPerFrameValue, 'pixelsPerFrame');
  return roundValue(pixels / pixelsPerFrameValue, rounding);
}

export function frameToPixel(frame: number, geometry: TimelineGeometry): number;
export function frameToPixel(frame: number, pixelsPerFrameValue: number, scrollLeft?: number, originPx?: number): number;
export function frameToPixel(
  frame: number,
  geometryOrPixelsPerFrame: TimelineGeometry | number,
  scrollLeft = 0,
  originPx = 0,
): number {
  assertFinite(frame, 'frame');
  const geometry = resolveGeometry(geometryOrPixelsPerFrame, scrollLeft, originPx);
  return geometry.originPx + frame * geometry.pixelsPerFrame - geometry.scrollLeft;
}

export function pixelToFrame(pixel: number, geometry: TimelineGeometry): number;
export function pixelToFrame(pixel: number, pixelsPerFrameValue: number, scrollLeft?: number, originPx?: number): number;
export function pixelToFrame(
  pixel: number,
  geometryOrPixelsPerFrame: TimelineGeometry | number,
  scrollLeft = 0,
  originPx = 0,
): number {
  assertFinite(pixel, 'pixel');
  const geometry = resolveGeometry(geometryOrPixelsPerFrame, scrollLeft, originPx);
  return (pixel - geometry.originPx + geometry.scrollLeft) / geometry.pixelsPerFrame;
}

export const frameToPixels = frameToPixel;
export const pixelsToFrame = pixelToFrame;

export function frameRangeToPixels(range: FrameRange, geometry: TimelineGeometry): {left: number; right: number; width: number} {
  assertRange(range);
  const left = frameToPixel(range.startFrame, geometry);
  const right = frameToPixel(range.endFrame, geometry);
  return {left, right, width: right - left};
}

export function pixelRangeToFrames(
  left: number,
  right: number,
  geometry: TimelineGeometry,
  rounding: Exclude<RoundingMode, 'none'> = 'round',
): FrameRange {
  assertFinite(left, 'left');
  assertFinite(right, 'right');
  if (right <= left) throw new RangeError('right must be greater than left');
  const startFrame = roundValue(pixelToFrame(left, geometry), rounding);
  const endFrame = roundValue(pixelToFrame(right, geometry), rounding);
  return {startFrame, endFrame: Math.max(startFrame + 1, endFrame)};
}

/**
 * Recomputes scrollLeft so the same timeline frame remains below an anchor
 * pixel after zooming.  The returned scroll value is content-relative and
 * works with a non-zero ruler/canvas origin.
 */
export function zoomAroundAnchor(input: ZoomAnchorInput): ZoomAnchorResult {
  const anchorPixel = input.anchorPixel ?? input.anchorPx;
  if (anchorPixel === undefined) throw new RangeError('anchorPixel is required');
  assertFinite(anchorPixel, 'anchorPixel');
  assertFinite(input.scrollLeft, 'scrollLeft');
  const minZoom = input.minZoom ?? 0.1;
  const maxZoom = input.maxZoom ?? 8;
  if (!Number.isFinite(minZoom) || !Number.isFinite(maxZoom) || minZoom <= 0 || maxZoom < minZoom) throw new RangeError('invalid zoom bounds');
  assertPositive(input.fps, 'fps');
  assertPositive(input.pixelsPerSecond, 'pixelsPerSecond');
  const zoom = clamp(input.nextZoom, minZoom, maxZoom);
  const originPx = input.originPx ?? 0;
  const previousPixelsPerFrame = pixelsPerFrame({fps: input.fps, pixelsPerSecond: input.pixelsPerSecond, zoom: input.zoom});
  const anchorFrame = (anchorPixel - originPx + input.scrollLeft) / previousPixelsPerFrame;
  const nextPixelsPerFrame = pixelsPerFrame({fps: input.fps, pixelsPerSecond: input.pixelsPerSecond, zoom});
  const scrollLeft = anchorFrame * nextPixelsPerFrame + originPx - anchorPixel;
  return {zoom, scrollLeft, anchorFrame, pixelsPerFrame: nextPixelsPerFrame};
}

export function scrollForZoomAnchor(
  anchorFrame: number,
  anchorPixel: number,
  scale: TimelineScale,
  nextZoom: number,
  originPx = 0,
): number {
  assertFinite(anchorFrame, 'anchorFrame');
  assertFinite(anchorPixel, 'anchorPixel');
  const nextScale = {...scale, zoom: nextZoom};
  return anchorFrame * pixelsPerFrame(nextScale) + originPx - anchorPixel;
}

export const zoomToAnchor = zoomAroundAnchor;
export const adjustScrollForZoom = scrollForZoomAnchor;

export function clampFrame(frame: Frame, durationFrames: number): Frame {
  assertFinite(frame, 'frame');
  if (!Number.isInteger(durationFrames) || durationFrames < 1) throw new RangeError('durationFrames must be a positive integer');
  return clamp(frame, 0, durationFrames);
}

export function clampFrameRange(range: FrameRange, durationFrames: number): FrameRange {
  assertRange(range);
  const startFrame = clampFrame(range.startFrame, durationFrames);
  const endFrame = clampFrame(range.endFrame, durationFrames);
  if (endFrame <= startFrame) throw new RangeError('clamped range must contain at least one frame');
  return {startFrame, endFrame};
}

export function clamp(value: number, min: number, max: number): number {
  assertFinite(value, 'value');
  return Math.min(max, Math.max(min, value));
}

function resolveGeometry(value: TimelineGeometry | number, scrollLeft: number, originPx: number): Required<TimelineGeometry> {
  if (typeof value === 'number') {
    assertFinite(scrollLeft, 'scrollLeft');
    assertFinite(originPx, 'originPx');
    assertPositive(value, 'pixelsPerFrame');
    return {pixelsPerFrame: value, scrollLeft, originPx};
  }
  assertPositive(value.pixelsPerFrame, 'pixelsPerFrame');
  return {
    pixelsPerFrame: value.pixelsPerFrame,
    scrollLeft: value.scrollLeft ?? 0,
    originPx: value.originPx ?? 0,
  };
}

function roundValue(value: number, rounding: RoundingMode): number {
  if (rounding === 'floor') return Math.floor(value);
  if (rounding === 'ceil') return Math.ceil(value);
  if (rounding === 'round') return Math.round(value);
  return value;
}

function assertRange(range: FrameRange): void {
  if (!Number.isInteger(range.startFrame) || !Number.isInteger(range.endFrame) || range.startFrame < 0 || range.endFrame <= range.startFrame) {
    throw new RangeError('frame range must be positive and half-open');
  }
}

function assertFinite(value: number, name: string): void {
  if (!Number.isFinite(value)) throw new RangeError(`${name} must be finite`);
}

function assertPositive(value: number, name: string): void {
  if (!Number.isFinite(value) || value <= 0) throw new RangeError(`${name} must be positive`);
}
