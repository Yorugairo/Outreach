import type {ApprovedEasing, ApprovedSpringPreset, AnimatableProperty, KeyframeTracks, NumericKeyframe} from './types';

export const APPROVED_EASINGS: readonly ApprovedEasing[] = ['linear', 'smoothstep', 'ease_in', 'ease_out', 'ease_in_out'];
export const APPROVED_SPRING_PRESETS: readonly ApprovedSpringPreset[] = ['gentle', 'snappy', 'bouncy'];

export function isApprovedEasing(value: unknown): value is ApprovedEasing {
  return value === 'linear' || value === 'smoothstep' || value === 'ease_in' || value === 'ease_out' || value === 'ease_in_out';
}

export function isApprovedSpringPreset(value: unknown): value is ApprovedSpringPreset {
  return value === 'gentle' || value === 'snappy' || value === 'bouncy';
}

/** The approved easing set mirrors the deterministic Remotion motion recipes. */
export function easeProgress(progress: number, easing: ApprovedEasing = 'smoothstep'): number {
  if (!Number.isFinite(progress)) throw new RangeError('progress must be finite');
  if (!isApprovedEasing(easing)) throw new RangeError(`unsupported easing: ${String(easing)}`);
  const t = clamp01(progress);
  if (easing === 'linear') return t;
  if (easing === 'ease_in') return t * t;
  if (easing === 'ease_out') return 1 - (1 - t) * (1 - t);
  // The existing renderer intentionally maps smoothstep and ease_in_out to
  // the same bounded curve for low-resolution/full-render parity.
  return t * t * (3 - 2 * t);
}

/** A deterministic, bounded-at-endpoint approximation for approved spring labels. */
export function springProgress(progress: number, preset: ApprovedSpringPreset = 'gentle'): number {
  if (!Number.isFinite(progress)) throw new RangeError('progress must be finite');
  if (!isApprovedSpringPreset(preset)) throw new RangeError(`unsupported spring preset: ${String(preset)}`);
  const t = clamp01(progress);
  if (t === 0 || t === 1) return t;
  const settings: Record<ApprovedSpringPreset, {damping: number; frequency: number}> = {
    gentle: {damping: 4.5, frequency: 7},
    snappy: {damping: 7, frequency: 9},
    bouncy: {damping: 2.8, frequency: 12},
  };
  const {damping, frequency} = settings[preset];
  const curve = (value: number) => 1 - Math.exp(-damping * value) * Math.cos(frequency * value);
  return curve(t) / curve(1);
}

export function normalizeKeyframes(keyframes: readonly NumericKeyframe[]): NumericKeyframe[] {
  const normalized = keyframes.map((keyframe) => ({...keyframe})).sort((left, right) => left.frame - right.frame);
  for (let index = 0; index < normalized.length; index += 1) {
    const keyframe = normalized[index];
    if (!Number.isInteger(keyframe.frame) || keyframe.frame < 0 || !Number.isFinite(keyframe.value)) {
      throw new RangeError('keyframes require non-negative integer frames and finite values');
    }
    if (keyframe.easing !== undefined && !isApprovedEasing(keyframe.easing)) {
      throw new RangeError(`unsupported easing: ${String(keyframe.easing)}`);
    }
    if (keyframe.springPreset !== undefined && !isApprovedSpringPreset(keyframe.springPreset)) {
      throw new RangeError(`unsupported spring preset: ${String(keyframe.springPreset)}`);
    }
    if (index > 0 && normalized[index - 1].frame === keyframe.frame) {
      throw new RangeError(`duplicate keyframe at frame ${keyframe.frame}`);
    }
  }
  return normalized;
}

export function validateKeyframes(
  keyframes: readonly NumericKeyframe[],
  range?: {startFrame: number; endFrame: number},
): {valid: boolean; errors: string[]} {
  const errors: string[] = [];
  try {
    const normalized = normalizeKeyframes(keyframes);
    if (range) {
      if (!Number.isInteger(range.startFrame) || !Number.isInteger(range.endFrame) || range.endFrame <= range.startFrame) errors.push('invalid keyframe range');
      if (normalized.some((keyframe) => keyframe.frame < range.startFrame || keyframe.frame > range.endFrame)) errors.push('keyframe is outside item range');
    }
  } catch (error) {
    errors.push(error instanceof Error ? error.message : String(error));
  }
  return {valid: errors.length === 0, errors};
}

/**
 * Interpolates a numeric track and clamps outside the authored keyframe span.
 * The easing on the left keyframe controls the segment leading to the right
 * keyframe; this makes a track serializable without a separate segment list.
 */
export function interpolateKeyframes(
  keyframes: readonly NumericKeyframe[],
  frame: number,
  defaultEasing: ApprovedEasing = 'smoothstep',
): number | undefined {
  if (!Number.isFinite(frame)) throw new RangeError('frame must be finite');
  const normalized = normalizeKeyframes(keyframes);
  if (normalized.length === 0) return undefined;
  if (normalized.length === 1 || frame <= normalized[0].frame) return normalized[0].value;
  const last = normalized[normalized.length - 1];
  if (frame >= last.frame) return last.value;

  for (let index = 0; index < normalized.length - 1; index += 1) {
    const left = normalized[index];
    const right = normalized[index + 1];
    if (frame <= right.frame) {
      const progress = (frame - left.frame) / (right.frame - left.frame);
      const eased = left.springPreset ? springProgress(progress, left.springPreset) : easeProgress(progress, left.easing ?? defaultEasing);
      return left.value + (right.value - left.value) * eased;
    }
  }
  return last.value;
}

export const interpolateNumericKeyframes = interpolateKeyframes;

export function evaluateKeyframeTracks(
  tracks: KeyframeTracks,
  frame: number,
  defaults: Partial<Record<AnimatableProperty, number>> = {},
): Partial<Record<AnimatableProperty, number>> {
  const values: Partial<Record<AnimatableProperty, number>> = {};
  for (const property of Object.keys(tracks) as AnimatableProperty[]) {
    const keyframes = tracks[property];
    if (!keyframes) continue;
    const value = interpolateKeyframes(keyframes, frame);
    if (value !== undefined) values[property] = value;
  }
  for (const property of Object.keys(defaults) as AnimatableProperty[]) {
    if (values[property] === undefined && defaults[property] !== undefined) values[property] = defaults[property];
  }
  return values;
}

export function setKeyframe(
  keyframes: readonly NumericKeyframe[],
  nextKeyframe: NumericKeyframe,
): NumericKeyframe[] {
  const withoutFrame = keyframes.filter((keyframe) => keyframe.frame !== nextKeyframe.frame);
  return normalizeKeyframes([...withoutFrame, nextKeyframe]);
}

export function removeKeyframe(keyframes: readonly NumericKeyframe[], frame: number): NumericKeyframe[] {
  return normalizeKeyframes(keyframes.filter((keyframe) => keyframe.frame !== frame));
}

function clamp01(value: number): number {
  return Math.min(1, Math.max(0, value));
}
