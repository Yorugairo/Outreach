# Triage digest - 621 operator corrections, 2026-07-29 .. 2026-09-13 (P54 T2, HG2)

Verdicts from 12 read-only explorer batches, merged and checked by the parent. Only the operator turns a candidate into a ruling or a gate. Quotes are the ledger's verbatim text (first 400 characters).

| verdict | rows |
| --- | --- |
| recorded | 375 |
| noise | 120 |
| episode | 63 |
| superseded | 27 |
| memory | 13 |
| craft | 8 |
| ruling-candidate | 7 |
| gate-candidate | 5 |
| conflict | 3 |

## Conflicts - a record contradicts the operator (3)

- **win-on-presentation** - `ee466c018002` 2026-08-22T20:54 - anchor `docs/content-video-engine/21-ART-STYLE-REFERENCE-REVIEW.md:What this does and does not prove`
  - Operator: we can win on presentation with real facts and context-aware plates. Doc 21: the natural experiment does not support "we win on presentation".
  - > also alicia invests / nick invests are performing better than stick trader and casual finance is doing better than them.  /watch:watch https://www.youtube.com/@ZenTraderXBT/videos and https://www.youtube.com/watch?v=qkY2vaoARBU  and https://www.youtube.com/watch?v=win4jTx0KBc they often don't even animate much at all. It shows I feel we shoudl be able to win on presentation by bringing in actual f
- **reduced-motion-video** - `02dbf7702cd8` 2026-08-23T06:11 - anchor `docs/content-video-engine/39-EVIDENCE-CHART-SYSTEM.md:10.1 The record document is ANIMATED — it reads along with the voice`
  - P15 plan (Motion) records the operator: reduced-motion governs the console, never the video. Doc 39 §10.1 rule 5 still says honour it on the animated record document.
  - > i tihnk prefers-reduced-motion is mainly for website development, not video development
- **magnific-cancelled-local-upscale** - `9821f0386743` 2026-09-02T05:07 - anchor `docs/content-video-engine/08-TOOLING-ALTERNATIVES.md:7. Magnific: adopt as a governed media workbench`
  - Doc 08 section 7 still adopts Magnific (API key, Kling wrapper, upscale). Operator: Magnific is cancelled, upscale locally. The Chirp half is already in voice-lane-split.
  - > i actually cancelled mymagnific so it's not premium anymore; we could do the upscale ourselves locally. I would prefer chirps because elevenlabs is expensive and i'd rather save it for youtube

## Ruling candidates (7)

- **long-form-runtime-floor** - `cf1f8b376e5e` 2026-08-29T07:19
  - Long form is never under 8 min. Kit and phase guides treat 8:00 as a table column only, and P1.md even has a "< 5 min" row. No floor is stated anywhere.
  - > wait what duration video are you expecting ofr the response video? I thinkw e were well beyond 504 seconds, i dont think we make vdieos shorter than 8 minutes
- **hybrid-brand-advice** - `4b43b0fc0c51` 2026-08-31T20:31
  - A hybrid-brand channel not built to sell: advice built for flippable channels (e.g. no real photo) doesn't bind it; the operator's face is on the table
  - > does tim have anything to say about banners? what about my picture, use the finance host, the robot, or my real photo? I know tim says don't use real photo but thats also because he tries to build people to flip their channel. this is more of a hybrid-brand channel, i don't intend to sell it
- **facebook-close-reader-stake** - `cd2e32426cdd` 2026-09-02T19:27
  - Facebook script closes on how the tech moves the market and so the viewer's own money (401k, index), not an analyst's hook. brand-voice has register only. 0 hits.
  - > re-write me the 300 word facebook script. write now it challenges "if you're tracking the printers.." but that's not the right close. Most of these people aren't tracking anything. We need to be talking to average people and explaining to them HOW this tech/ai / data center stuff impacts the market and why/how that impacts them.
- **audience-borrowing-costs** - `2e2e84c1559f` 2026-09-05T05:53
  - Shorts/Facebook viewers mostly aren't homeowners, so say "your borrowing costs", not "your mortgage". Only the dossier has the phrase; no rule records why
  - > yes, i think the other thing to say that we applied yesterday and dropped: "Your borrowing costs" is better than "your mortgage" because most people consuming shorts on facebook are not home owners.  after that, i approve elevenlabs and we can move to production
