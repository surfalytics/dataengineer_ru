export const meta = {
  name: 'book-prep',
  description: 'Book summary, part 1: split a PDF/EPUB into chapter text files, count words, draft the glossary',
  whenToUse: 'First step of a new book summary on dataengineer.ru. Run it before the book-summary workflow. The owner checks its plan, then book-summary runs on it.',
  phases: [
    { title: 'Split', detail: 'table of contents, page ranges, chNN.txt, word counts' },
    { title: 'Glossary', detail: 'term table for all chapters (sonnet)', model: 'sonnet' },
  ],
}

// args: { source: "/abs/path/book.pdf" | ".epub", slug: "designing-data-intensive-applications",
//         group: "engineering", scratch: "/abs/scratch/dir", scriptsPrefix?: "ddia" }
const a = args || {}
const missing = ['source', 'slug', 'group', 'scratch'].filter(k => !a[k])
if (missing.length) {
  return { error: `missing args: ${missing.join(', ')}`, usage: 'args: {source, slug, group, scratch, scriptsPrefix?}' }
}
const prefix = a.scriptsPrefix || a.slug
const src = `${a.scratch}/src`
const planPath = `${a.scratch}/book-plan.json`
const glossaryPath = `scripts/${prefix}-diagrams/glossary.md`
const bookDir = `src/content/docs/book-summaries/${a.group}/${a.slug}`

const PLAN = {
  type: 'object',
  properties: {
    title: { type: 'string' }, author: { type: 'string' }, publisher: { type: 'string' }, year: { type: 'string' },
    technical: { type: 'boolean', description: 'true if SQL/DuckDB practice fits (modeling, SQL, ETL)' },
    chapters: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          n: { type: 'integer' }, title: { type: 'string' }, titleRu: { type: 'string' },
          file: { type: 'string', description: 'NN-english-slug.md' },
          src: { type: 'string' }, pages: { type: 'string' }, words: { type: 'integer' },
          oldPage: { type: 'string', description: 'path of the existing page, empty if none' },
          sql: { type: 'boolean', description: 'true if this chapter itself has SQL or DuckDB code or examples' },
        },
        required: ['n', 'title', 'titleRu', 'file', 'src', 'pages', 'words', 'oldPage', 'sql'],
      },
    },
    skipped: { type: 'array', items: { type: 'string' }, description: 'parts not treated as chapters (preface, appendix, index) and why' },
    problems: { type: 'array', items: { type: 'string' } },
  },
  required: ['title', 'author', 'technical', 'chapters', 'skipped', 'problems'],
}

phase('Split')
const plan = await agent(`Prepare the book for a Russian summary on dataengineer.ru. Do not write any pages.

Book: ${a.source}
Output folder (scratchpad, never in git): ${src}

1. Read the table of contents as text. PDF: \`pdftotext -f 1 -l 20 "${a.source}" - | head -400\`. Never open PDF pages as images.
2. PDF: find the offset between printed page numbers and PDF page numbers. Check the first page of 2-3 chapters with \`pdftotext -f N -l N\`. Then split:
   \`python3 -I scripts/book-tools/split_source.py "${a.source}" ${src} --chapters "1:first-last,2:first-last,..."\`
   EPUB: run \`split_source.py "${a.source}" ${src}\`, then copy the chapter documents to ${src}/chNN.txt (two-digit number).
3. Check each chNN.txt: its first lines must show the chapter title, and its end must be just before the next chapter. Fix the ranges if not.
4. Count words: \`python3 -I scripts/book-tools/words.py ${src}\` (only the chNN.txt rows matter).
5. Only real chapters get a number. List preface, appendix, glossary and index under "skipped" with a reason. Keep a preface only if it has real content, as chapter 0.
6. For each chapter: \`file\` = NN-<short English slug in lowercase with hyphens>.md; \`titleRu\` = a short Russian title. If ${bookDir}/ already exists, set \`oldPage\` to the matching existing page path (keep its file name), else "". Set \`sql\` = true if the chapter has SQL or DuckDB code or examples (\`grep -ci "select \\|duckdb" chNN.txt\`, then look).
7. Write the result as JSON to ${planPath}.

Keep tool output short (head, tail). Return the plan.`, { label: 'split', phase: 'Split', schema: PLAN, model: 'sonnet', effort: 'medium' })

if (!plan || !plan.chapters || !plan.chapters.length) {
  return { error: 'split failed', plan }
}
// The agent sometimes returns bare file names. Make every src an absolute path.
plan.chapters = plan.chapters.map(c => ({ ...c, src: c.src.startsWith('/') ? c.src : `${src}/${c.src.replace(/^.*\//, '')}` }))
log(`${plan.chapters.length} chapters, ${plan.chapters.reduce((s, c) => s + c.words, 0)} words`)

const GLOSS = {
  type: 'object',
  properties: {
    path: { type: 'string' }, terms: { type: 'integer' },
    openQuestions: { type: 'array', items: { type: 'string' }, description: 'terms where the owner must pick the form: term, options, your advice' },
  },
  required: ['path', 'terms', 'openQuestions'],
}

phase('Glossary')
const glossary = await agent(`Make the term glossary for the Russian summary of "${plan.title}" (${plan.author}).

Load the \`book-summary\` skill and follow its section "1. Glossary first". Do not write chapter pages.
Chapter text files: ${src}/ch*.txt. Skim them for terms; you do not need every detail.
Write ${glossaryPath} as a table \`English | Как пишем | Не писать | Пояснение\`. If the file exists, keep its rows and add new ones.
Only terms that need a rule get a row: the term has a wrong form to avoid, or there is a choice between English and a Russian word, or the book uses it in a special sense. Skip plain words and product names. Aim for 30-60 rows.
Reuse before you decide: read the glossaries of other books (\`ls scripts/*-diagrams/glossary.md\`, read 2-3 that are close to this topic) and take their forms. Do not grep all summary pages.
Site-wide forms win over everything: \`scripts/ru-proofread/calques.tsv\` lists them (for example \`pipeline\`, never пайплайн). Never put a form from that file into "Как пишем".
One form per term. When you are not sure which form the owner wants (English or an established Russian word), take the form from the other glossaries and list the term under openQuestions.
Return the path, the number of terms, and the open questions.`, { label: 'glossary', phase: 'Glossary', schema: GLOSS, model: 'sonnet', effort: 'medium' })

return {
  plan,
  planPath,
  glossary,
  next: {
    workflow: 'book-summary',
    args: {
      slug: a.slug, group: a.group, scratch: a.scratch, source: a.source, scriptsPrefix: prefix,
      title: plan.title, author: plan.author, technical: plan.technical,
      glossary: glossaryPath, chapters: plan.chapters,
    },
  },
}
