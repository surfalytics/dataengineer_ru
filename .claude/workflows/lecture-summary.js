export const meta = {
  name: 'lecture-summary',
  description: 'Lecture summary, part 2: write, size-check, review, flow-edit and clarity-edit every lecture of a YouTube course in parallel, then overview, nav, EPUB, build',
  whenToUse: 'After lecture-prep, with its "next.args". Also to redo some lectures: pass "only": [3, 5]. Lectures already done are skipped, so a rerun continues where it stopped.',
  phases: [
    { title: 'Status', detail: 'which lecture stages are already done (script, copied by sonnet)', model: 'sonnet' },
    { title: 'Write', detail: 'one writer per lecture (sonnet, high)', model: 'sonnet' },
    { title: 'Size', detail: 'fix pages outside 15-25% of the transcript (max one retry)', model: 'opus' },
    { title: 'Review', detail: 'correctness review (sonnet, medium)', model: 'sonnet' },
    { title: 'Flow', detail: 'flow pass only when --stats is LOW (opus, medium)', model: 'opus' },
    { title: 'Clarity', detail: 'final read: vague text, AI slop, contradictions, gaps in explanations (opus, medium)', model: 'opus' },
    { title: 'Code', detail: 'optional (checkCode: true): run every code example, match outputs (sonnet, medium)', model: 'sonnet' },
    { title: 'Course', detail: 'registers, overview, nav, section (opus, high)', model: 'opus' },
    { title: 'Build', detail: 'EPUB, npm run build (sonnet)', model: 'sonnet' },
  ],
}

// args: the "next.args" object returned by lecture-prep:
// { slug, group, scratch, scriptsPrefix, glossary, practice: 'python' | 'duckdb' | 'none',
//   course: { title, code, school, term, lecturers, site, playlistUrl, license },
//   lectures: [{ n, title, titleRu, file, src, videoId, url, minutes, words, captions, lecturer,
//                materials, slidesUrl, oldPage, notes? }],
//   notes?: "text for every writer", courseNotes?: "text for the Course step",
//   only?: [n, ...], skipCourse?: false, redo?: false, checkCode?: false,
//   publish?: false,      // with only: still run the Course and Build steps, so the written lectures go on the site
//                         // (the overview lists every lecture and links only the written ones)
//   reviewOnly?: false,   // pages exist: skip write and size, run review/flow/clarity/code, skip course steps
//   models?: { write: 'opus/high', ... } }  // per-stage model/effort override. Never use haiku for Russian text.
const a = args || {}
const missing = ['slug', 'group', 'scratch', 'course', 'glossary', 'lectures'].filter(k => !a[k])
if (missing.length) {
  return { error: `missing args: ${missing.join(', ')}`, usage: 'Run lecture-prep first and pass its next.args.' }
}

const C = a.course
const prefix = a.scriptsPrefix || a.slug
const practice = a.practice || 'none'
const M = (stage, model, effort) => {
  const o = (a.models || {})[stage]
  if (!o) return { model, effort }
  const [om, oe] = o.split('/')
  return { model: om || model, effort: oe || effort }
}
// Size of a lecture page in % of its transcript. Speech is wordier than a book, so the range is lower than 20-40%.
const LO = 15, HI = 25, AIM = 20, DRAFT_MAX = 22, FLOW_MAX = 27, CLARITY_MAX = 30
const TARGET = `--target ${LO}-${HI}`
const courseDir = `src/content/docs/lecture-summaries/${a.group}/${a.slug}`
const urlBase = `/lecture-summaries/${a.group}/${a.slug}`
const stateDir = `${a.scratch}/state`
const beforeDir = `${a.scratch}/before`
const pad = n => String(n).padStart(2, '0')
const url = l => `${urlBase}/${l.file.replace(/\.md$/, '')}/`
const page = l => `${courseDir}/${l.file}`
const mark = (l, stage) => `${stateDir}/lec${pad(l.n)}.${stage}.done`

