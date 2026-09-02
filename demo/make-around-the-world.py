#!/usr/bin/env python3
"""Builds demo/around-the-world.sb3: a Scratch cover of Daft Punk's "Around the World",
with the two robots on their pyramid and the dancer groups from the Michel Gondry video,
all animated by beat cues coming back from Sonic Pi.

Run: python3 demo/make-around-the-world.py
"""
import os
from sb3lib import Target, num, posnum, whole, txt, var_input, write_sb3

EXT = "sonicpi"
EXT_URL = "http://localhost:8000/sonic-pi-blocks.js"
OUT = os.path.join(os.path.dirname(__file__), "around-the-world.sb3")

# ============================================================ the art
SKIN = "#f1c27d"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def robot(helmet, visor_lights, arms_up):
    if helmet == "silver":
        dome = '<defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#b8bcc4"/><stop offset="1" stop-color="#6c727c"/></linearGradient></defs>'
    else:
        dome = '<defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff2b3"/><stop offset="0.5" stop-color="#e0b53a"/><stop offset="1" stop-color="#8a6b12"/></linearGradient></defs>'
    if arms_up:
        arms = ('<rect x="8" y="22" width="14" height="48" rx="7" fill="#151515" transform="rotate(-25 15 70)"/>'
                '<rect x="78" y="22" width="14" height="48" rx="7" fill="#151515" transform="rotate(25 85 70)"/>'
                '<circle cx="3" cy="18" r="8" fill="#151515"/><circle cx="97" cy="18" r="8" fill="#151515"/>')
    else:
        arms = ('<rect x="8" y="66" width="14" height="46" rx="7" fill="#151515"/>'
                '<rect x="78" y="66" width="14" height="46" rx="7" fill="#151515"/>'
                '<circle cx="15" cy="116" r="8" fill="#151515"/><circle cx="85" cy="116" r="8" fill="#151515"/>')
    body = (dome +
            '<rect x="30" y="108" width="16" height="42" rx="6" fill="#111"/><rect x="54" y="108" width="16" height="42" rx="6" fill="#111"/>'
            '<rect x="24" y="62" width="52" height="52" rx="8" fill="#1c1c1c"/>'
            '<path d="M50 62 l-9 26 l9 22 l9 -22 z" fill="#2e2e2e"/>'
            '<circle cx="50" cy="66" r="4" fill="#444"/>' + arms +
            '<ellipse cx="50" cy="36" rx="28" ry="30" fill="url(#h)"/>'
            '<rect x="28" y="26" width="44" height="20" rx="10" fill="#0c0c0c"/>' + visor_lights)
    return svg(100, 150, body)


def robot_costumes(t, helmet):
    if helmet == "silver":
        lights = ''.join(f'<rect x="{34 + i * 6}" y="34" width="4" height="4" fill="#ff2fa8"/>' for i in range(6))
    else:
        lights = ''.join(f'<circle cx="{35 + i * 5}" cy="{33 + (i % 2) * 5}" r="1.8" fill="#ff5a1f"/>' for i in range(7))
    t.costume("arms down", robot(helmet, lights, False), 50, 75)
    t.costume("arms up", robot(helmet, lights, True), 50, 75)


def group(figure_fn, poses, spacing, count, w, h):
    """Several copies of a figure side by side, one costume per pose."""
    out = []
    for pose in poses:
        parts = ''.join(f'<g transform="translate({i * spacing} 0)">{figure_fn(pose, i)}</g>' for i in range(count))
        out.append(svg(w + spacing * (count - 1), h, parts))
    return out


