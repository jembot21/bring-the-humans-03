# AI gue baru menang duit — session 1 complete

This directory contains the recovered first-session work for make.fun bounty
`bring-the-humans-03`: fresh official assets, their provenance and rules,
the existing 30-second storyboard, and sample renders of its first eight seconds.
The full video and audio belong to session 2. Nothing has been posted.

## Reproduce the samples

Requires Python 3 and Pillow (verified with Pillow 10.2.0).
Run from the repository root:

```sh
python3 video/source/render_frames.py
python3 video/source/verify_samples.py
```

The default writes twelve native **1080 × 1920** PNGs to `frames-test/`.
`frame-0000.png` proves the first frame; `frame-0030.png` shows the rolling
counter; `frame-0047.png` shows `$100.00`; `frame-0060.png` is the mascot cut;
`frame-0090.png` and `frame-0165.png` show the other subtitle beats;
`frame-0210.png` shows the submitted bounty check.

To choose other samples from scenes 1–2:

```sh
python3 video/source/render_frames.py --frames 0 15 47 60 90 165 239
```

Frame intervals are half-open at 30 fps: scene 1 is `[0, 60)`;
scene 2 is `[60, 240)`. The renderer accepts at most 60 samples per command,
rejects other scenes, and restricts outputs to `video/`. It has no full-video
or posting command. Restore the default samples before running verification,
which expects the boundary samples listed above.

## Official assets and evidence

- `assets/manifest.json` and `assets/llms.txt` are the complete current pack
  fetched in the recovery session with a freshness query; read both in full.
- `PRESS.md` quotes the authoritative badge/field values and records every
  downloaded body, including older responses retained with `-initial` names.
- `assets/fetch-log.json` includes exact source/request URLs, fetch times,
  bytes and SHA-256 hashes. HTTP header files belong to the same requests.
- `assets/press-lock.json` preserves the manifest-derived specifications and
  the selected image entries for session 2. The renderer checks the actual
  files directly against the full manifest, including all image hashes.
- `frames-test/validation.json` records each sample's subtitle, layout,
  animation state, source hashes and output hash.
- `frames-test/verification.json` records checks on the saved PNGs: native
  dimensions, exact opaque badge pixels, clearance, safe text, subtitle
  boundaries, stable hook and counter settlement.
- `frames-test/REVIEW.md` records the actual visual inspection.

The badge is the untouched full-frame PNG composited at **(0, 0)** as the
last layer at **100%**, retaining its built-in **(120, 272, 330, 128)** box.
The mascot illustration already contains a laptop; its complete drawing is
scaled proportionally and placed on an original desk. The adjacent submission
card avoids painting over the mascot. The official end card is downloaded,
hash-checked and retained intact; it is not rendered in this session.

The renderer intersects the storyboard's safe region with the manifest's
TikTok/Reels safe zone. It therefore uses **x 120…888, y 269…1248** for
essential text, with subtitles in **(144, 1106)–(864, 1232)**. This is the one
layout correction to the restarted session's plan.

## Refreshing the assets later

```sh
python3 video/source/fetch_press.py
```

This downloads both documents and the three chosen PNGs again, using the
manifest's exact source URLs with a unique query to bypass older cached
responses. It rejects image bytes that differ from the current manifest and
appends to the fetch log. After a refresh, reread both documents, reconcile
`PRESS.md` and `press-lock.json` with any changed rules, and regenerate/review
the samples. A refresh does not silently approve new brand rules.

## Session 2 handoff

Implement scenes 3–6, produce Indonesian voice/music/effects, and assemble
the full 900-frame video. Keep the badge until the end card starts at frame
810, then remove it. Use the official static magenta card for the storyboard's
three-second last slide, adding only `8vr38xr3` in its prescribed field.
Fetch and license JetBrains Mono Bold or Inter Bold before drawing that code;
the bundled counter font is not a permitted substitute for the referral field.
The guide's transparent-video and ffmpeg recipe is also saved in `assets/llms.txt`
for reference; do not substitute its timing for the static-card storyboard.
