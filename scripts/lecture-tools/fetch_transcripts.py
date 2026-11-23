# /// script
# requires-python = ">=3.10"
# dependencies = ["yt-dlp[default]>=2025.11.12"]
# ///
"""Download YouTube lecture transcripts as clean text files for a lecture summary.

Run with uv (it installs yt-dlp in a cached env; YouTube also needs `deno`: `brew install deno`):

  uv run scripts/lecture-tools/fetch_transcripts.py <playlist or video URL/ID> [...] --out <scratch>/src
  uv run scripts/lecture-tools/fetch_transcripts.py "https://www.youtube.com/playlist?list=PL..." \\
      --out <scratch>/src --only 1-3,5

Input: playlist URLs or IDs, video URLs or IDs, in any mix. Videos are numbered 1..N in the order
given (playlist order inside a playlist). `--only` picks numbers from that list, so the numbers stay
the same between runs. A video URL with `list=` means the whole playlist.

Output in --out, per lecture NN (two digits):
  lecNN.md    the transcript: `# title`, a source line, one `## <chapter> [mm:ss]` heading per
              YouTube chapter (or one per 10 minutes), paragraphs that start with `[mm:ss]`
  lecNN.json  metadata: video id, url, title, channel, date, duration, captions kind, chapters,
              description (it often has links to the course site and slides)
  index.json  every video of the list (also the ones not fetched): n, id, title, minutes, words, captions

Captions: a manual track in --lang first (any `en*` key: en, en-US, en-<name>), then the automatic
track (`en-orig`, then `en`). A video with no track gets captions "none"; a private or deleted
video gets "unavailable". The script reports them and goes on. Files that exist are kept, so a
rerun continues after an error. --force downloads again.

If YouTube asks to sign in or keeps returning HTTP 429: wait and rerun, raise --sleep, or pass
--cookies-from-browser chrome.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError

WORD = re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")  # the same rule as scripts/book-tools/words.py
SENT_END = re.compile(r"[.?!…][\"'”’)\]]*$")
NOISE = [
    re.compile(r"\[\s*(?:music|applause|laughter|laughs|laughing|inaudible|silence|crosstalk|"
               r"chuckling|chuckles|background noise|no audio|music playing|indistinct[^\]]*)\s*\]", re.I),
    re.compile(r"\(\s*(?:music|applause|laughter|laughs|laughing|inaudible|silence|crosstalk)\s*\)", re.I),
    re.compile(r"♪[^♪]*♪|♪"),
    re.compile(r"\b(?:um+|uh+|uhm|erm)\b,?\s*", re.I),
]
VIDEO_ID = re.compile(r"[\w-]{11}")
PLAYLIST_ID = re.compile(r"(?:PL|UU|OL|FL)[\w-]{10,}")
GONE = ("Private video", "Video unavailable", "This video has been removed", "This video is unavailable")


def parse_only(spec):
    out = set()
    for part in (spec or "").split(","):
        part = part.strip()
        if part:
            a, _, b = part.partition("-")
            out.update(range(int(a), int(b or a) + 1))
    return out


def clock(sec):
    sec = int(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def ydl_opts(args, flat=False):
    o = {"skip_download": True, "quiet": True, "no_warnings": True, "noprogress": True}
    if flat:
        o["extract_flat"] = "in_playlist"
    if args.cookies_from_browser:
        o["cookiesfrombrowser"] = (args.cookies_from_browser,)
    return o


def classify(raw):
    """-> ('playlist', url) or ('video', id)."""
    if PLAYLIST_ID.fullmatch(raw):
        return "playlist", f"https://www.youtube.com/playlist?list={raw}"
    if VIDEO_ID.fullmatch(raw):
        return "video", raw
    u = urllib.parse.urlparse(raw)
    q = urllib.parse.parse_qs(u.query)
    if "list" in q:
        if "v" in q:
            print(f"note: {raw} has list=, so the whole playlist is used")
        return "playlist", f"https://www.youtube.com/playlist?list={q['list'][0]}"
    if "v" in q:
        return "video", q["v"][0]
    m = re.search(r"(?:youtu\.be/|/shorts/|/live/|/embed/)([\w-]{11})", raw)
    if m:
        return "video", m.group(1)
    sys.exit(f"not a YouTube video or playlist: {raw}")


def expand(inputs, args):
    """Inputs -> [{id, title, duration, playlist}] in order. Only playlists are fetched here (flat)."""
    videos = []
    with yt_dlp.YoutubeDL(ydl_opts(args, flat=True)) as ydl:
        for raw in inputs:
            kind, ref = classify(raw.strip())
            if kind == "video":
                videos.append({"id": ref, "title": "", "duration": None, "playlist": None})
                continue
            info = ydl.extract_info(ref, download=False)
            for e in info.get("entries") or []:
                if e and e.get("id"):
                    videos.append({"id": e["id"], "title": e.get("title") or "", "duration": e.get("duration"),
                                   "playlist": info.get("title")})
    return videos


def pick_track(info, lang):
    """Manual track in `lang` first, then the automatic one. -> (kind, key, json3 url)."""
    def json3(fmts):
        return next((f["url"] for f in fmts or [] if f.get("ext") == "json3"), None)

    manual = info.get("subtitles") or {}
    for k in sorted((k for k in manual if k == lang or k.startswith(lang + "-")), key=lambda k: (k != lang, k)):
        if json3(manual[k]):
            return "manual", k, json3(manual[k])
    auto = info.get("automatic_captions") or {}
    for k in (f"{lang}-orig", lang):
        if json3(auto.get(k)):
            return "auto", k, json3(auto[k])
    return "none", None, None


def cues_from_json3(data):
    cues = []
    for ev in data.get("events", []):
        if "segs" not in ev or ev.get("aAppend"):
            continue
        text = "".join(s.get("utf8", "") for s in ev["segs"]).replace("\n", " ")
        for rx in NOISE:
            text = rx.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            cues.append((ev.get("tStartMs", 0) / 1000, text))
    return cues


def build_text(title, url, src_line, cues, chapters, para_sec):
    """Transcript as Markdown: chapter headings and paragraphs of about para_sec seconds."""
    if not chapters:
        end = int(max((t for t, _ in cues), default=0))
        chapters = [{"start_time": s, "title": f"Minutes {s // 60}-{s // 60 + 10}"} for s in range(0, end + 1, 600)]
    marks = sorted(chapters, key=lambda c: c["start_time"])
    lines = [f"# {title}", "", f"Source: {url} · {src_line}", ""]
    ci, para, p_start = 0, [], None

    def flush():
        if para:
            lines.extend([f"[{clock(p_start)}] " + " ".join(para), ""])

    for t, text in cues:
        if ci < len(marks) and t >= marks[ci]["start_time"] - 0.5:
            flush()
            para, p_start = [], None
            while ci < len(marks) and t >= marks[ci]["start_time"] - 0.5:
                ci += 1
            c = marks[ci - 1]
            lines.extend([f"## {c['title'].strip()} [{clock(c['start_time'])}]", ""])
        if para and ((t - p_start >= para_sec and SENT_END.search(para[-1])) or t - p_start >= 2 * para_sec):
            flush()
            para, p_start = [], None
        if p_start is None:
            p_start = t
        para.append(text)
    flush()
    return "\n".join(lines).rstrip() + "\n"


def fetch_one(ydl, vid):
    """-> (info, kind, track key, json3 data). Waits and retries on HTTP 429."""
    url = f"https://www.youtube.com/watch?v={vid}"
    for attempt in range(4):
        try:
            info = ydl.extract_info(url, download=False)
            kind, key, sub_url = pick_track(info, ARGS.lang)
            data = json.loads(ydl.urlopen(sub_url).read()) if sub_url else None
            return info, kind, key, data
        except Exception as e:  # noqa: BLE001 - DownloadError or an HTTP error from yt-dlp's network layer
            if ("429" not in str(e) and "Too Many Requests" not in str(e)) or attempt == 3:
                raise
            wait = 30 * 2 ** attempt
            print(f"  HTTP 429, waiting {wait}s", file=sys.stderr)
            time.sleep(wait)


def fetch(n, v, ydl, out):
    """Fetch one video into lecNN.md + lecNN.json. -> index row."""
    row = {"n": n, "id": v["id"], "title": v["title"], "minutes": round((v["duration"] or 0) / 60),
           "playlist": v["playlist"], "file": None, "words": 0, "captions": None}
    md, js = out / f"lec{n:02d}.md", out / f"lec{n:02d}.json"
    if md.exists() and js.exists() and not ARGS.force:
        meta = json.loads(js.read_text())
        row.update(file=md.name, words=meta["words"], captions=meta["captions"], title=meta["title"],
                   minutes=round((meta["duration"] or 0) / 60))
        print(f"{n:3d}  kept    {meta['words']:6d} words  {meta['title'][:70]}")
        return row
    try:
        info, kind, key, data = fetch_one(ydl, v["id"])
    except DownloadError as e:
        if any(g in str(e) for g in GONE):
            row["captions"] = "unavailable"
            print(f"{n:3d}  UNAVAILABLE  {v['id']}  {v['title'][:60]}")
            return row
        raise
    url = f"https://www.youtube.com/watch?v={v['id']}"
    chapters = [{"start_time": int(c["start_time"]), "title": c["title"]} for c in info.get("chapters") or []]
    meta = {
        "n": n, "id": v["id"], "url": url, "title": info.get("title"), "channel": info.get("channel"),
        "uploadDate": info.get("upload_date"), "duration": info.get("duration"),
        "durationString": info.get("duration_string"), "captions": kind, "captionTrack": key,
        "chapters": chapters, "description": info.get("description") or "", "words": 0,
    }
    row.update(title=meta["title"], minutes=round((meta["duration"] or 0) / 60), captions=kind)
    if data:
        cues = cues_from_json3(data)
        md.write_text(build_text(meta["title"], url, f"{meta['durationString']} · captions: {kind} ({key})",
                                 cues, chapters, ARGS.para))
        meta["words"] = sum(len(WORD.findall(t)) for _, t in cues)
        row.update(file=md.name, words=meta["words"])
        print(f"{n:3d}  {kind:6s}  {meta['words']:6d} words  {len(chapters):2d} chapters  {meta['title'][:60]}")
    else:
        print(f"{n:3d}  NO CAPTIONS in '{ARGS.lang}'  {meta['title'][:70]}")
    js.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    return row


def main():
    out = Path(ARGS.out)
    out.mkdir(parents=True, exist_ok=True)
    videos = expand(ARGS.inputs, ARGS)
    only = parse_only(ARGS.only)
    index_path = out / "index.json"
    old = {r["n"]: r for r in json.loads(index_path.read_text())} if index_path.exists() else {}
    index = []
    print(f"{len(videos)} videos in the list")
    try:
        with yt_dlp.YoutubeDL(ydl_opts(ARGS)) as ydl:
            fetched = 0
            for n, v in enumerate(videos, 1):
                if only and n not in only:
                    prev = old.get(n)
                    index.append(prev if prev and prev["id"] == v["id"] else
                                 {"n": n, "id": v["id"], "title": v["title"], "minutes": round((v["duration"] or 0) / 60),
                                  "playlist": v["playlist"], "file": None, "words": 0, "captions": None})
                    continue
                if fetched:
                    time.sleep(ARGS.sleep)
                index.append(fetch(n, v, ydl, out))
                fetched += 1
    except DownloadError as e:
        print(f"\nYouTube error: {str(e)[:300]}\nFiles done so far are kept. Wait and rerun, "
              "or try --cookies-from-browser chrome.", file=sys.stderr)
        sys.exit(1)
    finally:
        done = {r["n"] for r in index}
        index += [r for n, r in sorted(old.items()) if n not in done and n <= len(videos)]
        index_path.write_text(json.dumps(sorted(index, key=lambda r: r["n"]), ensure_ascii=False, indent=1))
    for label, kind in (("automatic captions (check names and terms)", "auto"), ("no captions", "none"),
                        ("unavailable", "unavailable")):
        nums = [r["n"] for r in index if r.get("captions") == kind]
        if nums:
            print(f"{label}: {nums}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="+", help="playlist URL or ID, video URL or ID")
    ap.add_argument("--out", required=True, help="output folder, e.g. <scratch>/src")
    ap.add_argument("--only", help="numbers to fetch, e.g. 1-3,5 (default: all)")
    ap.add_argument("--lang", default="en", help="caption language (default en)")
    ap.add_argument("--para", type=int, default=60, help="seconds per paragraph (default 60)")
    ap.add_argument("--sleep", type=float, default=2, help="seconds between videos (default 2)")
    ap.add_argument("--force", action="store_true", help="download again even if files exist")
    ap.add_argument("--cookies-from-browser", metavar="BROWSER", help="e.g. chrome, firefox, safari")
    ARGS = ap.parse_args()
    main()
