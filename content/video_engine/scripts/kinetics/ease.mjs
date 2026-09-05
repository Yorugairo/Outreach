/* kinetics/ease.mjs - the timing module, part 1 (FINDING-the-animation-math s2; wired 2026-09-05 behind
   kinetics.min_jerk). This file is the SOURCE OF TRUTH: sync_kinetics.py inlines it into the scene-evidence
   player between the KINETICS:BEGIN ease and KINETICS:END markers, so the template stays standalone and
   `node --test` reaches the math (P43 T1). Self-contained on purpose: nothing here reads a template symbol.
   minJerk - Flash & Hogan 1985, the jerk-minimising quintic 10t^3 - 15t^4 + 6t^5: zero velocity AND zero
             acceleration at both ends, so a spatial transition neither snaps nor sags. */
export const minJerk = (u) => { u = Math.min(1, Math.max(0, u)); return u * u * u * (10 - 15 * u + 6 * u * u); };
