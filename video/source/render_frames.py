#!/usr/bin/env python3
"""Deterministic 900-frame ad renderer with native official brand layers."""
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


@lru_cache(maxsize=64)
def font(face, size):
    files = {"hook": "NotoSans-CondensedBlack.ttf", "bold": "NotoSans-Bold.ttf",
             "body": "NotoSans-Regular.ttf", "mono": "DejaVuSansMono-Bold.ttf",
             "referral": "JetBrainsMono-Bold.ttf"}
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
        # The final scene uses the complete card at its original size and origin.
        self.card = self.asset(card_entry)
        self.end_spec = self.manifest["referral_card"]["fields"]["9:16"]
        self.end_code = self.timeline["referral_code"]
        if self.card.size != self.size or self.end_code != "8vr38xr3":
            raise ValueError("The native end card and approved referral code are required")
        if self.timeline["badge_frames"] != [0, self.timeline["scenes"][-1]["start"]]:
            raise ValueError("Badge must end exactly when the end card starts")
        if self.badge.getchannel("A").getbbox() != self.badge_bounds:
            raise ValueError("Badge alpha bounds differ from manifest")
        # Proportional scaling is allowed for the mascot; keep the complete drawing intact.
        self.mascot = self.mascot_source.resize((530, round(610*530/741)), Image.Resampling.LANCZOS)
        self.background = self.make_background()
        self.room = self.make_room()
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

    @staticmethod
    def ease(value):
        value = max(0.0, min(1.0, value))
        return value*value*(3-2*value)

    def scene3(self, im, frame):
        local = frame/self.fps-8
        self.text(im, "BOUNTY DI", (144, 450), "hook", 86)
        self.text(im, "make.fun", (144, 551), "bold", 84, MINT)
        cards = []
        for index, amount in enumerate((100, 250, 500)):
            delay = index*0.35
            if local < delay:
                cards.append({"text": f"Bounty {index+1:02d} · ${amount}", "visible": False})
                continue
            arrival = self.ease((local-delay)/0.42)
            offset = round(24*(1-arrival))
            x, y = 144+offset, 680+index*136
            box = (x, y, x+720, y+116)
            self.check(f"bounty {index+1} card", box)
            card = Image.new("RGBA", self.size)
            d = ImageDraw.Draw(card)
            selected = index == 0 and local >= 1.15
            complete = index == 0 and local >= 6.5
            d.rounded_rectangle(box, radius=24, fill="#18242b" if selected else "#1c1b2e",
                                outline=MINT if selected else "#544b68", width=3 if selected else 2)
            if selected:
                d.rounded_rectangle((x+10, y+27, x+15, y+89), radius=2, fill=MINT)
            prefix = f"Bounty {index+1:02d} · "
            label = prefix+f"${amount}"
            self.text(card, label, (x+30, y+27), "bold", 43)
            money_x = round(x+30+font("bold", 43).getlength(prefix))
            self.text(card, f"${amount}", (money_x, y+27), "bold", 43, MINT)
            d.rounded_rectangle((x+30, y+86, x+588, y+92), radius=3, fill="#373648")
            progress = max(0, min(1, (local-1.15)/5.35)) if index == 0 else 0
            if progress:
                d.rounded_rectangle((x+30, y+86, x+30+max(6, round(558*progress)), y+92),
                                    radius=3, fill=MINT)
            centre = (x+665, y+57)
            if complete:
                d.ellipse((centre[0]-23, centre[1]-23, centre[0]+23, centre[1]+23), fill=MINT)
                d.line((centre[0]-12, centre[1], centre[0]-3, centre[1]+9,
                        centre[0]+14, centre[1]-11), fill=INK, width=5, joint="curve")
            else:
                d.ellipse((centre[0]-22, centre[1]-22, centre[0]+22, centre[1]+22),
                          outline="#668174" if selected else "#635a79", width=2)
                d.ellipse((centre[0]-5, centre[1]-5, centre[0]+5, centre[1]+5),
                          fill=MINT if selected else MUTED)
            card.putalpha(card.getchannel("A").point(lambda value: round(value*arrival)))
            im.alpha_composite(card)
            cards.append({"text": label, "visible": True, "arrival": round(arrival, 4),
                          "selected": selected, "win_check": complete, "bounds": box,
                          "progress": round(progress, 4)})
        return {"title": "BOUNTY DI make.fun", "cards": cards, "win_at_s": 14.5}

    def make_room(self):
        """Original flat illustration, with room furniture below the badge."""
        im = self.background.copy()
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((112, 460, 976, 1476), radius=48, fill="#141426", outline="#302b43", width=2)
        # A distant night window and restrained moonlight.
        d.rounded_rectangle((650, 493, 914, 736), radius=25, fill="#20213c", outline="#45405e", width=6)
        d.line((782, 501, 782, 728), fill="#45405e", width=5)
        d.line((658, 616, 906, 616), fill="#45405e", width=5)
        d.ellipse((830, 525, 877, 572), fill="#c7c5e3")
        d.ellipse((842, 517, 884, 559), fill="#20213c")
        for x, y in ((682, 539), (736, 587), (811, 674), (863, 647)):
            d.ellipse((x-2, y-2, x+2, y+2), fill="#8586ac")
        # Headboard, mattress, pillow and the bedside table.
        d.rounded_rectangle((145, 794, 708, 1228), radius=30, fill="#41394f", outline="#655871", width=3)
        d.rounded_rectangle((158, 883, 715, 1317), radius=42, fill="#d7cdca")
        d.rounded_rectangle((223, 775, 570, 964), radius=52, fill="#e4dbd5", outline="#b1a4b2", width=3)
        d.arc((242, 790, 551, 947), 105, 275, fill="#bdb0be", width=3)
        d.rounded_rectangle((154, 1271, 720, 1328), radius=18, fill="#4d4159")
        d.line((184, 1324, 184, 1405), fill="#41364f", width=18)
        d.line((678, 1324, 678, 1405), fill="#41364f", width=18)
        d.rounded_rectangle((742, 1041, 941, 1074), radius=12, fill="#6d5a70")
        d.rounded_rectangle((761, 1073, 920, 1223), radius=16, fill="#3c304a", outline="#5b4965", width=2)
        d.line((778, 1223, 778, 1345), fill="#3c304a", width=12)
        d.line((902, 1223, 902, 1345), fill="#3c304a", width=12)
        d.line((861, 821, 861, 1035), fill="#a9989d", width=8)
        d.ellipse((825, 1023, 897, 1042), fill="#9c868e")
        d.polygon(((817, 778), (900, 778), (927, 846), (790, 846)), fill="#b9a4a8")
        d.line((791, 846, 927, 846), fill="#ead6c2", width=5)
        d.line((139, 1435, 951, 1435), fill="#272239", width=3)
        return im

    def scene4(self, im, frame):
        time = frame/self.fps
        im.alpha_composite(self.room)
        d = ImageDraw.Draw(im)
        waking = self.ease((time-19)/0.7)
        lift = round(54*waking)
        self.check("original sleeping person", (195, 676, 718, 1282), False)
        # A warm, round face, soft curly hair, and a shirt visible above the duvet.
        d.rounded_rectangle((280, 887-lift, 619, 1056-lift), radius=78, fill="#4b6575")
        d.rounded_rectangle((372, 881-lift, 433, 949-lift), radius=22, fill="#bb856b")
        d.ellipse((303, 748-lift, 495, 940-lift), fill="#cd9678", outline="#e0ae8d", width=2)
        d.ellipse((478, 836-lift, 509, 880-lift), fill="#c88f73")
        for x, y, r in ((330, 761, 33), (364, 739, 37), (409, 738, 37), (452, 751, 32), (474, 781, 25)):
            d.ellipse((x-r, y-r-lift, x+r, y+r-lift), fill="#28202b")
        d.rounded_rectangle((311, 788-lift, 326, 844-lift), radius=7, fill="#28202b")
        if time < 19:
            d.arc((340, 839-lift, 378, 861-lift), 8, 174, fill="#4b3034", width=5)
            d.arc((414, 839-lift, 452, 861-lift), 8, 174, fill="#4b3034", width=5)
        else:
            for x in (357, 432):
                d.ellipse((x-10, 839-lift, x+10, 862-lift), fill="#fff4e6")
                d.ellipse((x-2, 842-lift, x+8, 858-lift), fill="#362432")
            d.arc((339, 822-lift, 376, 845-lift), 195, 336, fill="#4b3034", width=4)
            d.arc((414, 822-lift, 449, 845-lift), 195, 336, fill="#4b3034", width=4)
        d.line((395, 851-lift, 390, 873-lift, 401, 876-lift), fill="#a7685d", width=3)
        d.arc((374, 873-lift, 419, 903-lift), 20, 160, fill="#633c42", width=3)
        # The blanket has only modest breathing; no camera or badge motion.
        breath = round(2*math.sin((time-16)*2*math.pi/3)) if time < 19 else 0
        d.rounded_rectangle((159, 954+breath, 715, 1282), radius=48, fill="#686084", outline="#9583ac", width=3)
        d.arc((246, 974+breath, 629, 1228), 184, 327, fill="#83769f", width=3)
        d.line((191, 998+breath, 674, 998+breath), fill="#b4a0c1", width=3)
        d.line((192, 1020+breath, 674, 1020+breath), fill="#7f7299", width=2)
        if time < 19:
            for index, (x, y, size) in enumerate(((530, 730, 31), (571, 684, 23), (604, 646, 17))):
                self.text(im, "z", (x, y-round(2*math.sin((time-16)+index))), "bold", size, "#8b83a8",
                          name=f"sleep symbol {index+1}")
        raising = self.ease((time-20.5)/0.5)
        phone_w, phone_h = round(98+240*raising), round(174+242*raising)
        phone_x, phone_y = round(768-433*raising), round(867-201*raising)
        if raising > 0:
            # The hand is original art and reaches from the person to the phone.
            d.line((578, 945, phone_x+25, phone_y+phone_h-53), fill="#cd9678", width=40)
            d.ellipse((phone_x-16, phone_y+phone_h-121, phone_x+28, phone_y+phone_h-30), fill="#dea685")
        phone = Image.new("RGBA", (338, 416))
        pd = ImageDraw.Draw(phone)
        pd.rounded_rectangle((0, 0, 337, 415), radius=38, fill="#3c384d", outline="#8d889e", width=3)
        pd.rounded_rectangle((12, 13, 325, 403), radius=27, fill="#0d2025" if time >= 21 else "#121626")
        pd.rounded_rectangle((132, 21, 207, 33), radius=6, fill="#343347")
        if time >= 21:
            pd.ellipse((133, 86, 205, 158), fill=MINT)
            pd.line((150, 121, 164, 135, 189, 106), fill=INK, width=7, joint="curve")
            pd.text((169, 182), "HADIAH MASUK", font=font("bold", 30), fill=WHITE, anchor="mt")
            pd.text((169, 241), "$100.00", font=font("mono", 60), fill=MINT, anchor="mt")
            pd.rounded_rectangle((54, 338, 284, 343), radius=2, fill="#3d6058")
            pd.rounded_rectangle((87, 358, 250, 362), radius=2, fill="#254a45")
            self.check("phone payout label", (phone_x+45, phone_y+182, phone_x+294, phone_y+217))
            self.check("phone payout amount", (phone_x+40, phone_y+241, phone_x+298, phone_y+298))
        else:
            pd.ellipse((137, 142, 200, 205), outline=MINT if time >= 19 else "#444359", width=4)
            pd.line((153, 174, 169, 183, 187, 163), fill=MINT if time >= 19 else "#55536a", width=5)
        if (phone_w, phone_h) != phone.size:
            phone = phone.resize((phone_w, phone_h), Image.Resampling.LANCZOS)
        self.check("original phone", (phone_x, phone_y, phone_x+phone_w, phone_y+phone_h), time >= 21)
        im.alpha_composite(phone, (phone_x, phone_y))
        return {"asleep": time < 19, "eyes_open_at_s": 19,
                "phone_raising": round(raising, 4), "phone_bounds": (phone_x, phone_y, phone_x+phone_w, phone_y+phone_h),
                "payout_visible": time >= 21, "payout_at_s": 21,
                "payout_text": ["HADIAH MASUK", "$100.00"] if time >= 21 else []}

    def scene5(self, im, frame):
        lines = ["Masukin agent lo", "ke bounty di", "make.fun."]
        if " ".join(lines) != "Masukin agent lo ke bounty di make.fun.":
            raise ValueError("CTA must preserve the approved exact wording")
        self.text(im, lines[0], (144, 488), "hook", 88)
        self.text(im, lines[1], (144, 603), "hook", 106)
        button = (144, 784, 864, 969)
        self.check("CTA outline", button)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle(button, radius=32, fill="#142b2b", outline=MINT, width=4)
        self.centred(im, lines[2], 826, "bold", 104, MINT)
        self.check("end card direction arrow", (800, 1003, 837, 1055))
        d.line((818, 1003, 818, 1051), fill=MINT, width=5)
        d.line((803, 1036, 818, 1051, 833, 1036), fill=MINT, width=5, joint="curve")
        return {"cta": " ".join(lines), "lines": lines, "steady": True}

    def scene6(self, frame):
        # No scene background, badge, subtitles, fades, or additional copy.
        im = self.card.copy()
        d = ImageDraw.Draw(im)
        code_spec = self.end_spec["code"]
        cover = code_spec["cover"]
        x0, y0, x1, y1 = rect(cover)
        d.rectangle((x0, y0, x1-1, y1-1), fill=code_spec["cover_with"])
        # The .25/.95 s events fall halfway between 30 fps frame timestamps.
        # Sample typing at frame centres: one character each three frames,
        # with all eight present in the frame covering the 27.95 s deadline.
        typing_time = (frame+0.5)/self.fps
        count = max(0, min(len(self.end_code), math.floor((typing_time-27.25+1e-8)/0.1)+1))
        text = self.end_code[:count]
        f = font("referral", code_spec["font_size_px"])
        full_bounds = f.getbbox(self.end_code)
        ink_height = full_bounds[3]-full_bounds[1]
        xy = (code_spec["box"]["x"], round(code_spec["centre_y"]-ink_height/2))
        text_bounds = d.textbbox(xy, text, font=f, anchor="lt") if text else None
        if text:
            if not within(text_bounds, rect(code_spec["box"])):
                raise ValueError("Referral code must fit its exact manifest field box")
            d.text(xy, text, font=f, fill=code_spec["colour"], anchor="lt")
        return im, {"card_source": "makefun-card-9x16.png", "card_native": True,
                    "code": text, "full_code": self.end_code, "code_bounds": text_bounds,
                    "code_font": "JetBrains Mono Bold", "code_size_px": code_spec["font_size_px"],
                    "code_centre_y": code_spec["centre_y"], "caret_cover": rect(cover),
                    "typing_from_s": 27.25, "typing_complete_s": 27.95,
                    "typing_sample": "frame centre", "complete_by_frame": 838}

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
        if not isinstance(frame, int) or not 0 <= frame < self.timeline["duration_frames"]:
            raise ValueError("Frame must be in the complete 0–899 ad timeline")
        self.objects = []
        scene = next(s["id"] for s in self.timeline["scenes"] if s["start"] <= frame < s["end"])
        if scene == 6:
            im, state = self.scene6(frame)
            cue = None
        else:
            im = self.background.copy()
            state = getattr(self, f"scene{scene}")(im, frame)
            cue = self.subtitles(im, frame)
            # Full 1080×1920 overlay at the origin, 100%, as the final layer.
            # Only the diagnostic comparison is cropped, never the composited asset.
            before = im.crop(self.badge_bounds)
            im.alpha_composite(self.badge, (0, 0))
            expected = Image.alpha_composite(before, self.badge.crop(self.badge_bounds))
            if ImageChops.difference(expected.convert("RGB"), im.crop(self.badge_bounds).convert("RGB")).getbbox():
                raise ValueError("Official badge must be the final unchanged compositing layer")
        record = {"frame": frame, "time_s": round(frame/self.fps, 6), "scene": scene,
                  "size": self.size, "safe_text_bounds": self.safe,
                  "badge_bounds": self.badge_bounds, "badge_exclusion": self.badge_exclusion,
                  "badge_native_composite": scene != 6, "subtitle": cue, "state": state,
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
    if any(not 0 <= f < 900 for f in args.frames) or len(args.frames) > 60:
        parser.error("Request up to 60 sample frames from the whole ad (0–899)")
    renderer = Renderer()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for frame in args.frames:
        im, record = renderer.render(frame)
        path = out / f"frame-{frame:04d}.png"
        im.save(path)
        record.update(file=path.name, sha256=digest(path))
        records.append(record)
        print(f"{path.relative_to(VIDEO)}: scene {record['scene']}, {frame/30:.3f}s, layout/asset checks PASS")
    report = {"scope": "Requested native-size frames from the complete six-scene renderer",
              "manifest_sha256": digest(ASSETS / "manifest.json"),
              "guide_sha256": digest(ASSETS / "llms.txt"),
              "renderer_sha256": digest(Path(__file__)), "frames": records}
    (out / "validation.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")


if __name__ == "__main__":
    main()