- **level-line-axis-floor** - `9e6d4f0a3f04` 2026-09-05T10:47
  - A level line's y-axis starts at the series' own low in the window (Japan's lowest since 2000), not 0. E28 s1 zero baseline covers bars; E53 s4 shared scales only
  - > maybe don't start from 0, maybe start from the lowest amount that japan has held since 2000?
- **foley-background-level** - `7096b624ebee` 2026-09-05T19:19
  - Transition foley is background, about 8-10 dB under the voice, never a main effect; whirl not jet. Only per-cue gains exist; no level rule recorded
  - > why is the freesound token empty? we should have access. Maybe it's on the other worktree where we made the first short. That whoosh sound is too mechanical, it sounds like a jet almost, ours shoudl sound like a whirl/whirlpool/spinning/spiralling. alos the sounds should still be background sounds not main effects, so iti should be like ~8-10 db below maybe
- **derived-is-added-layer** - `bfb9c40b69b6` 2026-09-08T15:25
  - A reproducible DERIVED figure is our originality layer, not a liability. The per-chart choreography ask is already in japan-tariff-trick/CHART-CHOREOGRAPHY.md
  - > Better, but Did you review the rest of the video or only that chart?  also 6240 is reproducible by taking the $30k car and applying the 25% tariffs. Derived isn't a bad thing, it's our added layer which is required for "original content" these days. We kept the cars at $30k a piece for simplicity, even though in real life trucks cost more.  But I do think that the chart itself should probably be a

## Gate candidates (5)

- **spoken-chart-not-on-screen** - `dc64bab50209` 2026-08-29T20:15
  - Gate: any line that names or points at a visual ("the spike", "the chart") must have a matching dock or page on screen in that window. No gate measures this.
  - > also you open on the "spike" but you don't have the spike ons creen, you talk about charts without the charts on screen. we have descriptions/semantics saved fora r eason.  Are you  sayin you completely skipped making a manifest of plates ->evidence? option A is what you were supposed to have done already done..why is process collapsing today?
- **sub-6s-plate** - `69ff558bdf67` 2026-08-29T22:46
  - Gate: flag any world plate under 6s, and fail one that carries a dock. BUILD-PIPELINE only says "under ~8s one piece or none". Nothing checks plate length.
  - > the baloon dock doesn't even make sense, i dont know why we have such a short plate and evidence there -- it doesnt add anything, and i'm not sure why it exists, why do we have a plate less than 6 seconds long?
- **thumbnail-text-clipping** - `3570a6280d20` 2026-09-02T00:39
  - Measure each glyph's pixel box on the thumbnail or sticker against the frame edges at display size. G45 and J12 only check the words. 0 hits for "measure pixel" or "thumbnail text".
  - > it's better but still aprtially cut, i dont know why you can't see that.
- **punch-crops-text** - `16d1b9558a10` 2026-09-03T07:29
  - Gate would find a text box the page punch-in cuts partway (partly inside the zoomed frame); the dim value is only a tuning pick
  - > that focus actiong ot way too dark, the gemini agent was wrong about 80%, try 64% if that was 80%.  what should we do about the fact that we wrote "If you're so bullish why trim?" up in the corner like that and then we zoom in and it's gone but there's still some text that's not cut off?
- **black-frame-at-seam** - `ec736d324128` 2026-09-05T10:45
  - Black flash at a scene change before the wipe/mount. Gate: flag near-black frames at a boundary with no declared dip. Only M29 (sound) is registered; E47 found it by hand
  - > we're having a frame glitch on the wipe timings, our timing is off i tihnk because we've delt with this before, probably broke on the-build. as soon as the scene change happens there's a black flash, THEN the page wipes

## Craft notes (unrecorded) (8)

- **prompt-construction-not-fill** - `89e530c948c6` 2026-08-31T09:07
  - > no, that doesn't read like memory chips. I think you calling it wordart or something killed it. It should read like the world memory, if the owrd memory was built out of memory chips; that's probably the way to phrase it for GPT
- **thumbnail-drop-shadow** - `23bc6fd85951` 2026-09-02T00:58
  - A hard drop shadow on thumbnail text reads as a doubled glitch; use a clean outline, no shadow. The brand sheet says "outlined" with no shadow rule.
  - > you don't see that?
- **spoken-vs-shown-reference** - `c40077974f0f` 2026-09-04T01:44
  - > I think we should say "Here's what the news isn't saying: Our biggest customer just stopped buying."  instead of making the cable news reference. We already show the people on tv, but most people dont watch tv, it works as a cultural reference on screen but its not convincing to say.  And i should have gone a step further: most people listening to youtube shorts dont own bonds, they want to know w
- **spoken-figures-rounded** - `5ad72826538f` 2026-09-04T01:49
  - > Should we just said "The Fed" instead of Federal reserve? I don't like saying "one point one" nobody would say that. the number is on the screen, either say "over one trillion" or say "A trillion"
- **shared-stake-close** - `0a23e0fb1762` 2026-09-04T02:46
  - > it should be "and the tab is ours" not "The tab is yours." to close.
- **short-signpost** - `e658a43a2d97` 2026-09-05T05:14
  - > the signpost gets dramaticalyl shortened, "so the first number:"  not "which brings us to the two numbers i rpomised"
- **say-the-visual-gag** - `a58cf9b87226` 2026-09-05T05:18
  - > we should probably say "on youtube, it's sixty-three stick figures."  If we don't say it, we're relying a lot more on the eleven labs recorder to hit the timing right for it to play well
- **bracket-cheap-callout** - `9c870523df79` 2026-09-08T16:25
  - > to be fair, the bracket is a cheap, relatively bad way that we use just to add some extra motion/callouts on the screen, cutting the bracket is not at all a loss. We're replacing itw ith something much etter.

## Working preferences (unrecorded) (13)

- **grilling-universal** - `2539b47a9998` 2026-08-24T18:42
  - > grilling should maybe be added to global AGENTS.md so its universal for all agents across repos.  yes, you can audit and prune most of the skills. SEO/CRM is important but we've mostly moved it off of Claude responsibilities and most of the rules are in docs, mostly we need to retain the design skills, research/web skills, and youtube/content generation skills. probably ~20 skils
- **confirm-before-export** - `66fc6a00319b` 2026-08-25T07:06
  - > don't just export it, i want to confirm first
- **sound-judged-in-context** - `67086ece55fb` 2026-08-31T10:58
  - > ok suno should be accessible now. It uses cowork in the sidebar so you might even be able to just drop a work order into cowork in there rather than having to click around the page yourself.  i'm not even sure what sound you're going for with the test sound. i have no idea how to begin judging sounds except to put it on the actual timeline and hear it while watching, i suppose you don't have any r
- **debug-on-slices-not-full-render** - `cdb700456b4a` 2026-09-02T02:43
  - > we should stop rendering the full video - there's still a weird flash right before the wipe, we need to fix it
- **veo-extend-not-omni** - `377104a363b7` 2026-09-02T23:46
  - > only veo can be extended, not omni.
- **grill-click-answers** - `d27d43873833` 2026-09-03T08:02
  - > when i ask you to grill me, is it possible to put it through the actual planning flow where i can answer by clicking your answers instead of typing if i want to? that was the one benefit the slash command from pocock added i think
- **player-provenance** - `362d21b7617a` 2026-09-05T01:18
  - > make sure you're using the player that you/we built not the bad one that gemini rebuilt
- **new-bars-are-deltas** - `54f1cbbf551e` 2026-09-05T04:28
  - > it will be more than just those because it also has to pass all of our previous gates -- the micro and macro gates are already built into the process, what you just wrote are only the new things it must fix
- **reread-backlog-after-build** - `a1006b5e44c9` 2026-09-05T11:02
  - > seems like maybe now that we've got some hands on work done you should read the evidence/research/exploration/backlog docs again to see if we're ready to pull anything else in
- **flow-mcp-multi-agent** - `1d4f2208b6be` 2026-09-08T19:29
  - > we should try the same prompts testing @Mikemasterv3 vs @Mike2 and @HollowStickMike characters. Google is logged in.  Also sounds like we need to modify the MCP  so that it handles multi-agent use better
- **one-shot-before-ruling** - `52b69ddfcc51` 2026-09-12T16:29
  - > I think we should try to one-shot a short to test our current settings and capabilities before committing some of those decisions
- **astra-authoring-motion** - `7476b72a9f9b` 2026-09-13T05:25
  - > yes, the latter, authoring motions.  I think part of it is because we used the actual maths to create our own engine instead of using standard out-of-the-box engines is why i notice a difference between fable and other models. Maybe now that we've modularized it there's less difference
- **portable-docs-routing** - `b822ef486b1a` 2026-09-13T05:32
  - > those portable docs are probably more stale than we care to admit also. I dont think it makes sense to add the pack to agents.md, it prbably makes sense to add the routing to find it instead.  this does sound like an interesting way to go about it /prp-plan 1-6; no privacy concerns.  Let's do step 1 an see if ti's valuable at all

## Superseded - never promote (27)

- **word-fix-patch** - `c92f7eb8c3af` 2026-08-23T00:19 - anchor `D1`
  - The one-word patch from existing timings was overturned by D1, the MASTER TAKE rule: splice-repair of a broken take is banned, retake instead (doc 37 §8).
  - > i dont thinkw e need to rebuild teh whole vdieo if that fix comes back good. you should be able to find the script and the exact word timing if you search local, or just pull the script from elevenlabs, its available with timings
- **integration-branch** - `b3c5db4fbda0` 2026-08-23T18:07 - anchor `5a990ed283af`
  - "We use /staging, not main" was reversed four minutes later: the operator accepted main (row 5a990ed283af), and the repo now merges doctrine to main.
  - > that's because we don't use mane, we use /staging and /trades-staging
- **sweep-ease** - `e78f1e2493b7` 2026-08-24T11:50 - anchor `378c453fc11e`
  - The noticeable sweep ease (0.22) was rejected in the next message as worse than linear. §8.16 settled a middle value of 0.08.
  - > yes, the hand can probably even start drawing earlier. its also okay if it accelerates against it's stroke slightly i think becuse it's not actually doing line drawing. you can probably give a very minor ease and a very minor reduction in draw delay
- **chart-persists-across-wipes** - `65ab93b50ed0` 2026-08-29T21:31 - anchor `E25`
  - 08-29 asked for a chart to hold across 3 plates while the world wipes (doc 29 9.15 item 2). E25 (09-03): a chart never survives a plate change; it re-enters if needed.
  - > also for that initial chart that persists across 3 pages -- we shouldn't even be bringing it back in -- it should persist while everything around it wipes.
- **tts-tag-cap** - `ceebc116db49` 2026-08-30T16:20 - anchor `docs/content-video-engine/37-TTS-DELIVERY-STANDARDS.md:21. BREAK TAGS RETIRED from the provider payload`
  - The ~3-tag cap was recorded in doc 37 section 1, then replaced the same day: zero tags go to the provider and pauses move to the edit. No E-id or ledger row for it
  - > isn't part of what we learned from the Eleven Labs docs yesterday  that we geniunely are supposed to cap the tags?
- **delegation-cost** - `f28b087a5764` 2026-08-31T10:10 - anchor `5e9914632250`
  - Doubt that subagent summaries save work (you end up re-reading); on 09-05 the operator chose to delegate doc lookup and retrieval, keeping design and planning
  - > except we see that in practice when they hand you that 500-token conclusion, it probably leads you to have to go look at the code base yourself anyways often times.   i dont want to pay for eleven labs sound generation - they're already our most expensive monthly subscription. do they have anything free?   I'm on Suno Pro
- **remotion-render-port** - `8877c40ddd61` 2026-09-01T21:45 - anchor `2d5c2b91f834`
  - Wanted a Remotion port over screen-capturing the player; his next message took the 1440p player render, and render_episode.py capture stands (BACKLOG B8)
  - > launch the localhost server. and I think we should definitely do the remotion port, why would we screen-capture the player?
- **shorts-make-it-ours** - `657b23724b57` 2026-09-03T00:47 - anchor `eb972f2bfe45`
  - On the NotebookLM lane, generated plates and topic charts ("make it ours") were ruled out later that day: "the phase 1 treatment is the answer for this lane"
  - > we can try it, we have to figure out for ourselves what "our own" looks like given what we have. You're the creative director here.  If we can genuinely provide more quality cheaply then we should do it - so that would be image generation and drawing charts that fit the topic etc.   we should build the retokened outro to see what it looks like.
- **evidence-over-notebooklm** - `fb714290d5bc` 2026-09-03T00:48 - anchor `eb972f2bfe45`
  - Putting real-data evidence over NotebookLM pictures was dropped for the shorts lane; phase 1 rejects chart panels on the picture (shorts-lane-phase1-standard)
  - > we already know how to make evidence layers work and draw attention on any layer, so we can always draw evidence wherever we want really, as long as we're sure that whatever we're drawing over is of less interest than what we're doing.
- **reel-audio-level** - `f73d1f291a5d` 2026-09-03T02:56 - anchor `9ec5e721e4a0`
  - The operator's own later row set the reel at 22 under ("go to 22"; voice 0 / reel -22 / music -26), not ~20; the memory file still says "10 dB under the mix"
  - > the film noise is too loud -  it should sit somewhere between our music layer and the voice layer, but it should be closer to the music layer, the music layer is set ~24 below the voice over? so the reel should sit like ~20 under probably, where does that sit us?
- **ledger-soak-outline** - `5577e215d654` 2026-09-03T05:29 - anchor `6f3cfba4ae00`
  - Kept as E22 addendum 2, then undone by addendum 3 (plain cream) and addendum 7 (outline dropped entirely)
  - > that's nto what i meant by bleed, i meant like the world plate should enter as an unravelling, textured cream. Then a half savor, then we literally bleed/seep the charcoal on to the page as if it is soaking up ink, and then we use the outline component to draw the border (100% tight match, not the open space like your example here)
- **uneven-charcoal-radius** - `9c74b085deaa` 2026-09-03T05:35 - anchor `ce86ff61d3c0`
  - Operator threw out the uneven-halo try minutes later ("no, that's not right either"); E22 addendum 3 lists it as refused
  - > the coffee isn't a good look, what i wanted was for the charcoal fill to go out to an uneven radius
- **plain-cream-line** - `ce86ff61d3c0` 2026-09-03T05:37 - anchor `6f3cfba4ae00`
  - The plain cream, soak, then line sequence gave way to the deckle (addendum 4) and to no line at all (addendum 7)
  - > no, that's  not right either. let's go back to just a plain cream background, then the  scribble/soak then the line draw
- **line-inside-deckle** - `879d7b735fbc` 2026-09-03T06:58 - anchor `6f3cfba4ae00`
  - The inner line was retired by E22 addendum 7 (no outline); only the cream-ground half survives (addendum 5)
  - > the line actually needs to be inside; and I think my original insticts were maybe right; the cream deckle would have read like the charcoal was fill, playing literally like charcoal on a scroll or similar, but with the white, it just looks kind of broken. One more try to salavage the white is to put the drawn line as the stabilizing line that turns it into a clean fill within the deckle instead of
- **flow-host-clips** - `ed903887bda6` 2026-09-03T19:02 - anchor `E40`
  - E40 later made stills the asset and clips the exception, driven by start and end frames; stock host enter/exit clips never became policy
  - > should we build a few Flow videos that are just our Robo Character or  Host exiting or entering onto worlds like our chart plates, and various financial type buildings?
- **flow-lane-owner** - `219727747aad` 2026-09-03T19:48 - anchor `E57`
  - E57 split Flow by size: a whole episode's plates go to Gemini, a couple of plates we drive ourselves; E30 also says no agent owns a lane
  - > we'll let Gemini do theflow stuff lol, not your speciality.
- **gap-threshold** - `2d75469e6de3` 2026-09-04T15:49 - anchor `E38`
  - The 0.45 s gap cut was replaced by Wealth Logic's measured 0.30 s, cut at 0.8 of the gap (E38, 47 §5b M13). Gap cuts matched only 28-44% of authored scene starts
  - > here's their process:  Instead of:  1. Writing a script and arbitrarily assigning scene durations (e.g. "Scene 1: 6s, Scene 2: 8s"), or 2. Compressing and cutting out silences to make the audio artificially rapid-fire, then fighting timeline drift...  The natural acoustic gaps in the raw narration are the scene boundaries. Why This Works (The Physics of Attention)  1. The Transition Lives in the S
- **brand-line-placement** - `5cb85d7e1253` 2026-09-05T05:41 - anchor `f677a1f0fb3b`
  - Put the triad as the script's last line; overturned minutes later (triad cut, outro carries it), then E41 s2. The gap-cut plan is recorded (E41 s3/M13)
  - > for the eleven labs cut its because we took out spacing and such by compressing gaps, but also we plan not to do that now because we're applying the cuts into the space and then only trimming the tail is the plan right?  also, we should put ""not a panic. not a plot. mechanics." as the very last line, if we're over, we simply cut it., the ring being 1 line before still carries, it's basically the 
- **mount-start-word** - `741e694527b3` 2026-09-05T19:36 - anchor `898550a34df4`
  - Mount start on "here." overturned 7 min later: the dissolve and mount begin at "went home" (29 s9.31); the stepped fade survived
  - > that, and i think we should start the transition for the mount as soon as we say "here." at 1:03 and let the fade be more step motion
- **press-cue-level** - `c1e928f964c7` 2026-09-05T20:38 - anchor `a41b51383fee`
  - 11-12 dB under became 14-15 dB minutes later, then halved again to gain 0.08 (E44 s2a, R26-5)
  - > Man, Now THAT is a short! press cameras just need to be a tiny bit quieter, probably 11-12 db under instead of 9
- **caption-smooth-front** - `693af4500458` 2026-09-05T21:44 - anchor `d93bf481a6ca`
  - Smooth red front with words landing inside was rejected next round ("still not right"); the blend shipped, red box kept, no halo
  - > i think red is better, i think the halo is too much, and the way the marker reads still keeps the viewer hung on 1 word,i think it needs to flow smoothly, maybe even our advantage of using time is that we can stretch it smoothly, and land the captions inside of the marker instead of forcing the marker to wait on the captions
- **shorts-render-resolution** - `07cf2252b73e` 2026-09-06T21:05 - anchor `66e38be5bf08`
  - Operator floated 1080p; a minute later ruled "okay we keep the 1440" (tokyo-short-render.md: render once at 1440x2560, no 1080 variant)
  - > also, isn't rendering in 4k on shorts just wasted time? shouldn't we render at 1080p?
- **zoom-pan-frame** - `b2f76e255ba6` 2026-09-08T21:56 - anchor `E50`
  - Rejects zoom pan frame, but the operator's later words in E50 accept it: "zoom pan frame would work if the zoom is fast with a woosh" (the snap blur)
  - > no, it's not zoom pan frame
- **card-border-shadow** - `cae924e845ef` 2026-09-08T22:07 - anchor `95ed2a4a6613`
  - Shadow AND border was overturned: a thrown card has rounded corners, no black frame and the cream/deckle as its edge (CAPABILITIES card page)
  - > i think it neds both shadow and border maybe, and probably the cream edg should e a little bigger.  Also the holding page isn't supposed to show around it, it 's supposed to land as the card/dock size, then zoom to fill
- **chirp-voice-youtube** - `06cdf463a7b8` 2026-09-09T04:24 - anchor `E70`
  - E54 kept Chirp on YouTube to learn from real people. E70 (09-12) reversed it for YouTube (no plays); Facebook keeps Chirp and the bed stays -20
  - > iu accudebtakky ckised the eouside ub in the player. i think we should leave the music for now, i'm providing more actual content depth for them so i don't want too much musical interference.  I think i also have to keep the chirp voice. so far that's the feedback i've gotten from real people and were early in this journey and changing voice is cheap. wel'll try out the chirp voice and collect rea
- **stop-drawing-rings** - `fda38012ef0d` 2026-09-09T14:06 - anchor `a6ba1f2e1bc0`
  - The blanket "stop drawing rings" was narrowed two hours later: a ring keeps one use, circling a number or point on a chart (E56)
  - > Looks good, except I think drawing the ring on the wafer is dumb. if that wafer is going to do anything we should give it a light shimmer or a spotlight .  We have to stop drawing "rings" or circles on everything - that's just a cheap call-out mechanism, not a high quality animation
- **dip-default** - `e438b2c38e68` 2026-09-12T02:10 - anchor `d4c276b0ea71`
  - "No dip by default at all" was narrowed minutes later: the dip stays the default when the world actually changes, just never for a dock (E47 corrected)
  - > i think we shuld just not do it at that default at all though, that's how we have hidden bad frames that have to be manually deteced.

