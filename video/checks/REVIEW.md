# Final local delivery review — session 3

The master passed the requested visual checks. No renderer or asset fixes and
no master re-render were needed. The final master remains the session-2 file:
`video/out/makefun-ad-a.mp4`, 1080 × 1920, 30 fps, 900 frames, 30.000 seconds.
Its SHA-256 is
`de1667ef2fb8b983dcfbb4fd06f74670da20fa81d258872a1fe85877e5d6f0cd`.

These PNGs were extracted from the encoded master with FFmpeg, then each was
opened and visually inspected:

| Time / frame | Extracted file | Inspection result |
|---|---|---|
| 0.000 s / 0 | [master-00.000s.png](master-00.000s.png) | PASS: the official badge is already visible; the complete exact hook “AI GUE BARU SAJA MENANG $100.” and opening subtitle are legible. |
| 0.500 s / 15 | [master-00.500s.png](master-00.500s.png) | PASS: badge and giant hook remain clear; opening subtitle is readable. Counter digits are rolling as planned. |
| 5.000 s / 150 | [master-05.000s.png](master-05.000s.png) | PASS: the official mascot and laptop, adjacent bounty submission card and “Kenalin, ini agent AI gue.” subtitle are clear; content leaves the badge clear. |
| 12.000 s / 360 | [master-12.000s.png](master-12.000s.png) | PASS: all three bounty amounts, board title and “ngerjain bounty — yang menang” subtitle are legible; essential text remains inside the safe area. |
| 20.000 s / 600 | [master-20.000s.png](master-20.000s.png) | PASS: waking person and phone read clearly; “Dia yang kerja.” subtitle is readable and inside the safe area; badge is unobstructed. |
| 25.000 s / 750 | [master-25.000s.png](master-25.000s.png) | PASS: exact CTA and matching subtitle are readable, inside the safe area and clear of the badge. |
| 29.000 s / 870 | [master-29.000s.png](master-29.000s.png) | PASS: the official referral end card fills the entire frame; “8vr38xr3” is complete and legible inside its field; the separate badge and subtitles are absent as planned. |
| 29.967 s / 899 | [master-29.967s.png](master-29.967s.png) | PASS: the actual final frame holds the complete referral end card and readable code. |

The source badge, end card and mascot hashes and dimensions match the fresh
press manifest. Current production source hashes and the master hash match the
render report. All 900 production frame records were checked for the exact
subtitle cues, essential text bounds **(120, 269)–(888, 1248)** and **24 px**
badge clearance. The eight inspected frames were also reproduced from the
matching renderer to confirm native badge composition and that the end card is
modified only inside its code field. The full code is present from frame 838
and held to frame 899. See [layout-and-assets.json](layout-and-assets.json).

The preview was rendered from this verified master with Lanczos scaling of
the complete frame to 720 × 1280, H.264 at 1000 kb/s CBR, original AAC audio
stream copy and MP4 faststart. File: `video/out/makefun-ad-a-preview.mp4`.
Size: **4,508,146 bytes / 4.51 MB**. Duration and frame count remain **30.000
seconds / 900 frames at 30 fps**. All six corresponding preview frames at
0.5, 5, 12, 20, 25 and 29 seconds were opened and passed the same readability
checks; their PNGs are saved here as `preview-*.png`.

Both complete video/audio files decoded without FFmpeg errors. All **1,408**
AAC packet payload hashes, timestamps and durations are identical between
master and preview, confirming that the preview keeps exactly the same audio.
See [preview-verification.json](preview-verification.json) and
[preview-ffprobe.json](preview-ffprobe.json).

Video deviations from the storyboard: **no deviations**. This review covers
local deliverables; nothing was uploaded or posted. The human's posting
instructions and exact caption are in [HANDOFF.md](../HANDOFF.md).
