#!/usr/bin/env python3
"""Check the saved sample PNGs against press pixels, safe bounds and subtitle cues."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops

VIDEO = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((VIDEO / "assets/manifest.json").read_text())
    timeline = json.loads((VIDEO / "source/timeline.json").read_text())
    report = json.loads((VIDEO / "frames-test/validation.json").read_text())
    badge = Image.open(VIDEO / "assets/makefun-badge-9x16.png").convert("RGBA")
    alpha = badge.getchannel("A")
    opaque = alpha.point(lambda a: 255 if a == 255 else 0)
    badge_rgb = badge.convert("RGB")
    spec = manifest["brand_badge"]["aspects"]["9:16"]
    box = spec["badge"]
    bbox = (box["x"], box["y"], box["x"]+box["width"], box["y"]+box["height"])
    assert alpha.getbbox() == bbox
    safe_box = spec["safe_zone"]["box"]
    official_safe = (safe_box["x"], safe_box["y"], safe_box["x"]+safe_box["width"],
                     safe_box["y"]+safe_box["height"])
    safe = tuple([max(timeline["safe_text_bounds"][i], official_safe[i]) if i < 2 else
                  min(timeline["safe_text_bounds"][i], official_safe[i]) for i in range(4)])
    images = {}
    for record in report["frames"]:
        path = VIDEO / "frames-test" / record["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
        im = Image.open(path).convert("RGB")
        assert im.size == (1080, 1920)
        # Independent check of the saved RGB pixels: every opaque brand pixel is exact.
        delta = ImageChops.difference(im, badge_rgb)
        marked = Image.new("RGB", im.size)
        marked.paste(delta, mask=opaque)
        assert marked.getbbox() is None, f"Badge pixels changed in {path.name}"
        assert record["badge_bounds"] == list(bbox)
        for item in record["objects"]:
            x0, y0, x1, y1 = item["bounds"]
            gap = manifest["brand_badge"]["clear_space_px"]
            assert x1 <= bbox[0]-gap or x0 >= bbox[2]+gap or y1 <= bbox[1]-gap or y0 >= bbox[3]+gap
            if item["essential"]:
                assert safe[0] <= x0 < x1 <= safe[2] and safe[1] <= y0 < y1 <= safe[3]
        cue = next(c for c in timeline["subtitles"] if c["start"] <= record["frame"] < c["end"])
        assert record["subtitle"]["text"] == cue["text"]
        assert " ".join(record["subtitle"]["lines"]) == cue["text"]
        assert record["scene"] == (1 if record["frame"] < 60 else 2)
        images[record["frame"]] = im
    assert {0, 30, 47, 59, 60, 89, 90, 164, 165, 210, 239} <= images.keys()
    # The exact hook is fully visible and pixel-stable from frame 0 through the hook scene.
    hook_region = (120, 440, 888, 824)
    for frame in (30, 47, 59):
        assert ImageChops.difference(images[0].crop(hook_region), images[frame].crop(hook_region)).getbbox() is None
    counter_region = (290, 923, 720, 1037)
    assert ImageChops.difference(images[30].crop(counter_region), images[47].crop(counter_region)).getbbox()
    assert ImageChops.difference(images[47].crop(counter_region), images[59].crop(counter_region)).getbbox() is None
    result = {"passed": True, "sample_count": len(images), "badge_opaque_pixels_exact": True,
              "badge_alpha_bounds": bbox, "safe_text_bounds": safe,
              "badge_clearance_px": manifest["brand_badge"]["clear_space_px"],
              "subtitle_boundaries_checked": [0, 60, 89, 90, 164, 165, 239],
              "hook_visible_and_stable_from_frame_0": True,
              "counter_motion_and_settled_hold_checked": True}
    (VIDEO / "frames-test/verification.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
