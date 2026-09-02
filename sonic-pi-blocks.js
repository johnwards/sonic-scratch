// Sonic Pi blocks for Scratch (TurboWarp custom extension, runs unsandboxed from localhost:8000).
// Talks to bridge.rb, which forwards code to Sonic Pi and streams beat cues back.
(function (Scratch) {
  "use strict";

  const BRIDGE = (() => {
    try {
      const src = document.currentScript && document.currentScript.src;
      if (src) return new URL(src).origin;
    } catch (e) {}
    return "http://localhost:8000";
  })();

  const SYNTHS = [
    "beep", "saw", "prophet", "tb303", "dsaw", "fm", "pluck", "piano",
    "blade", "hollow", "dark_ambience", "mod_fm", "pretty_bell", "dull_bell",
    "chiplead", "chipbass", "supersaw", "zawa", "growl", "tri", "sine", "square",
  ];
  const SAMPLES = [
    "drum_heavy_kick", "drum_bass_hard", "drum_snare_soft", "drum_snare_hard",
    "drum_cymbal_closed", "drum_cymbal_open", "drum_tom_mid_soft", "drum_cowbell",
    "bd_haus", "bd_boom", "bd_tek", "sn_dub", "elec_blip", "elec_plip", "elec_ping",
    "elec_twang", "elec_blup", "perc_bell", "perc_snap", "ambi_choir", "ambi_piano",
    "ambi_drone", "guit_e_fifths", "guit_em9", "bass_hit_c", "loop_amen",
    "loop_breakbeat", "loop_industrial", "loop_garzul", "misc_crow", "vinyl_scratch",
  ];
  const FX = ["none", "reverb", "echo", "distortion", "wobble", "slicer", "bitcrusher", "flanger", "krush", "ixi_techno", "ping_pong", "vowel", "lpf", "hpf", "compressor"];
  const SAMPLE_OPTS = ["rate", "amp", "lpf", "hpf", "start", "finish", "pan", "attack", "release"];
  const SOUND_OPTS = ["cutoff", "res", "attack", "release", "sustain", "amp", "pan", "detune", "depth", "divisor"];
  const FX_OPTS = ["mix", "room", "phase", "decay", "amp", "cutoff", "res", "vowel_sound", "voice", "depth", "probability", "feedback", "wave", "invert_wave", "pulse_width", "smooth", "threshold", "slope_above"];
  const CHORDS = ["major", "minor", "major7", "minor7", "dom7", "dim", "aug", "sus2", "sus4", "m9", "add9", "5"];
  const SCALES = ["major", "minor", "major_pentatonic", "minor_pentatonic", "blues_major", "blues_minor", "dorian", "mixolydian", "chromatic"];

  const sym = (s) => ":" + (String(s).trim().toLowerCase().replace(/[^a-z0-9_]+/g, "_").replace(/^_+|_+$/g, "") || "x");
  const num = (v, fallback) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
  };
  // Accept a MIDI number (60), or a note name (c4, Fs3, eb, C) like Sonic Pi.
  const note = (v) => {
    const s = String(v).trim();
    if (s === "") return 60;
    if (/^-?\d+(\.\d+)?$/.test(s)) return s;
    if (/^[a-gA-G](s|b|#)?\d?$/.test(s)) return sym(s.replace("#", "s"));
    return 60;
  };
  const opts = (o) => Object.entries(o).map(([k, v]) => `${k}: ${v}`).join(", ");

  class SonicPiBlocks {
    constructor() {
      this.synth = "beep";
      this.synthOpts = {};
      this.fx = [];          // active effects, outermost first: [{name, opts}]
      this.sampleOpts = {};
      this.bpm = 60;
      this.amp = 1;
      this.status = { ready: false, lastMessage: "", lastError: "" };
      this.cues = {};       // name -> how many times Sonic Pi has cued it
      this.cueSeen = {};    // per hat block: count it last fired at
      this.lastCue = "";
      this.eventSeq = -1;   // -1 asks the bridge for the current position without replaying
      this.uploads = {};    // sound md5 -> promise of its file path on the bridge
      this.quietUntil = 0;  // ignore cues briefly after a stop; Sonic Pi takes a moment to go quiet
      this._poll();
      this._pollEvents();
      // The red stop sign only stops Scratch scripts. Live loops keep going in Sonic Pi
      // unless we tell it too. Only possible when running unsandboxed (localhost:8000).
      const runtime = Scratch.vm && Scratch.vm.runtime;
      if (runtime && typeof runtime.on === "function") {
        runtime.on("PROJECT_STOP_ALL", () => this.stopAll());
      }
    }

    _poll() {
      fetch(BRIDGE + "/status")
        .then((r) => r.json())
        .then((s) => (this.status = s))
        .catch(() => (this.status = { ready: false, lastMessage: "", lastError: "bridge not running" }))
        .finally(() => setTimeout(() => this._poll(), 1000));
    }

    _pollEvents() {
      fetch(BRIDGE + "/events?since=" + this.eventSeq)
        .then((r) => r.json())
        .then((d) => {
          const skew = Date.now() - d.now;
          this.eventSeq = d.seq;
          for (const e of d.events) {
            // Fire when the sound is actually heard, not when Sonic Pi scheduled it.
            const at = e.at + skew;
            if (at < this.quietUntil) continue;
            const delay = Math.min(5000, Math.max(0, at - Date.now()));
            setTimeout(() => {
              if (Date.now() < this.quietUntil) return;
              this.cues[e.name] = (this.cues[e.name] || 0) + 1;
              this.lastCue = e.name;
            }, delay);
          }
          setTimeout(() => this._pollEvents(), 0);
        })
        .catch(() => {
          this.eventSeq = -1;
          setTimeout(() => this._pollEvents(), 1000);
        });
    }

    getInfo() {
      const S = Scratch.ArgumentType.STRING, N = Scratch.ArgumentType.NUMBER;
      const str = (d) => ({ type: S, defaultValue: d });
      const n = (d) => ({ type: N, defaultValue: d });
      const menu = (m) => ({ type: S, menu: m });
      return {
        id: "sonicpi",
        name: "Sonic Pi",
        color1: "#e60067",
        color2: "#b8004f",
        color3: "#8f003d",
        blocks: [
          { opcode: "playNote", blockType: Scratch.BlockType.COMMAND, text: "play note [NOTE]",
            arguments: { NOTE: { type: Scratch.ArgumentType.NOTE, defaultValue: 60 } } },
          { opcode: "playNoteFor", blockType: Scratch.BlockType.COMMAND, text: "play note [NOTE] for [BEATS] beats",
            arguments: { NOTE: { type: Scratch.ArgumentType.NOTE, defaultValue: 60 }, BEATS: n(1) } },
          { opcode: "playChord", blockType: Scratch.BlockType.COMMAND, text: "play chord [NOTE] [CHORD]",
            arguments: { NOTE: str("c4"), CHORD: menu("chords") } },
          { opcode: "playSample", blockType: Scratch.BlockType.COMMAND, text: "play sample [SAMPLE]",
            arguments: { SAMPLE: menu("samples") } },
          { opcode: "sleepBeats", blockType: Scratch.BlockType.COMMAND, text: "sleep [BEATS] beats",
            arguments: { BEATS: n(1) } },
          { opcode: "playRecording", blockType: Scratch.BlockType.COMMAND, text: "play recording [SOUND] at note [NOTE]",
            arguments: { SOUND: menu("sounds"), NOTE: { type: Scratch.ArgumentType.NOTE, defaultValue: 60 } } },
          { opcode: "micStart", blockType: Scratch.BlockType.COMMAND, text: "start microphone (through the effects)" },
          { opcode: "micStop", blockType: Scratch.BlockType.COMMAND, text: "stop microphone" },
          "---",
          { opcode: "useSynth", blockType: Scratch.BlockType.COMMAND, text: "use synth [SYNTH]", arguments: { SYNTH: menu("synths") } },
          { opcode: "setSoundOpt", blockType: Scratch.BlockType.COMMAND, text: "set sound option [OPT] to [VALUE]",
            arguments: { OPT: menu("soundopts"), VALUE: n(100) } },
          { opcode: "clearSoundOpts", blockType: Scratch.BlockType.COMMAND, text: "clear sound options" },
          { opcode: "setSampleOpt", blockType: Scratch.BlockType.COMMAND, text: "set sample option [OPT] to [VALUE]",
            arguments: { OPT: menu("sampleopts"), VALUE: n(1) } },
          { opcode: "clearSampleOpts", blockType: Scratch.BlockType.COMMAND, text: "clear sample options" },
          { opcode: "useFx", blockType: Scratch.BlockType.COMMAND, text: "use effect [FX]", arguments: { FX: menu("fx") } },
          { opcode: "addFx", blockType: Scratch.BlockType.COMMAND, text: "also use effect [FX]", arguments: { FX: menu("fx") } },
          { opcode: "setFxOpt", blockType: Scratch.BlockType.COMMAND, text: "set effect option [OPT] to [VALUE]",
            arguments: { OPT: menu("fxopts"), VALUE: n(0.5) } },
          { opcode: "setBpm", blockType: Scratch.BlockType.COMMAND, text: "set tempo to [BPM] bpm", arguments: { BPM: n(60) } },
          { opcode: "setAmp", blockType: Scratch.BlockType.COMMAND, text: "set loudness to [AMP]", arguments: { AMP: n(1) } },
          "---",
          { opcode: "liveLoop", blockType: Scratch.BlockType.CONDITIONAL, branchCount: 1, text: "live loop [NAME]",
            arguments: { NAME: str("drums") } },
          { opcode: "liveLoopSynced", blockType: Scratch.BlockType.CONDITIONAL, branchCount: 1, text: "live loop [NAME] in time with [WITH]",
            arguments: { NAME: str("bass"), WITH: str("drums") } },
          { opcode: "stopLoop", blockType: Scratch.BlockType.COMMAND, text: "stop live loop [NAME]", arguments: { NAME: str("drums") } },
          { opcode: "stopAll", blockType: Scratch.BlockType.COMMAND, text: "stop all sounds" },
          "---",
          { opcode: "whenLoopRepeats", blockType: Scratch.BlockType.HAT, isEdgeActivated: true, text: "when live loop [NAME] repeats",
            arguments: { NAME: str("drums") } },
          { opcode: "whenLoopSound", blockType: Scratch.BlockType.HAT, isEdgeActivated: true, text: "when live loop [NAME] plays a sound",
            arguments: { NAME: str("drums") } },
          { opcode: "whenCue", blockType: Scratch.BlockType.HAT, isEdgeActivated: true, text: "when Sonic Pi cues [NAME]",
            arguments: { NAME: str("beat") } },
          { opcode: "cue", blockType: Scratch.BlockType.COMMAND, text: "cue [NAME]", arguments: { NAME: str("beat") } },
          { opcode: "cueCount", blockType: Scratch.BlockType.REPORTER, text: "count of cue [NAME]", arguments: { NAME: str("drums") } },
          { opcode: "lastCueName", blockType: Scratch.BlockType.REPORTER, text: "last cue" },
          "---",
          { opcode: "runCode", blockType: Scratch.BlockType.COMMAND, text: "run Sonic Pi code [CODE]", arguments: { CODE: str("play 72") } },
          { opcode: "scaleNote", blockType: Scratch.BlockType.REPORTER, text: "note [INDEX] of [ROOT] [SCALE] scale",
            arguments: { INDEX: n(1), ROOT: str("c4"), SCALE: menu("scales") } },
          { opcode: "isReady", blockType: Scratch.BlockType.BOOLEAN, text: "Sonic Pi ready?" },
          { opcode: "lastMessage", blockType: Scratch.BlockType.REPORTER, text: "last message from Sonic Pi" },
          { opcode: "lastError", blockType: Scratch.BlockType.REPORTER, text: "last error from Sonic Pi" },
        ],
        menus: {
          sounds: { acceptReporters: true, items: "_soundsMenu" },
          synths: { acceptReporters: true, items: SYNTHS },
          samples: { acceptReporters: true, items: SAMPLES },
          fx: { acceptReporters: true, items: FX },
          soundopts: { acceptReporters: true, items: SOUND_OPTS },
          sampleopts: { acceptReporters: true, items: SAMPLE_OPTS },
          fxopts: { acceptReporters: true, items: FX_OPTS },
          chords: { acceptReporters: true, items: CHORDS },
          scales: { acceptReporters: true, items: SCALES },
        },
      };
    }

    // ---- code building ----
    _settings() {
      const lines = [`use_bpm ${this.bpm}`, `use_synth ${sym(this.synth)}`];
      if (Object.keys(this.synthOpts).length) lines.push(`use_synth_defaults ${opts(this.synthOpts)}`);
      return lines;
    }
    // The effect chain as a list of with_fx opening lines, outermost first.
    _fxHeads() {
      return this.fx.map((f) => {
        const o = opts(f.opts);
        return `with_fx ${sym(f.name)}${o ? ", " + o : ""} do`;
      });
    }
    _wrapFx(lines) {
      let out = lines;
      for (const head of [...this._fxHeads()].reverse()) out = [head, ...out.map((l) => "  " + l), "end"];
      return out;
    }
    // The live loop being recorded on this thread, if any.
    _rec(util) {
      return util && util.thread && util.thread.spLoop;
    }
    // Play something: inside a live loop block it's recorded, otherwise sent straight away.
    _sound(lines, util) {
      const rec = this._rec(util);
      if (rec) {
        const fx = this._fxHeads();
        rec.lines.push({ fx, code: `cue ${sym(rec.name + "__sound")}` });
        for (const l of lines) rec.lines.push({ fx, code: l });
        return Promise.resolve();
      }
      return this._send([...this._settings(), ...this._wrapFx(lines)].join("\n"));
    }
    // A setting or plain statement: recorded inside a live loop, otherwise nothing to send
    // (immediate-mode settings are re-sent with every sound).
    _stmt(line, util) {
      const rec = this._rec(util);
      if (rec) rec.lines.push({ fx: this._fxHeads(), code: line });
    }
    _send(code) {
      return fetch(BRIDGE + "/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      }).then(() => undefined, () => undefined);
    }
    _wait(beats) {
      const ms = (num(beats, 1) * 60000) / this.bpm;
      return new Promise((r) => setTimeout(r, Math.max(0, ms)));
    }
    _assemble(rec) {
      const head = rec.sync ? `live_loop ${rec.name}, sync: ${rec.sync} do` : `live_loop ${rec.name} do`;
      // Every line carries the effect chain that was active. Nest with_fx blocks so a run of
      // lines sharing the same outer effect sits inside one block, splitting only where the
      // chain actually changes (e.g. a vowel setting that differs per note).
      const nest = (lines, depth) => {
        const out = [];
        let i = 0;
        while (i < lines.length) {
          const fxAt = lines[i].fx[depth];
          const run = [];
          while (i < lines.length && lines[i].fx[depth] === fxAt) run.push(lines[i++]);
          if (fxAt === undefined) out.push(...run.map((l) => l.code));
          else out.push(fxAt, ...nest(run, depth + 1).map((l) => "  " + l), "end");
        }
        return out;
      };
      // A settings line immediately replaced by another is noise; keep the last.
      const lines = rec.lines.filter((l, i) => {
        const next = rec.lines[i + 1];
        return !(l.code.startsWith("use_synth_defaults") && next && next.code.startsWith("use_synth_defaults") && JSON.stringify(next.fx) === JSON.stringify(l.fx));
      });
      const body = nest(lines, 0);
      if (!rec.lines.some((l) => /^sleep /.test(l.code))) body.push("sleep 1");
      return [head, ...body.map((l) => "  " + l), "end"].join("\n");
    }

    // ---- sounds ----
    playNote({ NOTE }, util) {
      return this._sound([`play ${note(NOTE)}, amp: ${this.amp}`], util);
    }
    playNoteFor({ NOTE, BEATS }, util) {
      const beats = num(BEATS, 1);
      const p = this._sound([`play ${note(NOTE)}, amp: ${this.amp}, release: ${Math.max(0.05, beats * 0.9)}`], util);
      if (this._rec(util)) { this._stmt(`sleep ${beats}`, util); return p; }
      return p.then(() => this._wait(beats));
    }
    playChord({ NOTE, CHORD }, util) {
      return this._sound([`play chord(${note(NOTE)}, ${sym(CHORD)}), amp: ${this.amp}`], util);
    }
    playSample({ SAMPLE }, util) {
      const o = opts({ amp: this.amp, ...this.sampleOpts });
      return this._sound([`sample ${sym(SAMPLE)}, ${o}`], util);
    }
    sleepBeats({ BEATS }, util) {
      const beats = num(BEATS, 1);
      if (this._rec(util)) { this._stmt(`sleep ${beats}`, util); return; }
      return this._wait(beats);
    }

    // ---- recordings from the Sounds tab ----
    _soundsMenu() {
      const vm = Scratch.vm;
      const target = vm && vm.runtime.getEditingTarget();
      const names = target ? target.sprite.sounds.map((snd) => snd.name) : [];
      return names.length ? names : ["(record a sound in the Sounds tab)"];
    }
    _findSound(name, util) {
      const targets = [util.target, ...(Scratch.vm ? Scratch.vm.runtime.targets : [])];
      for (const t of targets) {
        const snd = t && t.sprite.sounds.find((x) => x.name === name);
        if (snd) return snd;
      }
      return null;
    }
    // Send the sound's bytes to the bridge once; it saves them where Sonic Pi can read them.
    _uploadSound(snd) {
      const md5 = snd.assetId;
      if (!this.uploads[md5]) {
        const data = snd.asset && snd.asset.data;
        if (!data) return Promise.reject(new Error("sound data not loaded"));
        const ext = (snd.dataFormat || "wav").toLowerCase();
        this.uploads[md5] = fetch(`${BRIDGE}/sample/${md5}.${ext}`, {
          method: "POST",
          headers: { "Content-Type": "application/octet-stream" },
          body: data,
        }).then(async (r) => {
          const j = await r.json();
          if (!r.ok) throw new Error(j.error || "upload failed");
          return j.path;
        }).catch((e) => { delete this.uploads[md5]; throw e; });
      }
      return this.uploads[md5];
    }
    playRecording({ SOUND, NOTE }, util) {
      const snd = this._findSound(String(SOUND), util);
      if (!snd) return;
      const semis = toMidi(NOTE) - 60;   // 60 plays the recording as it was made
      const rec = this._rec(util);
      return this._uploadSound(snd).then((path) => {
        const line = `sample ${JSON.stringify(path)}, amp: ${this.amp}${semis ? `, rpitch: ${semis}` : ""}`;
        // Recording finished while we waited? Then the loop has already been sent; play it now.
        return this._sound([line], rec && util.thread.spLoop === rec ? util : null);
      }).catch((e) => { this.status.lastError = e.message; });
    }
    micStart(_, util) {
      const line = `live_audio :scratch_mic, amp: ${this.amp}`;
      if (this._rec(util)) { this._stmt(line, util); return; }
      return this._send([...this._settings(), ...this._wrapFx([line])].join("\n"));
    }
    micStop() {
      return this._send("live_audio :scratch_mic, :stop");
    }

    // ---- settings ----
    useSynth({ SYNTH }, util) {
      this.synth = String(SYNTH);
      this.synthOpts = {};
      this._stmt(`use_synth ${sym(this.synth)}`, util);
      this._stmt("use_synth_defaults", util);
    }
    setSoundOpt({ OPT, VALUE }, util) {
      const k = sym(OPT).slice(1);
      if (k !== "x") this.synthOpts[k] = num(VALUE, 0);
      this._stmt(`use_synth_defaults ${opts(this.synthOpts)}`, util);
    }
    clearSoundOpts(_, util) {
      this.synthOpts = {};
      this._stmt("use_synth_defaults", util);
    }
    useFx({ FX }) {
      const name = String(FX);
      this.fx = name === "none" ? [] : [{ name, opts: {} }];
    }
    addFx({ FX }) {
      const name = String(FX);
      if (name !== "none") this.fx.push({ name, opts: {} });
    }
    // Options apply to the most recently chosen effect.
    setFxOpt({ OPT, VALUE }) {
      const k = sym(OPT).slice(1);
      const f = this.fx[this.fx.length - 1];
      if (f && k !== "x") f.opts[k] = num(VALUE, 0);
    }
    setSampleOpt({ OPT, VALUE }) {
      const k = sym(OPT).slice(1);
      if (k !== "x") this.sampleOpts[k] = num(VALUE, 0);
    }
    clearSampleOpts() {
      this.sampleOpts = {};
    }
    setBpm({ BPM }, util) {
      this.bpm = Math.min(999, Math.max(1, num(BPM, 60)));
      this._stmt(`use_bpm ${this.bpm}`, util);
    }
    setAmp({ AMP }) {
      this.amp = Math.min(5, Math.max(0, num(AMP, 1)));
    }

    // ---- live loops (C-blocks) ----
    liveLoop({ NAME }, util) { return this._liveLoop(NAME, null, util); }
    liveLoopSynced({ NAME, WITH }, util) { return this._liveLoop(NAME, WITH, util); }
    _liveLoop(name, sync, util) {
      const frame = util.stackFrame;
      if (!frame.spLoop) {
        // First time through: run the blocks inside once, recording instead of playing.
        frame.spLoop = { name: sym(name), sync: sync ? sym(sync) : null, lines: [] };
        util.thread.spLoop = frame.spLoop;
        for (const l of this._settings()) frame.spLoop.lines.push({ fx: this._fxHeads(), code: l });
        util.startBranch(1, true);
        return;
      }
      // The blocks inside have all run: send the finished loop to Sonic Pi.
      const rec = frame.spLoop;
      delete frame.spLoop;
      util.thread.spLoop = null;
      return this._send(this._assemble(rec));
    }
    stopLoop({ NAME }) {
      return this._send(`live_loop ${sym(NAME)} do\n  stop\nend`);
    }
    stopAll() {
      this.cues = {};
      this.cueSeen = {};
      this.quietUntil = Date.now() + 700;
      return fetch(BRIDGE + "/stop", { method: "POST" }).then(() => undefined, () => undefined);
    }

    // ---- cues ----
    // Edge-triggered hats: Scratch evaluates these every frame for every such block.
    // Each fires once per new cue, per block (and per clone).
    _edge(name, util) {
      const key = `${util.target.id}:${util.thread.topBlock}:${name}`;
      const count = this.cues[name] || 0;
      if (!(key in this.cueSeen)) { this.cueSeen[key] = count; return false; }
      if (count > this.cueSeen[key]) { this.cueSeen[key] = count; return true; }
      return false;
    }
    whenLoopRepeats({ NAME }, util) { return this._edge(sym(NAME).slice(1), util); }
    whenLoopSound({ NAME }, util) { return this._edge(sym(NAME).slice(1) + "__sound", util); }
    whenCue({ NAME }, util) { return this._edge(sym(NAME).slice(1), util); }
    cue({ NAME }, util) {
      if (this._rec(util)) { this._stmt(`cue ${sym(NAME)}`, util); return; }
      return this._send(`cue ${sym(NAME)}`);
    }
    cueCount({ NAME }) { return this.cues[sym(NAME).slice(1)] || 0; }
    lastCueName() { return this.lastCue.replace(/__sound$/, ""); }

    // ---- misc ----
    runCode({ CODE }, util) {
      const code = String(CODE);
      if (this._rec(util)) { this._stmt(code, util); return; }
      return this._send(code);
    }
    scaleNote({ INDEX, ROOT, SCALE }) {
      const intervals = {
        major: [0, 2, 4, 5, 7, 9, 11], minor: [0, 2, 3, 5, 7, 8, 10],
        major_pentatonic: [0, 2, 4, 7, 9], minor_pentatonic: [0, 3, 5, 7, 10],
        blues_major: [0, 2, 3, 4, 7, 9], blues_minor: [0, 3, 5, 6, 7, 10],
        dorian: [0, 2, 3, 5, 7, 9, 10], mixolydian: [0, 2, 4, 5, 7, 9, 10],
        chromatic: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
      }[String(SCALE)] || [0, 2, 4, 5, 7, 9, 11];
      const root = toMidi(ROOT);
      const i = Math.max(0, Math.round(num(INDEX, 1)) - 1);
      return root + 12 * Math.floor(i / intervals.length) + intervals[i % intervals.length];
    }
    isReady() { return !!this.status.ready; }
    lastMessage() { return this.status.lastMessage || ""; }
    lastError() { return this.status.lastError || ""; }
  }

  function toMidi(v) {
    const s = String(v).trim();
    if (/^-?\d+(\.\d+)?$/.test(s)) return Math.round(Number(s));
    const m = /^([a-gA-G])(s|#|b)?(\d)?$/.exec(s);
    if (!m) return 60;
    const base = { c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11 }[m[1].toLowerCase()];
    const acc = m[2] === "b" ? -1 : m[2] ? 1 : 0;
    const oct = m[3] === undefined ? 4 : Number(m[3]);
    return 12 * (oct + 1) + base + acc;
  }

  Scratch.extensions.register(new SonicPiBlocks());
})(Scratch);
