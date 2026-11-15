// Сохранение позиции. Хранилище передаём параметром:
// в браузере это localStorage, в тестах — простой объект-заглушка.
import { normalizeIndex } from "./lineTrainer.js";

export const DEFAULT_KEY = "lyricsTrainer.lineIndex";

export function loadSavedIndex(storage, lineCount, key = DEFAULT_KEY) {
  return normalizeIndex(storage.getItem(key), lineCount);
}

export function saveIndex(storage, index, key = DEFAULT_KEY) {
  storage.setItem(key, String(index));
}
