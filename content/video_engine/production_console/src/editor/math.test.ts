import {describe, expect, it} from 'vitest';
import {frameRangeToPixels, frameToPixel, framesToPixels, framesToSeconds, pixelToFrame, pixelsToFrames, secondsToFrames, zoomAroundAnchor} from './math';

describe('timeline frame and pixel math', () => {
  it('converts seconds, frames, and pixels without losing the configured scale', () => {
    expect(secondsToFrames(2, 30)).toBe(60);
    expect(framesToSeconds(60, 30)).toBe(2);
    expect(framesToPixels(15, 2)).toBe(30);
    expect(pixelsToFrames(31, 2)).toBe(15.5);
    expect(frameToPixel(10, {pixelsPerFrame: 2, scrollLeft: 12, originPx: 5})).toBe(13);
    expect(pixelToFrame(13, {pixelsPerFrame: 2, scrollLeft: 12, originPx: 5})).toBe(10);
    expect(frameRangeToPixels({startFrame: 10, endFrame: 20}, {pixelsPerFrame: 2, scrollLeft: 12, originPx: 5})).toEqual({left: 13, right: 33, width: 20});
  });

  it('keeps the same frame under the anchor pixel while zooming', () => {
    const result = zoomAroundAnchor({
      fps: 30,
      pixelsPerSecond: 60,
      zoom: 1,
      nextZoom: 2,
      anchorPixel: 200,
      scrollLeft: 40,
    });
    expect(result.anchorFrame).toBe(120);
    expect(result.scrollLeft).toBe(280);
    expect(pixelToFrame(200, {pixelsPerFrame: result.pixelsPerFrame, scrollLeft: result.scrollLeft})).toBe(120);
  });
});