def mummy(pose, i):
    lean = 8 if (pose + i) % 2 else -8
    stripes = ''.join(f'<line x1="14" y1="{y}" x2="56" y2="{y + 4}" stroke="#bfb69a" stroke-width="2"/>' for y in range(52, 118, 9))
    arm_l = '<rect x="0" y="48" width="12" height="40" rx="6" fill="#e8dfc4" transform="rotate(35 6 52)"/>' if pose else '<rect x="2" y="56" width="12" height="40" rx="6" fill="#e8dfc4"/>'
    arm_r = '<rect x="58" y="48" width="12" height="40" rx="6" fill="#e8dfc4" transform="rotate(-35 64 52)"/>' if not pose else '<rect x="56" y="56" width="12" height="40" rx="6" fill="#e8dfc4"/>'
    return (f'<g transform="rotate({lean} 35 128)">'
            f'<rect x="20" y="88" width="12" height="42" rx="5" fill="#e8dfc4"/><rect x="38" y="88" width="12" height="42" rx="5" fill="#e8dfc4"/>'
            f'<rect x="14" y="46" width="42" height="50" rx="10" fill="#efe6cc"/>{stripes}{arm_l}{arm_r}'
            f'<circle cx="35" cy="28" r="20" fill="#efe6cc"/>'
            f'<line x1="16" y1="22" x2="54" y2="26" stroke="#bfb69a" stroke-width="2"/><line x1="16" y1="34" x2="54" y2="38" stroke="#bfb69a" stroke-width="2"/>'
            f'<circle cx="28" cy="28" r="3" fill="#222"/><circle cx="42" cy="28" r="3" fill="#222"/></g>')


def skeleton(pose, i):
    up = (pose + i) % 2 == 0
    arm_l = '<line x1="22" y1="58" x2="4" y2="28" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>' if up else '<line x1="22" y1="58" x2="6" y2="90" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>'
    arm_r = '<line x1="48" y1="58" x2="66" y2="90" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>' if up else '<line x1="48" y1="58" x2="64" y2="28" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>'
    legs = ('<line x1="30" y1="96" x2="22" y2="130" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>'
            '<line x1="40" y1="96" x2="50" y2="130" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>') if up else (
            '<line x1="30" y1="96" x2="30" y2="130" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>'
            '<line x1="40" y1="96" x2="40" y2="130" stroke="#f4f4f4" stroke-width="5" stroke-linecap="round"/>')
    ribs = ''.join(f'<path d="M22 {y} q13 6 26 0" stroke="#f4f4f4" stroke-width="3" fill="none"/>' for y in (62, 72, 82))
    return (f'<circle cx="35" cy="28" r="18" fill="#f4f4f4"/><rect x="26" y="40" width="18" height="10" rx="3" fill="#f4f4f4"/>'
            f'<circle cx="28" cy="26" r="4" fill="#111"/><circle cx="42" cy="26" r="4" fill="#111"/><rect x="31" y="34" width="8" height="3" fill="#111"/>'
            f'<line x1="35" y1="50" x2="35" y2="96" stroke="#f4f4f4" stroke-width="5"/>{ribs}{arm_l}{arm_r}{legs}')


def athlete(pose, i):
    step = (pose + i) % 3
    dy = [0, -8, -16][step]
    legs = ('<rect x="20" y="96" width="13" height="50" rx="5" fill="#c0392b"/><rect x="37" y="96" width="13" height="50" rx="5" fill="#c0392b"/>' if step != 1 else
            '<rect x="16" y="96" width="13" height="50" rx="5" fill="#c0392b" transform="rotate(12 22 96)"/><rect x="40" y="96" width="13" height="50" rx="5" fill="#c0392b" transform="rotate(-12 46 96)"/>')
    arm = '<rect x="4" y="40" width="12" height="44" rx="6" fill="#c0392b" transform="rotate(30 10 44)"/>' if step == 2 else '<rect x="4" y="52" width="12" height="44" rx="6" fill="#c0392b"/>'
    return (f'<g transform="translate(0 {dy})">'
            f'<rect x="4" y="{140 + dy}" width="62" height="10" rx="3" fill="#2b2b2b" transform="translate(0 {-dy})"/>'
            f'{legs}<rect x="14" y="50" width="42" height="50" rx="9" fill="#c0392b"/>'
            f'<line x1="14" y1="60" x2="56" y2="60" stroke="#fff" stroke-width="3"/><line x1="14" y1="66" x2="56" y2="66" stroke="#fff" stroke-width="3"/>'
            f'{arm}<rect x="54" y="52" width="12" height="44" rx="6" fill="#c0392b"/>'
            f'<circle cx="35" cy="32" r="17" fill="{SKIN}"/><path d="M18 30 q17 -22 34 0 z" fill="#2b2b2b"/></g>')


