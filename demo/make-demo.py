#!/usr/bin/env python3
"""Builds demo/sonic-pi-demo.sb3, a small Scratch project that shows off the Sonic Pi blocks.

Run: python3 demo/make-demo.py
Then in TurboWarp: File > Load from your computer > demo/sonic-pi-demo.sb3
"""
import os
from sb3lib import Target, num, posnum, whole, txt, var_input, write_sb3

EXT = "sonicpi"
EXT_URL = "http://localhost:8000/sonic-pi-blocks.js"
OUT = os.path.join(os.path.dirname(__file__), "sonic-pi-demo.sb3")

stage = Target("Stage", is_stage=True)
dj = Target("DJ")
i_var = dj.var("i", 0)


def sp(op, **inputs):
    return dj.block(f"sonicpi_{op}", inputs)


def menu(name, value):
    return dj.menu(EXT, name, value)


# ---- Script 1: green flag starts a drum loop and a bassline ----
dj.script(40, 40, [
    dj.block("event_whenflagclicked"),
    dj.block("looks_say", {"MESSAGE": txt("Starting the band...")}),
    sp("setBpm", BPM=num(110)),
    sp("useFx", FX=menu("fx", "none")),
    sp("liveLoop", NAME=txt("drums"), SUBSTACK=dj.substack([
        sp("playSample", SAMPLE=menu("samples", "bd_haus")),
        sp("sleepBeats", BEATS=num(0.5)),
        sp("playSample", SAMPLE=menu("samples", "drum_cymbal_closed")),
        sp("sleepBeats", BEATS=num(0.5)),
        sp("playSample", SAMPLE=menu("samples", "drum_snare_soft")),
        sp("sleepBeats", BEATS=num(0.5)),
        sp("playSample", SAMPLE=menu("samples", "drum_cymbal_closed")),
        sp("sleepBeats", BEATS=num(0.5)),
    ])),
    sp("useSynth", SYNTH=menu("synths", "tb303")),
    sp("liveLoopSynced", NAME=txt("bass"), WITH=txt("drums"), SUBSTACK=dj.substack([
        sp("playNoteFor", NOTE=dj.note("e2"), BEATS=num(1)),
        sp("playNoteFor", NOTE=dj.note("e2"), BEATS=num(0.5)),
        sp("playNoteFor", NOTE=dj.note("g2"), BEATS=num(0.5)),
        sp("playNoteFor", NOTE=dj.note("a2"), BEATS=num(1)),
        sp("playNoteFor", NOTE=dj.note("d2"), BEATS=num(1)),
    ])),
    dj.block("looks_say", {"MESSAGE": txt("Click me for a tune. Space = chord. Hold up arrow and move the mouse. S = stop.")}),
])

# ---- Script 2: the drum loop makes the sprite bounce, in time with Sonic Pi ----
dj.script(40, 720, [
    dj.block("sonicpi_whenLoopRepeats", {"NAME": txt("drums")}),
    dj.block("looks_changesizeby", {"CHANGE": num(15)}),
    dj.block("control_wait", {"DURATION": posnum(0.15)}),
    dj.block("looks_changesizeby", {"CHANGE": num(-15)}),
])


# ---- Script 3: click the sprite for a pentatonic run up and down ----
def scale_note():
    return dj.reporter("sonicpi_scaleNote", {
        "INDEX": var_input(i_var, 1),
        "ROOT": txt("c4"),
        "SCALE": menu("scales", "major_pentatonic"),
    })


dj.script(40, 950, [
    dj.block("event_whenthisspriteclicked"),
    sp("useSynth", SYNTH=menu("synths", "pluck")),
    sp("useFx", FX=menu("fx", "reverb")),
    dj.block("data_setvariableto", {"VALUE": txt(1)}, {"VARIABLE": list(i_var)}),
    dj.block("control_repeat", {"TIMES": whole(8), "SUBSTACK": dj.substack([
        sp("playNoteFor", NOTE=scale_note(), BEATS=num(0.25)),
        dj.block("looks_changeeffectby", {"CHANGE": num(25)}, {"EFFECT": ["COLOR", None]}),
        dj.block("data_changevariableby", {"VALUE": num(1)}, {"VARIABLE": list(i_var)}),
    ])}),
    dj.block("control_repeat", {"TIMES": whole(8), "SUBSTACK": dj.substack([
        dj.block("data_changevariableby", {"VALUE": num(-1)}, {"VARIABLE": list(i_var)}),
        sp("playNoteFor", NOTE=scale_note(), BEATS=num(0.25)),
        dj.block("looks_changeeffectby", {"CHANGE": num(-25)}, {"EFFECT": ["COLOR", None]}),
    ])}),
    dj.block("looks_cleargraphiceffects"),
])

