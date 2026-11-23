export const meta = {
  name: 'page-proofread',
  description: 'Proofread Russian site pages (not book summaries): correctness review, flow pass on dry pages, clarity pass. One agent per pass per batch of pages',
  whenToUse: 'For pages outside book-summaries/. Args: { scratch, batches: [{ name, pages: [...] }] }. Batches run in parallel. For book chapters use book-summary with reviewOnly instead.',
  phases: [
    { title: 'Review', detail: 'correctness review (sonnet, medium)', model: 'sonnet' },
    { title: 'Flow', detail: 'flow pass, only pages with a dry rhythm (opus, medium)', model: 'opus' },
    { title: 'Clarity', detail: 'final read: vague text, AI slop, contradictions (opus, medium)', model: 'opus' },
  ],
}

// args: {
//   scratch: '/abs/dir',                       // before/ copies of the pages go here
//   batches: [{ name: 'processing', pages: ['src/content/docs/processing/bi.md', ...], notes?: 'text for this batch' }],
//   notes?: 'text for every agent',
//   skipFlow?: false, skipClarity?: false,
//   models?: { review: 'sonnet/medium', flow: 'opus/medium', clarity: 'opus/medium' },  // per-stage override
// }
// Batch size: 2,000-4,000 Russian words of prose (about one book chapter). Pages of one batch share one agent per pass.
// After the run, the lead checks the diff, the guard, `check.py` and `npm run build` (see the ru-proofread skill).
const a = args || {}
const missing = ['scratch', 'batches'].filter(k => !a[k])
if (missing.length) return { error: `missing args: ${missing.join(', ')}` }
const bad = a.batches.filter(b => !b.name || !Array.isArray(b.pages) || !b.pages.length || b.pages.some(p => p.includes('/book-summaries/')))
if (bad.length) return { error: 'every batch needs a name and a list of pages outside book-summaries/', bad: bad.map(b => b.name || '?') }

// Never use haiku for Russian text.
const M = (stage, model, effort) => {
  const o = (a.models || {})[stage]
  if (!o) return { model, effort }
  const [om, oe] = o.split('/')
  return { model: om || model, effort: oe || effort }
}

const list = pages => pages.map(p => `- ${p}`).join('\n')
const loop = (pages, cmd) => `for p in ${pages.join(' ')}; do ${cmd}; done`
const guard = (pages, max) => loop(pages, `python3 -I scripts/ru-proofread/check.py --before ${a.scratch}/before/$p${max ? ' --max-change ' + max : ''} $p`)
const notes = b => [a.notes, b.notes].filter(Boolean).map(n => `Notes from the lead (follow them): ${n}`).join('\n')

const SITE = `These are site pages, not book summaries. Read the prompt file with these changes:
- There is no book, source text or glossary. Ignore what the prompt says about them. Never add facts. If a fact, number or link looks wrong or outdated, do not fix it: list it under meaning risks.
- Many pages are lists of links (courses, books, tools) with a short description. Fix the Russian of the descriptions. Do not change URLs, the order of items, emoji flags (🇷🇺 🇬🇧) or ⭐.
- In \`Name - description\` lines use a dash: \`Name — description\`.
- Headings: you may change only the letter case: «Архитектура Аналитического Решения» → «Архитектура аналитического решения». The anchor stays the same. Any other problem in a heading: list it under doubtful.
- Front matter (the block between the first two \`---\` lines): do not touch. List problems in it under doubtful.
- .mdx pages: do not touch \`import\` lines, component names, or the \`href\`, \`type\`, \`level\`, \`star\` attributes. You may fix the Russian in \`title\` and \`description\` attributes and in text between tags.
- Spelling: «дата-инженер» with a hyphen, in lower case inside a sentence. «Инжиниринг Данных» with capitals is the site name: keep it.
- One form per term on a page: keep the form the page uses most.
- Start every item of meaning risks and doubtful with the page and line: \`processing/dw.md:57 ...\`.`

