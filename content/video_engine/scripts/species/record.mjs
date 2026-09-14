/* species/record.mjs - THE RECORD DOCUMENT (P57 T21 / R26-99; doc 29's record species; CAPABILITIES
   "Record-document species"; the extraction of the scene-evidence player's `drawRecord`). SOURCE OF TRUTH,
   inlined into the scene-evidence player by sync_kinetics.py between KINETICS:BEGIN record and KINETICS:END.
   It imports nothing, so its place in the region order is only a place.

   A DOCK PAYLOAD, not a species kind - so it follows verdict.mjs's precedent exactly: this module registers NO
   painter. The engine's dock slot keeps the two lines that are the ENGINE's (the slot's `recState` lookup) and
   calls paintRecord BY NAME. P55 T7's decision stands unchanged and unbuilt: a DOCK_PAINTERS registry waits for
   a third dock painter - recorded, not built. Promoted from inline engine code with every golden byte-identical
   (`record-typewriter`, `record-typewriter@proof-attr`): each literal below is the value the inline code
   carried, to the digit, and no expression was re-associated.

   WHEN (`dock_payload:record`, CAPABILITIES.md:19, verbatim): "the sentence QUOTES someone's claim and the
   words themselves are the proof - the record types the line and the highlighter lands on the phrase as it is
   said".

   THE LAW - THE STROKE IS THE NARRATOR'S. The type clock is not a constant characters-per-second: every word
   appears on ITS OWN ONSET from the take's word timings (`record.words` [[word, t]], the same sidecar the
   captions read), and the word being spoken is cut over 0.72 of its own gap to the next onset, so a fast word
   types fast and a held word lingers. Three things the inline code decided and this module keeps:
     the CUT      the growing word is STRING-SLICED (`w.slice(0, round(len * p))`), never per-character opacity
                  or per-character nodes - a glyph is either typed or not, and no half-drawn glyph ever renders.
     the MARKER   the pulled phrase (`hl`, inclusive at both ends) is one `.hw` span per word whose
                  background-size sweeps 0 -> 100 % over SWEEP_S on a cubic-out from THAT word's onset, so the
                  highlighter lands on the phrase exactly as it is said.
     the SPACE    the space after the phrase's last word is a text node OUTSIDE the stroke (Tokyo 2026-09-10,
                  "yen($65 billion)" - inside it, the marker ran on past the quotation into the next word).
   The landing is the document's own: the attribution at end + ATTR_AFTER, the source line at end + SRC_AFTER -
   the paper says who said it only once the line has been said. Everything below is a pure function of t
   (scrub-safe: nothing is stored between frames, the whole quotation is rebuilt each frame from the onsets).
   The dials are ours to tune (42 s42.5), not findings. */

export const RECORD = Object.freeze({
  TYPE_FRAC: 0.72,    /* a word types over this fraction of its own gap to the NEXT onset [the engine's `* 0.72`] */
  SPAN_MIN: 0.08,     /* ... floored here, in seconds, so two onsets a frame apart still show a stroke */
  SWEEP_S: 0.2,       /* the marker's sweep across one highlighted word, in seconds (cubic-out) */
  ATTR_AFTER: 0.15,   /* the attribution appears this long after the quotation's `end` ... */
  SRC_AFTER: 0.45,    /* ... and the source line this long after it */
  HL_CLASS: "hw",     /* the marker span's class (the template's `.paper .hw` gradient) */
  CUR_CLASS: "pcur",  /* the block cursor's class, appended after the last typed word */
});

/* HOW MANY WORDS HAVE BEEN SPOKEN at t: the index of the last word whose onset has passed, -1 before the first.
   The onsets are the narrator's, so this is the whole clock - there is no characters/s anywhere in the file. */
export const recordTyped = (words, t) => {
  let i = -1;
  while (i + 1 < words.length && words[i + 1][1] <= t) i++;
  return i;
};

/* THE SPAN one word types over: 0.72 of its own gap to the next onset (the last word's gap is to `end`),
   floored at SPAN_MIN so a word crushed against the next still has a stroke rather than a jump. */
export const recordSpan = (ts, next, R = RECORD) => Math.max(R.SPAN_MIN, (next - ts) * R.TYPE_FRAC);

/* THE TYPE CLOCK of the word being spoken, 0 at its onset and 1 by onset + span, clamped at both ends. */
export const recordTypeClock = (t, ts, next, R = RECORD) =>
  Math.max(0, Math.min(1, (t - ts) / recordSpan(ts, next, R)));

/* HOW MANY CHARACTERS of that word stand at p - the string cut, rounded to a whole glyph. */
export const recordCut = (w, p) => Math.round(w.length * p);

/* THE MARKER'S WINDOW on a highlighted word: 0 at its onset, 1 by onset + SWEEP_S, on a cubic-out - the value
   the painter writes as the `.hw` span's background-size percentage. */
export const recordSweep = (t, ts, R = RECORD) => {
  const swept = Math.max(0, Math.min(1, (t - ts) / R.SWEEP_S));
  return 1 - Math.pow(1 - swept, 3);
};

/* THE LANDING: which of the paper's two feet are shown at t, from the quotation's own `end`. */
export const recordLanded = (t, end, R = RECORD) =>
  ({ attr: t > end + R.ATTR_AFTER, src: t > end + R.SRC_AFTER });

/* THE PAINTER. `st` is the engine's record state for the slot ({r, q, attr, src} - the payload and the three
   elements fillDock mounted); the engine's dock slot looks that up and calls this by name. */
export function paintRecord(st, t, R = RECORD) {
  const { r, q } = st, W = r.words;
  const i = recordTyped(W, t);
  const frag = document.createDocumentFragment();
  for (let k = 0; k <= i; k++) {
    const [w, ts] = W[k];
    const next = W[k + 1] ? W[k + 1][1] : r.end;
    let txt = w;
    if (k === i)            // string slicing, never per-character opacity
      txt = w.slice(0, recordCut(w, recordTypeClock(t, ts, next, R)));
    if (k >= r.hl[0] && k <= r.hl[1]) {
      const sp = document.createElement("span");
      sp.className = R.HL_CLASS;
      sp.textContent = (k < i && k < r.hl[1]) ? txt + " " : txt;
      sp.style.backgroundSize = (recordSweep(t, ts, R) * 100) + "% 100%";
      frag.append(sp);
      if (k === r.hl[1] && k < i) frag.append(document.createTextNode(" "));   /* the space after the phrase, outside the stroke (Tokyo 2026-09-10: "yen($65 billion)") */
    } else {
      frag.append(document.createTextNode(txt));
      if (k < i) frag.append(document.createTextNode(" "));
    }
  }
  const cur = document.createElement("span");
  cur.className = R.CUR_CLASS; frag.append(cur);
  q.replaceChildren(frag);
  const landed = recordLanded(t, r.end, R);
  st.attr.classList.toggle("shown", landed.attr);
  st.src.classList.toggle("shown", landed.src);
}