# ---- Script 4: space bar plays a random chord and bounces the sprite ----
dj.script(700, 40, [
    dj.block("event_whenkeypressed", {}, {"KEY_OPTION": ["space", None]}),
    sp("useSynth", SYNTH=menu("synths", "prophet")),
    sp("useFx", FX=menu("fx", "echo")),
    sp("playChord", NOTE=dj.reporter("operator_random", {"FROM": num(55), "TO": num(67)}, shadow=(10, "c4")),
       CHORD=menu("chords", "major")),
    dj.block("looks_changesizeby", {"CHANGE": num(20)}),
    dj.block("control_wait", {"DURATION": posnum(0.3)}),
    dj.block("looks_changesizeby", {"CHANGE": num(-20)}),
])

# ---- Script 5: up arrow: sprite jumps to the mouse and plays a note for its height ----
mouse_expr = dj.reporter("operator_add", {
    "NUM1": dj.reporter("operator_round", {"NUM": dj.reporter("operator_divide", {
        "NUM1": dj.reporter("sensing_mousey"), "NUM2": num(15)})}),
    "NUM2": num(60),
})
mouse_expr = [3, mouse_expr[1], dj.note(60)[1]]  # keep a note shadow behind the reporter

dj.script(700, 500, [
    dj.block("event_whenkeypressed", {}, {"KEY_OPTION": ["up arrow", None]}),
    dj.block("motion_setx", {"X": dj.reporter("sensing_mousex")}),
    dj.block("motion_sety", {"Y": dj.reporter("sensing_mousey")}),
    sp("useSynth", SYNTH=menu("synths", "chiplead")),
    sp("useFx", FX=menu("fx", "none")),
    sp("playNoteFor", NOTE=mouse_expr, BEATS=num(0.25)),
])

# ---- Script 6: S stops everything ----
dj.script(700, 800, [
    dj.block("event_whenkeypressed", {}, {"KEY_OPTION": ["s", None]}),
    sp("stopAll"),
    dj.block("looks_sayforsecs", {"MESSAGE": txt("Silence!"), "SECS": num(2)}),
])

dj.comment(40, -160, "Sonic Pi demo. Start Sonic Scratch first, then press the green flag.\n"
           "Green flag: drum loop + bassline (Sonic Pi keeps these in time itself).\n"
           "The sprite bounces on every 'drums' cue, so it's always in time with the music.\n"
           "Click the sprite: pentatonic tune. Space: random chord with echo.\n"
           "Hold up arrow while moving the mouse: play by height. S: stop.", width=620)

# ---- costumes ----
dj.costume("speaker", """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="140" viewBox="0 0 120 140">
<rect x="10" y="10" width="100" height="120" rx="18" fill="#e60067"/>
<circle cx="60" cy="50" r="22" fill="#fff"/><circle cx="60" cy="50" r="9" fill="#333"/>
<circle cx="60" cy="100" r="16" fill="#fff"/><circle cx="60" cy="100" r="6" fill="#333"/>
<rect x="24" y="22" width="12" height="6" rx="3" fill="#ffd166"/><rect x="84" y="22" width="12" height="6" rx="3" fill="#ffd166"/>
</svg>""", 60, 70)
stage.costume("night", """<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360">
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b1035"/><stop offset="1" stop-color="#3a1c71"/></linearGradient></defs>
<rect width="480" height="360" fill="url(#g)"/>
</svg>""", 240, 180)

n = write_sb3(OUT, stage, [dj], EXT, EXT_URL)
print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes, {n} blocks)")
