#!/usr/bin/env python3
"""Builds demo/happy.sb3: a blocks-only Scratch cover of Pharrell Williams' "Happy",
with a crowd of little yellow dancers who move to the beat cues coming back from Sonic Pi.

Transcribed from Songsterr tabs at 160 bpm: drums, claps, guitar stabs and bass from
"Pharrell Williams - Happy" (4185030), the chorus vocal line from "Happy;)" (3465534).

Run: python3 demo/make-happy.py
"""
import os
from sb3lib import Target, num, posnum, txt, var_input, write_sb3

EXT = "sonicpi"
EXT_URL = "http://localhost:8000/sonic-pi-blocks.js"
OUT = os.path.join(os.path.dirname(__file__), "happy.sb3")

# ============================================================ the art
YELLOW, BLUE, GOGGLE, SKIN_DARK = "#f7d31a", "#2b5fb3", "#8e9aa6", "#1b1b1b"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def yellow_fellow(pose, eyes=2, banana=False, i=0):
    """One little yellow dancer. pose 0: arms down; 1: arms up; 2: one arm up (waving)."""
    # Arms are outlined so a raised arm still reads against the yellow body.
    arm = lambda x, y, h: f'<rect x="{x}" y="{y}" width="10" height="{h}" rx="5" fill="{YELLOW}" stroke="#c9a400" stroke-width="1.5"/>'
    arm_up_l, arm_dn_l = arm(1, 26, 44), arm(4, 66, 36)
    arm_up_r, arm_dn_r = arm(59, 26, 44), arm(56, 66, 36)
    if pose == 1:
        arms = arm_up_l + arm_up_r
    elif pose == 2:
        arms = arm_dn_l + arm_up_r
    else:
        arms = arm_dn_l + arm_dn_r
    if banana:
        # Banana held aloft, swapping hands with the pose.
        right = '<path d="M62 26 q2 -22 -20 -24 q14 6 14 24 z" fill="#ffe14d" stroke="#b58900" stroke-width="1.5"/>'
        left = '<path d="M8 26 q-2 -22 20 -24 q-14 6 -14 24 z" fill="#ffe14d" stroke="#b58900" stroke-width="1.5"/>'
        arms = (arm_up_l + arm_dn_r + left) if pose == 1 else (arm_dn_l + arm_up_r + right)
    if eyes == 1:
        goggles = (f'<rect x="12" y="28" width="46" height="8" fill="{SKIN_DARK}"/>'
                   f'<circle cx="35" cy="32" r="13" fill="{GOGGLE}"/><circle cx="35" cy="32" r="9" fill="#fff"/>'
                   f'<circle cx="{35 + (i % 3) - 1}" cy="32" r="4" fill="#5a3a1a"/><circle cx="{35 + (i % 3) - 1}" cy="32" r="1.8" fill="#000"/>')
    else:
        goggles = (f'<rect x="10" y="28" width="50" height="8" fill="{SKIN_DARK}"/>'
                   f'<circle cx="26" cy="32" r="10" fill="{GOGGLE}"/><circle cx="26" cy="32" r="7" fill="#fff"/><circle cx="27" cy="32" r="3" fill="#5a3a1a"/>'
                   f'<circle cx="44" cy="32" r="10" fill="{GOGGLE}"/><circle cx="44" cy="32" r="7" fill="#fff"/><circle cx="45" cy="32" r="3" fill="#5a3a1a"/>')
    hair = ''.join(f'<path d="M{30 + k * 5} 8 q{-2 + k} -8 {k - 2} -12" stroke="{SKIN_DARK}" stroke-width="1.5" fill="none"/>' for k in range(3))
    smile = '<path d="M26 48 q9 8 18 0" stroke="#3a1f0a" stroke-width="2.5" fill="none" stroke-linecap="round"/>'
    return (f'<rect x="20" y="96" width="12" height="20" rx="4" fill="{BLUE}"/><rect x="38" y="96" width="12" height="20" rx="4" fill="{BLUE}"/>'
            f'<rect x="16" y="112" width="18" height="8" rx="3" fill="#111"/><rect x="36" y="112" width="18" height="8" rx="3" fill="#111"/>'
            f'<rect x="12" y="8" width="46" height="96" rx="23" fill="{YELLOW}"/>'
            f'<path d="M12 66 h46 v20 a23 23 0 0 1 -46 0 z" fill="{BLUE}"/>'
            f'<rect x="20" y="52" width="6" height="16" fill="{BLUE}"/><rect x="44" y="52" width="6" height="16" fill="{BLUE}"/>'
            f'<rect x="28" y="66" width="14" height="12" rx="2" fill="#1f4a8f"/>'
            f'{arms}{hair}{goggles}{smile}')


