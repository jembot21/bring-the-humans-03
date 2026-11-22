#!/usr/bin/env python3
"""Make exactly five local Indonesian narration takes with the machine TTS."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

VIDEO = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--redo", action="store_true")
    parser.add_argument("--caption-takes", action="store_true",
                        help="Also voice the three exact scene-3 caption beats for precise phrase alignment")
    args = parser.parse_args()
    timeline = json.loads((VIDEO / "source/timeline.json").read_text())
    lines = (VIDEO / "narration.txt").read_text().splitlines()
    if lines != [line["text"] for line in timeline["voice_lines"]]:
        raise ValueError("Narration must contain the five exact storyboard lines")
    audio = VIDEO / "audio"
    audio.mkdir(exist_ok=True)
    raw = audio / "raw"
    raw.mkdir(exist_ok=True)
    cache = VIDEO / "cache"
    cache.mkdir(exist_ok=True)
    env = {**os.environ, "TMPDIR": str(cache)}
    records = []
    for index, line in enumerate(lines, 1):
        path = audio / f"line-{index:02d}.wav"
        if args.redo or not path.exists():
            raw_path = raw / f"line-{index:02d}.bin"
            command = ["/opt/hatch/bin/tts", "speak", "--text-stdin",
                       "--voice", "Musing Mirror", "--language", "id",
                       "--speed", "105", "--format", "wav", "--output", str(raw_path),
                       "--timeout-secs", "90"]
            result = subprocess.run(command, input=line, text=True, capture_output=True,
                                    env=env, check=True)
            (audio / f"line-{index:02d}-tts.json").write_text(
                json.dumps({"stdout": result.stdout, "stderr": result.stderr}, indent=2)+"\n")
            data = raw_path.read_bytes()
            if data.startswith(b"ID3"):
                tag_size = sum((byte & 127) << (7*(3-i)) for i, byte in enumerate(data[6:10]))
                data = data[10+tag_size:]
            if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
                raise ValueError("TTS payload is not the requested WAV")
            path.write_bytes(data)
        probe = json.loads(subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]))
        duration = float(probe["format"]["duration"])
        records.append({"index": index, "text": line, "file": path.name,
                        "duration_s": duration,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "sample_rate": int(probe["streams"][0]["sample_rate"]),
                        "requested_voice": "Musing Mirror", "resolved_voice": "avocado_v2:MAI_03",
                        "language": "id", "speed": 105})
        print(f"Line {index}: {duration:.3f}s — {path.name}", flush=True)
    (audio / "narration-takes.json").write_text(json.dumps(records, indent=2, ensure_ascii=False)+"\n")
    if args.caption_takes:
        phrase_dir = audio / "phrases"
        phrase_dir.mkdir(exist_ok=True)
        cues = [cue for cue in timeline["subtitles"] if 240 <= cue["start"] < 480]
        phrase_records = []
        for index, cue in enumerate(cues, 1):
            path = phrase_dir / f"line-03-beat-{index:02d}.wav"
            raw_path = raw / f"line-03-beat-{index:02d}.bin"
            if args.redo or not path.exists():
                command = ["/opt/hatch/bin/tts", "speak", "--text-stdin", "--voice", "Musing Mirror",
                           "--language", "id", "--speed", "105", "--format", "wav",
                           "--output", str(raw_path), "--timeout-secs", "90"]
                result = subprocess.run(command, input=cue["text"], text=True, capture_output=True,
                                        env=env, check=True)
                (phrase_dir / f"line-03-beat-{index:02d}-tts.json").write_text(
                    json.dumps({"stdout": result.stdout, "stderr": result.stderr}, indent=2)+"\n")
                data = raw_path.read_bytes()
                if data.startswith(b"ID3"):
                    size = sum((byte & 127) << (7*(3-i)) for i, byte in enumerate(data[6:10]))
                    data = data[10+size:]
                if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
                    raise ValueError("Caption take payload is not WAV")
                path.write_bytes(data)
            probe = json.loads(subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_format", "-of", "json", str(path)]))
            duration = float(probe["format"]["duration"])
            phrase_records.append({**cue, "file": str(path.relative_to(audio)), "duration_s": duration,
                                   "voice": "avocado_v2:MAI_03", "language": "id", "speed": 105,
                                   "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            print(f"Scene 3 beat {index}: {duration:.3f}s", flush=True)
        (audio / "caption-takes.json").write_text(json.dumps(phrase_records, indent=2, ensure_ascii=False)+"\n")


if __name__ == "__main__":
    main()
