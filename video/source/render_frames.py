#!/usr/bin/env python3
"""Deterministic, official-assets PIL renderer. Only storyboard scenes 1 and 2."""
import argparse
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

VIDEO = Path(__file__).resolve().parents[1]
ASSETS = VIDEO / "assets"
WHITE = "#fff8ef"
MINT = "#8dffca"
MUTED = "#b5b3c8"
INK = "#101020"
SAMPLES = [0, 15, 30, 47, 59, 60, 89, 90, 164, 165, 210, 239]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect(box):
    return (box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"])


def intersects(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def within(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


@lru_cache(maxsize=32)
def font(face, size):
    files = {"hook": "NotoSans-CondensedBlack.ttf", "bold": "NotoSans-Bold.ttf",
             "body": "NotoSans-Regular.ttf", "mono": "DejaVuSansMono-Bold.ttf"}
    return ImageFont.truetype(str(ASSETS / "fonts" / files[face]), size)


class Renderer:
    def __init__(self):
        self.timeline = json.loads((VIDEO / "source/timeline.json").read_text())
        self.manifest = json.loads((ASSETS / "manifest.json").read_text())
        self.size = (self.timeline["width"], self.timeline["height"])
        self.fps = self.timeline["fps"]
        self.spec = self.manifest["brand_badge"]["aspects"]["9:16"]
        if self.size != (self.spec["frame"]["width"], self.spec["frame"]["height"]):
            raise ValueError("Canvas must equal the native badge overlay size")
        self.badge_bounds = rect(self.spec["badge"])
        gap = self.manifest["brand_badge"]["clear_space_px"]
        x0, y0, x1, y1 = self.badge_bounds
        self.badge_exclusion = (x0-gap, y0-gap, x1+gap, y1+gap)
        # Intersection of the storyboard's conservative text region and the pack's safe zone.
        original = self.timeline["safe_text_bounds"]
        official = rect(self.spec["safe_zone"]["box"])
        self.safe = (max(original[0], official[0]), max(original[1], official[1]),
                     min(original[2], official[2]), min(original[3], official[3]))
        badge_entry = next(e for e in self.manifest["brand_badge"]["files"]
                           if e["url"] == self.spec["overlay"])
        mascot_entry = next(e for e in self.manifest["files"]
                            if e["path"] == "illustrations/ghost-laptop-recording.png")
        card_entry = next(e for e in self.manifest["referral_card"]["files"]
                         if e["path"] == "referral-card/9x16/makefun-card-9x16.png")
        self.badge = self.asset(badge_entry)
        self.mascot_source = self.asset(mascot_entry)
        # Validate and retain the card for session 2; never draw it in scenes 1 or 2.
        self.card = self.asset(card_entry)
        if self.badge.getchannel("A").getbbox() != self.badge_bounds:
            raise ValueError("Badge alpha bounds differ from manifest")
        # Proportional scaling is allowed for the mascot; keep the complete drawing intact.
        self.mascot = self.mascot_source.resize((530, round(610*530/741)), Image.Resampling.LANCZOS)
        self.background = self.make_background()
        self.objects = []

    def asset(self, entry):
        path = ASSETS / Path(entry["path"]).name
        if digest(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise ValueError(f"Asset differs from manifest: {path.name}")
        im = Image.open(path).convert("RGBA")
        if im.size != (entry["width"], entry["height"]):
            raise ValueError(f"Wrong dimensions: {path.name}")
        return im

    def make_background(self):
        # Soft, static lighting: only original scene graphics are resampled.
        im = Image.new("RGB", (270, 480))
        pixels = im.load()
        for y in range(480):
            for x in range(270):
                violet = math.exp(-(((x-203)/123)**2 + ((y-195)/135)**2))
                green = math.exp(-(((x-30)/122)**2 + ((y-277)/116)**2))
                pixels[x, y] = (int(14+23*violet+2*green), int(13+9*violet+13*green),
                                int(26+46*violet+9*green))
        im = im.resize(self.size, Image.Resampling.BICUBIC).convert("RGBA")
        d = ImageDraw.Draw(im)
        d.ellipse((662, 497, 1144, 979), outline="#393047", width=2)
        d.ellipse((717, 552, 1089, 924), outline="#302b40", width=2)
        d.line((144, 1514, 936, 1514), fill="#282335", width=2)
        return im

    def check(self, name, bounds, essential=True):
        bounds = tuple(map(int, bounds))
        if essential and not within(bounds, self.safe):
            raise ValueError(f"{name} outside safe text area: {bounds}, safe {self.safe}")
        if intersects(bounds, self.badge_exclusion):
            raise ValueError(f"{name} violates badge clear space: {bounds}")
        self.objects.append({"name": name, "bounds": bounds, "essential": essential})

    def text(self, im, text, xy, face, size, fill=WHITE, name=None):
        d = ImageDraw.Draw(im)
        f = font(face, size)
        box = d.textbbox(xy, text, font=f, anchor="lt")
        self.check(name or text, box)
        d.text(xy, text, font=f, fill=fill, anchor="lt")
        return box

    def centred(self, im, text, y, face, size, fill=WHITE, centre=504, name=None):
        f = font(face, size)
        bounds = f.getbbox(text)
        width = bounds[2] - bounds[0]
        return self.text(im, text, (round(centre-width/2), y), face, size, fill, name)

    def counter(self, im, frame):
        panel = (144, 852, 864, 1058)
        self.check("counter panel", panel)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(panel, radius=28, fill="#151726", outline="#424951", width=2)
        d.rounded_rectangle((162, 871, 166, 899), radius=2, fill=MINT)
        self.text(im, "HADIAH BOUNTY", (184, 871), "bold", 25, MUTED)
        f = font("mono", 100)
        baseline = f.getmetrics()[0]
        glyph_width = math.ceil(f.getlength("0"))
        chars = "$000.00" if frame == 0 else "$100.00"
        total = glyph_width * len(chars)
        left = round(504-total/2)
        y, step, viewport_height = 923, 114, 114
        self.check("money counter", (left, y, left+total, y+viewport_height))
        positions = []
        for i, char in enumerate(chars):
            x = left + i*glyph_width
            column = Image.new("RGBA", (glyph_width, viewport_height))
            cd = ImageDraw.Draw(column)
            if char in "$." or frame == 0 or frame >= 47:
                cd.text((0, baseline), char, font=f, fill=MINT, anchor="ls")
                positions.append({"character": char, "offset": 0})
            else:
                digit_index = sum(c.isdigit() for c in chars[:i])
                # Every column moves up continuously, decelerating into its target.
                target = int(char)
                start = target - (16 + 3*digit_index)
                p = min(1, frame/46.5)
                position = start + (target-start)*(1-(1-p)**3)
                base = math.floor(position)
                offset = round((position-base)*step)
                for n in (base, base+1):
                    cd.text((0, baseline+(n-base)*step-offset), str(n % 10), font=f, fill=MINT, anchor="ls")
                positions.append({"target": char, "position": round(position, 5), "offset": offset})
            im.alpha_composite(column, (x, y))
        if frame >= 47:
            # Small win pips/ring only; headline and overall luminance remain steady.
            elapsed = (frame-47)/12
            ring = (787-int(elapsed*14), 870-int(elapsed*14),
                    833+int(elapsed*14), 916+int(elapsed*14))
            d.ellipse(ring, outline="#4f987d", width=2)
            d.ellipse((797, 880, 823, 906), fill=MINT)
            d.line((804, 893, 809, 898, 818, 887), fill=INK, width=3, joint="curve")
            for x, yy in ((831, 828), (878, 935), (123, 980)):
                d.ellipse((x-3, yy-3, x+3, yy+3), fill=MINT)
        return {"display": "$000.00" if frame == 0 else "$100.00" if frame >= 47 else "rolling",
                "settles_at_s": 1.55, "columns": positions}

    def scene1(self, im, frame):
        lines = ["AI GUE BARU", "SAJA MENANG", "$100."]
        if " ".join(lines) != self.timeline["hook"]:
            raise ValueError("Hook must equal the exact storyboard sentence")
        self.text(im, lines[0], (144, 450), "hook", 101)
        self.text(im, lines[1], (144, 557), "hook", 101)
        self.text(im, lines[2], (138, 671), "hook", 180, MINT)
        return {"hook": " ".join(lines), "counter": self.counter(im, frame)}

    def scene2(self, im, frame):
        local = (frame-60)/self.fps
        self.text(im, "KENALIN,", (144, 449), "hook", 92)
        self.text(im, "AGENT AI GUE.", (144, 550), "hook", 86)
        d = ImageDraw.Draw(im)
        # An original desk beneath the pack's complete ghost-and-laptop illustration.
        d.rounded_rectangle((130, 1053, 882, 1084), radius=12, fill="#4a4256")
        d.line((176, 1083, 176, 1469), fill="#2a2538", width=16)
        d.line((835, 1083, 835, 1469), fill="#2a2538", width=16)
        d.ellipse((186, 1031, 752, 1065), fill="#181528")
        bob = round(2*math.sin(local*2*math.pi/3))
        mascot_xy = (144, 632+bob)
        self.check("official mascot and laptop", (*mascot_xy, mascot_xy[0]+self.mascot.width,
                                                 mascot_xy[1]+self.mascot.height), False)
        im.alpha_composite(self.mascot, mascot_xy)
        # A simple original bounty submission card, adjacent to the laptop, above the desk.
        # It does not paint inside or recolour the official illustration.
        task = (665, 686, 864, 914)
        self.check("bounty submission card", task)
        d.rounded_rectangle(task, radius=20, fill="#191b2c", outline="#67607d", width=2)
        self.text(im, "BOUNTY", (682, 707), "bold", 24, WHITE)
        self.text(im, "$100", (682, 747), "mono", 36, MINT)
        progress = min(1.0, max(0.0, (local-0.5)/4.4))
        d.rounded_rectangle((682, 810, 845, 822), radius=6, fill="#363348")
        if progress > 0:
            d.rounded_rectangle((682, 810, 682+max(12, round(163*progress)), 822), radius=6, fill=MINT)
        complete = local >= 5.0
        self.text(im, "TERKIRIM" if complete else "SUBMIT", (682, 860), "bold", 20,
                  MINT if complete else MUTED)
        if complete:
            d.line((800, 853, 815, 867, 839, 841), fill=MINT, width=5, joint="curve")
        else:
            for i in range(3):
                color = MINT if int(local*3)%3 == i else "#39354b"
                d.rounded_rectangle((779+i*23, 847, 791+i*23, 853), radius=3, fill=color)
        return {"mascot_source": "ghost-laptop-recording.png", "mascot_xy": mascot_xy,
                "mascot_size": self.mascot.size, "bob_px": bob,
                "submission_progress": round(progress, 4), "submission_complete": complete}

    def subtitles(self, im, frame):
        cue = next((c for c in self.timeline["subtitles"] if c["start"] <= frame < c["end"]), None)
        if not cue:
            return None
        panel = self.timeline["subtitle_panel"]
        self.check("subtitle panel", panel)
        ImageDraw.Draw(im).rounded_rectangle(panel, radius=22, fill="#10111e", outline="#383345", width=2)
        f = font("body", 43)
        lines, line = [], ""
        for word in cue["text"].split():
            candidate = (line+" "+word).strip()
            if f.getlength(candidate) > panel[2]-panel[0]-56 and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
        if " ".join(lines) != cue["text"] or len(lines) > 2:
            raise ValueError("Subtitle wrapping must preserve every word and fit two lines")
        glyph_height = max(f.getbbox(line)[3]-f.getbbox(line)[1] for line in lines)
        line_step = 54
        block_height = glyph_height + (len(lines)-1)*line_step
        top = round((panel[1]+panel[3]-block_height)/2)
        for i, line in enumerate(lines):
            self.centred(im, line, top+i*line_step, "body", 43, name=f"subtitle line {i+1}")
        return {**cue, "lines": lines, "panel": panel}

    def render(self, frame):
        if not isinstance(frame, int) or not 0 <= frame < 240:
            raise ValueError("This session implements only frames 0–239; no full-video render")
        self.objects = []
        im = self.background.copy()
        scene = 1 if frame < 60 else 2
        state = self.scene1(im, frame) if scene == 1 else self.scene2(im, frame)
        cue = self.subtitles(im, frame)
        base = im.copy()
        # Full 1080×1920 overlay at the origin, 100%: never crop, move or resample it.
        im.alpha_composite(self.badge, (0, 0))
        expected = Image.alpha_composite(base, self.badge)
        if ImageChops.difference(expected.convert("RGB"), im.convert("RGB")).getbbox():
            raise ValueError("Official badge must be the final, unchanged compositing layer")
        record = {"frame": frame, "time_s": round(frame/self.fps, 6), "scene": scene,
                  "size": self.size, "safe_text_bounds": self.safe,
                  "badge_bounds": self.badge_bounds, "badge_exclusion": self.badge_exclusion,
                  "badge_native_composite": True, "subtitle": cue, "state": state,
                  "objects": self.objects}
        return im.convert("RGB"), record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", nargs="+", type=int, default=SAMPLES)
    parser.add_argument("--out", type=Path, default=VIDEO / "frames-test")
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(VIDEO):
        parser.error("All outputs must stay inside this repository under video/")
    # Validate the whole request before writing anything.
    if any(not 0 <= f < 240 for f in args.frames) or len(args.frames) > 60:
        parser.error("Request up to 60 sample frames from scenes 1–2 (0–239)")
    renderer = Renderer()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for frame in args.frames:
        im, record = renderer.render(frame)
        path = out / f"frame-{frame:04d}.png"
        im.save(path)
        record.update(file=path.name, sha256=digest(path))
        records.append(record)
        print(f"{path.relative_to(VIDEO)}: scene {record['scene']}, {frame/30:.3f}s, safe area and badge PASS")
    report = {"scope": "Session 1 samples only; scenes 1 and 2; no audio or full video",
              "manifest_sha256": digest(ASSETS / "manifest.json"),
              "guide_sha256": digest(ASSETS / "llms.txt"),
              "renderer_sha256": digest(Path(__file__)), "frames": records}
    (out / "validation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")


if __name__ == "__main__":
    main()
