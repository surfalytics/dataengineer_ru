// Собирает EPUB из конспектов книг и курсов лекций.
// Запуск: node scripts/epub/build.mjs                  — все книги и курсы
//         node scripts/epub/build.mjs mom-test         — одна книга или курс (по имени папки)
// Читает src/content/docs/book-summaries/<группа>/<книга>/*.md
//    и src/content/docs/lecture-summaries/<группа>/<курс>/*.md.
// Пишет public/downloads/<папка>.epub. На сайте файл доступен как /downloads/<папка>.epub.
// Нужна системная команда zip (есть в macOS и ubuntu-latest).
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
  cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { basename, extname, join, resolve } from 'node:path';
import GithubSlugger from 'github-slugger';
import yaml from 'js-yaml';
import { toString } from 'mdast-util-to-string';
import rehypeRaw from 'rehype-raw';
import rehypeStringify from 'rehype-stringify';
import remarkGfm from 'remark-gfm';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import sharp from 'sharp';
import { unified } from 'unified';
import { visit } from 'unist-util-visit';

const SITE = 'https://dataengineer.ru';
const TELEGRAM = 'https://t.me/rockyourdata';
// Подпись в начале и в конце каждой главы: сайт и Telegram-канал.
const CREDITS = `Источник: <a href="${SITE}/">dataengineer.ru</a> · Telegram: <a href="${TELEGRAM}">t.me/rockyourdata</a>`;
const ROOT = resolve(import.meta.dirname, '../..');
const DOCS = join(ROOT, 'src/content/docs');
// Виды конспектов: папка, подпись на обложке, строка с авторами, слово для заметки, пункт оглавления.
const KINDS = [
  { dir: 'book-summaries', label: 'Конспект книги', by: 'По книге', what: 'книги', overview: 'Обзор книги' },
  { dir: 'lecture-summaries', label: 'Конспект курса', by: 'Лекторы', what: 'лекций', overview: 'Обзор курса' },
];
const PUBLIC = join(ROOT, 'public');
const OUT = join(PUBLIC, 'downloads');
const MEDIA = {
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.gif': 'image/gif', '.svg': 'image/svg+xml', '.webp': 'image/webp',
};

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

// Все книги и курсы: [{ kind, group, slug, dir }]
// Курс без лекций (есть только страница «О курсе») пропускаем: в EPUB нечего читать.
function findBooks() {
  const books = [];
  const empty = [];
  for (const kind of KINDS) {
    const root = join(DOCS, kind.dir);
    if (!existsSync(root)) continue;
    for (const group of readdirSync(root, { withFileTypes: true })) {
      if (!group.isDirectory()) continue;
      for (const book of readdirSync(join(root, group.name), { withFileTypes: true })) {
        const dir = join(root, group.name, book.name);
        if (book.isDirectory() && existsSync(join(dir, 'index.md'))) {
          const parts = readdirSync(dir).filter((f) => f.endsWith('.md') && f !== 'index.md');
          if (parts.length) books.push({ kind, group: group.name, slug: book.name, dir });
          else empty.push(book.name);
        }
      }
    }
  }
  if (empty.length) console.log(`Без глав и лекций, EPUB не собираем: ${empty.join(', ')}`);
  return books;
}

