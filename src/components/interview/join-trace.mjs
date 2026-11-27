export const leftRows = [
  { id: 'a1', key: 2, value: 'Анна' },
  { id: 'a2', key: 1, value: 'Олег' },
  { id: 'a3', key: 2, value: 'Ира' },
];

export const rightRows = [
  { id: 'b1', key: 2, value: 'SQL' },
  { id: 'b2', key: 3, value: 'Git' },
  { id: 'b3', key: 2, value: 'Python' },
];

function hashJoin(record) {
  const partitions = { A0: [], B0: [], A1: [], B1: [] };
  const snapshot = () => Object.fromEntries(
    Object.entries(partitions).map(([name, rows]) => [name, rows.map(row => row.id)])
  );
  const distribute = (side, row) => {
    const number = row.key % 2;
    const target = side + number;
    partitions[target].push(row);
    record('Разбиение входов', `Строка (${row.key}, ${row.value}) переходит в ${target}, поскольку ${row.key} % 2 = ${number}.`, {
      hash: { partitions: snapshot(), move: { side, target, row } },
    });
  };
  for (const row of leftRows) distribute('A', row);
  for (const row of rightRows) distribute('B', row);
  const stored = snapshot();
  for (const n of [0, 1]) {
    const index = new Map();
    const state = (focus) => ({
      partitions: stored, group: n, focus,
      index: Array.from(index, ([key, rows]) => `${key} → ${rows.map(row => row.value).join(', ')}`).join(' · '),
    });
    for (const right of partitions['B' + n]) {
      if (!index.has(right.key)) index.set(right.key, []);
      index.get(right.key).push(right);
      record(`Хеш-таблица B${n}`, `Сохраняем занятие «${right.value}» под ключом ${right.key}.`, {
        hash: state([right.id]),
      });
    }
    for (const left of partitions['A' + n]) {
      const matches = index.get(left.key) ?? [];
      if (matches.length === 0) {
        record(`Поиск в B${n}`, `Ищем занятия для строки (${left.key}, ${left.value}). Ключа ${left.key} в B${n} нет.`, {
          hash: state([left.id]),
        });
      }
      for (const right of matches) {
        record(`Соединение A${n} и B${n}`, `Группа ${left.key} совпала. В результат попадают участник «${left.value}» и занятие «${right.value}».`, {
          pair: [left, right], hash: state([left.id, right.id]),
        });
      }
    }
  }
}

function mergeJoin(record) {
  const ascending = (a, b) => a.key - b.key;
  const a = [...leftRows].sort(ascending);
  const b = [...rightRows].sort(ascending);
  const order = { a, b };
  record('Сортировка', 'Упорядочиваем оба входа по ключу. Идентификаторы строк сохраняются.', order);
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    const left = a[i];
    const right = b[j];
    const focus = { ...order, left: [left], right: [right] };
    if (left.key !== right.key) {
      const leftIsSmaller = left.key < right.key;
      const side = leftIsSmaller ? 'A' : 'B';
      record('Сдвиг указателя', `Ключ в ${side} меньше. Совпадения дальше по другому входу уже не будет. Сдвигаем указатель ${side}.`, focus);
      if (leftIsSmaller) i++;
      else j++;
      continue;
    }
    const startA = i;
    const startB = j;
    while (i < a.length && a[i].key === left.key) i++;
    while (j < b.length && b[j].key === right.key) j++;
    const groupA = a.slice(startA, i);
    const groupB = b.slice(startB, j);
    record('Совпавшие группы', `С обеих сторон ключ ${left.key}. Здесь ${groupA.length} × ${groupB.length} = ${groupA.length * groupB.length} пары.`, {
      ...order, left: groupA, right: groupB,
    });
    for (const rowA of groupA) {
      for (const rowB of groupB) {
        record('Выдача пары', `Соединяем ${rowA.id} и ${rowB.id}. Для каждой строки A перебираем всю совпавшую группу B.`, {
          ...order, left: [rowA], right: [rowB], pair: [rowA, rowB],
        });
      }
    }
  }
  record('Конец входа', 'Вход A закончился. Оставшаяся строка b2 с ключом 3 не имеет пары.', order);
}

function nestedLoop(record) {
  for (const left of leftRows) {
    record('Внешний цикл', `Фиксируем строку ${left.id} из A. Просмотр B начинаем с первой строки.`, { left: [left] });
    for (const right of rightRows) {
      const equal = left.key === right.key;
      record('Внутренний цикл', equal
        ? `Ключи совпали. Добавляем пару (${left.id}, ${right.id}).`
        : `Ключи ${left.key} и ${right.key} различаются. Пропускаем эту пару.`, {
        left: [left], right: [right], pair: equal ? [left, right] : undefined,
      });
    }
  }
}

const algorithms = { 'hash-join': hashJoin, 'merge-join': mergeJoin, 'nested-loop': nestedLoop };

export function buildTrace(algorithm) {
  const steps = [];
  const result = [];
  function record(phase, note, state = {}) {
    if (state.pair) {
      const [left, right] = state.pair;
      result.push(algorithm === 'hash-join'
        ? `${left.key}, ${left.value}, ${right.value}`
        : `${left.id}, ${right.id}`);
    }
    steps.push({
      phase, note, a: state.a ?? leftRows, b: state.b ?? rightRows,
      left: state.left ?? [], right: state.right ?? [],
      hash: state.hash,
      result: [...result], added: Boolean(state.pair),
    });
  }
  record('Исходные данные', algorithm === 'hash-join'
    ? 'Соединяем участников с занятиями по номеру группы.'
    : 'Соединяем A и B по равенству ключей. Идентификаторы позволяют различить строки с одинаковым ключом.');
  algorithms[algorithm](record);
  const last = steps[steps.length - 1];
  record('Готово', `Получили ${result.length} пары. Две строки с ключом 2 в A совпали с двумя строками в B.`, {
    a: last.a, b: last.b, hash: last.hash && { partitions: last.hash.partitions },
  });
  return steps;
}