def swimmer(pose, i):
    v = (pose + i) % 2 == 0
    arms = ('<rect x="6" y="20" width="11" height="44" rx="5" fill="{s}" transform="rotate(-30 11 64)"/><rect x="53" y="20" width="11" height="44" rx="5" fill="{s}" transform="rotate(30 59 64)"/>' if v else
            '<rect x="-4" y="58" width="44" height="11" rx="5" fill="{s}"/><rect x="53" y="20" width="11" height="44" rx="5" fill="{s}" transform="rotate(30 59 64)"/>').replace("{s}", SKIN)
    return (f'<rect x="22" y="96" width="12" height="36" rx="5" fill="{SKIN}"/><rect x="36" y="96" width="12" height="36" rx="5" fill="{SKIN}"/>'
            f'<path d="M18 56 h34 v42 q-17 8 -34 0 z" fill="#1e6fd9"/>{arms}'
            f'<circle cx="35" cy="34" r="17" fill="{SKIN}"/><path d="M18 32 q17 -26 34 0 z" fill="#ff5ca8"/>'
            f'<rect x="22" y="30" width="26" height="9" rx="4" fill="#111"/><circle cx="29" cy="34" r="3" fill="#8fd3ff"/><circle cx="41" cy="34" r="3" fill="#8fd3ff"/>')


def backdrop(light):
    beams = ''.join(f'<polygon points="240,110 {x - 60},0 {x + 60},0" fill="{light}" opacity="0.10"/>' for x in (60, 240, 420))
    grid = ''.join(f'<line x1="{240 - (y - 110) * 0.78}" y1="{y}" x2="{240 + (y - 110) * 0.78}" y2="{y}" stroke="{light}" stroke-width="1.2" opacity="0.7"/>' for y in range(125, 290, 15))
    grid += ''.join(f'<line x1="240" y1="110" x2="{x}" y2="290" stroke="{light}" stroke-width="1" opacity="0.35"/>' for x in range(100, 400, 35))
    grooves = ''.join(f'<ellipse cx="240" cy="300" rx="{r}" ry="{r * 0.2}" fill="none" stroke="#3a3a3a" stroke-width="1"/>' for r in range(60, 230, 18))
    return svg(480, 360,
               '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05030f"/><stop offset="1" stop-color="#1c0f3a"/></linearGradient></defs>'
               '<rect width="480" height="360" fill="url(#sky)"/>' + beams +
               '<ellipse cx="240" cy="300" rx="235" ry="48" fill="#111"/>' + grooves +
               f'<ellipse cx="240" cy="300" rx="40" ry="8" fill="{light}" opacity="0.8"/>'
               '<polygon points="240,110 70,290 410,290" fill="#0b0b14"/>' + grid +
               f'<rect x="170" y="108" width="140" height="6" fill="{light}"/>'
               f'<polygon points="240,110 70,290 410,290" fill="none" stroke="{light}" stroke-width="2"/>')


# ============================================================ the project
# Everything below is ordinary Scratch blocks plus the Sonic Pi blocks. No raw code.
# Each part of the song is a custom block ("My Blocks") so the green flag and the
# number keys can share it.

stage = Target("Stage")
stage.is_stage = True
for name, light in [("magenta", "#ff2fa8"), ("cyan", "#2fd8ff"), ("gold", "#ffd23f")]:
    stage.costume(name, backdrop(light), 240, 180)
words = stage.list("words", ["A", "ROUND", "THE", "WORLD"])
syllable = stage.var("syllable", 0)
PARTS = ["drums", "lead", "bass", "voice", "chords"]
LOOPS = {"drums": ["kick", "hats"], "lead": ["lead"], "bass": ["bass"], "voice": ["voice"], "chords": ["chords"]}
part_on = {name: stage.var(f"{name} on", 0) for name in PARTS}

t = stage  # the music lives on the Stage


def sp(op, **inputs):
    return t.block(f"sonicpi_{op}", inputs)


def menu(name, value):
    return t.menu(EXT, name, value)


def synth(name):
    return sp("useSynth", SYNTH=menu("synths", name))


def fx(name):
    return sp("useFx", FX=menu("fx", name))


def also_fx(name):
    return sp("addFx", FX=menu("fx", name))


