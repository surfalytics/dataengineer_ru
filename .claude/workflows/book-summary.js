export const meta = {
  name: 'book-summary',
  description: 'Book summary, part 2: write, size-check, review, flow-edit and clarity-edit every chapter in parallel, then overview, nav, cover, EPUB, build',
  whenToUse: 'After book-prep, with its "next.args". Also to redo some chapters: pass "only": [3, 5]. Chapters already done are skipped, so a rerun continues where it stopped.',
  phases: [
    { title: 'Status', detail: 'which chapter stages are already done (haiku)', model: 'haiku' },
    { title: 'Write', detail: 'one writer per chapter (opus, high)', model: 'opus' },
    { title: 'Size', detail: 'fix pages outside 20-40% (max one retry)', model: 'opus' },
    { title: 'Review', detail: 'correctness review (sonnet, medium)', model: 'sonnet' },
    { title: 'Flow', detail: 'flow pass only when --stats is LOW (opus, medium)', model: 'opus' },
    { title: 'Clarity', detail: 'final read: vague text, AI slop, contradictions (opus, high)', model: 'opus' },
    { title: 'Code', detail: 'optional (checkCode: true): run every code example, match outputs (sonnet, medium)', model: 'sonnet' },
    { title: 'Book', detail: 'registers, overview, nav, cover (opus, high)', model: 'opus' },
    { title: 'Build', detail: 'EPUB, npm run build, carousel check (sonnet)', model: 'sonnet' },
  ],
}

// args: the "next.args" object returned by book-prep:
// { slug, group, scratch, source, scriptsPrefix, title, author, technical, glossary,
//   chapters: [{ n, title, titleRu, file, src, pages, words, oldPage }],
//   only?: [n, ...], skipBook?: false, redo?: false, checkCode?: false }
const a = args || {}
const missing = ['slug', 'group', 'scratch', 'title', 'glossary', 'chapters'].filter(k => !a[k])
if (missing.length) {
  return { error: `missing args: ${missing.join(', ')}`, usage: 'Run book-prep first and pass its next.args.' }
}

const prefix = a.scriptsPrefix || a.slug
const bookDir = `src/content/docs/book-summaries/${a.group}/${a.slug}`
const urlBase = `/book-summaries/${a.group}/${a.slug}`
const stateDir = `${a.scratch}/state`
const beforeDir = `${a.scratch}/before`
const pad = n => String(n).padStart(2, '0')
const url = c => `${urlBase}/${c.file.replace(/\.md$/, '')}/`
const page = c => `${bookDir}/${c.file}`

const all = [...a.chapters].sort((x, y) => x.n - y.n)
const todo = a.only ? all.filter(c => a.only.includes(c.n)) : all
if (!todo.length) return { error: 'no chapters selected', only: a.only }

const COMMON = `Rules for this run:
- You are one step of an automated pipeline. Do not start other agents. Do not ask questions: decide, and put doubts in your reply.
- Never run \`npm run build\` or \`npm run dev\`. Never edit shared files: index.md, src/nav.mjs, glossary.md, figures.md, README.md registers.
- Keep tool output short (\`| tail -20\`). Do not re-read a file right after you wrote it.`

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

phase('Status')
let status = { chapters: [] }
if (!a.redo) {
  status = (await agent(`Check pipeline state. Run commands only, change nothing.
For each chapter below:
- list which marker files exist in ${stateDir}/: chNN.write.done, chNN.review.done, chNN.flow.done, chNN.clarity.done, chNN.code.done (NN = two digits);
- if the page exists: \`python3 -I scripts/book-tools/words.py --source <src> <page>\` (take the %) and \`python3 -I scripts/ru-proofread/check.py --stats <page>\` (statsLow = true if it prints LOW).
Chapters (n | src | page):
${todo.map(c => `${c.n} | ${c.src} | ${page(c)}`).join('\n')}`,
    { label: 'status', phase: 'Status', schema: STATUS, model: 'haiku', effort: 'low' })) || { chapters: [] }
}
const st = n => status.chapters.find(s => s.n === n) || { done: [], pct: 0, statsLow: false }
const skipped = todo.filter(c => st(c.n).done.includes('clarity') && (!a.checkCode || st(c.n).done.includes('code')))
if (skipped.length) log(`already done, skipped: chapters ${skipped.map(c => c.n).join(', ')}`)

