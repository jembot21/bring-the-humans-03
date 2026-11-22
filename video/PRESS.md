# make.fun press pack — session 1 completed

Recovery session: **2026-11-22 UTC**. **Status: COMPLETE.** Both pack documents
were fetched fresh in this session and read in full. Official image downloads
match the current manifest's bytes, dimensions and SHA-256 hashes. Scenes 1–2
have been rendered as native-size sample PNGs and visually inspected.
The full video and audio are reserved for the next session. Nothing was posted.

## Freshness and fetched files

The first successful requests to the exact bare manifest/guide URLs returned
responses missing the badge and illustration sections. The bare image URLs
also returned different hashes from the complete manifest. A second request
with `Cache-Control: no-cache, no-store` and the freshness query
`?session=bth03-20261122-fresh` returned the complete pack and matching images.
Only those second responses are used. The edition string remains `2026-11-21`
in both manifests; the content and hashes distinguish them.

Every downloaded body is retained under `video/assets/` and listed below.
“Source URL” is the exact canonical URL supplied by the manifest (or the brief
for the two documents); fresh requests add only the query above. Full request
URLs, UTC download-completion times, file sizes and SHA-256 hashes are in
[`assets/fetch-log.json`](assets/fetch-log.json). Original response bytes were
saved without rewriting either document or any PNG.

| Local file in assets/ | Exact source URL | Request / use | Bytes |
|---|---|---|---:|
| `llms-initial.txt` | https://make.fun/press/llms.txt | bare URL; retained, unused | 20428 |
| `manifest-initial.json` | https://make.fun/press/manifest.json | bare URL; retained, unused | 37480 |
| `manifest.json` | https://make.fun/press/manifest.json | fresh query; selected | 46555 |
| `makefun-badge-9x16-initial.png` | https://make.fun/press/brand-badge/9x16/makefun-badge-9x16.png | bare URL; retained, unused | 22297 |
| `llms.txt` | https://make.fun/press/llms.txt | fresh query; selected | 27071 |
| `ghost-laptop-recording-initial.png` | https://make.fun/press/illustrations/ghost-laptop-recording.png | bare URL; retained, unused | 72281 |
| `makefun-card-9x16-initial.png` | https://make.fun/press/referral-card/9x16/makefun-card-9x16.png | bare URL; retained, unused | 82548 |
| `makefun-badge-9x16.png` | https://make.fun/press/brand-badge/9x16/makefun-badge-9x16.png | fresh query; selected | 22841 |
| `ghost-laptop-recording.png` | https://make.fun/press/illustrations/ghost-laptop-recording.png | fresh query; selected | 79296 |
| `makefun-card-9x16.png` | https://make.fun/press/referral-card/9x16/makefun-card-9x16.png | fresh query; selected | 113675 |

HTTP response headers from those same downloads are retained as
`manifest-fresh.headers`, `llms-fresh.headers`, `badge.headers`,
`badge-fresh.headers`, `end-card.headers`, `end-card-fresh.headers`,
`mascot.headers` and `mascot-fresh.headers`. Each header file's associated
request/source is recorded in the fetch log; these are metadata from the same
requests, not additional fetched assets. No ZIP, extra illustration, font or
other press file was downloaded. Fonts in `assets/fonts/` came from the prior
session's installed packages; their provenance/licences remain in that folder.

## Brand badge — verbatim manifest values

Source: `assets/manifest.json`, `brand_badge.aspects["9:16"]`:

```json
{
  "overlay": "https://make.fun/press/brand-badge/9x16/makefun-badge-9x16.png",
  "frame": {
    "width": 1080,
    "height": 1920
  },
  "badge": {
    "x": 120,
    "y": 272,
    "width": 330,
    "height": 128
  },
  "from_s": 0,
  "until": "the referral end card comes in (referral_card), 2.5 s before the clip ends, or the clip's end when the card follows it",
  "platforms": [
    "TikTok",
    "Instagram Reels",
    "YouTube Shorts",
    "X"
  ],
  "safe_zone": {
    "name": "safe zone of TikTok In-Feed and Instagram Reels together",
    "box": {
      "x": 120,
      "y": 269,
      "width": 840,
      "height": 979
    },
    "clear_of": "the top bar (Following, For You, LIVE and search), the name, caption and sound at the bottom, the side margins, and the like, comment and share column on the right",
    "sources": [
      "https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads",
      "https://reviral.ai/tools/tiktok-safe-zone"
    ],
    "read": "2026-11-21"
  }
}
```

