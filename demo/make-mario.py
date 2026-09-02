#!/usr/bin/env python3
"""Builds demo/mario.sb3: the Super Mario Bros. overworld theme (Koji Kondo) as chiptune,
built entirely from blocks, with a cartoon platformer scene that moves to the music.

Transcription: Songsterr tab s14064 (Koji Kondo - Super Mario Bros. Theme), tracks
Melody / Harmony / Triangle, bars 1-16 (intro, A section, B section, C section).
97 bpm as written there, i.e. the usual 194 bpm counted in eighths.

Run: python3 demo/make-mario.py
"""
import os
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sb3lib import Target, num, posnum, whole, txt, var_input, write_sb3  # noqa: E402

EXT = "sonicpi"
EXT_URL = "http://localhost:8000/sonic-pi-blocks.js"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mario.sb3")
BPM = 97

# ============================================================ the tune
# "note:beats" per bar. r = rest. Bars repeat a lot, so each part is built from
# sub-blocks: intro (bar 1), A (bars 2-3, played twice), B (bars 6-9, twice), C (14-16).
MELODY = {
    "intro": ["e5:1/4 e5:1/2 e5:1/2 c5:1/4 e5:1/2 g5:1/2 r:3/2"],
    "A": ["c5:3/4 g4:3/4 e4:3/4 a4:1/2 b4:1/2 as4:1/4 a4:1/2",
          "g4:1/3 e5:1/3 g5:1/3 a5:1/2 f5:1/4 g5:1/2 e5:1/2 c5:1/4 d5:1/4 b4:3/4"],
    "B": ["r:1/2 g5:1/4 fs5:1/4 f5:1/4 ds5:1/2 e5:1/2 gs4:1/4 a4:1/4 c5:1/2 a4:1/4 c5:1/4 d5:1/4",
          "r:1/2 g5:1/4 fs5:1/4 f5:1/4 ds5:1/2 e5:1/2 c6:1/2 c6:1/4 c6:1",
          "r:1/2 g5:1/4 fs5:1/4 f5:1/4 ds5:1/2 e5:1/2 gs4:1/4 a4:1/4 c5:1/2 a4:1/4 c5:1/4 d5:1/4",
          "r:1/2 ds5:3/4 d5:3/4 c5:3/4 r:1/2 r:3/4"],
    "C1": ["c5:1/4 c5:1/2 c5:1/2 c5:1/4 d5:1/2 e5:1/4 c5:1/2 a4:1/4 g4:1/2 r:1/2"],
    "C2": ["c5:1/4 c5:1/2 c5:1/2 c5:1/4 d5:1/4 e5:1/4 r:2"],
}
HARMONY = {
    "intro": ["fs4:1/4 fs4:1/2 fs4:1/2 fs4:1/4 fs4:1/2 b4:1/2 r:1/2 g4:1/2 r:1/2"],
    "A": ["e4:3/4 c4:3/4 g3:3/4 c4:1/2 d4:1/2 cs4:1/4 c4:1/2",
          "c4:1/3 g4:1/3 b4:1/3 c5:1/2 a4:1/4 b4:1/2 a4:1/2 e4:1/4 f4:1/4 d4:3/4"],
    "B": ["r:1/2 e5:1/4 ds5:1/4 d5:1/4 b4:1/2 c5:1/2 e4:1/4 f4:1/4 g4:1/2 c4:1/4 e4:1/4 f4:1/4",
          "r:1/2 e5:1/4 ds5:1/4 d5:1/4 b4:1/2 c5:1/2 f5:1/2 f5:1/4 f5:1",
          "r:1/2 e5:1/4 ds5:1/4 d5:1/4 b4:1/2 c5:1/2 e4:1/4 f4:1/4 g4:1/2 c4:1/4 e4:1/4 f4:1/4",
          "r:1/2 gs4:3/4 f4:3/4 e4:3/4 r:1/2 r:3/4"],
    "C1": ["gs4:1/4 gs4:1/2 gs4:1/2 gs4:1/4 as4:1/2 g4:1/4 e4:1/2 e4:1/4 c4:1/2 r:1/2"],
    "C2": ["gs4:1/4 gs4:1/2 gs4:1/2 gs4:1/4 as4:1/4 g4:1/4 r:2"],
}
BASS = {
    "intro": ["d2:1/4 d2:1/2 d2:1/2 d2:1/4 d2:1/2 g3:1/2 r:1/2 g2:1/2 r:1/2"],
    "A": ["g2:3/4 e2:3/4 c2:3/4 f2:1/2 g2:1/2 fs2:1/4 f2:1/2",
          "e2:1/3 c3:1/3 e3:1/3 f3:1/2 d3:1/4 e3:1/2 c3:1/2 a2:1/4 b2:1/4 g2:3/4"],
    "B": ["c2:3/4 g2:3/4 c3:1/2 f2:3/4 c3:1/4 c3:1/2 f2:1/2",
          "c2:3/4 e2:3/4 g2:1/4 c3:1/2 g4:1/2 g4:1/4 g4:1/2 g2:1/2",
          "c2:3/4 g2:3/4 c3:1/2 f2:3/4 c3:1/4 c3:1/2 f2:1/2",
          "c2:1/2 gs2:3/4 as2:3/4 c3:3/4 g2:1/4 g2:1/2 c2:1/2"],
    "C1": ["gs1:3/4 ds2:3/4 gs2:1/2 g2:3/4 c2:3/4 g1:1/2"],
    "C2": ["gs1:3/4 ds2:3/4 gs2:1/2 g2:3/4 c2:3/4 g1:1/2"],
}


