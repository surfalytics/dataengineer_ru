#!/usr/bin/env python3
"""Build a side-by-side HTML diff: before | after, with word-level highlights and change reasons.

Usage:
  python3 -I scripts/ru-proofread/compare.py BEFORE.md AFTER.md CHANGES.md OUT.html "Title"

BEFORE and AFTER must have the same number of lines (the review agent keeps the line structure).
CHANGES.md is the change log of the review agent: a Markdown table with the columns
Line | Было | Стало | Тип | Почему. Line numbers refer to BEFORE.md.
Open OUT.html in a browser. Keep OUT.html outside the repo.
"""
import difflib
import html
import re
import sys

before_p, after_p, changes_p, out_p, title = sys.argv[1:6]
A = open(before_p, encoding="utf-8").read().split("\n")
B = open(after_p, encoding="utf-8").read().split("\n")

# --- parse change log: line -> [(type, reason)]
notes = {}
for raw in open(changes_p, encoding="utf-8"):
    if not raw.startswith("|"):
        continue
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", raw.strip().strip("|"))]
    if len(cells) < 5 or not cells[0].isdigit():
        continue
    notes.setdefault(int(cells[0]), []).append((cells[3], cells[4]))

assert len(A) == len(B), f"line count differs: {len(A)} vs {len(B)}"


def words(s):
    return re.findall(r"\s+|[^\s]+", s)


def word_diff(a, b):
    ta, tb = words(a), words(b)
    sm = difflib.SequenceMatcher(None, ta, tb, autojunk=False)
    left, right = [], []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        x, y = html.escape("".join(ta[i1:i2])), html.escape("".join(tb[j1:j2]))
        if op == "equal":
            left.append(x)
            right.append(y)
        else:
            if x:
                left.append(f"<del>{x}</del>")
            if y:
                right.append(f"<ins>{y}</ins>")
    return "".join(left), "".join(right)


# --- find code fences to dim
in_code, code_lines = False, set()
for i, l in enumerate(A, 1):
    if l.strip().startswith("```"):
        code_lines.add(i)
        in_code = not in_code
    elif in_code:
        code_lines.add(i)

rows, changed = [], 0
for i, (a, b) in enumerate(zip(A, B), 1):
    cls = "code" if i in code_lines else ""
    if a == b:
        if not a.strip():
            continue
        rows.append(f'<tr class="same {cls}"><td class="n">{i}</td><td>{html.escape(a)}</td><td>{html.escape(b)}</td></tr>')
    else:
        changed += 1
        l, r = word_diff(a, b)
        tags = "".join(f'<span class="tag t-{t}">{html.escape(t)}</span>' for t, _ in notes.get(i, []))
        why = "".join(f"<li><b>{html.escape(t)}:</b> {html.escape(w)}</li>" for t, w in notes.get(i, []))
        rows.append(
            f'<tr class="chg"><td class="n">{i}<br>{tags}</td><td>{l}</td><td>{r}'
            + (f'<ul class="why">{why}</ul>' if why else "")
            + "</td></tr>"
        )

from collections import Counter

types = Counter(t for v in notes.values() for t, _ in v)
legend = " ".join(f'<span class="tag t-{t}">{t} · {n}</span>' for t, n in types.most_common())
wa, wb = len(" ".join(A).split()), len(" ".join(B).split())

page = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root{{--bg:#fff;--fg:#1d2330;--mut:#6b7385;--line:#e3e6ee;--del:#fde0e0;--delf:#9b1c1c;--ins:#d9f5e1;--insf:#14632c;--chg:#fffbea;--code:#f3f4f8}}
@media (prefers-color-scheme:dark){{:root{{--bg:#14171f;--fg:#e6e9f0;--mut:#8b93a7;--line:#2a3040;--del:#4a2226;--delf:#ffb3b3;--ins:#1f4a2c;--insf:#a8f0bd;--chg:#1d2230;--code:#1a1e29}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif}}
header{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px}}
h1{{font-size:17px;margin:0 0 6px}}
.meta{{color:var(--mut);font-size:13px;display:flex;gap:14px;flex-wrap:wrap;align-items:center}}
label{{cursor:pointer;user-select:none}}
table{{border-collapse:collapse;width:100%;table-layout:fixed}}
th{{position:sticky;top:78px;background:var(--bg);text-align:left;padding:8px 12px;border-bottom:2px solid var(--line);font-size:13px;color:var(--mut)}}
td{{vertical-align:top;padding:6px 12px;border-bottom:1px solid var(--line);white-space:pre-wrap;word-break:break-word}}
td.n{{width:78px;color:var(--mut);font-size:12px;text-align:right;white-space:normal}}
th:first-child{{width:78px}}
tr.chg td{{background:var(--chg)}}
tr.code td{{background:var(--code);font:12.5px/1.45 ui-monospace,Menlo,monospace;color:var(--mut)}}
body.only tr.same{{display:none}}
del{{background:var(--del);color:var(--delf);text-decoration:line-through;border-radius:3px;padding:0 2px}}
ins{{background:var(--ins);color:var(--insf);text-decoration:none;border-radius:3px;padding:0 2px;font-weight:600}}
.tag{{display:inline-block;font-size:11px;padding:1px 7px;border-radius:9px;background:var(--line);color:var(--fg);margin:2px 2px 0 0;font-weight:500}}
.t-punctuation{{background:#dbeafe;color:#1e3a8a}}.t-term{{background:#ede9fe;color:#4c1d95}}.t-grammar{{background:#fef3c7;color:#78350f}}
.t-typography{{background:#e5e7eb;color:#374151}}.t-meaning{{background:#fee2e2;color:#7f1d1d}}.t-flow{{background:#d1fae5;color:#064e3b}}
.t-calque{{background:#fce7f3;color:#831843}}.t-style{{background:#ffedd5;color:#7c2d12}}
@media (prefers-color-scheme:dark){{.tag[class*=t-]{{filter:brightness(.85) saturate(.9)}}}}
ul.why{{margin:8px 0 0;padding:8px 10px 8px 22px;background:var(--bg);border:1px dashed var(--line);border-radius:6px;font-size:12.5px;color:var(--mut);white-space:normal}}
</style></head><body class="only">
<header>
<h1>{html.escape(title)}</h1>
<div class="meta">
<span>Изменено строк: <b>{changed}</b></span><span>Слов: {wa} → {wb} ({(wb-wa)/wa*100:+.1f}%)</span>
<span>{legend}</span>
<label><input type="checkbox" id="only" checked> только изменённые строки</label>
<label><input type="checkbox" id="code"> показывать код</label>
</div></header>
<table><thead><tr><th></th><th>До</th><th>После (ru-proofread)</th></tr></thead><tbody>
{"".join(rows)}
</tbody></table>
<script>
const b=document.body;
document.getElementById('only').onchange=e=>b.classList.toggle('only',e.target.checked);
const style=document.createElement('style');style.id='codehide';style.textContent='tr.code{{display:none}}';document.head.appendChild(style);
document.getElementById('code').onchange=e=>{{style.disabled=e.target.checked}};
</script></body></html>"""
open(out_p, "w", encoding="utf-8").write(page)
print(f"{changed} changed lines, {len(rows)} rows -> {out_p}")