def group(poses, count, spacing, w, h, **kw):
    out = []
    for pose in poses:
        parts = ''.join(f'<g transform="translate({i * spacing} 0)">{yellow_fellow((pose + i) % 2 if pose < 2 else pose, eyes=(1 if i % 2 else 2), i=i, **kw)}</g>'
                        for i in range(count))
        out.append(svg(w + spacing * (count - 1), h, parts))
    return out


def sun():
    rays = ''.join(f'<polygon points="60,4 66,22 54,22" fill="#ffd23f" transform="rotate({a} 60 60)"/>' for a in range(0, 360, 30))
    return svg(120, 120, rays + '<circle cx="60" cy="60" r="34" fill="#ffb703"/><circle cx="60" cy="60" r="28" fill="#ffd23f"/>'
               '<circle cx="50" cy="56" r="3" fill="#7a4a00"/><circle cx="70" cy="56" r="3" fill="#7a4a00"/>'
               '<path d="M48 66 q12 10 24 0" stroke="#7a4a00" stroke-width="3" fill="none" stroke-linecap="round"/>')


def backdrop(top, bottom):
    clouds = ''.join(f'<g transform="translate({x} {y})" opacity="0.9"><ellipse cx="0" cy="0" rx="34" ry="14" fill="#fff"/>'
                     f'<ellipse cx="-18" cy="6" rx="20" ry="11" fill="#fff"/><ellipse cx="20" cy="6" rx="22" ry="12" fill="#fff"/></g>'
                     for x, y in [(90, 70), (330, 50), (420, 110)])
    return svg(480, 360,
               f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
               '<rect width="480" height="360" fill="url(#sky)"/>' + clouds +
               '<ellipse cx="240" cy="380" rx="340" ry="110" fill="#5cb85c"/><ellipse cx="240" cy="395" rx="260" ry="80" fill="#4caf50"/>'
               + ''.join(f'<circle cx="{x}" cy="{y}" r="5" fill="{c}"/>' for x, y, c in
                         [(60, 300, "#ff5e8a"), (120, 320, "#fff"), (400, 305, "#ff9f1c"), (450, 330, "#fff"), (30, 335, "#ff9f1c")]))


# ============================================================ the project
stage = Target("Stage")
stage.is_stage = True
for name, top, bottom in [("morning", "#6fc3ff", "#d9f2ff"), ("noon", "#3aa0ff", "#bfe6ff"), ("sunset", "#ff9a5c", "#ffe0b3")]:
    stage.costume(name, backdrop(top, bottom), 240, 180)

PARTS = ["drums", "claps", "verse", "chorus", "melody"]
LOOPS = {"drums": ["beat", "drums"], "claps": ["claps"], "verse": ["verse_chords", "verse_bass"],
         "chorus": ["chorus_chords", "chorus_bass"], "melody": ["melody"]}
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


def sound_opt(name, value):
    return sp("setSoundOpt", OPT=menu("soundopts", name), VALUE=num(value))


def fx_opt(name, value):
    return sp("setFxOpt", OPT=menu("fxopts", name), VALUE=num(value))


def loud(v):
    return sp("setAmp", AMP=num(v))


def sample(name):
    return sp("playSample", SAMPLE=menu("samples", name))


def note_for(n, beats):
    return sp("playNoteFor", NOTE=t.note(n), BEATS=num(beats))


def chord(root, kind):
    return sp("playChord", NOTE=txt(root), CHORD=menu("chords", kind))


def rest(beats):
    return sp("sleepBeats", BEATS=num(beats))


def live_loop(name, body, sync=None):
    if sync:
        return sp("liveLoopSynced", NAME=txt(name), WITH=txt(sync), SUBSTACK=t.substack(body))
    return sp("liveLoop", NAME=txt(name), SUBSTACK=t.substack(body))