def beats(frac):
    v = float(Fraction(frac))
    return int(v) if v == int(v) else round(v, 4)


# ============================================================ the art
# Real NES sprites, cut from sprite sheets and scaled up 3x (see demo/mario-sprites).
# 1 image pixel = 1 stage pixel, so a 16px NES sprite is 48px on the Scratch stage.
ART = os.path.join(os.path.dirname(__file__), "mario-sprites")


def png(name):
    with open(os.path.join(ART, f"{name}.png"), "rb") as f:
        return f.read()


def png_size(name):
    from struct import unpack
    d = png(name)
    return unpack(">II", d[16:24])


GROUND_Y = -60  # centre of a 48px sprite standing on the ground in the backdrop


# ============================================================ the project
stage = Target("Stage", is_stage=True)
for name in ("day", "sunset", "night"):
    stage.costume_png(name, png(f"backdrop-{name}"), 240, 180)

PARTS = ["drums", "bass", "melody", "harmony"]
part_on = {name: stage.var(f"{name} on", 0) for name in PARTS}
t = stage


def sp(op, **inputs):
    return t.block(f"sonicpi_{op}", inputs)


def menu(name, value):
    return t.menu(EXT, name, value)


def synth(name):
    return sp("useSynth", SYNTH=menu("synths", name))


def loud(v):
    return sp("setAmp", AMP=num(v))


def sample(name):
    return sp("playSample", SAMPLE=menu("samples", name))


def rest(b):
    return sp("sleepBeats", BEATS=num(b))


def note_for(n, b):
    return sp("playNoteFor", NOTE=t.note(n), BEATS=num(b))


def bars(text_bars):
    out = []
    for bar in text_bars:
        for tok in bar.split():
            n, d = tok.split(":")
            out.append(rest(beats(d)) if n == "r" else note_for(n, beats(d)))
    return out


def repeat(times, body):
    return t.block("control_repeat", {"TIMES": whole(times), "SUBSTACK": t.substack(body)})


def live_loop(name, body, sync=None):
    if sync:
        return sp("liveLoopSynced", NAME=txt(name), WITH=txt(sync), SUBSTACK=t.substack(body))
    return sp("liveLoop", NAME=txt(name), SUBSTACK=t.substack(body))


def part_done(name):
    return t.block("data_setvariableto", {"VALUE": txt(1)}, {"VARIABLE": list(part_on[name])})


