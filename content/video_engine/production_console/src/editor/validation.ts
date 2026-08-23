import type {CueTimelineItem, Frame, FrameRange, NarrationWord, SceneTimelineItem} from './types';

export type RangedItem = {id?: string; range: FrameRange};
export type SceneRangeLike = RangedItem & {sceneId?: string};
export type CueRangeLike = RangedItem & {cueId?: string; sceneId?: string};

export type SceneContiguityIssue = {
  code: 'invalid_range' | 'starts_after_zero' | 'gap' | 'overlap' | 'ends_before_duration' | 'ends_after_duration';
  sceneId?: string;
  previousSceneId?: string;
  startFrame?: Frame;
  endFrame?: Frame;
  expectedFrame?: Frame;
};

export type SceneContiguityResult = {
  valid: boolean;
  issues: SceneContiguityIssue[];
};

export type CueContainmentIssue = {
  code: 'missing_scene' | 'outside_scene' | 'crosses_scene' | 'invalid_range';
  cueId?: string;
  sceneId?: string;
};

export type CueContainmentResult = {
  valid: boolean;
  issues: CueContainmentIssue[];
};

export type WordGap = FrameRange;

export type WordGapTrimRequest = {
  originalRange: FrameRange;
  proposedRange: FrameRange;
  words: readonly NarrationWord[];
};

export type WordGapTrimValidation = {
  valid: boolean;
  errors: Array<'invalid_original_range' | 'invalid_proposed_range' | 'outside_original_range' | 'start_cuts_word' | 'end_cuts_word' | 'no_words_remaining' | 'invalid_word_timing'>;
  startGap?: WordGap;
  endGap?: WordGap;
};

export function validateSceneContiguity(
  scenes: readonly SceneRangeLike[] | readonly FrameRange[],
  durationFrames?: number,
): SceneContiguityResult {
  const ranges = scenes.map((scene, index) => isFrameRange(scene) ? {id: String(index), range: scene} : scene).slice().sort((left, right) => left.range.startFrame - right.range.startFrame || left.range.endFrame - right.range.endFrame || (left.id ?? '').localeCompare(right.id ?? ''));
  const issues: SceneContiguityIssue[] = [];
  for (const scene of ranges) {
    if (!isFrameRange(scene.range)) issues.push({code: 'invalid_range', sceneId: scene.id});
  }
  if (ranges.length > 0 && isFrameRange(ranges[0].range) && ranges[0].range.startFrame !== 0) {
    issues.push({code: 'starts_after_zero', sceneId: ranges[0].id, startFrame: ranges[0].range.startFrame, expectedFrame: 0});
  }
  for (let index = 1; index < ranges.length; index += 1) {
    const previous = ranges[index - 1];
    const current = ranges[index];
    if (!isFrameRange(previous.range) || !isFrameRange(current.range)) continue;
    if (current.range.startFrame > previous.range.endFrame) {
      issues.push({code: 'gap', sceneId: current.id, previousSceneId: previous.id, startFrame: current.range.startFrame, expectedFrame: previous.range.endFrame});
    } else if (current.range.startFrame < previous.range.endFrame) {
      issues.push({code: 'overlap', sceneId: current.id, previousSceneId: previous.id, startFrame: current.range.startFrame, expectedFrame: previous.range.endFrame});
    }
  }
  if (durationFrames !== undefined && ranges.length > 0) {
    const last = ranges[ranges.length - 1];
    if (isFrameRange(last.range) && last.range.endFrame < durationFrames) issues.push({code: 'ends_before_duration', sceneId: last.id, endFrame: last.range.endFrame, expectedFrame: durationFrames});
    if (isFrameRange(last.range) && last.range.endFrame > durationFrames) issues.push({code: 'ends_after_duration', sceneId: last.id, endFrame: last.range.endFrame, expectedFrame: durationFrames});
  }
  return {valid: issues.length === 0, issues};
}

export const scenesAreContiguous = (scenes: readonly SceneRangeLike[] | readonly FrameRange[], durationFrames?: number): boolean => validateSceneContiguity(scenes, durationFrames).valid;
export const validateSceneContinuity = validateSceneContiguity;

export function findContainingScene<T extends SceneRangeLike>(cue: CueRangeLike, scenes: readonly T[]): T | undefined {
  const byId = cue.sceneId ? scenes.find((scene) => scene.sceneId === cue.sceneId || scene.id === cue.sceneId) : undefined;
  if (byId) return isContained(cue.range, byId.range) ? byId : undefined;
  return scenes.find((scene) => isContained(cue.range, scene.range));
}

export function isCueContainedByScene(cue: CueRangeLike | CueTimelineItem, scene: SceneRangeLike | SceneTimelineItem): boolean {
  const cueSceneId = 'sceneId' in cue ? cue.sceneId : undefined;
  const sceneId = 'sceneId' in scene ? scene.sceneId : undefined;
  if (cueSceneId && sceneId && cueSceneId !== sceneId) return false;
  return isContained(cue.range, scene.range);
}

export const cueIsContainedInScene = isCueContainedByScene;

