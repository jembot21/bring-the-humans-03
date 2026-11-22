# AI gue baru menang duit — master

The complete original TikTok ad for make.fun bounty `bring-the-humans-03` is
`out/makefun-ad-a.mp4`: 1080 × 1920, constant 30 fps, 900 frames / 30 seconds,
H.264 High profile with 48 kHz stereo AAC audio. All work stays in this
repository. Nothing has been posted. The next session owns the full visual,
subtitle, listening and delivery review, plus the small preview file.

## Reproduce the master

Run from the repository root. Requires Python 3, Pillow, numpy, scipy,
ffmpeg/ffprobe and the machine's `/opt/hatch/bin/tts`. TTS requires network;
rendering and music synthesis use only local files.

```sh
python3 video/source/synthesize_narration.py --caption-takes
python3 video/source/create_audio.py
python3 video/source/render_master.py
```

Existing voice takes are reused. `--redo` explicitly regenerates them. The
five exact Indonesian lines are in `narration.txt`; the corresponding full
TTS takes are `audio/line-01.wav` through `line-05.wav`. All use language `id`,
requested voice **Musing Mirror**, resolved by the tool to
`avocado_v2:MAI_03`, at speed **105**. The service's original response bytes
are retained in `audio/raw/`; a prepended ID3 metadata tag is removed to make
valid PCM WAV files. Tool responses, durations and hashes are recorded.

`audio/processed/` contains the five arranged lines. The hook uses a
pitch-preserving time fit to finish at approximately 2.9 s, spanning the
scene-2 cut. Scenes 2 and 4 split in measured silent sentence pauses; their
phrases begin at 3, 5.5, 16 and 18.5 s. Scene 3 uses three additional exact
caption-beat takes from the same voice, at 8, 10.5 and 13 s, avoiding cuts
inside spoken words. The five complete original takes remain available.
CTA voice begins at 23 s. No scene cuts or drafted subtitle windows changed.
See `audio/narration-takes.json`, `caption-takes.json` and `mix-report.json`.

The original music is an 8-second, 120 BPM loop generated with seeded numpy
oscillators and noise: Cmaj7 / Am7 / Fmaj7 / G6, light plucks, bass and soft
percussion. It repeats quietly under the voice, ducks another 4 dB during
speech and resolves through the end card. Counter, card, payout and typing
sounds and room tone are synthesized too. No music or samples were downloaded.
`audio/music-loop.wav`, `audio/stems/` and the 30-second stereo `audio/mix.wav`
are retained. The mix uses two-pass loudness normalization.

## Six scenes and the official assets

`STORYBOARD.md` and `source/timeline.json` remain the creative and timing
sources. The six scenes start at 0, 2, 8, 16, 23 and 27 seconds. Subtitles are
burned in at their existing frame windows, preserving the exact wording,
punctuation and lowercase `make.fun`.

The renderer retains the existing first two scenes, then adds the sequential
bounty board with its $100 win check at 14.5 s; an original illustrated person
asleep, eyes opening at 19 s, raising the phone at 20.5 s and showing
`HADIAH MASUK` / `$100.00` at 21 s; and the exact steady CTA.

The press assets and documents are unchanged. `PRESS.md` records their exact
manifest values; `assets/fetch-log.json` and `assets/press-lock.json` retain
provenance. Source PNG hashes/dimensions are checked before every render.
The full 1080 × 1920 badge PNG is the final layer at **(0, 0), 100%**, on every
frame **0–809**, preserving its visible **(120, 272, 330, 128)** placement and
24 px clearance. Essential scene text uses **x 120…888, y 269…1248**; the
subtitle panel is **(144, 1106)–(864, 1232)**.

Frames **810–899** use the full official magenta referral card at its native
size and origin. Only **8vr38xr3** and the permitted white caret cover are
added inside its field. Code: JetBrains Mono Bold, 62 px, **#191419**, x **210**,
visible glyphs centred on y **1271**. Caret cover: **(208, 1230), 9 × 82 px**.
Typing is sampled at frame centres, one character per three frames from the
frame covering 27.25 s; all eight are present by **frame 838 / 27.933 s**, in
time for the 27.95 s deadline, and held through frame 899. No separate badge,
subtitle, effect or transition is drawn over the card. The unmodified font and
its SIL Open Font License/provenance are bundled in `assets/fonts/`.

## Render evidence and next-session handoff

`out/ffprobe.json` records both streams and the container metadata;
`out/render-report.json` records dimensions, codecs, frame count, duration,
source/master hashes and scene cuts. `out/frame-records.json` records all 900
frames' layout, subtitle and animation states. These are production records;
the full delivery review and listening check remain for the next session.

The original scene-1/2 samples and their previous review in `frames-test/`
remain intact. To render other native-size working stills without making a
preview video:

```sh
python3 video/source/render_frames.py --frames 0 47 60 263 435 480 570 630 690 810 817 838 899 --out video/cache/scenes
```

The renderer accepts up to 60 frames per still request, from all six scenes,
and restricts outputs to `video/`. `video/cache/` and Python bytecode are
ignored by git. `source/verify_samples.py` remains the earlier scene-1/2
saved-sample check. Full master visual/subtitle/brand/audio verification and
the small 720 × 1280 preview are the next session's work. No publishing or
posting command is part of this production pipeline.