def tune_part(name, tune, synth_name, amp, x, sync):
    """A part = one custom block holding a live loop that plays the 16-bar form
    intro, A A, B B, C1 C2 C1 using sub-blocks for the repeated bars."""
    t.define(f"{name} intro", x, 700, bars(tune["intro"]))
    t.define(f"{name} A", x, 1000, bars(tune["A"]))
    t.define(f"{name} B", x, 1500, bars(tune["B"]))
    t.define(f"{name} C", x, 2300, bars(tune["C1"]))
    t.define(name, x, 40, [
        synth(synth_name), loud(amp), sp("useFx", FX=menu("fx", "none")),
        live_loop(name, [
            t.call(f"{name} intro"),
            repeat(2, [t.call(f"{name} A")]),
            repeat(2, [t.call(f"{name} B")]),
            t.call(f"{name} C"),
            *bars(tune["C2"]),
            t.call(f"{name} C"),
        ], sync=sync),
        part_done(name),
    ])


# --- drums: the swung NES pattern, kick on 1 and 3, snare on 2 and 4, hats in between ---
def drum_beat(hit, hit_amp):
    return [loud(hit_amp), sample(hit), loud(0.35), sample("drum_cymbal_closed"), rest(0.5),
            sample("drum_cymbal_closed"), rest(beats("1/3")), sample("drum_cymbal_closed"), rest(beats("1/6"))]


t.define("drums", 700, 40, [
    sp("useFx", FX=menu("fx", "none")),
    live_loop("drums", [repeat(2, drum_beat("drum_heavy_kick", 1.0) + drum_beat("drum_snare_soft", 0.7))]),
    part_done("drums"),
])

# The NES had two pulse channels, a triangle channel and a noise channel.
# Bass follows the drums; melody and harmony follow the bass so all three start on the same bar.
tune_part("bass", BASS, "chipbass", 1.1, 1300, sync="drums")
tune_part("melody", MELODY, "square", 0.55, 1900, sync="drums")
tune_part("harmony", HARMONY, "chiplead", 0.35, 2500, sync="drums")


# --- the arrangement ---
def wait_bars(n):
    return t.block("control_wait_until", {"CONDITION": t.boolean("operator_gt", {
        "OPERAND1": t.reporter("sonicpi_cueCount", {"NAME": txt("drums")}), "OPERAND2": txt(n)})})


t.script(40, 40, [
    t.block("event_whenflagclicked"),
    sp("stopAll"),
    t.block("looks_switchbackdropto", {"BACKDROP": t.shadow("looks_backdrops", "BACKDROP", "day")}),
    t.block("control_wait", {"DURATION": posnum(0.5)}),
    sp("setBpm", BPM=num(BPM)),
    t.call("drums"),
    wait_bars(1),
    t.call("bass"), t.call("melody"), t.call("harmony"),
])
t.script(40, 560, [sp("whenLoopRepeats", NAME=txt("drums")), t.block("looks_nextbackdrop")])
t.script(40, 680, [t.block("event_whenkeypressed", {}, {"KEY_OPTION": ["space", None]}), sp("stopAll")])

for i, (k, name) in enumerate(zip("1234", PARTS)):
    t.script(40, 820 + i * 220, [
        t.block("event_whenkeypressed", {}, {"KEY_OPTION": [k, None]}),
        t.block("control_if_else", {
            "CONDITION": t.boolean("operator_equals", {"OPERAND1": var_input(part_on[name]), "OPERAND2": txt(1)}),
            "SUBSTACK": t.substack([sp("stopLoop", NAME=txt(name)),
                                    t.block("data_setvariableto", {"VALUE": txt(0)}, {"VARIABLE": list(part_on[name])})]),
            "SUBSTACK2": t.substack([t.call(name)]),
        }),
    ])

t.comment(40, -280, "SUPER MARIO BROS. THEME as chiptune, built entirely from blocks.\n"
          "Start Sonic Scratch first, then press the green flag. Drums start; a bar later the bass,\n"
          "melody and harmony all join on the same beat. Like the NES, there are two square-wave\n"
          "voices, a bass voice and drums. Each part is a custom block on the right; the repeated\n"
          "bars (A, B, C) are their own blocks so the tune is only written out once.\n"
          "Keys 1-4 switch parts on and off: drums, bass, melody, harmony. Space stops.",
          width=720, height=150)