// Страницы книги по порядку: обзор, затем главы по sidebar.order.
function readPages(book) {
  const pages = readdirSync(book.dir).filter((f) => f.endsWith('.md')).map((file) => {
    const raw = readFileSync(join(book.dir, file), 'utf8');
    const m = raw.match(/^---\n([\s\S]*?)\n---\n?/);
    const data = m ? yaml.load(m[1]) : {};
    const name = basename(file, '.md');
    const isIndex = name === 'index';
    return {
      name,
      isIndex,
      data,
      // Ссылку «Скачать EPUB» в сам файл не кладём.
      body: (m ? raw.slice(m[0].length) : raw).replace(/^.*\]\(\/downloads\/.*\n/gm, ''),
      order: isIndex ? -1 : (data.sidebar?.order ?? 9999),
      // Адрес страницы на сайте. По нему ищем ссылки между главами.
      url: `/${book.kind.dir}/${book.group}/${book.slug}/${isIndex ? '' : `${name.toLowerCase()}/`}`,
    };
  });
  pages.sort((a, b) => a.order - b.order || a.name.localeCompare(b.name));
  pages.forEach((p, i) => {
    p.file = `ch${String(i).padStart(2, '0')}.xhtml`;
    p.navLabel = p.isIndex ? book.kind.overview : (p.data.sidebar?.label ?? p.data.title);
  });
  return pages;
}

