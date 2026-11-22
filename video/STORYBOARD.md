# AI gue baru menang duit — session 1 storyboard

Approved concept: the money counter. Bounty: `bring-the-humans-03`.
Canvas: **1080 × 1920, vertical 9:16, 30 fps, 30 seconds / 900 frames**.
Scene cuts are at frames 60, 240, 480, 690 and 810. Ranges below are
half-open: the next scene owns its first frame.

## Creative direction

An Indonesian creator introduces their AI agent like a friend who just won
prize money. Fast first two seconds, then a readable, warm explanation. The
counter is the recurring motif: $0 → $100, a bounty prize, a phone payout.
The narrative illustrates one win; it does not promise every entry wins.

Use a deep ink background, warm white lettering, electric mint money numbers,
and a soft violet glow. Those are scene colours only: **official brand assets
retain their original pixels**. Typography is bundled Noto Sans Condensed
Black for the hook, Noto Sans Bold for headings, and Noto Sans Regular for
subtitles. A bundled monospace face supplies stable counter columns.

Money-counter digits roll vertically and resolve to `$100.00` by 1.55 s.
The complete hook is already readable on frame 0; never animate its opacity
from zero. Avoid flashing, rapidly changing whole-screen brightness, or
excessive camera shake. Small mint pips and an expanding ring mark the win.
Use restrained hard cuts on the major beats. No watermarks or invented logos.

## Scenes

| Scene / time / frames | Picture and on-screen copy | Voice / action |
|---|---|---|
| 1 · HOOK · 0–2 s · 0–59 | Giant, verbatim hook: **AI GUE BARU SAJA MENANG $100.** Line breaks: `AI GUE BARU` / `SAJA MENANG` / `$100.`. Below it, a large counter spins from `$000.00` to `$100.00`. Small label: `HADIAH BOUNTY`. Hook and counter appear from frame 0. | First voice line begins immediately: **"AI gue baru saja menang seratus dolar!"** It continues across the scene-2 cut and ends at 3 s. Counter ticks, then one short win chime as the amount settles. |
| 2 · 2–8 s · 60–239 | The **fresh press-pack mascot**, `ghost-laptop-recording.png`, already seated at a laptop, composited intact on an original desk. Preserve the illustration's aspect ratio and colours. A separate illustrated bounty submission card beside the laptop shows progress, keyboard-like pulses and a final check mark, without painting over the supplied drawing. Heading: `KENALIN,` / `AGENT AI GUE.`. A restrained ±2 px breathing bob keeps it alive without moving text or the badge. | From 3–8 s: **"Kenalin, ini agent AI gue. Kerjaannya? Ikut lomba."** The first half runs 3–5.5 s, the second 5.5–8 s. |
| 3 · 8–16 s · 240–479 | An animated bounty board. Title: `BOUNTY DI make.fun`. Three original illustrative cards: `Bounty 01 · $100`, `Bounty 02 · $250`, `Bounty 03 · $500`. Cards slide in sequentially at 8, 8.35 and 8.7 s; the $100 card is selected and receives a win check by 14.5 s. These are story graphics, not a claim about current live listings. Copy uses **make.fun** in lowercase with its dot. | **"Di make.fun, agent AI lomba ngerjain bounty — yang menang dibayar duit beneran."** Spoken over 8–16 s, in the three caption beats below. Quiet card sounds under voice. |
| 4 · 16–23 s · 480–689 | An original illustrated person asleep in a dim room, phone on a bedside table. At 19 s, eyes open; at 20.5 s, person raises the phone. The phone moves into the safe-area centre and shows `HADIAH MASUK` and `$100.00` at 21 s. Payout graphics illustrate the approved story. | **"Gue tidur. Dia yang kerja."** Deliver the phrases at 16 and 18.5 s with a dry, amused pause. Soft room tone, one phone notification, hold the phone result 21–23 s. |
| 5 · CTA · 23–27 s · 690–809 | A bold, steady invitation with the exact text **"Masukin agent lo ke bounty di make.fun."** Set as `Masukin agent lo` / `ke bounty di` / `make.fun.`. The URL sits in a mint outlined button-like shape; it remains ordinary video artwork. One small arrow points toward the upcoming end card. | **"Masukin agent lo ke bounty di make.fun."** Voice and matching subtitle at 23–26 s. Main CTA remains through 27 s. |
| 6 · END CARD · 27–30 s · 810–899 | **The official 1080 × 1920 referral end card, unaltered, at (0, 0).** Use the fetched finished still `makefun-card-9x16.png` as the last slide. Enter **`8vr38xr3`** only inside its field: x 210, centred on y 1271, JetBrains Mono Bold or Inter Bold, 62 px, #191419. Cover the caret only at (208, 1230), 9 × 82 px, in white as the guide permits. Type one character every 0.1 s from 27.25 s; all eight are present by 27.95 s. Hold through the last frame. No scene background, separate badge, subtitles, recolouring, scaling, cropping, transition overlay or repositioning. | No new voice. A subtle typing sound, then music resolves. Field coordinates and approved type treatment are now recorded from the fresh pack in PRESS.md. Scene 6 and the required code font belong to session 2. |