# --- sprites ---
def sprite(name, costumes, x, y, hidden=False):
    """costumes: list of (costume name, png file name)."""
    s = Target(name)
    for cname, file in costumes:
        w, h = png_size(file)
        s.costume_png(cname, png(file), w / 2, h / 2)
    s.x, s.y, s.size, s.visible = x, y, 100, not hidden
    s.script(40, 40, [s.block("event_whenflagclicked"),
                      s.block("looks_hide" if hidden else "looks_show"),
                      s.block("looks_switchcostumeto", {"COSTUME": s.shadow("looks_costume", "COSTUME", costumes[0][0])}),
                      s.block("motion_gotoxy", {"X": num(x), "Y": num(y)})])
    return s


def hat(s, kind, loop):
    return s.block(f"sonicpi_{kind}", {"NAME": txt(loop)})


# Mario jumps on every bass note.
plumber = sprite("Mario", [("stand", "mario-stand"), ("jump", "mario-jump")], -150, GROUND_Y)
plumber.script(40, 300, [
    hat(plumber, "whenLoopSound", "bass"),
    plumber.block("looks_switchcostumeto", {"COSTUME": plumber.shadow("looks_costume", "COSTUME", "jump")}),
    plumber.block("motion_changeyby", {"DY": num(40)}),
    plumber.block("control_wait", {"DURATION": posnum(0.12)}),
    plumber.block("motion_changeyby", {"DY": num(-40)}),
    plumber.block("looks_switchcostumeto", {"COSTUME": plumber.shadow("looks_costume", "COSTUME", "stand")}),
])

# Question blocks shimmer on the harmony.
qblocks = sprite("Question Blocks", [("shine 1", "qrow1"), ("shine 2", "qrow2"), ("shine 3", "qrow3")], 40, 40)
qblocks.script(40, 300, [hat(qblocks, "whenLoopSound", "harmony"), qblocks.block("looks_nextcostume")])

# Coins appear with the melody and spin on every note.
coin = sprite("Coins", [("wide", "coinrow1"), ("mid", "coinrow2"), ("thin", "coinrow3")], 40, 110, hidden=True)
coin.script(40, 300, [hat(coin, "whenLoopSound", "melody"), coin.block("looks_show"), coin.block("looks_nextcostume")])

# Mushroom slides along once a bar.
shroom = sprite("Mushroom", [("mushroom", "mushroom")], 190, GROUND_Y)
shroom.script(40, 300, [
    hat(shroom, "whenLoopRepeats", "drums"),
    shroom.block("motion_changexby", {"DX": num(18)}),
    shroom.block("control_if", {"CONDITION": shroom.boolean("operator_gt", {"OPERAND1": shroom.reporter("motion_xposition"), "OPERAND2": txt(235)}),
                                "SUBSTACK": shroom.substack([shroom.block("motion_setx", {"X": num(-235)})])}),
])

# The Goomba plods left on every drum hit.
walk = sprite("Goomba", [("step 1", "goomba1"), ("step 2", "goomba2")], 120, GROUND_Y)
walk.script(40, 300, [
    hat(walk, "whenLoopSound", "drums"),
    walk.block("looks_nextcostume"),
    walk.block("motion_changexby", {"DX": num(-4)}),
    walk.block("control_if", {"CONDITION": walk.boolean("operator_lt", {"OPERAND1": walk.reporter("motion_xposition"), "OPERAND2": txt(-235)}),
                              "SUBSTACK": walk.substack([walk.block("motion_setx", {"X": num(235)})])}),
])

sprites = [walk, shroom, plumber, qblocks, coin]
n = write_sb3(OUT, stage, sprites, EXT, EXT_URL)
raw = sum(1 for tt in [stage] + sprites for b in tt.blocks.values() if b["opcode"] == "sonicpi_runCode")
print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {n} blocks, {raw} raw-code blocks)")