def set_on(name, value):
    return t.block("data_setvariableto", {"VALUE": txt(value)}, {"VARIABLE": list(part_on[name])})


def stabs(pattern):
    """[(root, kind, beats) or (None, None, beats)] -> chord stab then sleep, or a rest."""
    out = []
    for root, kind, beats in pattern:
        if root:
            out.append(chord(root, kind))
        out.append(rest(beats))
    return out


def notes(pattern):
    """[(note or None, beats)] -> play-for blocks and rests."""
    return [note_for(n, b) if n else rest(b) for n, b in pattern]


# --- drums: a silent 'beat' loop for the dancers to bob to, then the groove and the claps ---
t.define("drums", 700, 40, [
    fx("none"), loud(1),
    live_loop("beat", [rest(1)]),
    live_loop("drums", [
        loud(1.4), sample("bd_haus"), loud(0.4), sample("drum_cymbal_closed"), rest(1),
        loud(0.8), sample("drum_snare_soft"), loud(0.4), sample("drum_cymbal_closed"), rest(0.5),
        loud(1.4), sample("bd_haus"), rest(0.5),
        loud(0.35), sample("drum_cymbal_open"), rest(0.5),
        loud(1.4), sample("bd_haus"), rest(0.5),
        loud(0.8), sample("drum_snare_soft"), loud(0.4), sample("drum_cymbal_closed"), rest(0.5),
        loud(1.4), sample("bd_haus"), rest(0.5),
    ], sync="beat"),
    set_on("drums", 1),
])

t.define("claps", 700, 1000, [
    fx("none"), loud(1.2),
    live_loop("claps", [rest(1), sample("perc_snap"), rest(2), sample("perc_snap"), rest(1)], sync="drums"),
    set_on("claps", 1),
])

# --- verse: the F7 / G stabs and the walking bass, four bars each ---
VERSE_STABS = [
    ("f3", "dom7", 1), ("g3", "major", 1), ("g3", "major", 1), (None, None, 0.5), ("g3", "major", 0.5),
    ("g3", "major", 1), ("g3", "major", 1), (None, None, 0.5), ("g3", "major", 0.5), ("g3", "major", 0.5), ("g3", "major", 0.5),
    ("f3", "dom7", 1), ("ab3", "major", 1), ("bb3", "major", 1), (None, None, 0.5), ("c4", "major", 0.5),
    (None, None, 1.5), ("bb3", "major", 0.5), (None, None, 0.5), ("bb3", "major", 0.5), ("bb3", "major", 0.5), ("bb3", "major", 0.5),
]
VERSE_BASS = [
    ("f1", 1), (None, 3),
    (None, 4),
    ("f2", 1), ("ab2", 1), ("bb2", 1), ("ab2", 0.5), ("c3", 0.5),
    (None, 0.5), ("bb2", 1), ("ab2", 1), ("f2", 0.5), ("ab2", 0.5), ("bb2", 0.5),
]
t.define("verse", 1300, 40, [
    sp("stopLoop", NAME=txt("chorus_chords")), sp("stopLoop", NAME=txt("chorus_bass")), set_on("chorus", 0),
    synth("pluck"), sound_opt("release", 0.6), loud(0.8), fx("none"),
    live_loop("verse_chords", stabs(VERSE_STABS), sync="drums"),
    synth("tb303"), sound_opt("cutoff", 82), sound_opt("res", 0.1), loud(1.2),
    live_loop("verse_bass", notes(VERSE_BASS), sync="drums"),
    set_on("verse", 1),
])