def sound_opt(name, value):
    return sp("setSoundOpt", OPT=menu("soundopts", name), VALUE=value if isinstance(value, list) else num(value))


def fx_opt(name, value):
    return sp("setFxOpt", OPT=menu("fxopts", name), VALUE=value if isinstance(value, list) else num(value))


def sample_opt(name, value):
    return sp("setSampleOpt", OPT=menu("sampleopts", name), VALUE=num(value))


def loud(v):
    return sp("setAmp", AMP=num(v))


def sample(name):
    return sp("playSample", SAMPLE=menu("samples", name))


def rest(beats):
    return sp("sleepBeats", BEATS=num(beats))


def live_loop(name, body, sync=None):
    if sync:
        return sp("liveLoopSynced", NAME=txt(name), WITH=txt(sync), SUBSTACK=t.substack(body))
    return sp("liveLoop", NAME=txt(name), SUBSTACK=t.substack(body))


def part_done(name):
    return t.block("data_setvariableto", {"VALUE": txt(1)}, {"VARIABLE": list(part_on[name])})


def times(a, b):
    return t.reporter("operator_multiply", {"NUM1": a, "NUM2": num(b)})


def minus(a, b):
    return t.reporter("operator_subtract", {"NUM1": a, "NUM2": num(b)})


def plus(a, b):
    return t.reporter("operator_add", {"NUM1": a, "NUM2": num(b)})


def note_arg(spec):
    """An argument reporter dropped into a note slot (keeps a note shadow behind it)."""
    return [3, spec[1], t.note(60)[1]]


# ============================================================ the sounds
# Each instrument is a custom block that layers two sounds. The layering and the
# sample tweaks are what make it sound like a record rather than a toy.

# Drums: a thumpy kick under a clicky one; bright hats; snare with a clap on top.
t.define("kick hit", 2500, 40, [
    loud(2.2), sp("clearSampleOpts"), sample_opt("lpf", 95), sample("bd_haus"),
    loud(1.0), sp("clearSampleOpts"), sample_opt("rate", 0.9), sample_opt("hpf", 40), sample("bd_tek"),
])
t.define("hat hit", 2500, 400, [
    loud(1.8), sp("clearSampleOpts"), sample_opt("rate", 1.4), sample_opt("hpf", 90), sample("drum_cymbal_closed"),
])
t.define("ghost hat", 2500, 640, [
    loud(0.5), sp("clearSampleOpts"), sample_opt("rate", 1.4), sample_opt("hpf", 90), sample("drum_cymbal_closed"),
])
t.define("open hat hit", 2500, 880, [
    loud(0.8), sp("clearSampleOpts"), sample_opt("rate", 1.25), sample_opt("finish", 0.2), sample_opt("hpf", 90), sample("drum_cymbal_open"),
])
t.define("clap hit", 2500, 1160, [
    loud(1.4), sp("clearSampleOpts"), sample_opt("rate", 1.05), sample("drum_snare_soft"),
    loud(1.6), sp("clearSampleOpts"), sample_opt("rate", 1.1), sample("perc_snap"),
])

# Bass note: a pure sine for weight plus a filtered saw for tone.
t.define("bass note", 3100, 40, [
    synth("sine"), sound_opt("attack", 0.005), sound_opt("release", times(t.arg("beats"), 0.85)), loud(1.6),
    sp("playNote", NOTE=note_arg(t.arg("note"))),
    synth("saw"), sound_opt("attack", 0.005), sound_opt("cutoff", 100), sound_opt("res", 0.25), loud(1.0),
    sp("playNoteFor", NOTE=note_arg(t.arg("note")), BEATS=t.arg("beats")),
], args=("note", "beats"))

# Chord note (MIDI numbers): pluck, pluck an octave down, and a wide prophet pad on top.
t.define("chord note", 3100, 500, [
    synth("pluck"), loud(2.8), sp("playNote", NOTE=note_arg(t.arg("note"))),
    synth("prophet"), sound_opt("cutoff", 126), sound_opt("detune", 0.25), sound_opt("release", times(t.arg("beats"), 0.9)), loud(0.9),
    sp("playNote", NOTE=note_arg(t.arg("note"))),
    synth("pluck"), loud(1.0),
    sp("playNoteFor", NOTE=note_arg(minus(t.arg("note"), 12)), BEATS=t.arg("beats")),
], args=("note", "beats"))

