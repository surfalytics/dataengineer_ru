# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Russian-language educational portal about data engineering (**dataengineer.ru**). A curated collection of learning resources for data engineers, BI developers, and data analysts. Built with Astro + Starlight and hosted on GitHub Pages.

## Development Commands

```bash
npm install        # Install dependencies (Node 20+)
npm run dev        # Local dev server (http://localhost:4321)
npm run build      # Build static site to dist/
npm run preview    # Preview the built site
```

No test suite exists — verify changes by running `npm run dev` locally and checking the site in a browser, and `npm run build` to catch schema/build errors.

## Architecture

- **Framework**: [Astro](https://astro.build/) 6 with the [Starlight](https://starlight.astro.build/) docs theme
- **Search**: [Pagefind](https://pagefind.app/) (built-in to Starlight), runs at build time with Russian-language stemming (activated by the `ru` locale)
- **Deployment**: Push to `main` triggers `.github/workflows/deploy.yml` (GitHub Actions → GitHub Pages). Custom domain via `public/CNAME`.

## Content Structure

All content is Markdown in `src/content/docs/`, grouped into one folder per sidebar section:

| Folder | Sidebar section |
|---|---|
| `processing/` | Обработка и аналитика |
| `tools/` | Инструменты |
| `ai/` | AI |
| `career/` | Карьера |
| `resources/` | Книги и Материалы |
| `community/` | Сообщество и Управление |
| `about/` | О проекте |

`src/content/docs/index.mdx` is the home page (Starlight `splash` template).

### Front Matter Format

```yaml
---
title: Название страницы
description: Краткое описание для поиска и SEO.
sidebar:
  order: 10          # position within the section (lower = higher)
  label: API         # optional, overrides title in the sidebar
tags:
  - sql              # custom field (see src/content.config.ts)
---
```

The content schema is extended in `src/content.config.ts` with optional `tags`, `track`, `author`, `pubDate` fields. Content is primarily curated resource lists with links, using emoji flags (🇷🇺/🇬🇧) for language and ⭐ for recommendations.

## Key Configuration

- **`astro.config.mjs`**: site URL, `ru` locale, sidebar (section order + `autogenerate` per folder), GA4, and `redirects` (legacy Jekyll URLs → new paths). When adding/renaming a page that has an old Jekyll URL, add a redirect entry here.
- **`src/content.config.ts`**: Starlight docs collection + schema extension.
- **`public/`**: static files served as-is. Images go in `public/assets/` and are referenced as `/assets/<file>`. Contains `CNAME` (custom domain) and `favicon.png`.
- **`src/assets/`**: imported/optimized images (the logo `surf2.svg`).
- **`src/styles/custom.css`**: brand CSS overrides.

### Image paths
Reference body images with root-absolute paths: `![alt](/assets/file.png)` (files live in `public/assets/`). Do **not** use relative `../assets/` paths.

## Navigation & Ordering

- Section order: the `sidebar` array in `astro.config.mjs`.
- Page order within a section: `sidebar.order` in front matter.
- Prev/Next pagination is automatic from sidebar order.

## Content Language

All content is in Russian. Maintain Russian language throughout when adding or editing content. The Starlight UI is localized via the `ru` locale.

## Contributing

Resources are added via Pull Requests. The PR template (`.github/pull_request_template.md`) asks for changed sections and whether local testing is needed before merge.
