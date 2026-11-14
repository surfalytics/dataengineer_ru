---
name: book-epub
description: Build and check the EPUB download of a book summary (конспект книги) on dataengineer.ru - run scripts/epub/build.mjs, validate the file, and add the "Скачать конспект в EPUB" link to the book overview page. Use as the last step of the book-summary skill, when a book or chapter is added or changed, or when the user asks for EPUB, a downloadable book, an e-reader file, or a fix to the EPUB script, cover or credits.
---

# Book EPUB

Each book summary has an EPUB file. People download it and read it on a phone or an e-reader.

The `book-summary` skill calls this skill as its last step. You can also run it alone to fix the EPUB of an existing book.

## How it works

| What | Where |
|---|---|
| Build script | `scripts/epub/build.mjs` |
| Input | `src/content/docs/book-summaries/<group>/<book-slug>/*.md` |
| Output | `public/downloads/<book-slug>.epub` (not in git) |
| URL on the site | `/downloads/<book-slug>.epub` |
| Link for readers | on the book overview page (`index.md`) |

- `npm run build` runs the script first, then builds the site. So the deploy always has fresh files.
- `npm run epub` builds only the EPUB files.
- The script finds books by itself: every folder with an `index.md`. A new book needs no change in the script.
- Chapter order is `sidebar.order`. The table of contents uses `sidebar.label`.

## Steps

1. **Add the link** to the overview page, right after the "пересказ, а не перевод" note:

   ```markdown
   📥 [Скачать конспект в EPUB](/downloads/<book-slug>.epub) — для телефона и электронной книги.
   ```

   `<book-slug>` is the folder name of the book. The script removes this line from the EPUB itself.

2. **Build** one book:

   ```bash
   node scripts/epub/build.mjs <book-slug>
   ```

   The script prints the number of pages and images. Compare them with the book: pages = chapters + 1.

3. **Fix every warning.** `! нет картинки: <path>` means the image file is missing in `public/`. The script drops that image. Fix the path on the page, then build again.

4. **Validate** the file:

   ```bash
   epubcheck public/downloads/<book-slug>.epub
   ```

   The result must be `0 fatals / 0 errors / 0 warnings`. If `epubcheck` is not installed (`brew install epubcheck`), do the smaller check and say so in your report:

   ```bash
   d=$(mktemp -d) && unzip -q public/downloads/<book-slug>.epub -d "$d" && xmllint --noout "$d"/OEBPS/*.xhtml "$d"/OEBPS/content.opf
   ```

   No output means every page is valid XML.

5. **Look at the result.** Unzip the file and read `OEBPS/cover.jpg` (the title must fit) and one chapter (`OEBPS/ch01.xhtml`).

6. **Run `npm run build`** and check that `dist/downloads/<book-slug>.epub` exists.

## What the script does to a page

| On the site | In the EPUB |
|---|---|
| `title` from front matter | The `<h1>` of the chapter |
| `![alt](/assets/...)` | The image is copied into the file |
| Link to a chapter of the same book | Link inside the file |
| Any other `/...` link | Link to `https://dataengineer.ru/...` |
| `<details>` with a solution | Always open. Many readers cannot collapse blocks |
| Code block | Plain monospace, no colours |
| Publisher cover | Not used. The script draws its own cover |

## Credits

Every chapter starts and ends with one line: `Источник: dataengineer.ru · Telegram: t.me/rockyourdata`. The cover shows both too. The text is in `CREDITS` and `TELEGRAM` at the top of the script. Change it there, not on the pages.

EPUB has no fixed pages. The reader app draws the page numbers. So we cannot put text next to a page number.

## Rules for pages, so the EPUB stays valid

- Use `.md`, not `.mdx`. The script reads only `.md` and does not know Starlight components.
- Images: root-absolute paths (`/assets/<book-slug>/...`), PNG or JPEG.
- Raw HTML: only `<details>` and `<summary>`. Other tags can break the XHTML.
- Do not use the publisher cover in the EPUB. A file with the original cover looks like the original book.

## Checklist

- [ ] The overview page has the EPUB link with the right `<book-slug>`.
- [ ] `node scripts/epub/build.mjs <book-slug>` prints no `!` warnings.
- [ ] Pages in the EPUB = chapters + 1.
- [ ] `epubcheck` shows 0 errors and 0 warnings (or the `xmllint` check passes and you said `epubcheck` was not run).
- [ ] You looked at the cover and one chapter.
- [ ] `npm run build` passes and `dist/downloads/<book-slug>.epub` exists.
