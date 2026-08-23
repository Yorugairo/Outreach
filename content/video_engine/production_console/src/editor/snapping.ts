import type {Frame, FrameRange, TimelineDocument} from './types';

export type SnapPointKind = 'document-boundary' | 'item-start' | 'item-end' | 'playhead' | 'custom';

export type SnapPoint = {
  frame: Frame;
  kind: SnapPointKind;
  id?: string;
  label?: string;
  priority?: number;
};

export type SnapResult = {
  frame: Frame;
  snapped: boolean;
  deltaFrames: number;
  target?: SnapPoint;
};

export type SnapRangeResult = {
  range: FrameRange;
  snapped: boolean;
  deltaFrames: number;
  edge: 'start' | 'end' | null;
  target?: SnapPoint;
};

export type SnapRangeOptions = {
  thresholdFrames: number;
  excludeItemId?: string;
  minFrame?: number;
  maxFrame?: number;
};

export function buildSnapPoints(
  document: TimelineDocument,
  options: {excludeItemIds?: readonly string[]; includeDocumentBoundaries?: boolean} = {},
): SnapPoint[] {
  const excluded = new Set(options.excludeItemIds ?? []);
  const points: SnapPoint[] = [];
  if (options.includeDocumentBoundaries !== false) {
    points.push({frame: 0, kind: 'document-boundary', id: 'document-start', priority: 0});
    points.push({frame: document.durationFrames, kind: 'document-boundary', id: 'document-end', priority: 0});
  }
  for (const item of document.items) {
    if (excluded.has(item.id)) continue;
    points.push({frame: item.range.startFrame, kind: 'item-start', id: item.id, label: item.label, priority: item.kind === 'scene' ? 1 : 2});
    points.push({frame: item.range.endFrame, kind: 'item-end', id: item.id, label: item.label, priority: item.kind === 'scene' ? 1 : 2});
  }
  return dedupeSnapPoints(points);
}

export function snapFrame(frame: Frame, points: readonly (SnapPoint | Frame)[], thresholdFrames: number): SnapResult {
  assertFiniteInteger(frame, 'frame');
  assertNonNegativeInteger(thresholdFrames, 'thresholdFrames');
  const candidates = points.map((point) => typeof point === 'number' ? {frame: point, kind: 'custom' as const} : point).filter((point) => Number.isInteger(point.frame));
  const target = nearestSnapPoint(frame, candidates, thresholdFrames);
  if (!target) return {frame, snapped: false, deltaFrames: 0};
  return {frame: target.frame, snapped: true, deltaFrames: target.frame - frame, target};
}

export const snapToNearest = snapFrame;

export function snapRange(range: FrameRange, points: readonly SnapPoint[], options: SnapRangeOptions): SnapRangeResult {
  assertRange(range);
  assertNonNegativeInteger(options.thresholdFrames, 'thresholdFrames');
  const minFrame = options.minFrame ?? 0;
  const maxFrame = options.maxFrame ?? Number.POSITIVE_INFINITY;
  if (!Number.isInteger(minFrame) || minFrame < 0 || (maxFrame !== Number.POSITIVE_INFINITY && !Number.isInteger(maxFrame)) || maxFrame <= minFrame) throw new RangeError('invalid snap bounds');
  const candidates = points.filter((point) => point.id !== options.excludeItemId);
  const startTarget = nearestSnapPoint(range.startFrame, candidates, options.thresholdFrames);
  const endTarget = nearestSnapPoint(range.endFrame, candidates, options.thresholdFrames);
  const duration = range.endFrame - range.startFrame;
  const startResult = startTarget ? {target: startTarget, edge: 'start' as const, delta: startTarget.frame - range.startFrame} : undefined;
  const endResult = endTarget ? {target: endTarget, edge: 'end' as const, delta: endTarget.frame - range.endFrame} : undefined;
  const valid = [startResult, endResult].filter((candidate): candidate is NonNullable<typeof candidate> => {
    if (!candidate) return false;
    const nextStart = range.startFrame + candidate.delta;
    const nextEnd = range.endFrame + candidate.delta;
    return nextStart >= minFrame && nextEnd <= maxFrame;
  });
  valid.sort((left, right) => Math.abs(left.delta) - Math.abs(right.delta) || (left.edge === 'start' ? -1 : 1) || left.target.frame - right.target.frame || (left.target.id ?? '').localeCompare(right.target.id ?? ''));
  const chosen = valid[0];
  if (!chosen) return {range, snapped: false, deltaFrames: 0, edge: null};
  return {
    range: {startFrame: range.startFrame + chosen.delta, endFrame: range.endFrame + chosen.delta},
    snapped: true,
    deltaFrames: chosen.delta,
    edge: chosen.edge,
    target: chosen.target,
  };
}

export function dedupeSnapPoints(points: readonly SnapPoint[]): SnapPoint[] {
  const byKey = new Map<string, SnapPoint>();
  for (const point of points) {
    if (!Number.isInteger(point.frame) || point.frame < 0) continue;
    const key = `${point.frame}:${point.kind}:${point.id ?? ''}`;
    const existing = byKey.get(key);
    if (!existing || (point.priority ?? 99) < (existing.priority ?? 99)) byKey.set(key, {...point});
  }
  return [...byKey.values()].sort((left, right) => left.frame - right.frame || (left.priority ?? 99) - (right.priority ?? 99) || left.kind.localeCompare(right.kind) || (left.id ?? '').localeCompare(right.id ?? ''));
}

function nearestSnapPoint(frame: Frame, points: readonly SnapPoint[], thresholdFrames: number): SnapPoint | undefined {
  const candidates = points
    .filter((point) => Math.abs(point.frame - frame) <= thresholdFrames)
    .slice()
    .sort((left, right) => Math.abs(left.frame - frame) - Math.abs(right.frame - frame) || (left.priority ?? 99) - (right.priority ?? 99) || left.frame - right.frame || (left.id ?? '').localeCompare(right.id ?? ''));
  return candidates[0];
}

function assertRange(range: FrameRange): void {
  if (!Number.isInteger(range.startFrame) || !Number.isInteger(range.endFrame) || range.startFrame < 0 || range.endFrame <= range.startFrame) throw new RangeError('range must be a positive half-open frame range');
}

function assertFiniteInteger(value: number, name: string): void {
  if (!Number.isInteger(value) || !Number.isFinite(value)) throw new RangeError(`${name} must be an integer`);
}

function assertNonNegativeInteger(value: number, name: string): void {
  if (!Number.isInteger(value) || value < 0) throw new RangeError(`${name} must be a non-negative integer`);
}