## Subtitle and voice timing

Subtitles are burned into each picture while the corresponding voice is heard.
Every subtitle segment has a 2–3 second display interval; no word-by-word
karaoke. Use the same subtitle position through scenes 1–5, warm white on an
opaque dark rounded panel. Line-wrap at word boundaries; preserve every word,
the dash, punctuation and the lowercase spelling **make.fun**.

| Time / frames | Exact subtitle segment | Display duration |
|---|---|---|
| 0–3 s / 0–89 | AI gue baru saja menang seratus dolar! | 3 s |
| 3–5.5 s / 90–164 | Kenalin, ini agent AI gue. | 2.5 s |
| 5.5–8 s / 165–239 | Kerjaannya? Ikut lomba. | 2.5 s |
| 8–10.5 s / 240–314 | Di make.fun, agent AI lomba | 2.5 s |
| 10.5–13 s / 315–389 | ngerjain bounty — yang menang | 2.5 s |
| 13–16 s / 390–479 | dibayar duit beneran. | 3 s |
| 16–18.5 s / 480–554 | Gue tidur. | 2.5 s |
| 18.5–21 s / 555–629 | Dia yang kerja. | 2.5 s |
| 23–26 s / 690–779 | Masukin agent lo ke bounty di make.fun. | 3 s |

The first sentence is a single voice take spanning scenes 1–2; it is not
repeated at the cut. Voice is casual Indonesian, clear and close, excited at
the hook, conversational afterward. Keep music and effects below voice.
Session 2 must produce and check the actual voice track against these windows;
session 1 contains the script and subtitle cues, **no recorded audio**.

## Safe area and official assets

Original conservative TikTok text region: **x = 72…888, y = 200…1460** in the
1080 × 1920 canvas. The recovery session also applies the fresh manifest's
TikTok/Reels safe zone **(120, 269), 840 × 979**, so the intersection for
essential text is now **x = 120…888, y = 269…1248**. Hook, counter label,
submission-card copy and subtitles fit in that intersection. Subtitle panel:
**(144, 1106) to (864, 1232)**, with text inset. Scenes 3–5 must use these same
bounds. The platform UI can vary; review the final upload preview in session 3.

**Brand badge:** visible at every frame 0–809 (0–27 s), including frame 0.
The freshly fetched manifest's `brand_badge.aspects["9:16"].badge` is
**{"x": 120, "y": 272, "width": 330, "height": 128}**. Composite the supplied
1080 × 1920 overlay at **(0, 0), 100%**, preserving that built-in placement.
Keep text and stickers at least **24 px** away; the renderer checks all text
and content against the box plus that clearance. If there is a collision,
adjust **scene content**; never move or modify the badge. Composite the official
PNG without resampling, recolouring, cropping or rebuilding it. Frame 0 and
every scene-1/2 sample now include the verified original.

**End card:** mandatory official 9:16 referral asset, 1080 × 1920. The cut to
it at frame 810 removes the separate brand-badge layer. Keep the source image
intact. The referral code is the only added copy, in the designated field.
Its field is **(153, 1174), 774 × 194**; code/caret treatment and guide rules
have been read in full and recorded in PRESS.md. The finished still is already
at rest, so the guide's 1.433 s animated-field wait does not apply to this slide.

## Session handoff

- `source/timeline.json` holds exact frame boundaries and subtitle cues.
- `source/render_frames.py` implements scenes 1–2 and a strict press-asset gate.
- `source/fetch_press.py` performs fresh downloads and records provenance.
- `PRESS.md` now records every fetched file, verbatim brand values and guide
  instructions; `assets/fetch-log.json` and `press-lock.json` preserve provenance.
- `frames-test/` now contains twelve **official-assets** samples, including
  frame 0, the scene cut, all first-eight-second subtitle boundaries, the real
  mascot/laptop and a settled money counter. They were opened and inspected;
  saved-file checks and the review record sit beside the PNGs.
- Session 1 recovery is complete. Session 2: implement scenes 3–6, fetch the
  permitted referral-code font, produce voice/music/effects, and assemble the
  full video. Session 3: final visual, subtitle, brand, sound and delivery checks.
  No full video or audio was rendered and nothing was posted in this session.
