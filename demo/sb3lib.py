"""Tiny helper for writing Scratch 3 (.sb3) projects by hand.

Covers just what the demos need: blocks with inputs/fields, nested reporters,
substacks, variables and lists, SVG costumes, and the extension URL so TurboWarp
loads the Sonic Pi blocks with the project.
"""
import hashlib
import json
import zipfile

_counter = [0]


def _id(prefix="b"):
    _counter[0] += 1
    return f"{prefix}{_counter[0]}"


# ---- primitive inputs (sb3 wire format) ----
def num(v):
    return [1, [4, str(v)]]


def posnum(v):
    return [1, [5, str(v)]]


def whole(v):
    return [1, [6, str(v)]]


def txt(v):
    return [1, [10, str(v)]]


def var_input(var, default=0):
    """A variable reporter dropped into a slot. `var` is (name, id) from Target.var()."""
    return [3, [12, var[0], var[1]], [4, str(default)]]


class Target:
    def __init__(self, name, is_stage=False):
        self.name = name
        self.is_stage = is_stage
        self.blocks = {}
        self.comments = {}
        self.variables = {}
        self.lists = {}
        self.costumes = []
        self.assets = []
        self.x = 0
        self.y = 0
        self.size = 100
        self.visible = True
        self.layer = 0 if is_stage else 1

    # ---- data ----
    def var(self, name, value=0):
        vid = _id("v")
        self.variables[vid] = [name, value]
        return (name, vid)

    def list(self, name, items):
        lid = _id("l")
        self.lists[lid] = [name, list(items)]
        return (name, lid)

    # ---- blocks ----
    def block(self, opcode, inputs=None, fields=None, mutation=None):
        bid = _id()
        self.blocks[bid] = {"opcode": opcode, "next": None, "parent": None, "inputs": inputs or {},
                            "fields": fields or {}, "shadow": False, "topLevel": False}
        if mutation:
            self.blocks[bid]["mutation"] = {"tagName": "mutation", "children": [], **mutation}
        return bid

    # ---- custom blocks ("My Blocks") ----
    def define(self, name, x, y, body_ids):
        """A `define <name>` hat with the given body. No arguments supported."""
        proto = _id("p")
        self.blocks[proto] = {"opcode": "procedures_prototype", "next": None, "parent": None, "inputs": {},
                              "fields": {}, "shadow": True, "topLevel": False,
                              "mutation": {"tagName": "mutation", "children": [], "proccode": name,
                                           "argumentids": "[]", "argumentnames": "[]", "argumentdefaults": "[]",
                                           "warp": "false"}}
        head = self.block("procedures_definition", {"custom_block": [1, proto]})
        self.script(x, y, [head] + body_ids)
        return head

    def call(self, name):
        return self.block("procedures_call", {}, {}, mutation={"proccode": name, "argumentids": "[]", "warp": "false"})

    def reporter(self, opcode, inputs=None, fields=None, shadow=(4, "0")):
        """A reporter/boolean block in an input slot. Returns the input spec."""
        rid = _id("r")
        self.blocks[rid] = {"opcode": opcode, "next": None, "parent": None, "inputs": inputs or {},
                            "fields": fields or {}, "shadow": False, "topLevel": False}
        return [3, rid, list(shadow)] if shadow else [2, rid]

    def boolean(self, opcode, inputs=None, fields=None):
        return self.reporter(opcode, inputs, fields, shadow=None)

    def shadow(self, opcode, field, value):
        sid = _id("s")
        self.blocks[sid] = {"opcode": opcode, "next": None, "parent": None, "inputs": {},
                            "fields": {field: [str(value), None]}, "shadow": True, "topLevel": False}
        return [1, sid]

    def note(self, v):
        return self.shadow("note", "NOTE", v)

    def menu(self, ext_id, name, value):
        return self.shadow(f"{ext_id}_menu_{name}", name, value)

    def chain(self, ids):
        for a, b in zip(ids, ids[1:]):
            self.blocks[a]["next"] = b
            self.blocks[b]["parent"] = a
        return ids

    def substack(self, ids):
        self.chain(ids)
        return [2, ids[0]]

    def script(self, x, y, ids):
        self.chain(ids)
        self.blocks[ids[0]].update({"topLevel": True, "x": x, "y": y})

    def comment(self, x, y, text, width=420, height=140):
        self.comments[_id("c")] = {"blockId": None, "x": x, "y": y, "width": width, "height": height,
                                   "minimized": False, "text": text}

    # ---- costumes ----
    def costume(self, name, svg, cx, cy):
        data = svg.encode()
        md5 = hashlib.md5(data).hexdigest()
        self.costumes.append({"name": name, "bitmapResolution": 1, "dataFormat": "svg", "assetId": md5,
                              "md5ext": f"{md5}.svg", "rotationCenterX": cx, "rotationCenterY": cy})
        self.assets.append((f"{md5}.svg", data))

    def costume_png(self, name, data, cx, cy):
        """A bitmap costume from PNG bytes. 1 image pixel = 1 stage pixel."""
        md5 = hashlib.md5(data).hexdigest()
        self.costumes.append({"name": name, "bitmapResolution": 1, "dataFormat": "png", "assetId": md5,
                              "md5ext": f"{md5}.png", "rotationCenterX": cx, "rotationCenterY": cy})
        self.assets.append((f"{md5}.png", data))

    # ---- output ----
    def _fix_parents(self):
        for bid, b in self.blocks.items():
            for inp in b["inputs"].values():
                for part in inp[1:]:
                    if isinstance(part, str) and part in self.blocks:
                        self.blocks[part]["parent"] = bid

    def to_json(self):
        self._fix_parents()
        common = {"isStage": self.is_stage, "name": self.name, "variables": self.variables, "lists": self.lists,
                  "broadcasts": {}, "blocks": self.blocks, "comments": self.comments, "currentCostume": 0,
                  "costumes": self.costumes, "sounds": [], "volume": 100, "layerOrder": self.layer}
        if self.is_stage:
            common.update({"tempo": 60, "videoTransparency": 50, "videoState": "off", "textToSpeechLanguage": None})
        else:
            common.update({"visible": self.visible, "x": self.x, "y": self.y, "size": self.size, "direction": 90,
                           "draggable": False, "rotationStyle": "all around"})
        return common


def write_sb3(path, stage, sprites, ext_id, ext_url):
    for i, s in enumerate(sprites, start=1):
        s.layer = i
    project = {
        "targets": [stage.to_json()] + [s.to_json() for s in sprites],
        "monitors": [],
        "extensions": [ext_id],
        "extensionURLs": {ext_id: ext_url},
        "meta": {"semver": "3.0.0", "vm": "0.2.0", "agent": "sonic-scratch demo generator"},
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps(project))
        seen = set()
        for t in [stage] + sprites:
            for name, data in t.assets:
                if name not in seen:
                    seen.add(name)
                    z.writestr(name, data)
    total = sum(len(t.blocks) for t in [stage] + sprites)
    return total
