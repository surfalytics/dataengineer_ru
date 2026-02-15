# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Russian-language educational portal about data engineering (**dataengineer.ru**). A curated collection of learning resources for data engineers, BI developers, and data analysts. Built with Jekyll and hosted on GitHub Pages.

## Development Commands

```bash
bundle install              # Install Ruby dependencies
bundle exec jekyll serve    # Local dev server (http://localhost:4000)
bundle exec jekyll build    # Build static site to _site/
```

Requires Ruby and Bundler. No test suite exists — verify changes by running `jekyll serve` locally and checking the site in a browser.

## Architecture

- **Static site generator**: Jekyll 4.3.4 with the `sighingnow/jekyll-gitbook` remote theme
- **Markdown engine**: kramdown with GFM input, MathJax for math, Rouge for syntax highlighting
- **Deployment**: Push to `main` triggers automatic GitHub Pages build. Custom domain via `CNAME` file.

## Content Structure

Three Jekyll collections, rendered in this order on the site:

1. **`_posts/`** — Technical topic pages (SQL, ETL, Spark, Data Warehouse, etc.). Each post uses `category: hard-skills` and `layout: post`.
2. **`_pages/`** — Standalone sections (career/job search, books, career tracks, communities, management, whitepapers). Uses `layout: post`.
3. **`_others/`** — About, contact, services pages.

### Front Matter Format

```yaml
---
title: Page Title
author: Дата Инженеръ          # or specific author name
date: 2024-11-03
category: hard-skills           # or Jekyll for _pages
layout: post
cover: ../assets/surf2.svg      # relative path varies by collection depth
---
```

Content is primarily curated resource lists with links, using emoji flags (🇷🇺/🇬🇧) for language and ⭐ for recommendations.

## Key Configuration

- **`_config.yml`**: Jekyll settings, theme, plugins (jekyll-feed, jekyll-readme-index, jemoji), collection definitions, permalink patterns
- **`CNAME`**: Custom domain `dataengineer.ru`
- **`_layouts/`**: Custom overrides for home, post, and search layouts
- **`_includes/`**: Template partials (head, footer, analytics, MathJax, Mermaid diagrams, search, Disqus)
- **`assets/`**: Images (PNG/SVG), GitBook theme assets, search index

## Content Language

All content is in Russian. Author name in posts is typically "Дата Инженеръ". When adding or editing content, maintain Russian language throughout.

## Contributing

Resources are added via Pull Requests. The PR template (`.github/pull_request_template.md`) asks for changed sections and whether local testing is needed before merge.
