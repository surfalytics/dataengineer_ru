// Отправляет изменённые страницы в IndexNow (Яндекс) после деплоя.
// Запуск: node scripts/indexnow.mjs <before-sha> <after-sha>
// Проверка без запроса: INDEXNOW_DRY_RUN=1 node scripts/indexnow.mjs ...
// Берёт файлы из src/content/docs, которые изменились между двумя коммитами,
// превращает их в URL и шлёт одним POST-запросом. Ошибка не роняет деплой.
import { execFileSync } from 'node:child_process';
import { readdirSync } from 'node:fs';

const SITE = 'https://dataengineer.ru';
const HOST = 'dataengineer.ru';
const DOCS = 'src/content/docs/';
const ENDPOINT = 'https://yandex.com/indexnow';

const [before, after] = process.argv.slice(2);
if (!before || !after || /^0+$/.test(before)) {
  console.log('IndexNow: нет предыдущего коммита, пропускаем.');
  process.exit(0);
}

// Ключ лежит в public/<key>.txt, имя файла = ключ.
const keyFile = readdirSync('public').find((f) => /^[a-f0-9]{32}\.txt$/.test(f));
if (!keyFile) {
  console.log('::warning::IndexNow: файл ключа не найден в public/.');
  process.exit(0);
}
const key = keyFile.replace(/\.txt$/, '');

// src/content/docs/processing/sql.md -> /processing/sql/ ; .../index.mdx -> /.../
function toUrl(file) {
  if (!file.startsWith(DOCS) || !/\.mdx?$/.test(file)) return null;
  let p = file.slice(DOCS.length).replace(/\.mdx?$/, '');
  p = p.replace(/(^|\/)index$/, '');
  return `${SITE}/${p ? p.toLowerCase() + '/' : ''}`;
}

const diff = execFileSync('git', ['diff', '--name-status', '-M', before, after, '--', DOCS], { encoding: 'utf8' });
const urls = new Set();
for (const line of diff.trim().split('\n').filter(Boolean)) {
  // Строки: "M\tfile", "A\tfile", "D\tfile", "R100\told\tnew". Для удалённых и
  // переименованных тоже шлём старый URL: Яндекс быстрее уберёт его из поиска.
  for (const file of line.split('\t').slice(1)) {
    const url = toUrl(file);
    if (url) urls.add(url);
  }
}

if (urls.size === 0) {
  console.log('IndexNow: страницы не менялись.');
  process.exit(0);
}

const urlList = [...urls].slice(0, 10000);
console.log(`IndexNow: отправляем ${urlList.length} URL:\n${urlList.join('\n')}`);
if (process.env.INDEXNOW_DRY_RUN) process.exit(0); // локальная проверка без запроса
try {
  const res = await fetch(ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ host: HOST, key, keyLocation: `${SITE}/${keyFile}`, urlList }),
  });
  const text = await res.text();
  // 200 = принято, 202 = ключ ещё проверяется (это нормально в первый раз).
  if (res.status === 200 || res.status === 202) {
    console.log(`IndexNow: ответ ${res.status} ${text}`);
  } else {
    console.log(`::warning::IndexNow: ответ ${res.status} ${text}`);
  }
} catch (err) {
  console.log(`::warning::IndexNow: запрос не прошёл: ${err}`);
}
