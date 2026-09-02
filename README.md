# Sonic Scratch

Sonic Pi blocks for Scratch. Make music with Scratch blocks, played by [Sonic Pi](https://sonic-pi.net).

Everything runs on your own computer. Nothing to sign up for, nothing to pay.

## Install

**Mac**: open Terminal and paste

```
curl -fsSL https://raw.githubusercontent.com/johnwards/sonic-scratch/main/install.sh | bash
```

**Windows**: open PowerShell and paste

```
irm https://raw.githubusercontent.com/johnwards/sonic-scratch/main/install.ps1 | iex
```

You need [Sonic Pi](https://sonic-pi.net) installed. On a Mac with Homebrew the installer
installs it for you. Otherwise download it from sonic-pi.net first, then run the installer.

## Play

Double-click **Sonic Scratch** (in Applications on a Mac, on the Desktop or Start Menu on Windows).

A window opens showing Sonic Pi booting, then Scratch opens in your browser with a pink
**Sonic Pi** category in the blocks palette. The first time, the browser asks whether
turbowarp.org may connect to devices on your local network. Click **Allow**.

Keep the Sonic Scratch window open while you play. Close it to stop.

## Demos

Four projects live in the `demo` folder of the install (`~/Library/Application Support/Sonic Scratch`
on a Mac, `%LOCALAPPDATA%\SonicScratch` on Windows). Open them with File > Load from your computer.

**around-the-world.sb3** is the show: a cover of Daft Punk's *Around the World*, with the two robots
on their pyramid and the dancers from the video on a spinning record. It is built entirely from
blocks. Each part of the song is a custom block holding a `live loop`, and everything that moves is
triggered by those loops, so it stays in time with the sound. Press the green flag and the parts come
in one at a time as Sonic Pi counts the bars. Keys 1 to 5 switch the drums, lead synth, bass, voice
and chords on and off. Space stops.

**mario.sb3** is the chiptune one: the Super Mario Bros overworld theme on square-wave synths,
using the real NES sprites on a World 1-1 backdrop. Mario jumps on the bass notes, coins spin on
the melody, question blocks shimmer on the harmony, and a Goomba plods along to the drums. Keys 1
to 4 toggle drums, bass, melody and harmony. The sprites are the real NES ones; see
`demo/mario-sprites/SOURCE.md`.

**happy.sb3** is Pharrell's *Happy* with a crowd of minion-like dancers: bobbers on the beat,
jumpers on the claps, a banana crew that shows up for the chorus melody, and a sun that spins.
Keys 1 to 5 toggle drums, claps, verse, chorus and melody.

**sonic-pi-demo.sb3** is the small one: a drum loop, a bassline, a tune when you click the sprite,
a chord on space, and the mouse controlling pitch when you hold the up arrow.

## Blocks

Play things:

- `play note [60]` — MIDI number or a name like `c4`, `fs3`, `eb5`
- `play note [60] for [1] beats` — holds the note and waits
- `play chord [c4] [major]`
- `play sample [drum_heavy_kick]`
- `sleep [1] beats` — waits, timed by the tempo

Settings (apply to every play block after them):

- `use synth [beep]`
- `set sound option [cutoff] to [95]` — the knobs on the synth: cutoff, res, attack, release,
  sustain, amp, pan, detune, depth. `clear sound options` resets them.
- `use effect [reverb]` — pick `none` to turn off
- `set effect option [room] to [0.5]` — the knobs on the effect: mix, room, phase, decay,
  vowel_sound, voice and so on
- `set tempo to [120] bpm`
- `set loudness to [1]`

Live loops (Sonic Pi keeps these going on its own, in perfect time):

- `live loop [drums] { ... }` — a C-block. The blocks inside are played by Sonic Pi over and
  over. Put `sleep` blocks in for the gaps. `repeat` and variables work inside.
- `live loop [bass] in time with [drums] { ... }` — waits for the next cycle of `drums` before
  starting, so the two line up
- `stop live loop [drums]`
- `stop all sounds` — the red stop sign does this too

In time with the music (this is how the demos animate):

- `when live loop [drums] repeats` — hat block, fires each time the loop goes round
- `when live loop [bass] plays a sound` — hat block, fires on every note or sample in the loop
- `count of cue [drums]` — how many times the loop has gone round since the last stop; handy for
  "wait until count of cue drums > 8" to bring parts in on the bar
- `cue [name]` and `when Sonic Pi cues [name]` — your own named cues
- `last cue`

Other:

- `run Sonic Pi code [play 72]` — anything Sonic Pi understands
- `note [3] of [c4] [major] scale` — reporter, handy for melodies in a loop
- `Sonic Pi ready?`, `last message from Sonic Pi`, `last error from Sonic Pi`

Tips: for drum beats use a live loop, since Scratch's own timing drifts and Sonic Pi's doesn't.
Every block's generated Sonic Pi code is printed in the Sonic Scratch window, which is a nice
way to see the real code behind the blocks.

## How it works

```
Scratch (TurboWarp, in your browser)
   │  HTTP to localhost:8000
   ▼
bridge.rb  (runs on the Ruby that ships inside Sonic Pi)
   │  OSC /run-code, the same protocol the Sonic Pi app uses
   ▼
Sonic Pi server + audio engine (started for you by the bridge)
```

The Scratch editor is [TurboWarp](https://turbowarp.org), a Scratch-compatible editor that
opens and saves normal `.sb3` files. It's used because the official scratch.mit.edu editor
can't load custom extensions. Projects using these blocks won't make sound on the Scratch
website, only in TurboWarp with Sonic Scratch running.

Port 8000 matters: TurboWarp trusts `http://localhost:8000` and runs the extension inside the
page rather than in a sandbox. The sandbox has no origin, so modern browsers block it from
reaching `localhost` without ever asking.

The installers don't need admin rights. On a Mac the app is built on your machine by the
installer, so macOS doesn't treat it as an untrusted download.

## Files

- `bridge.rb` — the bridge. Run by hand with Sonic Pi's Ruby, e.g. on a Mac:
  `"/Applications/Sonic Pi.app/Contents/Resources/app/server/native/ruby/bin/ruby" bridge.rb`
  (`PORT=`, `NO_OPEN=1` and `DEBUG=1` are honoured)
- `sonic-pi-blocks.js` — the Scratch extension
- `bin/sonic-scratch.command`, `bin/sonic-scratch.cmd` — launchers the shortcuts point at
- `install.sh`, `install.ps1` — installers
- `demo/` — the demo projects and the Python scripts that generate them (`sb3lib.py` is a
  small helper for writing Scratch projects by hand)

## Uninstall

Mac: delete `/Applications/Sonic Scratch.app` and `~/Library/Application Support/Sonic Scratch`.
Windows: delete the Desktop and Start Menu shortcuts and `%LOCALAPPDATA%\SonicScratch`.
