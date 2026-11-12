#!/usr/bin/env python3
"""Helpers for the Airflow book diagrams (N, E, Z, T, run). Needs the local canvas server on :3456.
Output: public/assets/data-pipelines-with-apache-airflow/<name>.png. Scenes: dataengineer_ru/af-<name>."""
import base64, json, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

API = "http://127.0.0.1:3456"
OUT = Path(__file__).resolve().parents[2] / "public/assets/data-pipelines-with-apache-airflow"
STYLE = {  # fill, stroke
    "p": ("#a5d8ff", "#1971c2"), "g": ("#b2f2bb", "#2f9e44"), "r": ("#ffc9c9", "#e03131"),
    "y": ("#ffec99", "#f08c00"), "db": ("#99e9f2", "#0c8599"), "q": ("#ffd8a8", "#e8590c"),
    "n": ("#e9ecef", "#868e96"), "pu": ("#eebefa", "#9c36b5"),
}
W, H, FONT = 250, 100, 20

def call(path, payload=None, method="POST"):
    req = urllib.request.Request(API + path, data=json.dumps(payload or {}).encode(),
                                 headers={"content-type": "application/json"}, method=method)
    return json.load(urllib.request.urlopen(req, timeout=60))

def N(id, text, x, y, k="p", w=W, h=H, shape="rectangle"):
    return dict(id=id, text=text, x=x, y=y, k=k, w=w, h=h, shape=shape)

def E(a, b, label="", dashed=False, head=True):
    return dict(a=a, b=b, label=label, dashed=dashed, head=head)

def Z(text, x, y, w, h):  # zone rectangle + title
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
            els.append(dict(id=it["id"], type=it["shape"], x=it["x"], y=it["y"], width=it["w"], height=it["h"],
                            label={"text": it["text"]}, backgroundColor=f, strokeColor=s, fillStyle="solid",
                            fontSize=FONT, fontFamily=6, strokeWidth=2, roughness=1))
    for e in spec["edges"]:
        d = dict(type="arrow", x=0, y=0, start={"id": e["a"]}, end={"id": e["b"]}, strokeWidth=2,
                 strokeColor="#495057", roughness=1,
                 endArrowhead="arrow" if e["head"] else None)
        if e["dashed"]: d["strokeStyle"] = "dashed"
        if e["label"]: d["label"] = {"text": e["label"]}
        els.append(d)
    return els

def run(name, spec):
    scene = f"dataengineer_ru/af-{name}"
    try:
        call("/api/scenes", {"name": scene})
    except urllib.error.HTTPError as e:  # scene exists (re-run): reopen and clear it
        if e.code != 409: raise
        call("/api/scenes/open", {"name": scene})
        call("/api/elements/clear", method="DELETE")
    call("/api/elements/batch", {"elements": build(spec)})
    r = call("/api/export/image", {"format": "png", "scale": 2, "padding": 30})
    raw = OUT / f"{name}.png"
    raw.write_bytes(base64.b64decode(r["data"]))
    call("/api/scenes/save")
    subprocess.run(["node", "-e",
        "const s=require('sharp'),fs=require('fs');const p=process.argv[1];"
        "s(p).resize({width:1600,withoutEnlargement:true}).png({palette:true,quality:90,compressionLevel:9})"
        ".toBuffer().then(b=>fs.writeFileSync(p,b))", str(raw)], check=True,
        cwd=Path(__file__).resolve().parents[2])
    print("ok", name, raw.stat().st_size)

def col(i): return i * 300
def row(j): return j * 150