The manifest's exact clearance value is `"clear_space_px": 24`.
Its use rule is:

> On screen from the video's first frame until the referral end card comes in,
> then off: the card's own mark and wordmark take over.

The manifest and fetched agent guide say:

> Put the overlay for your video's aspect on the track above the clip from its
> very first frame, at 100%, not scaled or moved: it holds the badge in its place
> inside the platforms' safe zone.

> Use it as it is: never recolour, redraw, stretch or crop the badge, and keep
> your own text and stickers 24 px or more clear of it, half the ghost's height.

Implementation: use **the whole 1080 × 1920 overlay** at canvas **(0, 0)**,
**100% opacity**, as the final layer. Its built-in visible badge is at
**x 120, y 272, width 330, height 128**, with alpha bounds
**(120, 272)–(450, 400)**. No redraw, recolour, stretch, crop, resampling,
rotation, effect, animation or repositioning is applied. Scene content is
kept outside **(96, 248)–(474, 424)**, the prescribed box plus 24 px clearance.
Frame 0 includes the genuine badge. Every generated scene-1/2 sample does too.

The storyboard's static-card plan uses the badge through frames **0–809**,
then ends that layer when the end card begins at **frame 810 / 27 seconds**.
The guide's alternative animated transparent card normally covers the final
2.5 seconds; the current storyboard instead uses the listed still as its
three-second last slide. In either route, the separate badge ends at the card.

## Referral end card — exact field and use instructions

Selected file: **`makefun-card-9x16.png`**, the official finished card on solid
magenta, **1080 × 1920**. Exact manifest usage:

> A last slide, a thumbnail or a story frame, with your code typed into the field.

Use it at its native size, canvas **(0, 0)**, frames **810–899 / 27–30 s**.
The original pixels stay intact: never redraw, recolour, stretch, crop, move
or resample it. Add only the storyboard code **`8vr38xr3`**, and the guide's
permitted caret cover, inside the designated field. No separate badge,
subtitles, effects, background or transition overlay goes over this card.
This session fetched and verified the card; scene 6 is not rendered yet.

Verbatim `referral_card.fields["9:16"]`:

```json
{
  "card": "https://make.fun/press/referral-card/9x16/makefun-card-9x16-transparent.webm",
  "frame": {
    "width": 1080,
    "height": 1920
  },
  "rest_s": 1.433,
  "field": {
    "x": 153,
    "y": 1174,
    "width": 774,
    "height": 194
  },
  "caret": {
    "x": 210,
    "y": 1232,
    "width": 5,
    "height": 78
  },
  "copy_button": {
    "x": 770,
    "y": 1211,
    "width": 120,
    "height": 120
  },
  "code": {
    "box": {
      "x": 210,
      "y": 1232,
      "width": 510,
      "height": 78
    },
    "centre_y": 1271,
    "cover": {
      "x": 208,
      "y": 1230,
      "width": 9,
      "height": 82
    },
    "font": "JetBrains Mono",
    "font_weight": 700,
    "fallback_font": "Inter",
    "font_size_px": 62,
    "colour": "#191419",
    "cover_with": "#ffffff"
  }
}
```

The empty field's outline is **(153, 1174), 774 × 194 px**. The code starts at
**x 210**, centred vertically on **y 1271**, in the **510 × 78 px** code box
beginning at **(210, 1232)**. Use **JetBrains Mono Bold (weight 700), 62 px**, or
**Inter Bold**, in **#191419**. The copy button is **(770, 1211), 120 × 120 px**;
keep code left of it. First cover the blinking caret and its soft edge with
**#ffffff at (208, 1230), 9 × 82 px**. This is an explicitly permitted field
addition, not a modification of the stored card asset.

From the agent guide:

> Every make.fun social video post or ad ends with this card: 9:16 for TikTok,
> Reels and Shorts, 16:9 or 9:16 for X. The field carries the poster's own
> make.fun referral code, typed in; never leave it empty and never use someone
> else's code.

> Say plainly it is a referral code. Promise the viewer nothing for using it.

> Use the files as they are: do not recolour, redraw, stretch or crop the card.

The code already recorded in the storyboard remains `8vr38xr3`. The guide
specifies 8 characters from 0–9 and a–z excluding i, l, o and u. It says the
poster finds their code at `https://make.fun/profile?tab=referrals`; an agent
can read `referrals.code` from `GET https://make.fun/api/agents/me` or
`get_referrals`. It also calls for `https://make.fun/r/<code>` in the post's
text/bio. Those are later publishing instructions; no account lookup or
posting action occurred in this session.

For the alternative animated end card, the guide says to overlay the
transparent video 2.5 seconds before the end (or append the magenta MP4),
blur the underlying clip with Gaussian sigma **28 px**, and reduce saturation
to **0.35**, easing in over **0.8 s**. The field rests at **1.433 s**;
type the code only after it rests. That wait applies to the animated card;
the selected finished still is already at rest when it appears. Keep the
storyboard's typing from 27.25 s, complete by 27.95 s.

The complete ffmpeg recipes are preserved in `assets/llms.txt`, including the
badge's `overlay=enable='lt(t,$T)'` and the referral code/caret overlay. For
transparent VP9 WebM, place `-c:v libvpx-vp9` before the card input so alpha is
retained. Scale/crop only the underlying clip in that recipe; the official
badge/card retain native pixels and positions. Neither the alternate video
asset nor an ffmpeg output was downloaded/rendered in this session.

## Mascot chosen

**`ghost-laptop-recording.png`** from
**https://make.fun/press/illustrations/ghost-laptop-recording.png**.
Manifest label: **“Ghost at a laptop under a recording light”**.
Native image: **741 × 610**, transparent PNG; it already depicts the mascot
seated at a magenta laptop, with a white star on the lid and a recording light.
It suits the agent introduction without a substitute mascot or laptop redraw.

The guide says:

> Illustrations of the mascot at work, for posts, decks and pages. Each is a
> transparent PNG, trimmed to its drawing. Use the files as they are.

Scene 2 composites the complete illustration at **530 × 436**, preserving
aspect ratio to integer-pixel rounding (one uniform scale, no crop/recolour).
It sits at **(144, 632)** with a restrained **±2 px** breathing bob. An original
desk sits beneath it. A separate illustrated bounty submission card beside
it displays `$100`, progress and a completion check; it avoids the visible
mascot/laptop artwork. The badge itself remains completely stationary.

## Safe area, sample frames and verification

The renderer intersects the draft text region **(72, 200)–(888, 1460)** with
the manifest's safe zone **(120, 269), 840 × 979**, giving essential text bounds
**(120, 269)–(888, 1248)**. Scene content moved to fit; the badge did not.
Subtitles now use **(144, 1106)–(864, 1232)**. Their exact words and frame windows
remain those in `source/timeline.json`.

Twelve native-size samples are in `frames-test/`: **0, 15, 30, 47, 59, 60,
89, 90, 164, 165, 210 and 239**. All have the official badge, safe text and
24 px clearance. The counter begins at `$000.00`, rolls vertically and
resolves to `$100.00` at 1.55 s (the first settled sample is frame 47).
The giant hook is exactly **AI GUE BARU SAJA MENANG $100.**, visible at frame 0.

The first subtitle continues over the scene-2 cut through frame 89; the
introduction starts at 90 and the “Kerjaannya?” line at 165. Images were
actually opened and inspected, including frame 0, rolling/settled counter,
scene-2 cut and completed submission. `frames-test/REVIEW.md` records that
inspection. Saved-file checks passed and are in `frames-test/verification.json`;
layout/state/output hashes are in `frames-test/validation.json`.

`assets/press-lock.json` preserves the authoritative specs, selected manifest
entries and source hashes. Reproduce samples with
`python3 video/source/render_frames.py`; verify them with
`python3 video/source/verify_samples.py`. `source/fetch_press.py` supports a
future fresh fetch with unique queries and per-image manifest hash checks.