// src may be a bare file name (lec03.md): resolve it against <scratch>/src
const all = a.lectures.map(l => ({ ...l, src: l.src.startsWith('/') ? l.src : `${a.scratch}/src/${l.src.replace(/^.*\//, '')}` })).sort((x, y) => x.n - y.n)
const todo = a.only ? all.filter(l => a.only.includes(l.n)) : all
if (!todo.length) return { error: 'no lectures selected', only: a.only }

const COMMON = `Rules for this run:
- You are one step of an automated pipeline. Do not start other agents. Do not ask questions: decide, and put doubts in your reply.
- Never run \`npm run build\` or \`npm run dev\`. Never edit shared files: index.md, src/nav.mjs, glossary.md, figures.md, README.md registers.
- Keep tool output short (\`| tail -20\`). Do not re-read a file right after you wrote it.`
// The proofread prompts were written for books. Tell the agents how to read them here.
const LECTURE_SOURCE = `The source is a lecture transcript (spoken text), not a book. Where a prompt says "book" or "book chapter", read "lecture" and "transcript".`

// ---------- Status: what is already done (makes reruns resume across sessions)
const STATUS = {
  type: 'object',
  properties: {
    chapters: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          n: { type: 'integer' },
          done: { type: 'array', items: { type: 'string' }, description: 'stage markers found: write, review, flow, clarity, code' },
          pct: { type: 'number', description: 'words.py % of source, 0 if no page' },
          statsLow: { type: 'boolean' },
        },
        required: ['n', 'done', 'pct', 'statsLow'],
      },
    },
  },
  required: ['chapters'],
}

// Status of every lecture, not only the selected ones: links may point only to pages that exist.
phase('Status')
const status = (await agent(`Run this one command. Reply with exactly the JSON it prints, copied as is. Do not run anything else and do not guess any value.
python3 -I scripts/book-tools/pipeline_state.py --unit lec ${a.scratch} ${all.map(l => JSON.stringify(`${l.n}|${l.src}|${page(l)}`)).join(' ')}`,
  { label: 'status', phase: 'Status', schema: STATUS, ...M('status', 'sonnet', 'low') })) || { chapters: [] }
const known = n => status.chapters.find(s => s.n === n) || { done: [], pct: 0, statsLow: false }
// redo: ignore the stage markers, so every stage runs again
const st = n => a.redo ? { done: [], pct: known(n).pct, statsLow: false } : known(n)
// A page exists after this run if it is written now or was written before (words.py found it: pct > 0).
const written = l => todo.includes(l) || known(l.n).pct > 0
const skipped = todo.filter(l => st(l.n).done.includes('clarity') && (!a.checkCode || st(l.n).done.includes('code')))
if (skipped.length) log(`already done, skipped: lectures ${skipped.map(l => l.n).join(', ')}`)

