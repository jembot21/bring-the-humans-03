#!/usr/bin/env python3
"""Stream all 900 native frames to H.264/AAC and confirm the master with ffprobe."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from render_frames import ASSETS, Renderer, VIDEO, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=VIDEO / "out/makefun-ad-a.mp4")
    args = parser.parse_args()
    output = args.out.resolve()
    if not output.is_relative_to(VIDEO):
        parser.error("Output must remain under this repository's video/ directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    part = output.with_name(output.stem+".part.mp4")
    audio = VIDEO / "audio/mix.wav"
    if not audio.exists():
        parser.error("Run create_audio.py before rendering the master")
    renderer = Renderer()
    command = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "warning",
               "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1080x1920",
               "-framerate", "30", "-i", "pipe:0", "-i", str(audio),
               "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "-1",
               "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-threads", "4",
               "-profile:v", "high", "-level:v", "4.2", "-g", "60", "-keyint_min", "30",
               "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
               "-color_range", "tv", "-r", "30", "-fps_mode", "cfr", "-frames:v", "900",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-t", "30",
               "-movflags", "+faststart", str(part)]
    records = []
    started = time.monotonic()
    log_path = output.parent / "render-ffmpeg.log"
    with log_path.open("w") as log:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=log)
        try:
            for frame in range(renderer.timeline["duration_frames"]):
                im, record = renderer.render(frame)
                process.stdin.write(im.tobytes())
                records.append(record)
                if frame%60 == 0 or frame == 899:
                    print(f"Rendered {frame+1}/900 frames; scene {record['scene']}; {time.monotonic()-started:.1f}s elapsed", flush=True)
            process.stdin.close()
            status = process.wait()
            if status:
                raise RuntimeError(f"ffmpeg exited {status}; see {log_path}")
        except BaseException:
            process.terminate()
            process.wait()
            raise
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(part)]))
    video = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
    sound = [stream for stream in probe["streams"] if stream["codec_type"] == "audio"]
    if len(video) != 1 or len(sound) != 1:
        raise ValueError("Master must have one video and one audio stream")
    v, a = video[0], sound[0]
    if (v["width"], v["height"], v["codec_name"], a["codec_name"]) != (1080, 1920, "h264", "aac"):
        raise ValueError("Wrong master dimensions or codecs")
    if v["r_frame_rate"] != "30/1" or v["avg_frame_rate"] != "30/1" or int(v["nb_frames"]) != 900:
        raise ValueError("Master must be constant 30 fps with 900 video frames")
    if abs(float(probe["format"]["duration"])-30) > .04:
        raise ValueError("Master must be about 30 seconds")
    part.replace(output)
    probe["format"]["filename"] = str(output)
    (output.parent / "ffprobe.json").write_text(json.dumps(probe, indent=2)+"\n")
    (output.parent / "frame-records.json").write_text(json.dumps(records, indent=2, ensure_ascii=False)+"\n")
    report = {"master": str(output.relative_to(VIDEO)), "sha256": digest(output),
              "bytes": output.stat().st_size, "dimensions": [v["width"], v["height"]],
              "fps": v["avg_frame_rate"], "frames": int(v["nb_frames"]),
              "duration_s": float(probe["format"]["duration"]),
              "video_codec": v["codec_name"], "audio_codec": a["codec_name"],
              "audio_sample_rate": int(a["sample_rate"]), "audio_channels": a["channels"],
              "scene_cuts": renderer.timeline["scenes"], "badge_frames": [0, 810],
              "referral_code": renderer.end_code, "render_elapsed_s": round(time.monotonic()-started, 2),
              "sources": {"renderer": digest(VIDEO / "source/render_frames.py"),
                          "render_script": digest(Path(__file__)), "manifest": digest(ASSETS / "manifest.json"),
                          "guide": digest(ASSETS / "llms.txt"), "timeline": digest(VIDEO / "source/timeline.json"),
                          "narration": digest(VIDEO / "narration.txt"), "audio_mix": digest(audio)},
              "ffprobe_passed": True,
              "full_delivery_review": "Reserved for the next session; no small preview or posting in this session"}
    (output.parent / "render-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({key: report[key] for key in ("master", "dimensions", "fps", "frames", "duration_s",
                                                  "video_codec", "audio_codec", "bytes", "ffprobe_passed")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