// Markdown -> XHTML. Правит картинки, ссылки, якоря и блоки <details>.
function renderPage(page, pages, images) {
  const byUrl = new Map(pages.map((p) => [p.url, p.file]));
  const slugger = new GithubSlugger();
  const sections = [];

  const fix = () => (tree) => {
    visit(tree, 'element', (node, index, parent) => {
      const p = node.properties ?? {};
      if (/^h[1-6]$/.test(node.tagName)) {
        p.id = slugger.slug(toString(node));
        if (node.tagName === 'h2') sections.push({ id: p.id, text: toString(node) });
      }
      if (node.tagName === 'img') {
        const src = String(p.src ?? '');
        const file = join(PUBLIC, src);
        if (!src.startsWith('/') || !existsSync(file)) {
          console.warn(`  ! нет картинки: ${src} (${page.name})`);
          parent.children.splice(index, 1);
          return index;
        }
        const name = src.replace(/^\/(assets\/)?/, '').replace(/\//g, '-');
        images.set(name, file);
        p.src = `images/${name}`;
        delete p.loading;
      }
      if (node.tagName === 'a' && typeof p.href === 'string' && p.href.startsWith('/')) {
        const [path, hash] = p.href.split('#');
        const target = byUrl.get(path.endsWith('/') ? path : `${path}/`);
        // Ссылка на главу этой книги ведёт внутрь файла. Остальные ведут на сайт.
        p.href = target ? target + (hash ? `#${hash}` : '') : SITE + p.href;
      }
      // Многие читалки не умеют <details>. Показываем решение сразу.
      if (node.tagName === 'details') { node.tagName = 'div'; p.className = ['details']; }
      if (node.tagName === 'summary') { node.tagName = 'p'; p.className = ['summary']; }
      // Атрибут align не разрешён в XHTML. Выравнивание переносим в style.
      if ((node.tagName === 'td' || node.tagName === 'th') && p.align) {
        p.style = `text-align: ${p.align}`;
        delete p.align;
      }
      node.properties = p;
    });
  };

  const html = unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(fix)
    .use(rehypeStringify, { closeSelfClosing: true, closeEmptyElements: true, space: 'html' })
    .processSync(page.body);

  page.sections = sections;
  return xhtml(page.data.title, `<h1>${esc(page.data.title)}</h1>\n<p class="credits">${CREDITS}</p>\n${String(html)}\n<p class="credits end">${CREDITS}</p>`);
}

function xhtml(title, body) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="ru" lang="ru">
<head>
<meta charset="UTF-8" />
<title>${esc(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
${body}
</body>
</html>
`;
}

// Разбивает текст на строки не длиннее max символов.
function wrap(text, max) {
  const lines = [];
  for (const w of text.split(/\s+/)) {
    const last = lines[lines.length - 1];
    if (last && (last + ' ' + w).length <= max) lines[lines.length - 1] = `${last} ${w}`;
    else lines.push(w);
  }
  return lines;
}

// Своя обложка с названием. Обложку издателя не берём: это чужая картинка.
async function makeCover(title, author, file, kind) {
  const lines = wrap(title, 20);
  const text = lines.map((l, i) => `<text x="100" y="${520 + i * 104}" font-size="84" font-weight="700" fill="#ffffff">${esc(l)}</text>`).join('');
  // В строку влезает около 48 символов. Длинный список авторов переносим между именами.
  const by = [];
  for (const name of `${kind.by}: ${author}`.split(/,\s*/)) {
    const last = by.length - 1;
    if (last >= 0 && `${by[last]}, ${name}`.length <= 46) by[last] = `${by[last]}, ${name}`;
    else if (last >= 0) { by[last] += ','; by.push(name); } else by.push(name);
  }
  const byText = by.flatMap((l) => (l.length > 46 ? wrap(l, 46) : [l]))
    .map((l, i) => `<text x="100" y="${560 + lines.length * 104 + i * 60}" font-size="46" fill="#c9d6e2">${esc(l)}</text>`).join('');
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" font-family="Helvetica, Arial, DejaVu Sans, sans-serif">
<rect width="1200" height="1600" fill="#0f2a43"/>
<rect x="100" y="250" width="160" height="12" fill="#35c2c1"/>
<text x="100" y="360" font-size="54" fill="#35c2c1">${kind.label}</text>
${text}
${byText}
<text x="100" y="1410" font-size="46" fill="#ffffff">dataengineer.ru</text>
<text x="100" y="1480" font-size="46" fill="#35c2c1">t.me/rockyourdata</text>
</svg>`;
  await sharp(Buffer.from(svg)).jpeg({ quality: 82 }).toFile(file);
}

const CSS = `body { font-family: serif; line-height: 1.5; margin: 0 5%; }
h1 { font-size: 1.5em; line-height: 1.25; margin: 1em 0; }
h2 { font-size: 1.25em; margin-top: 1.6em; }
h3 { font-size: 1.1em; margin-top: 1.3em; }
img { max-width: 100%; height: auto; }
pre { font-family: monospace; font-size: 0.8em; line-height: 1.35; white-space: pre-wrap; word-wrap: break-word; background: #f4f4f4; padding: 0.6em; border-radius: 4px; }
code { font-family: monospace; font-size: 0.9em; }
pre code { font-size: 1em; }
table { border-collapse: collapse; width: 100%; font-size: 0.85em; margin: 1em 0; }
th, td { border: 1px solid #999; padding: 0.3em 0.5em; text-align: left; vertical-align: top; }
blockquote { margin: 1em 0; padding-left: 1em; border-left: 3px solid #999; }
.details { margin: 0.5em 0 1em; padding-left: 1em; border-left: 3px solid #35c2c1; }
.summary { font-weight: bold; }
.source { font-size: 0.9em; }
.credits { font-size: 0.8em; color: #666; }
.credits.end { margin-top: 2em; padding-top: 0.6em; border-top: 1px solid #999; text-align: center; }
`;

async function buildBook(book) {
  const pages = readPages(book);
  const index = pages[0];
  const title = index.data.title;
  const author = index.data.author ?? '';
  const images = new Map();

  const work = mkdtempSync(join(tmpdir(), 'epub-'));
  const oebps = join(work, 'OEBPS');
  mkdirSync(join(oebps, 'images'), { recursive: true });
  mkdirSync(join(work, 'META-INF'));

  writeFileSync(join(work, 'mimetype'), 'application/epub+zip');
  writeFileSync(join(work, 'META-INF/container.xml'), `<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
`);
  writeFileSync(join(oebps, 'style.css'), CSS);
  await makeCover(title.replace(/\s+—\s+конспект (книги|курса|лекций)$/, ''), author, join(oebps, 'cover.jpg'), book.kind);
  writeFileSync(join(oebps, 'cover.xhtml'), xhtml(title, '<div style="text-align: center"><img src="cover.jpg" alt="Обложка конспекта" /></div>'));

  for (const page of pages) {
    let doc = renderPage(page, pages, images);
    if (page.isIndex) {
      const note = `<p class="source">Бесплатный конспект с сайта <a href="${SITE}${page.url}">dataengineer.ru</a>. Это пересказ, а не перевод ${book.kind.what}.</p>`;
      doc = doc.replace('</p>', `</p>\n${note}`);
    }
    writeFileSync(join(oebps, page.file), doc);
  }
  for (const [name, file] of images) cpSync(file, join(oebps, 'images', name));

  const navItems = pages.map((p) => {
    const sub = p.sections.length
      ? `\n<ol>${p.sections.map((s) => `<li><a href="${p.file}#${esc(s.id)}">${esc(s.text)}</a></li>`).join('')}</ol>`
      : '';
    return `<li><a href="${p.file}">${esc(p.navLabel)}</a>${sub}</li>`;
  }).join('\n');
  writeFileSync(join(oebps, 'nav.xhtml'), xhtml('Содержание', `<nav epub:type="toc" id="toc">\n<h1>Содержание</h1>\n<ol>\n${navItems}\n</ol>\n</nav>`));

  // Дата: последний коммит книги. Так файл не меняется без изменений в тексте.
  let modified = new Date().toISOString();
  try {
    const out = execFileSync('git', ['log', '-1', '--format=%cI', '--', book.dir], { cwd: ROOT, encoding: 'utf8' }).trim();
    if (out) modified = new Date(out).toISOString();
  } catch { /* нет git: берём текущее время */ }
  const hash = createHash('sha1').update(`${SITE}/${book.slug}`).digest('hex');
  const uuid = `${hash.slice(0, 8)}-${hash.slice(8, 12)}-5${hash.slice(13, 16)}-a${hash.slice(17, 20)}-${hash.slice(20, 32)}`;

  const manifest = [
    '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
    '<item id="css" href="style.css" media-type="text/css"/>',
    '<item id="cover-image" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
    '<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>',
    ...pages.map((p, i) => `<item id="ch${i}" href="${p.file}" media-type="application/xhtml+xml"/>`),
    ...[...images.keys()].map((name, i) => `<item id="img${i}" href="images/${esc(name)}" media-type="${MEDIA[extname(name).toLowerCase()]}"/>`),
  ].join('\n');
  writeFileSync(join(oebps, 'content.opf'), `<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id" xml:lang="ru">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="id">urn:uuid:${uuid}</dc:identifier>
<dc:title>${esc(title)}</dc:title>
<dc:language>ru</dc:language>
<dc:creator>dataengineer.ru</dc:creator>
<dc:publisher>dataengineer.ru</dc:publisher>
<dc:description>${esc(index.data.description ?? '')}</dc:description>
<dc:source>${SITE}${index.url}</dc:source>
<meta property="dcterms:modified">${modified.replace(/\.\d+Z$/, 'Z')}</meta>
</metadata>
<manifest>
${manifest}
</manifest>
<spine>
<itemref idref="cover"/>
<itemref idref="nav"/>
${pages.map((_, i) => `<itemref idref="ch${i}"/>`).join('\n')}
</spine>
</package>
`);

  // mimetype идёт первым и без сжатия. Так требует формат EPUB.
  mkdirSync(OUT, { recursive: true });
  const epub = join(OUT, `${book.slug}.epub`);
  rmSync(epub, { force: true });
  execFileSync('zip', ['-X0q', epub, 'mimetype'], { cwd: work });
  execFileSync('zip', ['-Xr9Dq', epub, 'META-INF', 'OEBPS'], { cwd: work });
  rmSync(work, { recursive: true, force: true });
  console.log(`${book.slug}.epub: ${pages.length} страниц, ${images.size} картинок`);
}

const only = process.argv[2];
const books = findBooks().filter((b) => !only || b.slug === only);
if (!books.length) {
  console.error(`Книга или курс не найдены: ${only}`);
  process.exit(1);
}
for (const book of books) await buildBook(book);