# --- chorus: Db, C, F, F stabs and bass, four bars ---
CHORUS_STABS = [
    ("cs4", "major", 1), (None, None, 0.5), ("cs4", "major", 0.5), (None, None, 1), ("cs4", "major", 0.5), (None, None, 0.5),
    ("c4", "minor7", 1), (None, None, 0.5), ("c4", "minor7", 0.5), (None, None, 1), ("c4", "minor7", 0.5), ("c4", "minor7", 0.5),
    ("f3", "dom7", 1), (None, None, 0.5), ("f3", "dom7", 0.5), ("g3", "major", 1), (None, None, 0.5), ("f3", "dom7", 0.5),
    ("f3", "dom7", 1), (None, None, 0.5), ("f3", "dom7", 0.5), (None, None, 2),
]
CHORUS_BASS = [
    ("cs2", 1), (None, 0.5), ("cs2", 0.5), ("cs2", 0.5), ("gs2", 0.5), ("cs3", 0.5), ("gs2", 0.5),
    ("c2", 0.5), ("c2", 0.5), (None, 0.5), ("c2", 0.5), ("c2", 0.5), ("g2", 0.5), ("c3", 1),
    ("f2", 0.5), ("f2", 0.5), (None, 0.5), ("f2", 0.5), ("f2", 1), ("f3", 1),
    ("f2", 0.5), ("f2", 0.5), (None, 0.5), ("f2", 0.5), ("f2", 1), (None, 1),
]
t.define("chorus", 1300, 900, [
    sp("stopLoop", NAME=txt("verse_chords")), sp("stopLoop", NAME=txt("verse_bass")), set_on("verse", 0),
    synth("pluck"), sound_opt("release", 0.6), loud(0.8), fx("none"),
    live_loop("chorus_chords", stabs(CHORUS_STABS), sync="drums"),
    synth("tb303"), sound_opt("cutoff", 82), sound_opt("res", 0.1), loud(1.2),
    live_loop("chorus_bass", notes(CHORUS_BASS), sync="drums"),
    set_on("chorus", 1),
])

# --- melody: the chorus vocal line, eight bars ---
MELODY = [
    (None, 1), ("f4", 0.5), ("eb4", 0.5), ("f4", 1), ("eb4", 0.5), ("f4", 0.5),
    ("f4", 0.5), ("f4", 1), ("f4", 1), (None, 0.5), ("f4", 0.5), ("eb4", 0.5),
    ("g4", 1), ("f4", 1), ("eb4", 1), ("c4", 0.5), ("f4", 0.5),
    (None, 0.5), ("eb4", 0.5), (None, 0.5), ("c4", 0.5), ("c4", 0.5), (None, 0.5), ("eb4", 0.5), (None, 0.5),
    ("f4", 0.5), ("eb4", 0.5), ("f4", 0.5), ("eb4", 0.5), ("f4", 1.5), ("g4", 0.5),
    (None, 0.5), ("eb4", 0.5), (None, 0.5), ("c4", 0.5), ("c4", 0.5), (None, 0.5), ("eb4", 0.5), (None, 0.5),
    ("f4", 0.5), ("eb4", 0.5), ("f4", 0.5), (None, 0.5), ("f4", 1), ("eb4", 0.5), ("f4", 1),
    ("bb3", 0.5), (None, 0.5), ("c4", 0.5), ("c4", 0.5), (None, 0.5), ("eb4", 0.5), (None, 0.5),
]
assert sum(b for _, b in MELODY) == 32, sum(b for _, b in MELODY)
t.define("melody", 1900, 40, [
    synth("prophet"), sound_opt("cutoff", 95), loud(0.7),
    fx("reverb"), fx_opt("room", 0.6), fx_opt("mix", 0.3),
    live_loop("melody", notes(MELODY), sync="chorus_chords"),
    set_on("melody", 1),
])


# --- the arrangement: bring the parts in as Sonic Pi counts the bars ---
def wait_bars(bars):
    return t.block("control_wait_until", {"CONDITION": t.boolean("operator_gt", {
        "OPERAND1": t.reporter("sonicpi_cueCount", {"NAME": txt("drums")}), "OPERAND2": txt(bars)})})


t.script(40, 40, [
    t.block("event_whenflagclicked"),
    sp("stopAll"),
    t.block("looks_switchbackdropto", {"BACKDROP": t.shadow("looks_backdrops", "BACKDROP", "morning")}),
    t.block("control_wait", {"DURATION": posnum(0.5)}),
    sp("setBpm", BPM=num(160)),
    t.call("drums"),
    wait_bars(2), t.call("claps"),
    wait_bars(6), t.call("verse"),
    wait_bars(14), t.call("chorus"),
    wait_bars(15), t.call("melody"),
])
t.script(40, 700, [sp("whenLoopRepeats", NAME=txt("drums")), t.block("looks_nextbackdrop")])
t.script(40, 820, [t.block("event_whenkeypressed", {}, {"KEY_OPTION": ["space", None]}), sp("stopAll")])