// ---------- Schemas
const WRITE = {
  type: 'object',
  properties: {
    page: { type: 'string' }, srcWords: { type: 'integer' }, pageWords: { type: 'integer' }, pct: { type: 'number' },
    diagramsDrawn: { type: 'integer' }, diagramsSkipped: { type: 'integer' },
    codeOk: { type: 'boolean' }, codeProblems: { type: 'array', items: { type: 'string' } },
    checkErrors: { type: 'integer', description: 'ERROR count from check.py at the end' },
    doubtful: { type: 'array', items: { type: 'string' }, description: 'doubtful places in the book, meaning risks' },
  },
  required: ['page', 'srcWords', 'pageWords', 'pct', 'diagramsDrawn', 'diagramsSkipped', 'codeOk', 'codeProblems', 'checkErrors', 'doubtful'],
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
const CLARITY = {
  type: 'object',
  properties: {
    changes: { type: 'integer' }, byType: { type: 'string', description: 'e.g. vague 3, slop 2, contradiction 1' },
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
const FLOW = {
  type: 'object',
  properties: {
    paragraphs: { type: 'integer' }, meaningRisks: { type: 'array', items: { type: 'string' } },
    guardOk: { type: 'boolean' }, pct: { type: 'number' },
  },
  required: ['paragraphs', 'meaningRisks', 'guardOk', 'pct'],
}

// ---------- Per-chapter pipeline (no barrier: chapter 1 can be in review while chapter 7 is still writing)
const chapterResults = await pipeline(
  todo.filter(c => !skipped.includes(c)),

  // Stage 1: write
  async (_, c) => {
    const s = st(c.n)
    if (s.done.includes('write')) return { c, write: { page: page(c), pct: s.pct, reused: true } }
    const i = all.findIndex(x => x.n === c.n)
    const prev = all[i - 1], next = all[i + 1]
    const write = await agent(`Write chapter ${c.n} of the Russian summary of "${a.title}" (${a.author}).

Load the \`book-summary\` skill and follow "Chapter steps (worker)". Use the translation guide, "Diagrams", "Chapter page" and "Hands-on code".${(a.technical || c.sql) ? ' Add `## Практика в DuckDB` (read `references/duckdb-practice.md`): ' + (a.technical ? 'this is a technical book.' : 'this chapter uses SQL or DuckDB.') : ' Do not add `## Практика в DuckDB`: the book is not technical and this chapter has no SQL. Code from the book still goes on the page as "Hands-on code from the book" says.'}
Work in few, large steps: plan the whole page, write it with one \`Write\`, then fix with \`Edit\`. Every extra turn re-reads your whole context.
Before you write, get the word budget per section: \`python3 -I scripts/book-tools/words.py --sections ${c.src}\`. Keep each section near its budget. A first draft above 40% wastes tokens: you pay for the words and again for cutting them.
The Russian title "${c.titleRu}" is a draft from the prep step. If it is not natural Russian or breaks the glossary, write a better one. Use the same title in \`title\`, \`sidebar.label\`, and report it in \`doubtful\` so the lead can align links.
Other chapters of this book (other writers draw their diagrams at the same time): ${all.filter(x => x.n !== c.n).map(x => `${x.n}. ${x.title}`).join('; ')}. Draw a diagram for an idea only if this chapter explains it; if the idea belongs to another chapter, link to that chapter instead.

| Input | Value |
|---|---|
| Book chapter (plain text, the only source you read) | ${c.src} (${c.words} words, PDF pages ${c.pages}) |
| Book PDF/EPUB (open one page as an image only to see a figure you redraw) | ${a.source} |
| Chapter | ${c.n}. ${c.title} — по-русски: ${c.titleRu} |
| Page to write | ${page(c)} |
| Old page to keep our additions from | ${c.oldPage ? `${c.oldPage} (read with \`git show HEAD:${c.oldPage}\`)` : 'none'} |
| Glossary (read only) | ${a.glossary} |
| Your registers | scripts/${prefix}-diagrams/glossary-ch${pad(c.n)}.md, figures-ch${pad(c.n)}.md; scripts/${prefix}-code/README-ch${pad(c.n)}.md |
| Diagrams | scripts/${prefix}-diagrams/ch${pad(c.n)}_diagrams.py + excb.py (copy from scripts/data-quality-fundamentals-diagrams/ if missing). The canvas is shared with other writers: excb.py has a lock. Look at every PNG: every flow between boxes needs an arrow, a label alone is not enough. |
| Images | public/assets/${a.slug}/ch${pad(c.n)}-<name>.png |
| Size target | ${Math.round(c.words * 0.2)}-${Math.round(c.words * 0.4)} prose words, aim for ${Math.round(c.words * 0.3)} |
| Previous / next | ${prev ? `[${prev.titleRu}](${url(prev)})` : 'none (first chapter: link to the overview ' + urlBase + '/)'} / ${next ? `[${next.titleRu}](${url(next)})` : 'none'} |

At the end:
1. \`python3 -I scripts/book-tools/words.py --source ${c.src} ${page(c)}\`
2. \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${page(c)}\`, fix every ERROR.
3. \`mkdir -p ${stateDir} && touch ${stateDir}/ch${pad(c.n)}.write.done\`

${COMMON}`, { label: `write ch${c.n}`, phase: 'Write', schema: WRITE, model: 'opus', effort: 'high' })
    if (!write) throw new Error(`writer failed for chapter ${c.n}`)
    return { c, write }
  },

  // Stage 2: size check, one retry
  async (r) => {
    if (!r) return r
    const pct = r.write.pct
    if (st(r.c.n).done.includes('review') || (pct >= 20 && pct <= 40)) return r
    const size = await agent(`The page ${page(r.c)} is ${pct}% of the book chapter ${r.c.src}. The target is 20-40%, aim for 30%.
${pct > 40 ? 'Cut it: drop repeats, side examples and minor details. Keep every main idea, definition, number and warning.' : 'It is too thin: add the main ideas, arguments and examples of the book that are missing. Read the book chapter for them.'}
Change the page only with \`Edit\`. Do not touch code blocks, links, front matter, or headings.
Then run \`python3 -I scripts/book-tools/words.py --source ${r.c.src} ${page(r.c)}\` and \`python3 -I scripts/ru-proofread/check.py ${page(r.c)}\` (fix every ERROR).
Return the new % and one line on what you changed.

${COMMON}`, { label: `size ch${r.c.n}`, phase: 'Size', schema: SIZE, model: 'opus', effort: 'medium' })
    if (size && (size.pct < 20 || size.pct > 40)) log(`chapter ${r.c.n} is still ${size.pct}% after one size fix`)
    return { ...r, size }
  },

  // Stage 3: correctness review (fresh agent, never the writer)
  async (r) => {
    if (!r) return r
    if (st(r.c.n).done.includes('review')) return { ...r, review: { reused: true, statsLow: st(r.c.n).statsLow } }
    const before = `${beforeDir}/ch${pad(r.c.n)}.md`
    const review = await agent(`Proofread a Russian page: correctness review.

1. \`mkdir -p ${beforeDir} && [ -f ${before} ] || cp ${page(r.c)} ${before}\`
2. Read \`.claude/skills/ru-proofread/references/review-prompt.md\` and do the job in its prompt block. File: ${page(r.c)}. Glossary: ${a.glossary}. Get the script output yourself: \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${page(r.c)}\`.
3. Guard: \`python3 -I scripts/ru-proofread/check.py --before ${before} ${page(r.c)}\`. If it shows ERROR, undo the edit that caused it. guardOk = no ERROR left.
4. \`python3 -I scripts/ru-proofread/check.py --stats ${page(r.c)}\`. statsLow = it prints LOW, or check.py reports \`choppy\`.
5. \`touch ${stateDir}/ch${pad(r.c.n)}.review.done\`

${COMMON}`, { label: `review ch${r.c.n}`, phase: 'Review', schema: REVIEW, model: 'sonnet', effort: 'medium' })
    if (!review) throw new Error(`review failed for chapter ${r.c.n}`)
    if (!review.guardOk) log(`chapter ${r.c.n}: guard still fails after review`)
    return { ...r, review }
  },

  // Stage 4: flow pass, only when the rhythm is LOW
  async (r) => {
    if (!r) return r
    if (st(r.c.n).done.includes('flow') || !r.review.statsLow) return r
    const before = `${beforeDir}/ch${pad(r.c.n)}.md`
    const flow = await agent(`Proofread a Russian page: flow pass.

1. Read \`.claude/skills/ru-proofread/references/flow-prompt.md\` and do the job in its prompt block. File: ${page(r.c)}. Glossary: ${a.glossary}. Get the numbers yourself: \`python3 -I scripts/ru-proofread/check.py --stats ${page(r.c)}\` and \`python3 -I scripts/ru-proofread/check.py --only choppy,same-opener,long-sentence ${page(r.c)}\`.
2. Guard: \`python3 -I scripts/ru-proofread/check.py --before ${before} --max-change 10 ${page(r.c)}\`. If it shows ERROR, undo the edit that caused it.
3. Size: \`python3 -I scripts/book-tools/words.py --source ${r.c.src} ${page(r.c)}\`. If it is over 40%, undo your longest additions until it is 40% or less.
4. \`touch ${stateDir}/ch${pad(r.c.n)}.flow.done\`

${COMMON}`, { label: `flow ch${r.c.n}`, phase: 'Flow', schema: FLOW, model: 'opus', effort: 'medium' })
    return { ...r, flow }
  },

  // Stage 5: clarity pass, always (stats cannot see vague text, AI slop or contradictions)
  async (r) => {
    if (!r) return r
    if (st(r.c.n).done.includes('clarity')) return r
    const before = `${beforeDir}/ch${pad(r.c.n)}.md`
    const flagged = [...(r.write.doubtful || []), ...(r.review.doubtful || [])].filter(d => /\bline\s*\d+|строк[аеи]\s*\d+/i.test(d))
    const clarity = await agent(`Proofread a Russian page: clarity pass (final read).

1. Read \`.claude/skills/ru-proofread/references/clarity-prompt.md\` and do the job in its prompt block. File: ${page(r.c)}. Book chapter: ${r.c.src}. Glossary: ${a.glossary}.
   Places the writer flagged as unclear: ${flagged.length ? '\n' + flagged.map(d => '   - ' + d).join('\n') : 'none'}
2. Guard: \`python3 -I scripts/ru-proofread/check.py --before ${before} --max-change 20 ${page(r.c)}\` and \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${page(r.c)}\`. If either shows ERROR, undo the edit that caused it.
3. Size: \`python3 -I scripts/book-tools/words.py --source ${r.c.src} ${page(r.c)}\`. Take the %. Clarity beats brevity: up to 50% is fine when your additions make the page clearer.
4. \`touch ${stateDir}/ch${pad(r.c.n)}.clarity.done\`

${COMMON}`, { label: `clarity ch${r.c.n}`, phase: 'Clarity', schema: CLARITY, model: 'opus', effort: 'high' })
    if (!clarity) log(`chapter ${r.c.n}: clarity pass failed`)
    return { ...r, clarity }
  },

  // Stage 6 (optional, checkCode: true): every code example runs and its output on the page is real
  async (r) => {
    if (!r || !a.checkCode || st(r.c.n).done.includes('code')) return r
    const code = await agent(`Check the code examples of chapter ${r.c.n}: ${page(r.c)}.
Code folder: scripts/${prefix}-code/ (files ch${pad(r.c.n)}_*, requirements*.txt, README.md).

1. List every code block on the page: language, and the \`text\` output block under it, if any.
2. SQL: \`python3 scripts/kimball-diagrams/check_sql.py ${page(r.c)}\` must print OK. Then check outputs: run the sql blocks in order in one \`duckdb :memory:\` session and compare each result with the \`text\` block under it on the page.
3. Python: run each ch${pad(r.c.n)}_*.py the page uses with \`python3 -I scripts/book-tools/same_output.py <script>\` (add \`--python <venv>/bin/python\` if it needs packages: make a venv in ${a.scratch}/venv-code-ch${pad(r.c.n)} from the requirements file). Compare its output with the page.
4. dbt or other projects (ch${pad(r.c.n)}_* folders or run scripts): run them as their README says, in a venv in ${a.scratch}. Compare the results with the page.
5. Shell, YAML and Jinja blocks that are not files: check they match the files in the code folder, or run them in a temp folder.
6. Fix: if an output on the page differs from the real output, paste the real output. If code fails, make the smallest fix that keeps what the example teaches, and update the output. Never type output by hand. Edit only code blocks, their outputs and one sentence about them; no other prose.
7. If something cannot run here (paid API, cloud warehouse, GPU), do not fake it: count it as notRun and say why.
8. \`touch ${stateDir}/ch${pad(r.c.n)}.code.done\`
Do not edit README.md or other shared registers: put status changes in problems.

${COMMON}`, { label: `code ch${r.c.n}`, phase: 'Code', schema: CODE, model: 'sonnet', effort: 'medium' })
    if (!code) log(`chapter ${r.c.n}: code check failed`)
    return { ...r, code }
  },
)

const ok = chapterResults.filter(Boolean)
const failed = todo.filter(c => !skipped.includes(c) && !ok.some(r => r.c.n === c.n))
if (failed.length) log(`failed chapters: ${failed.map(c => c.n).join(', ')}. Rerun with only: [${failed.map(c => c.n).join(', ')}]`)

const report = {
  chapters: ok.map(r => ({
    n: r.c.n,
    page: page(r.c),
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
  skipped: skipped.map(c => c.n),
  failed: failed.map(c => c.n),
}

// ---------- Whole book (needs all chapters: a real barrier)
if (a.skipBook || a.only || failed.length) {
  log(a.only || a.skipBook ? 'book steps skipped (partial run)' : 'book steps skipped: some chapters failed')
  return report
}

phase('Book')
report.book = await agent(`Finish the book "${a.title}" (${a.author}): all chapters are written and proofread.

Load the \`book-summary\` skill, then read its \`references/lead.md\`. Do lead steps 5, 6 and 7 only:
- merge scripts/${prefix}-diagrams/glossary-chNN.md, figures-chNN.md and scripts/${prefix}-code/README-chNN.md into the registers, then delete the -chNN files;
- overview page ${bookDir}/index.md (section "Overview page"), with the EPUB link line from the book-epub skill;
- src/nav.mjs, the row in src/content/docs/book-summaries/index.md, the cover (section "Cover"; source: ${a.source}), the link in src/content/docs/resources/books.md if the book is there.
Run \`python3 -I scripts/ru-proofread/check.py --glossary ${a.glossary} ${bookDir}/index.md\` and fix every ERROR. Run \`check.py --stats\` on index.md too; if it shows LOW, link the sentences (rules in \`.claude/skills/ru-proofread/references/rules.md\`, section "Flow").
Add the chapters' new clarity patterns to scripts/ru-proofread/calques.tsv if they are real and repeatable (keep its format; WARN level unless sure): ${JSON.stringify(ok.flatMap(r => (r.clarity && r.clarity.newPatterns) || []))}
Check the chapters as a set (writers worked in parallel and could not see each other):
- Titles: every chapter's \`title\`, \`sidebar.label\`, the Previous/Next link texts in other chapters, and the overview tables must use the same Russian chapter title. Writers may have changed the draft titles.
- Diagrams: \`ls public/assets/${a.slug}/\`. If two chapters show the same idea, keep the diagram in the chapter that explains it more, replace the other image with one sentence and a link to that chapter, delete the extra PNG, and mark it skipped in figures.md.
Do not run npm run build: the next step does it.
Reply with one short line per item: done, or the problem.

${COMMON.split('\n').filter(l => !l.includes('shared files')).join('\n')}`, { label: 'book', phase: 'Book', model: 'opus', effort: 'high' })

phase('Build')
report.build = await agent(`Build and check the book "${a.slug}".
1. Load the \`book-epub\` skill and follow it for ${a.slug}: build, validate, link on the overview page.
2. \`npm run build 2>&1 | tail -30\`. Fix only clear, small errors in this book's files (front matter, links). Report anything else.
3. \`grep -c "${a.slug}.jpg" dist/index.html\` must print 1 or more (the cover is in the carousel).
Reply with one short line per check: ok, or the problem.`, { label: 'build', phase: 'Build', model: 'sonnet', effort: 'medium' })

return report