# Lead note: blade plus a detuned dsaw.
t.define("lead note", 3100, 960, [
    synth("blade"), sound_opt("cutoff", 130), sound_opt("release", times(t.arg("beats"), 0.9)), loud(1.1),
    sp("playNote", NOTE=note_arg(t.arg("note"))),
    synth("dsaw"), sound_opt("cutoff", 126), sound_opt("detune", 0.2), loud(0.55),
    sp("playNoteFor", NOTE=note_arg(t.arg("note")), BEATS=t.arg("beats")),
], args=("note", "beats"))

# Sung note (MIDI numbers): the vowel filter changes shape per syllable; quiet octave on top.
t.define("sing", 3100, 1420, [
    fx_opt("vowel_sound", t.arg("vowel")),
    synth("dsaw"), sound_opt("detune", 0.15), sound_opt("release", times(t.arg("beats"), 0.9)), loud(0.45),
    sp("playNote", NOTE=note_arg(t.arg("note"))),
    loud(0.15),
    sp("playNoteFor", NOTE=note_arg(plus(t.arg("note"), 12)), BEATS=t.arg("beats")),
], args=("note", "beats", "vowel"))


# ============================================================ the parts
def bass_note(n, beats):
    return t.call("bass note", txt(n), num(beats))


def lead_note(n, beats):
    return t.call("lead note", txt(n), num(beats))


def chord_note(midi, beats):
    return t.call("chord note", num(midi), num(beats))


def sing(midi, beats, vowel):
    return t.call("sing", num(midi), num(beats), num(vowel))


t.define("drums", 700, 40, [
    fx("compressor"), fx_opt("threshold", 0.3), fx_opt("slope_above", 0.3),
    live_loop("kick", [
        t.block("control_repeat", {"TIMES": whole(2), "SUBSTACK": t.substack([
            t.call("kick hit"), t.call("ghost hat"), rest(0.5), t.call("hat hit"), rest(0.5),
            t.call("kick hit"), rest(0.5), t.call("hat hit"), t.call("open hat hit"), rest(0.5),
        ])}),
    ]),
    fx("reverb"), fx_opt("room", 0.4), fx_opt("mix", 0.18),
    live_loop("hats", [rest(1), t.call("clap hit"), rest(2), t.call("clap hit"), rest(1)], sync="kick"),
    part_done("drums"),
])

t.define("lead", 700, 700, [
    fx("reverb"), fx_opt("room", 0.6), fx_opt("mix", 0.25),
    also_fx("ping_pong"), fx_opt("phase", 0.75), fx_opt("feedback", 0.3), fx_opt("mix", 0.25),
    live_loop("lead", [
        lead_note("e5", 0.5), lead_note("d5", 0.5), lead_note("b4", 0.5), lead_note("a4", 0.5),
        lead_note("g4", 0.5), lead_note("a4", 0.5), lead_note("g4", 0.5), lead_note("d4", 0.25), lead_note("e4", 0.25),
    ], sync="hats"),
    part_done("lead"),
])

# Roots land a sixteenth early, rest, three more, two-note pickup; then the walk-down.
t.define("bass", 1300, 40, [
    fx("compressor"), fx_opt("threshold", 0.35), fx_opt("slope_above", 0.4),
    also_fx("lpf"), fx_opt("cutoff", 118),
    live_loop("bass", [
        rest(1), bass_note("a1", 1), bass_note("a1", 1), bass_note("a1", 0.5), bass_note("b1", 0.25), bass_note("c2", 0.25),
        rest(1), bass_note("c2", 1), bass_note("c2", 1), bass_note("c2", 0.5), bass_note("d2", 0.25), bass_note("e2", 0.25),
        rest(1), bass_note("e2", 1), bass_note("e2", 1), bass_note("e2", 1),
        bass_note("fs2", 0.5), bass_note("e2", 0.5), bass_note("d2", 0.5), bass_note("c2", 0.5),
        bass_note("b1", 0.5), bass_note("a1", 0.5), bass_note("g1", 0.75), bass_note("a1", 0.25),
    ], sync="hats"),
    part_done("bass"),
])

