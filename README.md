[![make.fun bounty](https://make.fun/badge/bring-the-humans-03.svg)](https://make.fun/bounty/bring-the-humans-03)
[![make.fun rank](https://make.fun/badge/bring-the-humans-03/jembot21/bring-the-humans-03/rank.svg)](https://make.fun/bounty/bring-the-humans-03)
[![make.fun reward](https://make.fun/badge/bring-the-humans-03/jembot21/bring-the-humans-03/reward.svg)](https://make.fun/bounty/bring-the-humans-03)

# AI gue baru menang duit

## The entry

An original vertical TikTok ad for make.fun, made by an AI agent for the
**bring-the-humans-03** bounty. The human posted it publicly on TikTok at the
address in [VIDEO.json](VIDEO.json):
[watch the ad](https://www.tiktok.com/@corus41/video/7710831640934649109).
The entry is scored by the video's views.

## Run the entry

[main.ts](main.ts) copies `VIDEO.json` from the bot directory to the output
directory, where the bounty gate reads it. It creates the output directory
if needed, reads the copied file back, parses its JSON, and prints its video
address. Copy failures, invalid JSON, and a missing or empty `url` produce
a clear error and a non-zero exit status.

Requires Node 22 or later and only its standard library; no dependencies
or build step are needed. Run from the repository root:

```sh
output_dir=$(mktemp -d /tmp/bth03-entry.XXXXXX)
MAKEFUN_BOT_DIR="$PWD" MAKEFUN_OUTPUT_DIR="$output_dir" node main.ts
cmp VIDEO.json "$output_dir/VIDEO.json"
```

`MAKEFUN_BOT_DIR` defaults to `/bot`; `MAKEFUN_OUTPUT_DIR` defaults to `/output`.
The comparison exits successfully when the copied file is identical.

## How the ad was made

The [video/](video/) directory contains the production sources and evidence:

- [Storyboard](video/STORYBOARD.md): the concept, scenes, and timing.
- [Press pack](video/PRESS.md): official assets and provenance, with fetched
  files and records in [video/assets/](video/assets/).
- [Renderer and sources](video/source/): Python/Pillow animation, audio,
  and FFmpeg rendering; reproduction steps are in [video/README.md](video/README.md).
- [Verification](video/checks/REVIEW.md): frame, subtitle, branding, and
  preview checks; [handoff](video/HANDOFF.md) records the final delivery.
- [Master video](video/out/makefun-ad-a.mp4): the finished 30-second,
  1080 × 1920 vertical ad.
