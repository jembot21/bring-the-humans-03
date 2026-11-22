#!/usr/bin/env python3
"""Arrange Indonesian VO, synthesize original 120 BPM music/effects, and mix."""
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import wave

import numpy as np
from scipy.signal import butter, sosfilt

VIDEO = Path(__file__).resolve().parents[1]
AUDIO = VIDEO / "audio"
RATE = 48000
SECONDS = 30
COUNT = RATE*SECONDS
RNG = np.random.default_rng(20261122)


def write_wav(path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.asarray(samples)
    channels = 1 if data.ndim == 1 else data.shape[1]
    if np.max(np.abs(data), initial=0) > 1:
        raise ValueError(f"Clipping in {path.name}")
    pcm = np.rint(data*32767).astype("<i2")
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(pcm.tobytes())


def level(samples, db):
    rms = float(np.sqrt(np.mean(samples**2)))
    return samples*(10**(db/20)/max(rms, 1e-12))


def add(track, samples, start, pan=0, wrap=False):
    samples = np.asarray(samples)
    if samples.ndim == 1 and track.ndim == 2:
        samples = samples[:, None]*np.array([math.sqrt((1-pan)/2), math.sqrt((1+pan)/2)])
    index = round(start*RATE)
    if wrap:
        index %= len(track)
        first = min(len(samples), len(track)-index)
        track[index:index+first] += samples[:first]
        if first < len(samples):
            track[:len(samples)-first] += samples[first:]
    else:
        count = min(len(samples), len(track)-index)
        if count > 0:
            track[index:index+count] += samples[:count]


def frequency(midi):
    return 440*2**((midi-69)/12)


def pluck(midi, duration=0.64):
    t = np.arange(round(duration*RATE))/RATE
    f = frequency(midi)
    body = np.sin(2*np.pi*f*t)+0.24*np.sin(2*np.pi*2*f*t)*np.exp(-t*10)
    body += 0.08*np.sin(2*np.pi*3*f*t)*np.exp(-t*18)
    envelope = (1-np.exp(-t*350))*np.exp(-t*7)*np.minimum(1, (duration-t)/0.025)
    return body*envelope


def tone(hz, duration, decay=8):
    t = np.arange(round(duration*RATE))/RATE
    return np.sin(2*np.pi*hz*t)*(1-np.exp(-t*500))*np.exp(-decay*t)*np.minimum(1, (duration-t)/0.02)


def music():
    """Four original bars; notes and tails wrap to make a continuous 8 s loop."""
    loop = np.zeros((RATE*8, 2), dtype=np.float64)
    chords = [(60, 64, 67, 71), (57, 60, 64, 67), (53, 57, 60, 64), (55, 59, 62, 67)]
    for bar, notes in enumerate(chords):
        t = np.arange(round(2.28*RATE))/RATE
        envelope = np.minimum(1, t/0.10)*np.minimum(1, (2.28-t)/0.28)
        pad = sum(np.sin(2*np.pi*frequency(note)*t) for note in notes)/len(notes)
        add(loop, pad*envelope*0.065, bar*2, pan=(-0.16 if bar%2 else 0.16), wrap=True)
        for index in range(4):
            add(loop, pluck(notes[index]+12)*0.20, bar*2+index*.5+.25,
                pan=(-.27 if index%2 else .27), wrap=True)
        for index in range(4):
            t = np.arange(round(.43*RATE))/RATE
            bass = np.sin(2*np.pi*frequency(notes[0]-12)*t)
            env = np.minimum(1, t/.012)*np.exp(-t*3)*np.minimum(1, (.43-t)/.045)
            add(loop, bass*env*.16, bar*2+index*.5, wrap=True)
    for beat in range(16):
        t = np.arange(round(.19*RATE))/RATE
        phase = 2*np.pi*(49*t+25*(1-np.exp(-25*t))/25)
        kick = np.sin(phase)*np.exp(-t*26)*np.minimum(1, t/.004)
        add(loop, kick*.17, beat*.5, wrap=True)
        for offset in (0, .25):
            hat = RNG.standard_normal(round(.065*RATE))
            hat = sosfilt(butter(2, 4200, btype="highpass", fs=RATE, output="sos"), hat)
            t = np.arange(len(hat))/RATE
            hat *= np.minimum(1, t/.003)*np.exp(-t*80)*np.minimum(1, (.065-t)/.01)
            add(loop, hat*.016, beat*.5+offset, pan=.22, wrap=True)
        if beat%4 in (1, 3):
            t = np.arange(round(.1*RATE))/RATE
            soft_click = RNG.standard_normal(len(t))
            soft_click = sosfilt(butter(2, 2500, fs=RATE, output="sos"), soft_click)
            soft_click *= np.minimum(1, t/.002)*np.exp(-t*47)*np.minimum(1, (.1-t)/.015)
            add(loop, soft_click*.035, beat*.5, pan=-.13, wrap=True)
    loop = level(loop, -32.5)
    write_wav(AUDIO / "music-loop.wav", loop)
    bed = loop[np.arange(COUNT) % len(loop)].copy()
    # A quiet tonic resolution for the official final slide.
    t = np.arange(RATE*2)/RATE
    final = sum(np.sin(2*np.pi*frequency(note)*t) for note in (60, 64, 67, 72))/4
    final *= np.minimum(1, t/.035)*np.exp(-t*1.6)*np.minimum(1, (2-t)/.4)
    add(bed, final*.025, 28)
    bed[:round(.025*RATE)] *= np.linspace(0, 1, round(.025*RATE))[:, None]
    bed[round(29.15*RATE):] *= np.linspace(1, 0, len(bed)-round(29.15*RATE))[:, None]
    return bed


def voice_piece(path, interval=None, tempo=1, trim=True):
    with wave.open(str(path)) as file:
        duration = file.getnframes()/file.getframerate()
    start, end = interval or (0, duration)
    filters = [f"atrim=start={start:.8f}:end={end:.8f}", "asetpts=PTS-STARTPTS"]
    if abs(tempo-1) > 1e-6:
        filters.append(f"atempo={tempo:.8f}")
    filters += ["highpass=f=70", "lowpass=f=8000",
                "acompressor=threshold=0.08:ratio=2:attack=10:release=100:makeup=1", "aresample=48000"]
    data = subprocess.check_output(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path),
                                    "-af", ",".join(filters), "-ar", str(RATE), "-ac", "1",
                                    "-f", "f32le", "pipe:1"])
    samples = np.frombuffer(data, dtype="<f4").astype(np.float64)
    if trim:
        hop = 240
        frames = samples[:len(samples)//hop*hop].reshape(-1, hop)
        energies = np.sqrt(np.mean(frames**2, axis=1))
        active = np.flatnonzero(energies > max(.0015, float(energies.max())*.024))
        if not len(active):
            raise ValueError("Silent narration take")
        first = max(0, active[0]*hop-round(.015*RATE))
        last = min(len(samples), (active[-1]+1)*hop+round(.035*RATE))
        samples = samples[first:last]
    # Gentle gain matching on active speech; preserve dynamics after compression.
    active = np.abs(samples) > .01
    rms = np.sqrt(np.mean(samples[active]**2))
    gain = min(10**(-19.5/20)/rms, .74/max(np.abs(samples)))
    samples *= gain
    fade = min(round(.004*RATE), len(samples)//2)
    samples[:fade] *= np.linspace(0, 1, fade)
    samples[-fade:] *= np.linspace(1, 0, fade)
    return samples, {"source": str(path.relative_to(VIDEO)), "source_start_s": start,
                     "source_end_s": end, "pitch_preserving_tempo": tempo,
                     "edited_duration_s": len(samples)/RATE, "gain_db": 20*math.log10(gain)}


def narration():
    timeline = json.loads((VIDEO / "source/timeline.json").read_text())
    takes = json.loads((AUDIO / "narration-takes.json").read_text())
    track = np.zeros(COUNT)
    records = []
    pieces = [
        (1, 0, 3, "line-01.wav", (.10, takes[0]["duration_s"]), (takes[0]["duration_s"]-.10)/2.92, False),
        (2, 3, 5.5, "line-02.wav", (0, 2.32), 1, True),
        (2, 5.5, 8, "line-02.wav", (2.32, takes[1]["duration_s"]), 1, True),
        (3, 8, 10.5, "phrases/line-03-beat-01.wav", None, 1, True),
        (3, 10.5, 13, "phrases/line-03-beat-02.wav", None, 1, True),
        (3, 13, 16, "phrases/line-03-beat-03.wav", None, 1, True),
        (4, 16, 18.5, "line-04.wav", (0, 1.13), 1, True),
        (4, 18.5, 21, "line-04.wav", (1.13, takes[3]["duration_s"]), 1, True),
        (5, 23, 26, "line-05.wav", None, 1, True),
    ]
    line_tracks = {index: np.zeros(round((line["end"]-line["start"])/30*RATE))
                   for index, line in enumerate(timeline["voice_lines"], 1)}
    for line, start, end, name, interval, tempo, trim in pieces:
        samples, record = voice_piece(AUDIO / name, interval, tempo, trim)
        if len(samples)/RATE > end-start-.025:
            fit = (len(samples)/RATE)/(end-start-.045)
            samples, record = voice_piece(AUDIO / name, interval, tempo*fit, trim)
        if start+len(samples)/RATE > end+.001:
            raise ValueError("Narration exceeds its caption/scene window")
        add(track, samples, start)
        line_start = timeline["voice_lines"][line-1]["start"]/30
        add(line_tracks[line], samples, start-line_start)
        records.append({**record, "line": line, "start_s": start, "end_s": start+len(samples)/RATE,
                        "caption_end_s": end})
    for index, samples in line_tracks.items():
        write_wav(AUDIO / "processed" / f"line-{index:02d}.wav", samples)
    return track, records


def effects():
    track = np.zeros((COUNT, 2))
    events = []

    def put(samples, start, label, gain, pan=0):
        add(track, samples*gain, start, pan=pan)
        events.append({"label": label, "time_s": start, "duration_s": len(samples)/RATE})

    for start in np.linspace(.12, 1.46, 9):
        put(tone(1150, .045, 60), float(start), "counter tick", .009)
    for start, gain in ((1.55, .026), (14.5, .014), (21, .019)):
        for index, note in enumerate((84, 88, 91)):
            put(pluck(note, .50), start+.045*index, "win chime", gain, pan=(index-1)*.12)
    for start in (8, 8.35, 8.7):
        t = np.arange(round(.14*RATE))/RATE
        noise = RNG.standard_normal(len(t))
        noise = sosfilt(butter(2, 1900, fs=RATE, output="sos"), noise)
        noise *= np.sin(np.pi*t/.14)**2
        put(noise, start, "card slide", .013, -.08)
    put(tone(880, .21, 11)+.35*tone(1320, .21, 13), 19, "phone notification", .022)
    for index in range(8):
        t = np.arange(round(.032*RATE))/RATE
        click = RNG.standard_normal(len(t))
        click = sosfilt(butter(2, 2200, fs=RATE, output="sos"), click)
        click *= np.minimum(1, t/.002)*np.exp(-t*145)*np.minimum(1, (.032-t)/.004)
        put(click, 27.25+index*.1, "referral typing", .025, -.05)
    room = RNG.standard_normal(RATE*7)
    room = sosfilt(butter(2, 380, fs=RATE, output="sos"), room)
    room = level(room, -51)
    room[:round(.2*RATE)] *= np.linspace(0, 1, round(.2*RATE))
    room[-round(.2*RATE):] *= np.linspace(1, 0, round(.2*RATE))
    put(room, 16, "synthesized room tone", 1)
    return track, events


def main():
    voice, voice_records = narration()
    bed = music()
    fx, events = effects()
    # Music is roughly 13 dB below active speech, with a further 4 dB duck.
    hop = 480
    envelope = np.sqrt(np.mean(voice.reshape(-1, hop)**2, axis=1))
    activity = (envelope > .009).astype(float)
    smooth = np.empty_like(activity)
    current = 0.0
    for index, value in enumerate(activity):
        coefficient = .22 if value > current else .065
        current += coefficient*(value-current)
        smooth[index] = current
    duck = np.repeat(10**((-4*smooth)/20), hop)
    bed *= duck[:, None]
    stereo_voice = np.repeat(voice[:, None], 2, axis=1)
    premaster = stereo_voice+bed+fx
    if np.max(np.abs(premaster)) > .89:
        premaster *= .89/np.max(np.abs(premaster))
    write_wav(AUDIO / "stems" / "narration.wav", voice)
    write_wav(AUDIO / "stems" / "music.wav", bed)
    write_wav(AUDIO / "stems" / "effects.wav", fx)
    premaster_path = AUDIO / "mix-premaster.wav"
    write_wav(premaster_path, premaster)
    # Two-pass loudness normalization; keep music's relative level intact.
    result = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(premaster_path),
                             "-af", "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json",
                             "-f", "null", "-"], capture_output=True, text=True, check=True)
    match = re.search(r"\{\s*\"input_i\"[\s\S]*?\}", result.stderr)
    if not match:
        raise ValueError("Missing loudness analysis")
    loudness = json.loads(match.group(0))
    measured = ":".join(f"measured_{key}={loudness[source]}" for key, source in
                        (("I", "input_i"), ("TP", "input_tp"), ("LRA", "input_lra"), ("thresh", "input_thresh")))
    filter_string = f"loudnorm=I=-16:TP=-1.5:LRA=9:{measured}:offset={loudness['target_offset']}:linear=true"
    mix_path = AUDIO / "mix.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-i", str(premaster_path),
                    "-af", filter_string, "-ar", str(RATE), "-ac", "2", "-c:a", "pcm_s16le", str(mix_path)], check=True)
    report = {"duration_s": SECONDS, "sample_rate": RATE, "channels": 2,
              "synthesis": {"voice": "Musing Mirror / avocado_v2:MAI_03", "language": "id", "speed": 105},
              "voice_edits": voice_records,
              "notes": ["The hook is fitted with pitch preserved so it continues across the 2 s cut and finishes within 3 s.",
                        "Scene 2/4 phrases split only in the measured silent sentence pauses.",
                        "Scene 3 uses separately synthesized exact caption beats; the five complete original takes are retained.",
                        "Scene cuts and all drafted caption windows remain unchanged."],
              "music": {"original": True, "method": "Seeded numpy oscillators/noise; no downloaded music or samples",
                        "tempo_bpm": 120, "loop_seconds": 8, "loop_rms_dbfs": -32.5, "voice_duck_db": 4,
                        "chords": ["Cmaj7", "Am7", "Fmaj7", "G6"], "seed": 20261122},
              "effects": events, "loudness_analysis": loudness, "master_lufs_target": -16,
              "master_true_peak_target_dbtp": -1.5,
              "mix_sha256": hashlib.sha256(mix_path.read_bytes()).hexdigest()}
    (AUDIO / "mix-report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    for record in voice_records:
        print(f"Voice line {record['line']}: {record['start_s']:.3f}–{record['end_s']:.3f}s", flush=True)
    print(f"Original music/effects mixed to {mix_path.relative_to(VIDEO)}, 30 s / 48 kHz / stereo", flush=True)


if __name__ == "__main__":
    main()
