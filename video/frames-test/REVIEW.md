# Session 1 sample review — 2026-11-22 UTC

Status: **PASS for scenes 1–2 sample composition and official-asset integration.**
These are still samples of the first eight seconds, not a finished ad or an
audio/motion review of an encoded video.

## Images actually opened and inspected

| Image | What was checked | Result |
|---|---|---|
| `frame-0000.png` | Genuine badge from the very first frame; exact giant hook; `$000.00`; subtitle readability and margins | PASS |
| `frame-0030.png` | Counter digits at different vertical offsets; fixed headline and decimal; no badge/text collision | PASS |
| `frame-0047.png` | `$100.00` settled; small win ring/check/pips; badge still at native placement | PASS |
| `frame-0060.png` | Scene-2 cut; complete official ghost/laptop illustration; original desk and adjacent bounty card; first sentence still subtitled | PASS |
| `frame-0090.png` | `Kenalin, ini agent AI gue.` begins at 3 s; clear type and laptop composition | PASS |
| `frame-0165.png` | `Kerjaannya? Ikut lomba.` begins at 5.5 s; progress and keyboard-like pulses | PASS |
| `frame-0210.png` | Bounty progress full, `TERKIRIM` and check; mascot intact; subtitle and badge clear | PASS |

The original fetched `ghost-laptop-recording.png` was also opened before
composition. The original fetched `makefun-card-9x16.png` was opened to confirm
the finished magenta card, empty field, caret and copy button. It remains
unaltered in `assets/`; no scene-6 render or code overlay was produced yet.

## Corrections made during inspection

The draft subtitle panel was below the current press pack's TikTok/Reels safe
zone. It moved to **(144, 1106)–(864, 1232)**. All essential text now fits the
intersection **(120, 269)–(888, 1248)**. Scene headings start below the badge
and its 24 px clearance; the badge itself stayed at **(120, 272), 330 × 128**.

The counter's separately drawn decimal initially aligned to the tops of the
digits. It now shares their baseline, visibly giving `$000.00` / `$100.00`.
The final frame-0 and counter samples were regenerated and reopened after
this correction.

## Saved-file evidence

`verification.json` reports twelve native **1080 × 1920** samples checked:

- All opaque badge pixels match the supplied PNG exactly at their original
  coordinates; source hash and alpha bounds match the fresh manifest.
- Every recorded content box clears the badge by at least 24 px, and all
  essential text/panels are within the safe region.
- Subtitle words and boundary frames 0, 60, 89, 90, 164, 165 and 239 match the
  preserved timeline. The first sentence continues over the scene cut.
- The hook is pixel-stable from frame 0 through the sampled hook scene.
- The counter moves before settlement and holds the same `$100.00` digits
  across frames 47 and 59.

`validation.json` records all twelve output hashes, frame numbers, scene
states, text bounds and source hashes. Only the seven sample frames listed
above were visually opened; the remaining samples were checked by the
saved-file verifier. There is no encoded full-video, recorded voice or music
to assess in this session.
