import { describe, expect, it } from "vitest";
import { DEFAULT_KEY, loadSavedIndex, saveIndex } from "../src/storage.js";

// Заглушка вместо localStorage: тот же интерфейс getItem/setItem, но в памяти.
function fakeStorage(initial = {}) {
  const data = { ...initial };
  return {
    getItem: (key) => (key in data ? data[key] : null),
    setItem: (key, value) => { data[key] = value; },
  };
}

describe("storage", () => {
  it("продолжает с сохранённой строки", () => {
    const storage = fakeStorage({ [DEFAULT_KEY]: "3" });
    expect(loadSavedIndex(storage, 4)).toBe(3);
  });

  it("без сохранения начинает с 0", () => {
    expect(loadSavedIndex(fakeStorage(), 4)).toBe(0);
  });

  it("испорченное значение даёт 0", () => {
    const storage = fakeStorage({ [DEFAULT_KEY]: "сорок" });
    expect(loadSavedIndex(storage, 4)).toBe(0);
  });

  it("saveIndex пишет индекс строкой", () => {
    const storage = fakeStorage();
    saveIndex(storage, 2);
    expect(storage.getItem(DEFAULT_KEY)).toBe("2");
  });
});
