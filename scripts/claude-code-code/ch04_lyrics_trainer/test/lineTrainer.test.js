import { describe, expect, it } from "vitest";
import { createLineTrainer, normalizeIndex } from "../src/lineTrainer.js";
import { lines } from "../src/texts.js";

describe("createLineTrainer", () => {
  it("по умолчанию начинает с первой строки", () => {
    const trainer = createLineTrainer(lines);
    expect(trainer.currentLine()).toBe(lines[0]);
    expect(trainer.currentIndex()).toBe(0);
  });

  it("переходит к следующей строке", () => {
    const trainer = createLineTrainer(lines);
    expect(trainer.next()).toBe(lines[1]);
    expect(trainer.currentIndex()).toBe(1);
  });

  it("после последней строки возвращается к первой", () => {
    const trainer = createLineTrainer(lines, lines.length - 1);
    expect(trainer.next()).toBe(lines[0]);
    expect(trainer.currentIndex()).toBe(0);
  });
});

describe("normalizeIndex", () => {
  it("возвращает 0 для плохих значений", () => {
    expect(normalizeIndex("не число", lines.length)).toBe(0);
    expect(normalizeIndex(null, lines.length)).toBe(0);
    expect(normalizeIndex(-1, lines.length)).toBe(0);
    expect(normalizeIndex(99, lines.length)).toBe(0);
    expect(normalizeIndex(2.5, lines.length)).toBe(0);
  });

  it("оставляет правильный индекс, даже если это строка", () => {
    expect(normalizeIndex("2", lines.length)).toBe(2);
  });
});
