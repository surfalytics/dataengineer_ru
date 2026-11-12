# Схемы курса «Базовый минимум Dimensional Modeling»

Картинки: `public/assets/practice/modeling/*.png`. Запуск из корня репозитория.

| Что | Как собрать |
|---|---|
| ER-схемы (`src/*.mmd`): источник, star schema, Data Vault | `scripts/modeling-diagrams/build.sh [name ...]` (Mermaid CLI через `npx`) |
| Остальные схемы (потоки, сравнения) | `python3 scripts/modeling-diagrams/excalidraw_build.py [name ...]` |

`excalidraw_build.py` нужен локальный Excalidraw-сервер на `http://127.0.0.1:3456`.
Сцены сохраняются как `dataengineer_ru/dm-<name>` в `~/dev/excalidraw/diagrams`.