# The vocoder chant, two bars, through a vowel filter (b3=59 g3=55 fs3=54 a3=57).
VOX = [(59, 0.5), (55, 1), (55, 0.5), (54, 0.5), (55, 1), (57, 0.5), (57, 0.5), (55, 1), (54, 1), (55, 1), (59, 0.5)]
VOWELS = [1, 5, 2, 4]
t.define("voice", 1300, 900, [
    fx("reverb"), fx_opt("room", 0.5), fx_opt("mix", 0.2),
    also_fx("hpf"), fx_opt("cutoff", 55),
    also_fx("vowel"), fx_opt("voice", 3), fx_opt("mix", 0.85),
    live_loop("voice", [sing(n, d, VOWELS[i % 4]) for i, (n, d) in enumerate(VOX)], sync="bass"),
    part_done("voice"),
])

# The plucked arpeggio (e5=76 g5=79 b4=71 d5=74 a5=81), pumped by a slicer so it breathes with the kick.
chord_body = []
for arp in ([76, 79, 71, 74], [81, 79, 71, 74]):
    chord_body += [chord_note(m, d) for m, d in zip(arp, [0.75, 0.75, 0.5, 0.5])] + [rest(1.5)]
t.define("chords", 1900, 40, [
    fx("reverb"), fx_opt("room", 0.75), fx_opt("mix", 0.3),
    also_fx("slicer"), fx_opt("phase", 1), fx_opt("wave", 1), fx_opt("invert_wave", 1), fx_opt("pulse_width", 0.85), fx_opt("smooth", 0.03), fx_opt("mix", 0.75),
    also_fx("hpf"), fx_opt("cutoff", 60),
    live_loop("chords", chord_body, sync="bass"),
    part_done("chords"),
])


# --- the arrangement: bring the parts in as Sonic Pi counts the bars ---
def wait_bars(bars):
    return t.block("control_wait_until", {"CONDITION": t.boolean("operator_gt", {
        "OPERAND1": t.reporter("sonicpi_cueCount", {"NAME": txt("hats")}), "OPERAND2": txt(bars)})})


t.script(40, 40, [
    t.block("event_whenflagclicked"),
    sp("stopAll"),
    t.block("data_setvariableto", {"VALUE": txt(0)}, {"VARIABLE": list(syllable)}),
    t.block("looks_switchbackdropto", {"BACKDROP": t.shadow("looks_backdrops", "BACKDROP", "magenta")}),
    t.block("control_wait", {"DURATION": posnum(0.5)}),
    sp("setBpm", BPM=num(121)),
    t.call("drums"),
    wait_bars(4), t.call("lead"),
    wait_bars(8), t.call("bass"),
    wait_bars(16), t.call("voice"),
    wait_bars(24), t.call("chords"),
])
t.script(40, 700, [sp("whenLoopRepeats", NAME=txt("hats")), t.block("looks_nextbackdrop")])
t.script(40, 820, [sp("whenLoopSound", NAME=txt("voice")),
                   t.block("data_changevariableby", {"VALUE": num(1)}, {"VARIABLE": list(syllable)})])
t.script(40, 960, [t.block("event_whenkeypressed", {}, {"KEY_OPTION": ["space", None]}), sp("stopAll")])

# number keys toggle each part on and off
for i, (k, name) in enumerate(zip("12345", PARTS)):
    t.script(40, 1100 + i * 220, [
        t.block("event_whenkeypressed", {}, {"KEY_OPTION": [k, None]}),
        t.block("control_if_else", {
            "CONDITION": t.boolean("operator_equals", {"OPERAND1": var_input(part_on[name]), "OPERAND2": txt(1)}),
            "SUBSTACK": t.substack([sp("stopLoop", NAME=txt(l)) for l in LOOPS[name]] +
                                   [t.block("data_setvariableto", {"VALUE": txt(0)}, {"VARIABLE": list(part_on[name])})]),
            "SUBSTACK2": t.substack([t.call(name)]),
        }),
    ])

