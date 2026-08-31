
### 9.23 A chart carries its OWN story (operator, 2026-08-30)

"The charts need to fully communicate their own story without
narration." The monitor failed this three ways at once: an unlabeled
reference line ("what is the white dotted line?"), a floating
annotation with no leader to its point ("looks like an accident"),
and no date axis. The gates, all template-enforced now:

- **Every series on the plot is named** - reference/dashed series
  included (their end labels fade in with the line).
- **An offset annotation is TIED to its point** - |dy| > 40 draws a
  dotted leader from dot to chip automatically.
- **Log charts get date ticks too** (the my(y0) double-transform bug
  rendered them dateless - fixed; baseline is the pixel constant).
- The test: mute the narration, screenshot the chart, hand it to a
  stranger. If any ink needs the voiceover to explain it, the chart
  is not done.