// ---------- Schemas
const WRITE = {
  type: 'object',
  properties: {
    page: { type: 'string' }, srcWords: { type: 'integer' }, pageWords: { type: 'integer' }, pct: { type: 'number' },
    title: { type: 'string', description: 'the Russian title used in title and sidebar.label' },
    diagramsDrawn: { type: 'integer' }, diagramsSkipped: { type: 'integer' },
    codeOk: { type: 'boolean' }, codeProblems: { type: 'array', items: { type: 'string' } },
    checkErrors: { type: 'integer', description: 'ERROR count from check.py at the end' },
    doubtful: { type: 'array', items: { type: 'string' }, description: 'unclear audio, caption errors you were not sure about, places where a missing slide was needed, meaning risks' },
  },
  required: ['page', 'srcWords', 'pageWords', 'pct', 'title', 'diagramsDrawn', 'diagramsSkipped', 'codeOk', 'codeProblems', 'checkErrors', 'doubtful'],
}
const SIZE = {
  type: 'object',
  properties: { pct: { type: 'number' }, note: { type: 'string' } },
  required: ['pct', 'note'],
}
const REVIEW = {
  type: 'object',
  properties: {
    changes: { type: 'integer' }, byType: { type: 'string', description: 'e.g. calque 5, punctuation 3' },
    meaningRisks: { type: 'array', items: { type: 'string' } }, doubtful: { type: 'array', items: { type: 'string' } },
    guardOk: { type: 'boolean' }, statsLow: { type: 'boolean' },
  },
  required: ['changes', 'byType', 'meaningRisks', 'doubtful', 'guardOk', 'statsLow'],
}
const FLOW = {
  type: 'object',
  properties: {
    paragraphs: { type: 'integer' }, meaningRisks: { type: 'array', items: { type: 'string' } },
    guardOk: { type: 'boolean' }, pct: { type: 'number' },
  },
  required: ['paragraphs', 'meaningRisks', 'guardOk', 'pct'],
}
const CLARITY = {
  type: 'object',
  properties: {
    changes: { type: 'integer' }, byType: { type: 'string', description: 'e.g. vague 3, slop 2, contradiction 1, gap 2' },
    deleted: { type: 'integer', description: 'sentences deleted' },
    found: { type: 'array', items: { type: 'string' }, description: 'every problem line from step 1: "line N, type T: problem → fixed" or "→ left: why"' },
    meaningRisks: { type: 'array', items: { type: 'string' } },
    newPatterns: { type: 'array', items: { type: 'string' }, description: 'bad → good, for calques.tsv' },
    guardOk: { type: 'boolean' }, pct: { type: 'number' },
  },
  required: ['changes', 'byType', 'deleted', 'found', 'meaningRisks', 'newPatterns', 'guardOk', 'pct'],
}
const CODE = {
  type: 'object',
  properties: {
    blocks: { type: 'integer', description: 'code blocks checked' },
    ok: { type: 'integer' }, fixed: { type: 'integer' }, notRun: { type: 'integer' },
    problems: { type: 'array', items: { type: 'string' }, description: 'block, what was wrong, what you did; or why not run' },
  },
  required: ['blocks', 'ok', 'fixed', 'notRun', 'problems'],
}

const PRACTICE = {
  python: 'This course has Python practice: add `## Практика` with 2-3 small Python tasks (skill section "Code and practice").',
  duckdb: 'This course has SQL practice: add `## Практика` with 2-3 SQL tasks on DuckDB (skill section "Code and practice").',
  none: 'This course has no practice: no `## Практика` section. Code the lecturer shows still goes on the page as "Code and practice" says.',
}[practice] || ''

