# lecture-tools

Helpers for lecture summaries (`lecture-summary` skill) and the `lecture-prep` / `lecture-summary` workflows in `.claude/workflows/`. Word counts, stage markers and the status row use the shared scripts in `scripts/book-tools/` (`words.py --target 30-40`, `pipeline_state.py --unit lec`, `status.py --kind lecture`).

| File | What it does |
|---|---|
| `fetch_transcripts.py` | YouTube playlist or videos → `lecMM.md` transcripts with chapters and timestamps, `lecMM.json` metadata, `index.json` |
| `check_code.py` | Every `lecNN_*.py` of a course is on the lecture page, and its output on the page is the real output |
| `status.md` | One row per course: status, lectures done, PR, what is left |
| `status.md` rows `planned` | Courses with only the «О курсе» page. The plan and its order: `TODO.md` in the repo root |

Transcripts stay in the scratchpad. Never commit them.

## Setup

- `uv` runs the script. It reads the dependency list at the top of the script and installs `yt-dlp` into its cache. Nothing is installed globally.
- `deno` must be installed: YouTube needs a JavaScript runtime since late 2025.

```bash
brew install uv deno
```

## Download transcripts

```bash
# a whole playlist
uv run scripts/lecture-tools/fetch_transcripts.py "https://www.youtube.com/playlist?list=PL..." --out <scratch>/src

# only videos 1-3 and 5 of the playlist (numbers stay the same between runs)
uv run scripts/lecture-tools/fetch_transcripts.py "<playlist URL>" --out <scratch>/src --only 1-3,5

# single videos, in this order (URL or 11-character ID)
uv run scripts/lecture-tools/fetch_transcripts.py JuoVZkPBiKk "https://youtu.be/vHYeChEf2lA" --out <scratch>/src

# a Russian lecture
uv run scripts/lecture-tools/fetch_transcripts.py "<URL>" --out <scratch>/src --lang ru
```

- A video URL with `list=` means the whole playlist.
- Files that exist are kept. A rerun continues after an error. `--force` downloads again.
- About 4 seconds per video.

### What you get

```text
# Stanford CS336 Language Modeling from Scratch | Spring 2026 | Lecture 1: Overview, Tokenization

Source: https://www.youtube.com/watch?v=JuoVZkPBiKk · 1:19:22 · captions: manual (en-US)

## Course introduction [00:00]

[00:04] Welcome, everyone to CS 336, Language Models from Scratch. This is the teaching staff. ...
```

- One `##` heading per YouTube chapter. Without chapters, one heading per 10 minutes.
- Paragraphs of about 60 seconds (`--para`). Each starts with its time: use it for the `▶ [mm:ss](https://youtu.be/<id>?t=<s>)` links.
- Removed: `[Music]`, `[Applause]`, `[Laughter]`, `♪`, and the fillers "um", "uh". Speaker names (`CARTER ZENKE:`) stay: they show student questions.
- `words.py` skips the `[mm:ss]` marks, so the word count is the speech only.

### Which captions

1. A manual track in `--lang` (`en`, `en-US`, or a named track like `en-j3PyPqV-e1s`): a human transcript.
2. If there is none, the automatic track (`en-orig`, then `en`): speech recognition. It has punctuation now, but names, numbers and terms can be wrong ("CS 33336" for CS 336). The writer checks them against the slides.
3. If there is none either: `captions: none`. See "No captions" below.

## Troubleshooting

| Problem | What to do |
|---|---|
| `HTTP 429` | The script waits and retries 3 times. If it still fails, wait 10-30 minutes and rerun with `--sleep 10`. Finished files are kept |
| "Sign in to confirm you're not a bot" | Add `--cookies-from-browser chrome` (or `firefox`, `safari`). You must be logged in to YouTube in that browser |
| Extraction errors after a YouTube change | Get the newest `yt-dlp`: add `--refresh-package yt-dlp` after `uv run` |
| `captions: none` | Rare for university courses. Download the audio with `uvx --from 'yt-dlp[default]' yt-dlp -x --audio-format m4a -o <scratch>/audio/%(id)s.%(ext)s <URL>` and transcribe it with Whisper (for example `uvx --from mlx-whisper mlx_whisper` on Apple Silicon). Not automated yet |
| `captions: unavailable` | The video is private or deleted. Skip it |

Tested 2026-11-23 with `yt-dlp` 2026.10.26: Stanford CS336 Spring 2026 (playlist of 18, manual `en-US`), Harvard CS50 SQL lecture 0 (manual `en`), Stanford CME295 Autumn 2026 lecture 1 (manual, named track).

## Size of a lecture

| Lecture | Minutes | Words of speech | Page at 20% |
|---|---|---|---|
| CS336 (2026), lecture 1 | 79 | 11,500 | 2,300 |
| CS50 SQL, lecture 0 | 79 | 12,800 | 2,550 |
| CME295 (2026), lecture 1 | 104 | 13,600 | 2,700 |

Speech runs at about 145 words per minute. A lecture page is 30-40% of the transcript (since 2026-11-24; it was 15-25%): the courses teach fundamentals, and the owner chose full explanations over short pages.

## Measured cost

Add a row after each course run: `python3 -I scripts/book-tools/token_usage.py <transcript dir of the run>`.

First run: Stanford CME295 (Autumn 2026), lecture 1 only, with `publish: true`, 2026-11-23. List API prices.

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Prep: fetch 7 transcripts, slides, glossary (70 terms) | sonnet | 3 | 0.76 | 2 minutes |
| Status (2 calls) | sonnet | 2 | 0.23 | |
| Write lecture 1 (13,600 words, 104 min) | sonnet/high | 1 | 1.14 | Page 22%, 3 diagrams, 5 scripts |
| Review | sonnet/medium | 1 | 0.28 | 2 changes |
| Clarity | opus/medium | 1 | 0.89 | 10 changes |
| Course: overview, section, tab, nav, card | opus/high | 1 | 1.51 | Includes the one-time section setup |
| Build: EPUB, `npm run build` | sonnet | 1 | 0.15 | |
| **Total** | | **10** | **4.96** | 15 minutes |

- One lecture costs about $2.30 (write, review, clarity).
- The Course step runs once per run. Write several lectures in one run (`"only": [2, 3, 4]`) instead of one run per lecture.

Second run: CME295, all 7 lectures (lecture 1 expanded), 2026-11-24. New size 30-40% and the new workflow: Diagrams stage, `check_code.py`, `merge_registers.py --unit lec`, short report, writer read limits.

| Step | Model | Agents | Est. $ | Note |
|---|---|---|---|---|
| Prep: 7 transcripts, slides, glossary (158 terms) | sonnet | 3 | 0.81 | |
| Write 7 lectures | sonnet/high | 7 | 8.75 | 14-33 turns. Pages 34-38%. 0 diagram runs in writers |
| Diagrams (28 drawn, 4 fixed) | sonnet/medium | 7 | 1.03 | |
| Review | sonnet/medium | 7 | 1.73 | |
| Clarity | opus/medium | 7 | 5.03 | Flow pass not needed in any lecture |
| Code check (49 blocks, 0 flagged) | sonnet/low | 7 | 0.71 | No fix agent was needed |
| Course + registers + build + status | opus + sonnet | 5 | 2.27 | |
| **Total** | | **43** | **20.33** | 17 minutes |

- One lecture now costs about $2.50 at 35% (it was $2.30 at 22%): pages 1.6 times longer for 7% more money.
- A course of N lectures: about $2.50 × N + $3 (prep, course step, build).
