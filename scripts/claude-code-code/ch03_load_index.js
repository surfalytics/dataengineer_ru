// Глава 3: сохранение строки в localStorage и безопасный откат на строку 0.
// В Node нет localStorage, поэтому здесь простая замена на Map.
// Запуск: node scripts/claude-code-code/ch03_load_index.js
const store = new Map();
const localStorage = {
  getItem: (k) => (store.has(k) ? store.get(k) : null),
  setItem: (k, v) => store.set(k, String(v)),
  removeItem: (k) => store.delete(k),
};

const lines = Array.from({ length: 14 }, (_, i) => `строка ${i + 1}`);
const STORAGE_KEY = "lyricsTrainer.lineIndex";

function loadIndex() {
  const stored = Number(localStorage.getItem(STORAGE_KEY));
  if (!Number.isInteger(stored) || stored < 0 || stored >= lines.length) {
    return 0;
  }
  return stored;
}

// Что вернёт loadIndex() для разных сохранённых значений
for (const value of [null, "5", "13", "14", "99", "-1", "2.5", "abc"]) {
  if (value === null) localStorage.removeItem(STORAGE_KEY);
  else localStorage.setItem(STORAGE_KEY, value);
  console.log(`${JSON.stringify(value).padEnd(6)} -> ${loadIndex()}`);
}
