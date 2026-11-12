---
name: diagrams
description: Make diagrams for dataengineer.ru pages - Excalidraw for flows, architecture, pipelines and decision trees; Mermaid only for ER diagrams (tables and relationships, star schemas). Use when a page needs a схема, diagram, ERD, star schema picture, or when fixing an existing diagram image.
---

# Diagrams

Pick the tool by what the diagram shows.

| Diagram shows | Tool | Example |
|---|---|---|
| Tables, columns, keys, relationships (ER, star schema) | Mermaid `erDiagram` | `public/assets/data-warehouse-toolkit/ch10-bank-star.png` |
| Flow, pipeline, architecture, lifecycle, comparison, decision tree | Excalidraw | `public/assets/data-warehouse-toolkit/ch01-kimball-architecture.png` |

Do not draw flows in Mermaid. Do not draw ER in Excalidraw.

Special case: the SQL course ERDs (`practice/sql/*/index.md`) are inline SVG made by `scripts/sql-tutorial-db/erd.py` from the database. Re-run that script; do not edit the SVG by hand.

## Where files go

| What | Path |
|---|---|
| Image | `public/assets/<section-or-book>/<name>.png` |
| Mermaid source | `scripts/<topic>-diagrams/src/<name>.mmd` |
| Excalidraw spec | `scripts/<topic>-diagrams/excalidraw_build.py` |
| Excalidraw scene | `~/dev/excalidraw/diagrams/dataengineer_ru/<prefix>-<name>.excalidraw` |

- Name: lowercase Latin with hyphens. For books, start with the chapter: `ch05-scd-types.png`.
- Image in the page: `![<alt по-русски>](/assets/<section>/<name>.png)`. The `alt` says what the picture shows.
- Limits: max 1600px wide, under 200 KB, PNG with palette.

## Mermaid (ER only)

Reference setup: `scripts/kimball-diagrams/` (`build.sh`, `mermaid.json`, `src/*.mmd`).

```
erDiagram
  FACT_SALES }o--|| DIM_DATE : "date_key"
  FACT_SALES {
    int date_key FK
    decimal sales_amount
  }
  DIM_DATE {
    int date_key PK
    date full_date
  }
```

- Table names in UPPER_CASE like `FACT_*`, `DIM_*`, `BRIDGE_*`. Mark `PK` and `FK`. Show only the columns the text talks about.
- Render: `npx -y @mermaid-js/mermaid-cli -c mermaid.json -b white -s 2 -i <name>.mmd -o <name>.png`, then compress with `sharp` (resize to 1600px, `png({palette:true})`). `build.sh` does both. Copy it for a new topic and change `OUT`.
- Theme: `{"theme":"neutral","themeVariables":{"fontSize":"16px"}}`.
- Wide diagrams are hard to read on a page. Prefer a vertical layout.

## Excalidraw (everything else)

Uses the local Excalidraw canvas server on `http://127.0.0.1:3456` (the `excalidraw` MCP server talks to the same canvas).

1. Create a new scene: `POST /api/scenes {"name": "dataengineer_ru/<prefix>-<name>"}`. Never draw on the current scene or on `Board`. If the scene exists (409), open it with `POST /api/scenes/open` and clear it only when you are rebuilding that same diagram.
2. Add elements: `POST /api/elements/batch {"elements": [...]}`.
3. Export: `POST /api/export/image {"format":"png","scale":2,"padding":30}`. Decode base64 and write to `public/assets/...`.
4. Save the scene: `POST /api/scenes/save`.
5. Compress with `sharp` like above.

For more than 2-3 diagrams, write a spec script so they can be rebuilt. Reference: `scripts/kimball-diagrams/excalidraw_build.py` (nodes `N(...)`, edges `E(...)`, zones `Z(...)`, notes `T(...)`). Copy it and change the output folder and scene prefix.

Style:

| Use | Fill | Stroke |
|---|---|---|
| Main step / process | `#a5d8ff` | `#1971c2` |
| Good / result | `#b2f2bb` | `#2f9e44` |
| Problem / risk | `#ffc9c9` | `#e03131` |
| Warning / note | `#ffec99` | `#f08c00` |
| Storage / database | `#99e9f2` | `#0c8599` |
| Neutral / source | `#e9ecef` | `#868e96` |
| ETL / transform | `#eebefa` | `#9c36b5` |

- `roughness: 1`, `strokeWidth: 2`, `fontFamily: 6`, font size 20. Boxes about 250x100.
- Group related boxes in a dashed zone with a title.
- Labels in Russian. Tech terms stay in English: `Extract`, `fact table`.
- Keep it simple: up to about 12 boxes. Split a big idea into two diagrams.

## Check

- Open the PNG and look at it. Text must not overflow boxes. Arrows must connect.
- File size under 200 KB.
- Tell the user the scene name and the image path.
