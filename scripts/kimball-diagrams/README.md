# Diagrams for the Data Warehouse Toolkit summary

- **ER diagrams (tables and relationships):** Mermaid. Sources in `src/*.mmd`.
  Build: `scripts/kimball-diagrams/build.sh [name ...]`
- **All other diagrams (flows, architecture, decision trees):** Excalidraw.
  Specs are in `excalidraw_build.py`. Needs the local canvas server on `:3456`.
  Build: `python3 scripts/kimball-diagrams/excalidraw_build.py [name ...]`
  Scenes are saved as `dataengineer_ru/dwt-<name>` in `~/dev/excalidraw/diagrams`.
- Output of both: `public/assets/data-warehouse-toolkit/<name>.png`.
- SQL check: `python3 scripts/kimball-diagrams/check_sql.py <chapter.md>`.