# number keys toggle each part on and off
for i, (k, name) in enumerate(zip("12345", PARTS)):
    t.script(40, 960 + i * 220, [
        t.block("event_whenkeypressed", {}, {"KEY_OPTION": [k, None]}),
        t.block("control_if_else", {
            "CONDITION": t.boolean("operator_equals", {"OPERAND1": var_input(part_on[name]), "OPERAND2": txt(1)}),
            "SUBSTACK": t.substack([sp("stopLoop", NAME=txt(l)) for l in LOOPS[name]] + [set_on(name, 0)]),
            "SUBSTACK2": t.substack([t.call(name)]),
        }),
    ])

t.comment(40, -260, "HAPPY, built entirely from blocks. Start Sonic Scratch first, then press the green flag.\n"
          "Each part of the song is a custom block on the right. Inside each one, a 'live loop' block\n"
          "holds the notes; Sonic Pi keeps it repeating in perfect time. Drums, then claps, then the verse,\n"
          "then the chorus with its tune. The dancers move on cues coming back from Sonic Pi.\n"
          "Keys 1-5 switch parts: drums, claps, verse, chorus, tune. Space stops.", width=700, height=130)


# --- Sprites ---
def dancers(name, poses, count, x, y, size, hat, loop, hidden_until_cue, banana=False):
    d = Target(name)
    w = 70
    for i, s in enumerate(group(poses, count, 62, w, 122, banana=banana)):
        d.costume(f"pose {i + 1}", s, (w + 62 * (count - 1)) / 2, 61)
    d.x, d.y, d.size = x, y, size
    d.visible = not hidden_until_cue
    flag = [d.block("event_whenflagclicked"),
            d.block("looks_switchcostumeto", {"COSTUME": d.shadow("looks_costume", "COSTUME", "pose 1")})]
    flag.append(d.block("looks_hide") if hidden_until_cue else d.block("looks_show"))
    d.script(40, 40, flag)
    d.script(40, 260, [d.block(f"sonicpi_{hat}", {"NAME": txt(loop)}), d.block("looks_show"), d.block("looks_nextcostume")])
    return d


# Bobbers nod on every beat of the silent 'beat' loop; jumpers leap on each clap;
# the banana crew wave on every note of the tune, and only turn up when it starts.
bobbers = dancers("Bobbers", [0, 1], 4, -120, -60, 60, "whenLoopRepeats", "beat", False)
jumpers = dancers("Jumpers", [0, 1], 3, 130, -70, 62, "whenLoopSound", "claps", False)
jumpers.script(40, 460, [
    jumpers.block("sonicpi_whenLoopSound", {"NAME": txt("claps")}),
    jumpers.block("motion_changeyby", {"DY": num(25)}),
    jumpers.block("control_wait", {"DURATION": posnum(0.12)}),
    jumpers.block("motion_changeyby", {"DY": num(-25)}),
])
bananas = dancers("Banana crew", [0, 1], 3, 0, -125, 55, "whenLoopSound", "melody", True, banana=True)

sunny = Target("Sun")
sunny.costume("sun", sun(), 60, 60)
sunny.x, sunny.y, sunny.size = 180, 130, 80
sunny.script(40, 40, [sunny.block("event_whenflagclicked"), sunny.block("looks_show"),
                      sunny.block("motion_pointindirection", {"DIRECTION": [1, [8, "90"]]})])
sunny.script(40, 220, [sunny.block("sonicpi_whenLoopRepeats", {"NAME": txt("beat")}),
                       sunny.block("motion_turnright", {"DEGREES": num(15)})])
sunny.script(40, 380, [sunny.block("sonicpi_whenLoopSound", {"NAME": txt("claps")}),
                       sunny.block("looks_changesizeby", {"CHANGE": num(12)}),
                       sunny.block("control_wait", {"DURATION": posnum(0.12)}),
                       sunny.block("looks_changesizeby", {"CHANGE": num(-12)})])

sprites = [sunny, bobbers, jumpers, bananas]
n = write_sb3(OUT, stage, sprites, EXT, EXT_URL)
raw = sum(1 for tt in [stage] + sprites for b in tt.blocks.values() if b["opcode"] == "sonicpi_runCode")
print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {n} blocks, {raw} raw-code blocks)")
