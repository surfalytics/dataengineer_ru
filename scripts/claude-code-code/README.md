# Код к конспекту Claude Code: Up and Running

Скрипты лежат в этой папке. Платных API нет: где книга вызывает Anthropic API, у нас модель-заглушка.
Запуск из корня репозитория: Python — `python3 -I scripts/claude-code-code/<файл>.py`; JavaScript — Node 24; lyrics-trainer главы 4 — `cd scripts/claude-code-code/ch04_lyrics_trainer && npm install && npm test`.
Prompt-ы и команды внутри сессии Claude Code не запускаются без подписки, поэтому на страницах они даны как текст.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | Включить agent teams: `export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` и запуск `claude` | на странице | ok: `export` проверен в bash; запуск `claude` нужен установленный Claude Code и подписка |
| 1 | Запрос к agent teams (наш вариант для dbt-проекта, в книге — для Spring Boot) | на странице, блок `text` | не запускается: это текст запроса к Claude Code, нужна подписка; вывод в книге пересказан словами, не скопирован |
| 2 | Команды установки (curl, irm, CMD) | на странице, без изменений | ok: однострочные команды из книги; не запускались, они меняют систему |
| 2 | `claude --version` | на странице, реальный вывод `2.1.325 (Claude Code)` | ok |
| 2 | `claude doctor`, `/statusline`, `/logout`, `/login`, `! open index.html` | на странице, текст | ok: команды внутри интерактивной сессии, вывода на странице нет |
| 2 | `statusLine` в `~/.claude/settings.json` | на странице | ok: фрагмент JSON из книги |
| 2 | Скрипт statusline (в книге только настройка) | `ch02_statusline.sh` + тест `ch02_statusline_test.sh` (нужны bash, git, jq) | ok |
| 2 | Lyrics-trainer: один `index.html` | `ch02_lyrics_trainer/index.html` + проверка `node ch02_check_trainer.mjs` | ok, вывод одинаковый при повторах |
| 2 | Prompt для первой версии | на странице, наш текст по-русски | ok: это текст, не код |
| 3 | Prompt-ы: размытый и точный, уточняющие вопросы, `@`-ссылки, `/compact` с инструкцией, prompt про сохранение строки, обзор всего приложения | на странице, текст | ok: это текст, не код |
| 3 | `claude -p`, `git diff \| claude -p`, `claude -c -p`, `claude -c/-r/-n`, `--resume <id>` | на странице | ok: флаги `-p`, `-c`, `-r`, `-n` проверены по `claude --help`; запросы к модели не запускали |
| 3 | Python с Anthropic API: два запроса, модель не помнит имя | `ch03_stateless.py` (наша версия: модель-заглушка, без API; same x6) | ok |
| 3 | Тот же пример с настоящим Anthropic API | на странице, отдельный блок | не запускается: нужен платный `API key` |
| 3 | Свой `output style` «skeptical-senior-engineer» | `ch03_skeptical-data-engineer.md` (наша версия для дата-инженера; YAML frontmatter проверен) | ok |
| 3 | `loadIndex()` + `localStorage.setItem` в lyrics-trainer | `ch03_load_index.js` (Node 24, `localStorage` заменён на `Map`) | ok |
| 3 | `localStorage.getItem/setItem` в консоли браузера | на странице | ok: поведение проверено в `ch03_load_index.js` ("99" и "abc" дают 0) |
| 4 | `lineTrainer.js`: `normalizeIndex`, `createLineTrainer` | `ch04_lyrics_trainer/src/lineTrainer.js` (наша версия, комментарии по-русски) | ok |
| 4 | `storage.js`: хранилище передаётся параметром | `ch04_lyrics_trainer/src/storage.js` | ok |
| 4 | `main.js`: тонкий слой для DOM | `ch04_lyrics_trainer/src/main.js` | ok: `node --check`; нужен браузер, запуск `npm start` |
| 4 | Тесты Vitest для ядра и хранилища (заглушка вместо `localStorage`) | `ch04_lyrics_trainer/test/*.test.js` | ok: `npm install && npm test`, vitest 3.2.4, 9 тестов, проверено 3 раза |
| 4 | Prompt-ы: тесты, уточнение структуры, починка тестов, `/compact` с целью, контрольная сводка | на странице, текст | ok: это текст, не код |
| 4 | `CLAUDE.md` для lyrics-trainer, `CLAUDE.md` с `@AGENTS.md`, папка `auto memory`, `/add-dir` | на странице | ok: это текст и команды Claude Code, не запускали |