export function validateCueContainment(
  cues: readonly CueRangeLike[],
  scenes: readonly SceneRangeLike[],
): CueContainmentResult {
  const issues: CueContainmentIssue[] = [];
  for (const cue of cues) {
    if (!isFrameRange(cue.range)) {
      issues.push({code: 'invalid_range', cueId: cue.id ?? cue.cueId, sceneId: cue.sceneId});
      continue;
    }
    const matchingScene = cue.sceneId ? scenes.find((scene) => scene.sceneId === cue.sceneId || scene.id === cue.sceneId) : undefined;
    if (cue.sceneId && !matchingScene) {
      issues.push({code: 'missing_scene', cueId: cue.id ?? cue.cueId, sceneId: cue.sceneId});
      continue;
    }
    const containingScene = matchingScene ? (isContained(cue.range, matchingScene.range) ? matchingScene : undefined) : findContainingScene(cue, scenes);
    if (!containingScene) {
      const crosses = scenes.some((scene) => cue.range.startFrame < scene.range.endFrame && cue.range.endFrame > scene.range.startFrame);
      issues.push({code: crosses ? 'crosses_scene' : 'outside_scene', cueId: cue.id ?? cue.cueId, sceneId: cue.sceneId});
    }
  }
  return {valid: issues.length === 0, issues};
}

export const cuesAreContained = (cues: readonly CueRangeLike[], scenes: readonly SceneRangeLike[]): boolean => validateCueContainment(cues, scenes).valid;

export function wordGaps(words: readonly NarrationWord[], audioRange?: FrameRange): WordGap[] {
  const validWords = words.filter(isNarrationWord).slice().sort((left, right) => left.startFrame - right.startFrame || left.endFrame - right.endFrame);
  if (validWords.length === 0) return audioRange && audioRange.endFrame > audioRange.startFrame ? [{...audioRange}] : [];
  const startFrame = audioRange?.startFrame ?? validWords[0].startFrame;
  const endFrame = audioRange?.endFrame ?? validWords[validWords.length - 1].endFrame;
  const gaps: WordGap[] = [];
  let cursor = startFrame;
  for (const word of validWords) {
    if (word.startFrame > cursor) gaps.push({startFrame: cursor, endFrame: Math.min(word.startFrame, endFrame)});
    cursor = Math.max(cursor, word.endFrame);
    if (cursor >= endFrame) break;
  }
  if (cursor < endFrame) gaps.push({startFrame: cursor, endFrame});
  return gaps.filter((gap) => gap.endFrame > gap.startFrame);
}

export function validateWordGapTrim(request: WordGapTrimRequest): WordGapTrimValidation {
  const errors: WordGapTrimValidation['errors'] = [];
  if (!isFrameRange(request.originalRange)) errors.push('invalid_original_range');
  if (!isFrameRange(request.proposedRange)) errors.push('invalid_proposed_range');
  if (errors.length > 0) return {valid: false, errors};
  if (request.proposedRange.startFrame < request.originalRange.startFrame || request.proposedRange.endFrame > request.originalRange.endFrame) errors.push('outside_original_range');
  if (request.words.length === 0 || request.words.some((word) => !isNarrationWord(word) || word.startFrame < request.originalRange.startFrame || word.endFrame > request.originalRange.endFrame)) errors.push('invalid_word_timing');
  const gaps = wordGaps(request.words, request.originalRange);
  let startGap: WordGap | undefined;
  let endGap: WordGap | undefined;
  if (request.proposedRange.startFrame > request.originalRange.startFrame) {
    startGap = gaps.find((gap) => request.proposedRange.startFrame >= gap.startFrame && request.proposedRange.startFrame <= gap.endFrame);
    if (!startGap) errors.push('start_cuts_word');
  }
  if (request.proposedRange.endFrame < request.originalRange.endFrame) {
    endGap = gaps.find((gap) => request.proposedRange.endFrame >= gap.startFrame && request.proposedRange.endFrame <= gap.endFrame);
    if (!endGap) errors.push('end_cuts_word');
  }
  const remainingWords = request.words.filter((word) => word.startFrame >= request.proposedRange.startFrame && word.endFrame <= request.proposedRange.endFrame);
  if (remainingWords.length === 0) errors.push('no_words_remaining');
  return {valid: errors.length === 0, errors, startGap, endGap};
}

export const validateWordGapAudioTrim = validateWordGapTrim;

export function validateAudioTrim(
  originalRange: FrameRange,
  proposedRange: FrameRange,
  words: readonly NarrationWord[],
): WordGapTrimValidation {
  return validateWordGapTrim({originalRange, proposedRange, words});
}

export function isWordGapTrim(request: WordGapTrimRequest): boolean {
  return validateWordGapTrim(request).valid;
}

function isContained(inner: FrameRange, outer: FrameRange): boolean {
  return isFrameRange(inner) && isFrameRange(outer) && inner.startFrame >= outer.startFrame && inner.endFrame <= outer.endFrame;
}

function isFrameRange(value: unknown): value is FrameRange {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Record<string, unknown>;
  return Number.isInteger(candidate.startFrame) && Number.isInteger(candidate.endFrame) && (candidate.startFrame as number) >= 0 && (candidate.endFrame as number) > (candidate.startFrame as number);
}

function isNarrationWord(value: unknown): value is NarrationWord {
  return !!value && typeof value === 'object' && Number.isInteger((value as NarrationWord).startFrame) && Number.isInteger((value as NarrationWord).endFrame) && (value as NarrationWord).startFrame >= 0 && (value as NarrationWord).endFrame > (value as NarrationWord).startFrame;
}