// ---------- Per-lecture pipeline (no barrier: lecture 1 can be in review while lecture 7 is still writing)
const results = await pipeline(
  todo.filter(l => !skipped.includes(l)),

  // Stage 1: write
  async (_, l) => {
    const s = st(l.n)
    if (s.done.includes('write') || a.reviewOnly) return { l, write: { page: page(l), pct: s.pct, reused: true, doubtful: [] } }
    const i = all.findIndex(x => x.n === l.n)
    const prev = all[i - 1], next = all[i + 1]
    const w = Math.round
    const prevLink = !prev ? `none (first lecture): link to the overview ${urlBase}/`
      : written(prev) ? `[${prev.titleRu}](${url(prev)})` : `lecture ${prev.n} is not written yet: link to the overview ${urlBase}/ instead`
    const nextLink = !next ? 'none (last lecture)'
      : written(next) ? `[${next.titleRu}](${url(next)})` : `lecture ${next.n} is not written yet: leave out «Следующая», the Course step adds it later`
    const write = await agent(`Write lecture ${l.n} of the Russian summary of the course "${C.title}" (${C.school}${C.lecturers ? '; ' + C.lecturers : ''}).

Load the \`lecture-summary\` skill and follow "Lecture steps (writer)". It tells you which parts of the \`book-summary\` skill to read too.
${PRACTICE}
Work in few, large steps: plan the whole page, write it with one \`Write\`, then fix with \`Edit\`. Every extra turn re-reads your whole context.
Before you write, get the word budget per section: \`python3 -I scripts/book-tools/words.py ${TARGET} --sections ${l.src}\`. Aim for ${AIM}%. Keep the first draft at ${DRAFT_MAX}% or less: the clarity pass later needs room to add explanations.
The Russian title "${l.titleRu}" is a draft from the prep step. If it is not natural Russian or breaks the glossary, write a better one. Use the same title in \`title\` and \`sidebar.label\`, and return it in \`title\` so the lead can align links.
Other lectures of this course (other writers work at the same time): ${all.filter(x => x.n !== l.n).map(x => `${x.n}. ${x.title}`).join('; ')}. Explain and draw an idea in depth only if this lecture explains it; if it belongs to another lecture, link to that lecture instead.

| Input | Value |
|---|---|
| Transcript (the main source) | ${l.src} (${l.words} words, ${l.minutes} min, captions: ${l.captions}${l.captions === 'auto' ? ' — speech recognition: check names, numbers and terms against the slides' : ''}) |
| Slides and notes as text | ${l.materials || 'none: write from the transcript alone, and say in doubtful where a slide was needed'} |
| Video | https://www.youtube.com/watch?v=${l.videoId} — section links: \`▶ [mm:ss](https://youtu.be/${l.videoId}?t=<seconds>)\` |
| Slides link for the source line | ${l.slidesUrl || 'none'} |
| Lecturer | ${l.lecturer || 'see the start of the transcript'} |
| Lecture | ${l.n}. ${l.title} — по-русски: ${l.titleRu} |
| Page to write | ${page(l)} |
| Old page to keep our additions from | ${l.oldPage ? `${l.oldPage} (read with \`git show HEAD:${l.oldPage}\`)` : 'none'} |
| Glossary (read only) | ${a.glossary} |
| Your registers | scripts/${prefix}-diagrams/glossary-lec${pad(l.n)}.md, figures-lec${pad(l.n)}.md; scripts/${prefix}-code/README-lec${pad(l.n)}.md |
| Diagrams | scripts/${prefix}-diagrams/lec${pad(l.n)}_diagrams.py with scripts/${prefix}-diagrams/excb.py (the prep step set it up for this course; if it is missing, copy it from scripts/data-quality-fundamentals-diagrams/ and set OUT and the scene prefix as \`references/lead.md\` step 3 says). The canvas is shared with other writers: excb.py has a lock. Look at every PNG: every flow between boxes needs an arrow, a label alone is not enough. |
| Images | public/assets/${a.slug}/lec${pad(l.n)}-<name>.png |
| Code | scripts/${prefix}-code/lec${pad(l.n)}_<name>.py |
| Size target | ${w(l.words * LO / 100)}-${w(l.words * HI / 100)} prose words, aim for ${w(l.words * AIM / 100)} |
| Previous / next | ${prevLink} / ${nextLink} |
${(a.notes || l.notes) ? `\nNotes from the lead (follow them, they win over the defaults above):\n${a.notes ? '- ' + a.notes + '\n' : ''}${l.notes ? '- ' + l.notes + '\n' : ''}` : ''}
At the end:
1. \`python3 -I scripts/book-tools/words.py ${TARGET} --source ${l.src} ${page(l)}\`. If it is over ${HI}%, cut now with \`Edit\` until it is ${DRAFT_MAX}% or less: drop repeats, side examples and minor details, keep every main idea, number and warning.
2. \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${page(l)}\`, fix every ERROR.
3. \`mkdir -p ${stateDir} && touch ${mark(l, 'write')}\`

${COMMON}`, { label: `write lec${l.n}`, phase: 'Write', schema: WRITE, ...M('write', 'sonnet', 'high') })
    if (!write) throw new Error(`writer failed for lecture ${l.n}`)
    return { l, write }
  },

  // Stage 2: size check, one retry
  async (r) => {
    if (!r) return r
    const pct = r.write.pct
    if (a.reviewOnly || st(r.l.n).done.includes('review') || (pct >= LO && pct <= HI)) return r
    const size = await agent(`The page ${page(r.l)} is ${pct}% of the lecture transcript ${r.l.src}. The target is ${LO}-${HI}%, aim for ${AIM}%.
${pct > HI ? 'Cut it: drop repeats, side examples, stories and minor details. Keep every main idea, definition, number and warning, and the explanation of each main concept.' : 'It is too thin: add the main ideas, explanations and examples of the lecture that are missing. Read the transcript for them.'}
Change the page only with \`Edit\`. Do not touch code blocks, links, front matter, or headings.
Then run \`python3 -I scripts/book-tools/words.py ${TARGET} --source ${r.l.src} ${page(r.l)}\` and \`python3 -I scripts/ru-proofread/check.py ${page(r.l)}\` (fix every ERROR).
Return the new % and one line on what you changed.

${COMMON}`, { label: `size lec${r.l.n}`, phase: 'Size', schema: SIZE, ...M('size', 'opus', 'medium') })
    if (size && (size.pct < LO || size.pct > HI)) log(`lecture ${r.l.n} is still ${size.pct}% after one size fix`)
    return { ...r, size }
  },

  // Stage 3: correctness review (fresh agent, never the writer)
  async (r) => {
    if (!r) return r
    if (st(r.l.n).done.includes('review')) return { ...r, review: { reused: true, statsLow: st(r.l.n).statsLow } }
    const before = `${beforeDir}/lec${pad(r.l.n)}.md`
    const review = await agent(`Proofread a Russian page: correctness review.

1. \`mkdir -p ${beforeDir} && [ -f ${before} ] || cp ${page(r.l)} ${before}\`
2. Read \`.claude/skills/ru-proofread/references/review-prompt.md\` and do the job in its prompt block. File: ${page(r.l)}. Glossary: ${a.glossary}. Get the script output yourself: \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${page(r.l)}\`. ${LECTURE_SOURCE}
3. Guard: \`python3 -I scripts/ru-proofread/check.py --before ${before} ${page(r.l)}\`. If it shows ERROR, undo the edit that caused it. guardOk = no ERROR left.
4. \`python3 -I scripts/ru-proofread/check.py --stats ${page(r.l)}\`. statsLow = it prints LOW, or check.py reports \`choppy\`.
5. \`touch ${mark(r.l, 'review')}\`

${COMMON}`, { label: `review lec${r.l.n}`, phase: 'Review', schema: REVIEW, ...M('review', 'sonnet', 'medium') })
    if (!review) throw new Error(`review failed for lecture ${r.l.n}`)
    if (!review.guardOk) log(`lecture ${r.l.n}: guard still fails after review`)
    return { ...r, review }
  },

  // Stage 4: flow pass, only when the rhythm is LOW
  async (r) => {
    if (!r) return r
    if (st(r.l.n).done.includes('flow') || !r.review.statsLow) return r
    const before = `${beforeDir}/lec${pad(r.l.n)}.md`
    const flow = await agent(`Proofread a Russian page: flow pass.

1. Read \`.claude/skills/ru-proofread/references/flow-prompt.md\` and do the job in its prompt block. File: ${page(r.l)}. Glossary: ${a.glossary}. Get the numbers yourself: \`python3 -I scripts/ru-proofread/check.py --stats ${page(r.l)}\` and \`python3 -I scripts/ru-proofread/check.py --only choppy,same-opener,long-sentence ${page(r.l)}\`. ${LECTURE_SOURCE}
2. Guard: \`python3 -I scripts/ru-proofread/check.py --before ${before} --max-change 10 ${page(r.l)}\`. If it shows ERROR, undo the edit that caused it.
3. Size: \`python3 -I scripts/book-tools/words.py ${TARGET} --source ${r.l.src} ${page(r.l)}\`. If it is over ${FLOW_MAX}%, undo your longest additions until it is ${FLOW_MAX}% or less.
4. \`touch ${mark(r.l, 'flow')}\`

${COMMON}`, { label: `flow lec${r.l.n}`, phase: 'Flow', schema: FLOW, ...M('flow', 'opus', 'medium') })
    return { ...r, flow }
  },

  // Stage 5: clarity pass, always (stats cannot see vague text, AI slop, contradictions or gaps in explanations)
  async (r) => {
    if (!r) return r
    if (st(r.l.n).done.includes('clarity')) return r
    const before = `${beforeDir}/lec${pad(r.l.n)}.md`
    const flagged = [...(r.write.doubtful || []), ...((r.review && r.review.doubtful) || [])].filter(d => /\bline\s*\d+|строк[аеи]\s*\d+/i.test(d))
    const clarity = await agent(`Proofread a Russian page: clarity pass (final read).

1. Read \`.claude/skills/ru-proofread/references/clarity-prompt.md\` and do the job in its prompt block. File: ${page(r.l)}. Source (to check meaning): the lecture transcript ${r.l.src}${r.l.materials ? ` and the slides text ${r.l.materials}` : ''}. Glossary: ${a.glossary}. ${LECTURE_SOURCE}
   This page must teach a newcomer. Also check each main concept: does the page say what it is, why it is needed, and how it works? If one of these is missing and the transcript has it, add one or two sentences from the transcript (type "gap").
   Places the writer flagged as unclear: ${flagged.length ? '\n' + flagged.map(d => '   - ' + d).join('\n') : 'none'}
2. Guard: \`python3 -I scripts/ru-proofread/check.py --before ${before} --max-change 20 ${page(r.l)}\` and \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${page(r.l)}\`. If either shows ERROR, undo the edit that caused it.
3. Size: \`python3 -I scripts/book-tools/words.py ${TARGET} --source ${r.l.src} ${page(r.l)}\`. Take the %. Clarity beats brevity: up to ${CLARITY_MAX}% is fine when your additions make the page clearer.
4. \`touch ${mark(r.l, 'clarity')}\`

${COMMON}`, { label: `clarity lec${r.l.n}`, phase: 'Clarity', schema: CLARITY, ...M('clarity', 'opus', 'medium') })
    if (!clarity) log(`lecture ${r.l.n}: clarity pass failed`)
    return { ...r, clarity }
  },

  // Stage 6 (optional, checkCode: true): every code example runs and its output on the page is real
  async (r) => {
    if (!r || !a.checkCode || st(r.l.n).done.includes('code')) return r
    const code = await agent(`Check the code examples of lecture ${r.l.n}: ${page(r.l)}.
Code folder: scripts/${prefix}-code/ (files lec${pad(r.l.n)}_*, requirements*.txt, README.md).

1. List every code block on the page: language, and the \`text\` output block under it, if any. Solutions inside \`<details>\` count too.
2. SQL: \`python3 scripts/kimball-diagrams/check_sql.py ${page(r.l)}\` must print OK. Then check outputs: run the sql blocks in order in one \`duckdb :memory:\` session and compare each result with the \`text\` block under it on the page.
3. Python: make a venv in ${a.scratch}/venv-code-lec${pad(r.l.n)} from scripts/${prefix}-code/requirements.txt. Run \`python3 -I scripts/lecture-tools/check_code.py ${page(r.l)} scripts/${prefix}-code --prefix lec${pad(r.l.n)} --python <venv>/bin/python\`: every line must be ok. Then run \`python3 -I scripts/book-tools/same_output.py --python <venv>/bin/python <script>\` on each lec${pad(r.l.n)}_*.py: it must print same x6.
4. Shell blocks that are not files: run them in a temp folder.
5. Fix: if an output on the page differs from the real output, paste the real output. If code fails, make the smallest fix that keeps what the example teaches, and update the output. Never type output by hand. Edit only code blocks, their outputs and one sentence about them; no other prose.
6. If something cannot run here (GPU, paid API, large model), do not fake it: count it as notRun and say why.
7. \`touch ${mark(r.l, 'code')}\`
Do not edit README.md or other shared registers: put status changes in problems.

${COMMON}`, { label: `code lec${r.l.n}`, phase: 'Code', schema: CODE, ...M('code', 'sonnet', 'medium') })
    if (!code) log(`lecture ${r.l.n}: code check failed`)
    return { ...r, code }
  },
)

const ok = results.filter(Boolean)
const failed = todo.filter(l => !skipped.includes(l) && !ok.some(r => r.l.n === l.n))
if (failed.length) log(`failed lectures: ${failed.map(l => l.n).join(', ')}. Rerun with only: [${failed.map(l => l.n).join(', ')}]`)

const report = {
  lectures: ok.map(r => ({
    n: r.l.n,
    page: page(r.l),
    title: r.write.title || r.l.titleRu,
    pct: r.clarity ? r.clarity.pct : r.flow ? r.flow.pct : (r.size ? r.size.pct : r.write.pct),
    diagrams: r.write.diagramsDrawn,
    codeOk: r.write.codeOk,
    codeProblems: r.write.codeProblems || [],
    review: r.review.reused ? 'done earlier' : `${r.review.changes} changes (${r.review.byType})`,
    flow: r.flow ? `${r.flow.paragraphs} paragraphs` : 'not needed',
    clarity: r.clarity ? `${r.clarity.changes} changes, ${r.clarity.deleted} deleted (${r.clarity.byType})` : 'done earlier or failed',
    clarityFound: (r.clarity && r.clarity.found) || [],
    newPatterns: (r.clarity && r.clarity.newPatterns) || [],
    code: r.code ? `${r.code.blocks} blocks: ${r.code.ok} ok, ${r.code.fixed} fixed, ${r.code.notRun} not run` : (a.checkCode ? 'done earlier or failed' : 'not checked'),
    codeCheckProblems: (r.code && r.code.problems) || [],
    guardOk: (r.review.guardOk !== false) && (!r.flow || r.flow.guardOk) && (!r.clarity || r.clarity.guardOk),
    meaningRisks: [...(r.review.meaningRisks || []), ...((r.flow && r.flow.meaningRisks) || []), ...((r.clarity && r.clarity.meaningRisks) || [])],
    doubtful: [...(r.write.doubtful || []), ...(r.review.doubtful || [])],
  })),
  skipped: skipped.map(l => l.n),
  failed: failed.map(l => l.n),
}

// ---------- Status file: one row per course in scripts/lecture-tools/status.md (runs at the end of every run)
const recordStatus = async () => {
  report.statusFile = await agent(`Run this one command. Reply with its last output line only.
python3 -I scripts/book-tools/status.py ${a.slug} --kind lecture --group ${a.group} --title ${JSON.stringify(C.title)} --scratch ${a.scratch} --chapters ${all.map(l => l.n).join(',')}`,
    { label: 'status file', phase: 'Status', model: 'sonnet', effort: 'low' })
}

// ---------- Whole course (needs all lectures: a real barrier)
if (a.skipCourse || (a.only && !a.publish) || a.reviewOnly || failed.length) {
  log(a.only || a.skipCourse || a.reviewOnly ? 'course steps skipped (partial or review-only run; add "publish": true to put written lectures on the site)' : 'course steps skipped: some lectures failed')
  await recordStatus()
  return report
}

phase('Course')
const titles = new Map(ok.map(r => [r.l.n, r.write.title || r.l.titleRu]))
const notYet = all.filter(l => !written(l))
const PARTIAL = notYet.length ? `
Not all lectures are written yet. Written: ${all.filter(written).map(l => l.n).join(', ')}. Not written: ${notYet.map(l => l.n).join(', ')}.
- The overview lists every lecture of the course. Link only the written ones. A lecture that is not written gets its title without a link and «скоро» in the last column. Write the course parts (О чём курс, Как устроен курс) from the lecture titles and the course facts; do not invent content of unwritten lectures. Put \`## Главные идеи\` only for written lectures.
- In nav and in lecture-summaries/index.md the course is listed as usual: the sidebar shows only the pages that exist.
- Previous/Next lines: every written lecture links only to written lectures. Add a missing «Следующая» to a written lecture when the next lecture is now written.` : ''
report.course = await agent(`Finish the course "${C.title}": the lectures of this run are written and proofread.

Load the \`lecture-summary\` skill, then read its \`references/lead.md\`. Do lead steps 6, 7 and 8 only:
- merge scripts/${prefix}-diagrams/glossary-lecNN.md, figures-lecNN.md and scripts/${prefix}-code/README-lecNN.md into glossary.md, figures.md and README.md, then delete the -lecNN files;
- the overview page ${courseDir}/index.md (section "Overview page"), with the EPUB link line. Course facts: ${JSON.stringify(C)}. Practice: ${practice}.
  Lectures (n | title the writer used, or the draft title | minutes | page | written): ${all.map(l => `${l.n} | ${titles.get(l.n) || l.titleRu} | ${l.minutes} | ${url(l)} | ${written(l) ? 'yes' : 'no'}`).join('; ')}
- src/nav.mjs and the row in src/content/docs/lecture-summaries/index.md. If that index.md does not exist, this is the first course: also do "First course only: create the section".${PARTIAL}
Run \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${courseDir}/index.md\` (and on lecture-summaries/index.md if you wrote it) and fix every ERROR. Run \`check.py --stats\` on them too; if it shows LOW, link the sentences (rules in \`.claude/skills/ru-proofread/references/rules.md\`, section "Flow").
Add the lectures' new clarity patterns to scripts/ru-proofread/calques.tsv if they are real and repeatable (keep its format; WARN level unless sure): ${JSON.stringify(ok.flatMap(r => (r.clarity && r.clarity.newPatterns) || []))}
Check the lectures as a set (writers worked in parallel and could not see each other):
- Titles: every lecture's \`title\`, \`sidebar.label\`, the Previous/Next link texts in other lectures, and the overview tables must use the same Russian lecture title.
- Diagrams: \`ls public/assets/${a.slug}/\`. If two lectures show the same idea, keep the diagram in the lecture that explains it more, replace the other image with one sentence and a link to that lecture, delete the extra PNG, and mark it skipped in figures.md.
${a.courseNotes ? 'Notes from the lead (follow them): ' + a.courseNotes + '\n' : ''}Do not run npm run build: the next step does it.
Reply with one short line per item: done, or the problem.

${COMMON.split('\n').filter(x => !x.includes('shared files')).join('\n')}`, { label: 'course', phase: 'Course', ...M('course', 'opus', 'high') })

phase('Build')
report.build = await agent(`Build and check the course "${a.slug}".
1. Load the \`book-epub\` skill and follow it for ${a.slug}: the script builds lecture courses too. Build, validate, check the link on the overview page.
2. \`npm run build 2>&1 | tail -30\`. Fix only clear, small errors in this course's files (front matter, links). Report anything else.
3. \`ls dist/lecture-summaries/${a.group}/${a.slug}/index.html\` must exist.
Reply with one short line per check: ok, or the problem.`, { label: 'build', phase: 'Build', ...M('build', 'sonnet', 'medium') })

await recordStatus()
return report
