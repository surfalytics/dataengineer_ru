// Добавляет дату публикации страницы в <head> для сниппетов Яндекса.
// Дата = первый коммит файла страницы в git (с учётом переименований).
// Формат по документации Яндекса: <meta name="article:published_time" content="ISO 8601">.
import { execFileSync } from 'node:child_process';
import { defineRouteMiddleware } from '@astrojs/starlight/route-data';

const cache = new Map<string, string | undefined>();

function firstCommitDate(file: string): string | undefined {
  if (cache.has(file)) return cache.get(file);
  let date: string | undefined;
  try {
    const out = execFileSync('git', ['log', '--follow', '--diff-filter=A', '--format=%cI', '--', file], {
      encoding: 'utf8',
    });
    // git log идёт от новых к старым: самая первая дата — последняя строка.
    date = out.trim().split('\n').filter(Boolean).pop();
  } catch {
    date = undefined;
  }
  cache.set(file, date);
  return date;
}

export const onRequest = defineRouteMiddleware((context) => {
  const route = context.locals.starlightRoute;
  const date = firstCommitDate(route.entry.filePath);
  if (date) {
    route.head.push({ tag: 'meta', attrs: { name: 'article:published_time', content: date } });
  }
});