const COMMON = `Rules for this run:
- You are one step of an automated pipeline. Do not start other agents. Do not ask questions: decide, and put doubts in your reply.
- Edit only the pages listed above. Never run \`npm run build\` or \`npm run dev\`. Never edit scripts, skills or other shared files.
- Keep tool output short (\`| tail -40\`). Do not re-read a file right after you wrote it.`

// ---------- Schemas
const REVIEW = {
  type: 'object',
  properties: {
    changes: { type: 'integer' },
    byType: { type: 'string', description: 'e.g. spelling 4, punctuation 6, calque 3, typography 12' },
    meaningRisks: { type: 'array', items: { type: 'string' } },
    doubtful: { type: 'array', items: { type: 'string' } },
    guardOk: { type: 'boolean' },
    lowPages: { type: 'array', items: { type: 'string' }, description: 'page paths exactly as given: dry rhythm and at least one paragraph of 3+ sentences' },
  },
  required: ['changes', 'byType', 'meaningRisks', 'doubtful', 'guardOk', 'lowPages'],
}
const FLOW = {
  type: 'object',
  properties: {
    paragraphs: { type: 'integer' },
    tools: { type: 'string', description: 'e.g. link 6, join 4, unfold 2' },
    meaningRisks: { type: 'array', items: { type: 'string' } },
    guardOk: { type: 'boolean' },
    lengthChange: { type: 'string', description: 'length change per page from the guard, e.g. dw.md +3.1%, spark.md +4.0%' },
  },
  required: ['paragraphs', 'tools', 'meaningRisks', 'guardOk', 'lengthChange'],
}
const CLARITY = {
  type: 'object',
  properties: {
    changes: { type: 'integer' },
    byType: { type: 'string', description: 'e.g. vague 3, slop 2, contradiction 1' },
    deleted: { type: 'integer', description: 'sentences deleted, all pages' },
    found: { type: 'array', items: { type: 'string' }, description: 'every problem line from step 1: "page:line, type T: problem → fixed" or "→ left: why"' },
    meaningRisks: { type: 'array', items: { type: 'string' } },
    newPatterns: { type: 'array', items: { type: 'string' }, description: 'bad → good, for calques.tsv' },
    guardOk: { type: 'boolean' },
  },
  required: ['changes', 'byType', 'deleted', 'found', 'meaningRisks', 'newPatterns', 'guardOk'],
}

