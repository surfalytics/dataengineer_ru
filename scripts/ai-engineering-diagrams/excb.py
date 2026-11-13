#!/usr/bin/env python3
"""Shared helpers to draw book diagrams in Excalidraw (needs the local canvas server on :3456).
A diagram is a spec: dict(items=[N(...), Z(...), T(...)], edges=[E(...)]).
Per-chapter specs live in chNN_diagrams.py and call run_all(D).
Output: public/assets/ai-engineering/<name>.png. Scene: dataengineer_ru/aie-<name>.
Only one script draws on the shared canvas at a time (lock ~/dev/excalidraw/.canvas.lock)."""
import base64, json, subprocess, sys, time, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public/assets/ai-engineering"
LOCK = Path.home() / "dev/excalidraw/.canvas.lock"
STYLE = {  # fill, stroke
    "p": ("#a5d8ff", "#1971c2"), "g": ("#b2f2bb", "#2f9e44"), "r": ("#ffc9c9", "#e03131"),
    "y": ("#ffec99", "#f08c00"), "db": ("#99e9f2", "#0c8599"), "q": ("#ffd8a8", "#e8590c"),
    "n": ("#e9ecef", "#868e96"), "pu": ("#eebefa", "#9c36b5"),
}
W, H, FONT = 250, 100, 20

class canvas_lock:
    def __enter__(self):
        import fcntl
        LOCK.parent.mkdir(parents=True, exist_ok=True)
        self.f = open(LOCK, "w")
        t0 = time.time()
        while True:
            try:
                fcntl.flock(self.f, fcntl.LOCK_EX | fcntl.LOCK_NB); break
            except BlockingIOError:
                if time.time() - t0 > 600: raise SystemExit("canvas lock busy for 10 min")
                time.sleep(1)
        return self
    def __exit__(self, *a):
        self.f.close()

def call(path, payload=None, method="POST"):
    req = urllib.request.Request(API + path, data=None if method == "GET" else json.dumps(payload or {}).encode(),
                                 headers={"content-type": "application/json"}, method=method)
    return json.load(urllib.request.urlopen(req, timeout=60))

def N(id, text, x, y, k="p", w=W, h=H, shape="rectangle"):
    return dict(id=id, text=text, x=x, y=y, k=k, w=w, h=h, shape=shape)

def E(a, b, label="", dashed=False, head=True):
    return dict(a=a, b=b, label=label, dashed=dashed, head=head)

def Z(text, x, y, w, h):  # dashed zone + title
    return dict(zone=True, text=text, x=x, y=y, w=w, h=h)

def T(text, x, y, size=18, color="#868e96"):  # free text note
    return dict(note=True, text=text, x=x, y=y, size=size, color=color)

def build(spec):
    els = []
    for it in spec["items"]:
        if it.get("zone"):
            els.append(dict(type="rectangle", x=it["x"], y=it["y"], width=it["w"], height=it["h"],
                            backgroundColor="#f8f9fa", strokeColor="#adb5bd", fillStyle="solid",
                            strokeStyle="dashed", roughness=1, opacity=60))
            els.append(dict(type="text", x=it["x"] + 20, y=it["y"] + 12, text=it["text"], fontSize=20,
                            strokeColor="#495057", fontFamily=6))
        elif it.get("note"):
            els.append(dict(type="text", x=it["x"], y=it["y"], text=it["text"], fontSize=it["size"],
                            strokeColor=it["color"], fontFamily=6))
        else:
            f, s = STYLE[it["k"]]
            d = dict(id=it["id"], type=it["shape"], x=it["x"], y=it["y"], width=it["w"], height=it["h"],
                     backgroundColor=f, strokeColor=s, fillStyle="solid",
                     fontSize=FONT, fontFamily=6, strokeWidth=2, roughness=1)
            if it["text"]: d["label"] = {"text": it["text"]}  # empty text = plain bar
            els.append(d)
    for e in spec["edges"]:
        d = dict(type="arrow", x=0, y=0, start={"id": e["a"]}, end={"id": e["b"]}, strokeWidth=2,
                 strokeColor="#495057", roughness=1, endArrowhead="arrow" if e["head"] else None)
        if e["dashed"]: d["strokeStyle"] = "dashed"
        if e["label"]: d["label"] = {"text": e["label"]}
        els.append(d)
    return els

def run(name, spec):
    scene = f"dataengineer_ru/aie-{name}"
    OUT.mkdir(parents=True, exist_ok=True)
    with canvas_lock():
        els = build(spec)
        prev = call("/api/scenes", method="GET").get("current")
        for attempt in range(8):  # verify scene and element count, retry if another session touched the canvas
            try:
                call("/api/scenes", {"name": scene})
            except urllib.error.HTTPError as e:  # scene exists (re-run): reopen
                if e.code != 409: raise
                call("/api/scenes/open", {"name": scene})
            if call("/api/scenes", method="GET").get("current") != scene: continue
            call("/api/elements/clear", method="DELETE")
            call("/api/elements/batch", {"elements": els})
            time.sleep(2)  # let the canvas frontend render the new scene before export
            got = call("/api/elements", method="GET")["elements"]
            my_ids = {e["id"] for e in els if "id" in e}
            if (call("/api/scenes", method="GET").get("current") == scene and len(got) == len(els)
                    and my_ids <= {g.get("id") for g in got}):
                r = call("/api/export/image", {"format": "png", "scale": 2, "padding": 30})
                if call("/api/scenes", method="GET").get("current") == scene: break
            time.sleep(2)
        else:
            raise SystemExit(f"canvas busy, could not build {name}")
        raw = OUT / f"{name}.png"
        raw.write_bytes(base64.b64decode(r["data"]))
        call("/api/scenes/save")
        if prev and prev != scene:  # give the canvas back
            call("/api/scenes/open", {"name": prev})
    subprocess.run(["node", "-e",
        "const s=require('sharp'),fs=require('fs');const p=process.argv[1];"
        "s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9})"
        ".toBuffer().then(b=>fs.writeFileSync(p,b))", str(raw)], check=True, cwd=ROOT)
    print("ok", name, raw.stat().st_size)

def run_all(D):
    """Usage in chNN_diagrams.py:  if __name__ == '__main__': run_all(D)   (args = names, none = all)"""
    names = sys.argv[1:] or list(D)
    for n in names: run(n, D[n])
