import React from "react";
import { useCurrentFrame } from "remotion";
import type {
  TranscriptCaptionLine,
  TranscriptCaptionLineGroup,
  TranscriptCaptionProps,
  TranscriptCaptionToken,
  TranscriptCaptionTokenInput,
} from "./types";

export const CANONICAL_TRANSCRIPT_CAPTION_ID = "transcript_caption" as const;

const PUNCTUATION_WITHOUT_LEADING_SPACE = /^[,.;:!?%\u2026\u3001\u3002\uff0c\uff01\uff1f\uff1a\uff1b\u300d\u300f\u3009\u300b\u300d\u300f\u201d\u2019)\]}\u2013\u2014\-'"([{]+/u;
const OPENING_PUNCTUATION_AT_END = /[([\{"\u201c\u2018$\u00a3\u20ac\u00a5\u2013\u2014-]$/u;
const PUNCTUATION_ONLY = /^[\p{P}\p{S}]+$/u;

const readText = (value: TranscriptCaptionTokenInput, index: number): string => {
  const text = value.text ?? value.word ?? value.w;
  if (typeof text !== "string" || text.length === 0) {
    throw new TypeError(`tokens[${index}].text must be a non-empty string`);
  }
  return text;
};

const readFrame = (
  value: TranscriptCaptionTokenInput,
  camelKey: "startFrame" | "endFrame",
  snakeKey: "start_frame" | "end_frame",
  index: number,
): number => {
  const frame = value[camelKey] ?? value[snakeKey];
  if (typeof frame !== "number" || !Number.isFinite(frame) || !Number.isInteger(frame)) {
    throw new TypeError(`tokens[${index}].${camelKey} must be a finite integer`);
  }
  if (frame < 0) {
    throw new RangeError(`tokens[${index}].${camelKey} must be non-negative`);
  }
  return frame;
};

const readLineGroup = (
  value: TranscriptCaptionTokenInput,
  index: number,
): TranscriptCaptionLineGroup | undefined => {
  const lineGroup = value.lineGroup ?? value.line_group ?? value.line;
  if (lineGroup === undefined) return undefined;
  if (lineGroup !== 1 && lineGroup !== 2) {
    throw new RangeError(`tokens[${index}].lineGroup must be 1 or 2`);
  }
  return lineGroup;
};

const isCanonicalToken = (value: unknown): value is TranscriptCaptionToken => {
  if (!value || typeof value !== "object") return false;
  const token = value as Partial<TranscriptCaptionToken>;
  return (
    typeof token.text === "string" &&
    token.text.length > 0 &&
    typeof token.startFrame === "number" &&
    Number.isInteger(token.startFrame) &&
    token.startFrame >= 0 &&
    typeof token.endFrame === "number" &&
    Number.isInteger(token.endFrame) &&
    token.endFrame > token.startFrame &&
    (token.lineGroup === undefined || token.lineGroup === 1 || token.lineGroup === 2)
  );
};

const isFrozenCanonicalTokenList = (
  value: readonly (TranscriptCaptionToken | TranscriptCaptionTokenInput)[],
): boolean =>
  Object.isFrozen(value) && value.every((token) => Object.isFrozen(token) && isCanonicalToken(token));

const validateOrder = (tokens: readonly TranscriptCaptionToken[]): void => {
  let previousStart = -1;
  for (const [index, token] of tokens.entries()) {
    if (token.startFrame < previousStart) {
      throw new RangeError(`tokens[${index}].startFrame must not precede the previous canonical start`);
    }
    previousStart = token.startFrame;
  }
};

/** Clone, validate, and freeze canonical tokens without mutating source data. */
export const normalizeTranscriptCaptionTokens = (
  input: readonly TranscriptCaptionTokenInput[] | readonly TranscriptCaptionToken[],
): readonly TranscriptCaptionToken[] => {
  if (!Array.isArray(input)) {
    throw new TypeError("transcript caption tokens must be an array");
  }
  if (isFrozenCanonicalTokenList(input)) {
    const canonical = input as readonly TranscriptCaptionToken[];
    validateOrder(canonical);
    return canonical;
  }

  const rawTokens = input as readonly TranscriptCaptionTokenInput[];
  const tokens = rawTokens.map((raw, index) => {
    const text = readText(raw, index);
    const startFrame = readFrame(raw, "startFrame", "start_frame", index);
    const endFrame = readFrame(raw, "endFrame", "end_frame", index);
    if (endFrame <= startFrame) {
      throw new RangeError(`tokens[${index}].endFrame must be greater than startFrame`);
    }
    const lineGroup = readLineGroup(raw, index);
    const token: TranscriptCaptionToken = lineGroup === undefined
      ? { text, startFrame, endFrame }
      : { text, startFrame, endFrame, lineGroup };
    return Object.freeze(token);
  });
  const frozen = Object.freeze(tokens);
  validateOrder(frozen);
  return frozen;
};

const needsSpaceBetween = (previous: string, current: string): boolean => {
  if (!previous || !current) return false;
  if (/\s$/u.test(previous) || /^\s/u.test(current)) return false;
  if (PUNCTUATION_WITHOUT_LEADING_SPACE.test(current)) return false;
  if (OPENING_PUNCTUATION_AT_END.test(previous)) return false;
  return true;
};

/** Join token text without moving punctuation away from its canonical word. */
export const projectTranscriptCaptionText = (
  input: readonly TranscriptCaptionTokenInput[] | readonly TranscriptCaptionToken[],
): string => {
  const tokens = normalizeTranscriptCaptionTokens(input);
  return tokens.reduce((projection, token, index) => {
    if (index === 0) return token.text;
    const previous = tokens[index - 1].text;
    return `${projection}${needsSpaceBetween(previous, token.text) ? " " : ""}${token.text}`;
  }, "");
};

const isPunctuationToken = (token: TranscriptCaptionToken): boolean => PUNCTUATION_ONLY.test(token.text);

const captionLength = (tokens: readonly TranscriptCaptionToken[]): number =>
  projectTranscriptCaptionText(tokens).length;

const autoLineBreak = (tokens: readonly TranscriptCaptionToken[]): number | undefined => {
  if (tokens.length < 2) return undefined;
  const candidates = Array.from({ length: tokens.length - 1 }, (_, index) => index + 1).filter(
    (index) => !isPunctuationToken(tokens[index]),
  );
  if (!candidates.length) return undefined;
  const total = captionLength(tokens);
  const target = total / 2;
  return candidates.reduce((best, candidate) => {
    const leftLength = captionLength(tokens.slice(0, candidate));
    const bestLeftLength = captionLength(tokens.slice(0, best));
    const candidateScore = Math.abs(target - leftLength);
    const bestScore = Math.abs(target - bestLeftLength);
    if (candidateScore < bestScore) return candidate;
    if (candidateScore > bestScore) return best;
    return candidate < best ? candidate : best;
  }, candidates[0]);
};

const assignLineGroups = (tokens: readonly TranscriptCaptionToken[]): readonly TranscriptCaptionLineGroup[] => {
  if (!tokens.length) return [];
  const explicit = tokens.map((token) => token.lineGroup);
  const hasExplicitGroups = explicit.some((group) => group !== undefined);
  const groups: TranscriptCaptionLineGroup[] = [];

  if (!hasExplicitGroups) {
    const breakAt = autoLineBreak(tokens);
    const autoGroups = tokens.map((_, index) => (breakAt !== undefined && index >= breakAt ? 2 : 1));
    for (const [index, token] of tokens.entries()) {
      if (isPunctuationToken(token) && index > 0) autoGroups[index] = autoGroups[index - 1];
    }
    return autoGroups;
  }

  let previous: TranscriptCaptionLineGroup = 1;
  for (const [index, token] of tokens.entries()) {
    const requested = explicit[index];
    let group: TranscriptCaptionLineGroup = requested ?? previous;
    if (isPunctuationToken(token) && index > 0) {
      group = groups[index - 1];
    }
    groups.push(group);
    previous = group;
  }
  return groups;
};

/** Build frame-independent line groups; the result never exceeds two lines. */
export const buildTranscriptCaptionLines = (
  input: readonly TranscriptCaptionTokenInput[] | readonly TranscriptCaptionToken[],
): readonly TranscriptCaptionLine[] => {
  const tokens = normalizeTranscriptCaptionTokens(input);
  const groups = assignLineGroups(tokens);
  const lines: TranscriptCaptionLine[] = [];
  for (const lineGroup of [1, 2] as const) {
    const lineTokens = tokens
      .map((token, index) => ({ token, index }))
      .filter(({ index }) => groups[index] === lineGroup)
      .map(({ token }) => token);
    if (!lineTokens.length) continue;
    const groupedTokens = Object.freeze(
      lineTokens.map((token) => {
        if (token.lineGroup === lineGroup) return token;
        return Object.freeze({ ...token, lineGroup });
      }),
    );
    lines.push(Object.freeze({ lineGroup, tokens: groupedTokens }));
  }
  return Object.freeze(lines);
};

const readFrameForQuery = (frame: number): number => {
  if (typeof frame !== "number" || !Number.isFinite(frame)) {
    throw new TypeError("caption frame must be a finite number");
  }
  return frame;
};

/** Tokens revealed at their exact canonical starts; no derived stagger is used. */
export const getRevealedTranscriptCaptionTokens = (
  input: readonly TranscriptCaptionTokenInput[] | readonly TranscriptCaptionToken[],
  frame: number,
): readonly TranscriptCaptionToken[] => {
  const tokens = normalizeTranscriptCaptionTokens(input);
  const queryFrame = readFrameForQuery(frame);
  return Object.freeze(tokens.filter((token) => token.startFrame <= queryFrame));
};

/** The token currently covered by its canonical interval, useful for emphasis. */
export const getActiveTranscriptCaptionTokens = (
  input: readonly TranscriptCaptionTokenInput[] | readonly TranscriptCaptionToken[],
  frame: number,
): readonly TranscriptCaptionToken[] => {
  const tokens = normalizeTranscriptCaptionTokens(input);
  const queryFrame = readFrameForQuery(frame);
  return Object.freeze(tokens.filter((token) => token.startFrame <= queryFrame && queryFrame < token.endFrame));
};

export const getVisibleTranscriptCaptionTokens = getRevealedTranscriptCaptionTokens;

export type TranscriptCaptionRenderState = Readonly<{
  tokens: readonly TranscriptCaptionToken[];
  lines: readonly TranscriptCaptionLine[];
  revealedTokens: readonly TranscriptCaptionToken[];
  activeTokens: readonly TranscriptCaptionToken[];
  transcript: string;
}>;

export const getTranscriptCaptionRenderState = (
  input: readonly TranscriptCaptionTokenInput[] | readonly TranscriptCaptionToken[],
  frame: number,
): TranscriptCaptionRenderState => {
  const tokens = normalizeTranscriptCaptionTokens(input);
  return Object.freeze({
    tokens,
    lines: buildTranscriptCaptionLines(tokens),
    revealedTokens: getRevealedTranscriptCaptionTokens(tokens, frame),
    activeTokens: getActiveTranscriptCaptionTokens(tokens, frame),
    transcript: projectTranscriptCaptionText(tokens),
  });
};

const separatorFor = (tokens: readonly TranscriptCaptionToken[], index: number): string => {
  if (index === 0) return "";
  return needsSpaceBetween(tokens[index - 1].text, tokens[index].text) ? " " : "";
};

/**
 * Protected canonical caption renderer.  It keeps every token in a fixed line
 * slot with hidden placeholders so activation cannot reflow the caption.
 */
export const TranscriptCaptionAdapter: React.FC<TranscriptCaptionProps> = ({
  componentId = CANONICAL_TRANSCRIPT_CAPTION_ID,
  tokens: input,
  style,
  color = "#fffaf0",
  activeColor,
  backgroundColor = "transparent",
  fontSize = 28,
}) => {
  const frame = useCurrentFrame();
  const tokens = normalizeTranscriptCaptionTokens(input);
  const lines = buildTranscriptCaptionLines(tokens);
  const transcript = projectTranscriptCaptionText(tokens);
  if (!tokens.length) return null;

  return (
    <div
      data-component-id={componentId}
      data-transcript={transcript}
      aria-label={transcript}
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxSizing: "border-box",
        padding: "2px 8px",
        backgroundColor,
        color,
        fontFamily: "Inter, Arial, sans-serif",
        fontSize,
        fontWeight: 650,
        lineHeight: 1.14,
        textAlign: "center",
        overflow: "visible",
        ...style,
      }}
    >
      <span data-caption-line-count={lines.length} style={{ display: "flex", flexDirection: "column", alignItems: "center", maxWidth: "100%" }}>
        {lines.map((line) => (
          <span
            key={`line-${line.lineGroup}`}
            data-caption-line={line.lineGroup}
            style={{ display: "block", whiteSpace: "nowrap", minHeight: "1.14em" }}
          >
            {line.tokens.map((token, index) => {
              const revealed = frame >= token.startFrame;
              const active = token.startFrame <= frame && frame < token.endFrame;
              const separator = separatorFor(line.tokens, index);
              return (
                <React.Fragment key={`${token.startFrame}-${token.endFrame}-${index}`}>
                  {separator ? <span aria-hidden="true">{separator}</span> : null}
                  <span
                    data-caption-token={index}
                    data-caption-token-text={token.text}
                    data-caption-revealed={revealed ? "true" : "false"}
                    data-caption-active={active ? "true" : "false"}
                    style={{
                      display: "inline-block",
                      whiteSpace: "pre",
                      opacity: revealed ? 1 : 0,
                      visibility: revealed ? "visible" : "hidden",
                      color: active && activeColor ? activeColor : color,
                    }}
                  >
                    {token.text}
                  </span>
                </React.Fragment>
              );
            })}
          </span>
        ))}
      </span>
    </div>
  );
};

/** Create the one protected caption element used by Player and render paths. */
export const renderTranscriptCaption = (
  props: TranscriptCaptionProps,
): React.ReactElement => {
  const tokens = normalizeTranscriptCaptionTokens(props.tokens);
  return <TranscriptCaptionAdapter {...props} componentId={CANONICAL_TRANSCRIPT_CAPTION_ID} tokens={tokens} />;
};

export const renderWordTimedCaption = renderTranscriptCaption;