// ---------- One batch: review → flow (dry pages only) → clarity. Batches do not wait for each other.
const results = await pipeline(
  a.batches,

  // Stage 1: correctness review
  async (b) => {
    const review = await agent(`Proofread Russian site pages: correctness review (pass 1 of 3).

Pages (${b.pages.length}):
${list(b.pages)}

1. Save a copy of each page (pages saved earlier are kept): \`${loop(b.pages, `mkdir -p "$(dirname ${a.scratch}/before/$p)" && { [ -f ${a.scratch}/before/$p ] || cp $p ${a.scratch}/before/$p; }`)}\`
2. Script findings: \`python3 -I scripts/ru-proofread/check.py ${b.pages.join(' ')}\`.
3. Read \`.claude/skills/ru-proofread/references/review-prompt.md\` and do the job in its prompt block, page by page. Fix the script findings too: every ERROR, and every WARN that is a real problem.
4. Guard: \`${guard(b.pages)}\`. If it shows ERROR, undo the edit that caused it. guardOk = no ERROR left.
5. Rhythm: \`python3 -I scripts/ru-proofread/check.py --stats ${b.pages.join(' ')}\`. lowPages = the pages where it prints LOW or check.py reported \`choppy\`, and that have at least one paragraph of 3 or more sentences. A page that is only a list of links is not in lowPages.

${SITE}
${notes(b)}
${COMMON}`, { label: `review ${b.name}`, phase: 'Review', schema: REVIEW, ...M('review', 'sonnet', 'medium') })
    if (!review) throw new Error(`review failed for ${b.name}`)
    if (!review.guardOk) log(`${b.name}: guard still fails after review`)
    return { b, review }
  },

  // Stage 2: flow pass, only pages with a dry rhythm and real paragraphs
  async (r) => {
    if (!r) return r
    const low = r.b.pages.filter(p => (r.review.lowPages || []).some(l => p.endsWith(l) || l.endsWith(p)))
    if (a.skipFlow || !low.length) return { ...r, low }
    const flow = await agent(`Proofread Russian site pages: flow pass (pass 2 of 3). An earlier editor already fixed grammar, terms and typography.

Pages with a dry rhythm (work only on these):
${list(low)}

1. Read \`.claude/skills/ru-proofread/references/flow-prompt.md\` and do the job in its prompt block, page by page. Get the numbers yourself: \`python3 -I scripts/ru-proofread/check.py --stats ${low.join(' ')}\` and \`python3 -I scripts/ru-proofread/check.py --only choppy,same-opener,long-sentence ${low.join(' ')}\`.
   Work on paragraphs of prose. Lists of links and tables stay as they are.
2. Guard: \`${guard(low, 10)}\`. If it shows ERROR, undo the edit that caused it. guardOk = no ERROR left.

${SITE}
${notes(r.b)}
${COMMON}`, { label: `flow ${r.b.name}`, phase: 'Flow', schema: FLOW, ...M('flow', 'opus', 'medium') })
    if (!flow) log(`${r.b.name}: flow pass failed`)
    return { ...r, low, flow }
  },

  // Stage 3: clarity pass, always (the rhythm numbers cannot see vague text, AI slop or contradictions)
  async (r) => {
    if (!r || a.skipClarity) return r
    const flagged = r.review.doubtful || []
    const clarity = await agent(`Proofread Russian site pages: clarity pass (pass 3 of 3, the final read). Earlier editors already fixed grammar, terms and rhythm.

Pages (${r.b.pages.length}):
${list(r.b.pages)}

1. Read \`.claude/skills/ru-proofread/references/clarity-prompt.md\` and do the job in its prompt block, page by page. Read each page as a newcomer to data engineering.
   - There is no book to check against. You may add a few words that explain a term in plain words, if this is a plain fact of the field. Do not add new claims, numbers, names or opinions.
   - Contradiction inside a page: make the places match only if one of them is clearly wrong. Otherwise list it under meaning risks.
   - The limit of 3 deleted sentences is per page.
   Places the earlier editor flagged as doubtful (fix each one or say why it is fine): ${flagged.length ? '\n' + flagged.map(d => '   - ' + d).join('\n') : 'none'}
2. Guard: \`${guard(r.b.pages, 20)}\`. If it shows ERROR, undo the edit that caused it. guardOk = no ERROR left.
3. \`python3 -I scripts/ru-proofread/check.py ${r.b.pages.join(' ')}\`: fix every ERROR.

${SITE}
${notes(r.b)}
${COMMON}`, { label: `clarity ${r.b.name}`, phase: 'Clarity', schema: CLARITY, ...M('clarity', 'opus', 'medium') })
    if (!clarity) log(`${r.b.name}: clarity pass failed`)
    return { ...r, clarity }
  },
)

const ok = results.filter(Boolean)
return {
  batches: ok.map(r => ({
    name: r.b.name,
    pages: r.b.pages.length,
    review: `${r.review.changes} changes (${r.review.byType})`,
    flow: r.flow ? `${r.flow.paragraphs} paragraphs on ${r.low.length} pages (${r.flow.tools}); length ${r.flow.lengthChange}` : (r.low && r.low.length && !a.skipFlow ? 'failed' : 'not needed'),
    clarity: r.clarity ? `${r.clarity.changes} changes, ${r.clarity.deleted} deleted (${r.clarity.byType})` : (a.skipClarity ? 'skipped' : 'failed'),
    clarityFound: (r.clarity && r.clarity.found) || [],
    newPatterns: (r.clarity && r.clarity.newPatterns) || [],
    guardOk: r.review.guardOk !== false && (!r.flow || r.flow.guardOk) && (!r.clarity || r.clarity.guardOk),
    meaningRisks: [...(r.review.meaningRisks || []), ...((r.flow && r.flow.meaningRisks) || []), ...((r.clarity && r.clarity.meaningRisks) || [])],
    doubtful: r.review.doubtful || [],
  })),
  failed: a.batches.filter(b => !ok.some(r => r.b.name === b.name)).map(b => b.name),
}
