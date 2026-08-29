import {describe, expect, it} from 'vitest';
import {easeProgress, evaluateKeyframeTracks, interpolateKeyframes, normalizeKeyframes, springProgress, validateKeyframes} from './keyframes';

describe('approved keyframe interpolation', () => {
  it('supports the approved easing options and clamps endpoints', () => {
    const keyframes = [
      {frame: 0, value: 0, easing: 'linear' as const},
      {frame: 10, value: 10, easing: 'smoothstep' as const},
      {frame: 20, value: 20},
    ];
    expect(interpolateKeyframes(keyframes, -1)).toBe(0);
    expect(interpolateKeyframes(keyframes, 5)).toBe(5);
    expect(interpolateKeyframes(keyframes, 15)).toBe(15);
    expect(interpolateKeyframes(keyframes, 30)).toBe(20);
    expect(interpolateKeyframes([{frame: 0, value: 0, springPreset: 'gentle'}, {frame: 10, value: 1}], 5)).not.toBe(0.5);
    expect(easeProgress(0.5, 'smoothstep')).toBe(0.5);
    expect(easeProgress(0.5, 'ease_in')).toBe(0.25);
    expect(easeProgress(0.5, 'ease_out')).toBe(0.75);
    expect(easeProgress(0.5, 'ease_in_out')).toBe(0.5);
    expect(springProgress(0, 'gentle')).toBe(0);
    expect(springProgress(1, 'bouncy')).toBe(1);
    expect(evaluateKeyframeTracks({x: keyframes}, 5)).toEqual({x: 5});
  });

  it('normalizes ordering and rejects duplicate or unsupported keyframes', () => {
    expect(normalizeKeyframes([{frame: 10, value: 1}, {frame: 0, value: 0}]).map((keyframe) => keyframe.frame)).toEqual([0, 10]);
    expect(validateKeyframes([{frame: 0, value: 0}, {frame: 10, value: 1}], {startFrame: 0, endFrame: 10}).valid).toBe(true);
    expect(() => normalizeKeyframes([{frame: 0, value: 0}, {frame: 0, value: 1}])).toThrow('duplicate');
    expect(() => normalizeKeyframes([{frame: 0, value: 0, easing: 'bounce' as never}])).toThrow('unsupported');
  });
});
