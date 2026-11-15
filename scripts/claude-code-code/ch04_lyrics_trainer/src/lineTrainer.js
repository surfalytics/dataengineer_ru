// Ядро: правила навигации по строкам. Не знает ни про DOM, ни про localStorage.

// Любое плохое значение (не число, меньше 0, за концом текста) превращаем в 0.
export function normalizeIndex(value, length) {
  const index = Number(value);
  if (!Number.isInteger(index) || index < 0 || index >= length) {
    return 0;
  }
  return index;
}

export function createLineTrainer(lines, startIndex = 0) {
  let index = normalizeIndex(startIndex, lines.length);
  return {
    currentLine: () => lines[index],
    currentIndex: () => index,
    // После последней строки возвращаемся к первой.
    next() {
      index = (index + 1) % lines.length;
      return lines[index];
    },
  };
}