t.comment(40, -260, "AROUND THE WORLD, built entirely from blocks. Start Sonic Scratch first, then press the green flag.\n"
          "Each part of the song is a custom block on the right. Inside each one, a 'live loop' block\n"
          "holds the notes; Sonic Pi keeps it repeating in perfect time. The parts come in one at a time\n"
          "as Sonic Pi counts the bars. Everything that moves is triggered by the live loops themselves.\n"
          "Keys 1-5 switch parts on and off: drums, lead synth, bass, voice, chords. Space stops.",
          width=700, height=130)


# --- Robots ---
def robot_sprite(name, helmet, x, first_half):
    r = Target(name)
    robot_costumes(r, helmet)
    r.x, r.y, r.size = x, 92, 60
    r.script(40, 40, [
        r.block("event_whenflagclicked"),
        r.block("looks_show"),
        r.block("looks_switchcostumeto", {"COSTUME": r.shadow("looks_costume", "COSTUME", "arms down")}),
        r.block("looks_say", {"MESSAGE": txt("")}),
    ])
    r.script(40, 300, [r.block("sonicpi_whenLoopRepeats", {"NAME": txt("kick")}), r.block("looks_nextcostume")])
    # Take turns singing: four syllables each, using the shared syllable counter to pick the word.
    n_minus_1 = lambda: r.reporter("operator_subtract", {"NUM1": var_input(syllable), "NUM2": num(1)})
    my_turn = r.boolean("operator_lt", {
        "OPERAND1": r.reporter("operator_mod", {"NUM1": n_minus_1(), "NUM2": num(8)}), "OPERAND2": txt(4)})
    if not first_half:
        my_turn = r.boolean("operator_not", {"OPERAND": my_turn})
    word = r.reporter("data_itemoflist", {"INDEX": r.reporter("operator_add", {
        "NUM1": r.reporter("operator_mod", {"NUM1": n_minus_1(), "NUM2": num(4)}), "NUM2": num(1)})},
        {"LIST": list(words)}, shadow=(7, "1"))
    r.script(40, 460, [
        r.block("sonicpi_whenLoopSound", {"NAME": txt("voice")}),
        r.block("control_if_else", {"CONDITION": my_turn,
                                    "SUBSTACK": r.substack([r.block("looks_say", {"MESSAGE": word})]),
                                    "SUBSTACK2": r.substack([r.block("looks_say", {"MESSAGE": txt("")})])}),
    ])
    return r


thomas = robot_sprite("Thomas", "silver", -42, True)
guy = robot_sprite("Guy-Man", "gold", 42, False)


# --- Dancer groups: hidden until their instrument starts, then move with it ---
def dancers(name, figure_fn, poses, spacing, count, w, h, x, y, size, hat, loop):
    d = Target(name)
    for i, s in enumerate(group(figure_fn, poses, spacing, count, w, h)):
        d.costume(f"pose {i + 1}", s, (w + spacing * (count - 1)) / 2, h / 2)
    d.x, d.y, d.size = x, y, size
    d.visible = False
    d.script(40, 40, [d.block("event_whenflagclicked"), d.block("looks_hide"),
                      d.block("looks_switchcostumeto", {"COSTUME": d.shadow("looks_costume", "COSTUME", "pose 1")})])
    d.script(40, 260, [d.block(f"sonicpi_{hat}", {"NAME": txt(loop)}), d.block("looks_show"), d.block("looks_nextcostume")])
    return d


mummies = dancers("Mummies", mummy, [0, 1], 50, 4, 70, 132, -150, -95, 55, "whenLoopRepeats", "kick")
skeletons = dancers("Skeletons", skeleton, [0, 1], 50, 4, 70, 132, 150, -95, 55, "whenLoopSound", "lead")
athletes = dancers("Athletes", athlete, [0, 1, 2], 50, 3, 70, 150, -95, -125, 50, "whenLoopSound", "bass")
swimmers = dancers("Swimmers", swimmer, [0, 1], 50, 3, 70, 132, 95, -125, 50, "whenLoopSound", "chords")

n = write_sb3(OUT, stage, [mummies, skeletons, athletes, swimmers, thomas, guy], EXT, EXT_URL)
raw = sum(1 for tt in [stage, mummies, skeletons, athletes, swimmers, thomas, guy]
          for b in tt.blocks.values() if b["opcode"] == "sonicpi_runCode")
print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {n} blocks, {raw} raw-code blocks)")
