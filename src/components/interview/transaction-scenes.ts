type Tone = 'quiet' | 'active' | 'wait' | 'done';
type Cell = { text: string; detail: string; tone: Tone };
export type TxFrame = {
  a: Cell; b: Cell; resources: [Cell, Cell]; path: [string,string,string];
  title: string; note: string; waiting: boolean;
};
type Variant = {
  label: string; actors: [string,string]; resourceLabel: string; frames: TxFrame[];
};
const cell = (text: string, detail: string, tone: Tone = 'quiet'): Cell => ({text,detail,tone});
function moment(a: Cell, b: Cell, resources: [Cell,Cell], path: [string,string,string], title: string, note: string, waiting=false): TxFrame {
  return {a,b,resources,path,title,note,waiting};
}
function snapshot(repeatable: boolean): Variant {
  const level = repeatable ? 'Repeatable Read' : 'Read Committed';
  const read = cell('SELECT по двум таблицам','Остаток и бронь в одном запросе.','active');
  const writing = cell('UPDATE + INSERT','Списал 4 и создал бронь. До COMMIT.','active');
  const committed = cell('COMMIT','Списание и бронь зафиксированы вместе.','done');
  const before: [Cell,Cell] = [
    cell('stock · остаток','5 единиц на складе.','done'),
    cell('reservations · бронь','0 единиц в брони.','done'),
  ];
  const after: [Cell,Cell] = [
    cell('stock · остаток','1 единица на складе.','done'),
    cell('reservations · бронь','4 единицы в брони.','done'),
  ];
  return {label:level, actors:['Читает','Бронирует'], resourceLabel:'Что вернул последний SELECT сеанса A', frames:[
    moment(read,writing,before,['Первый SELECT','Снимок S1','Обе таблицы'],
      'Первое чтение: 5 на складе, 0 в брони','Чужая транзакция ещё открыта. Её списание и её бронь скрыты от читателя.'),
    moment(cell('Между запросами','Нового SELECT ещё не было.'),committed,before,
      ['Сеанс B','COMMIT','Обе записи'],'Бронь подтверждена','Уже полученный ответ читателя остаётся прежним. Теперь A повторит тот же запрос.'),
    moment(read,committed,repeatable ? before : after,['Второй SELECT',repeatable ? 'Тот же S1' : 'Новый S2','Обе таблицы'],
      repeatable ? 'Повторное чтение: снова 5 и 0' : 'Повторное чтение: теперь 1 и 4',
      repeatable ? 'В той же транзакции A продолжает читать обе таблицы через первый снимок. В S1 бронирование ещё не завершилось.' : 'Новая команда получила снимок после COMMIT. В нём видны и списание четырёх единиц, и бронь на четыре.'),
    moment(cell('COMMIT; SELECT','Читает в следующей транзакции.','active'),committed,after,
      ['Следующая транзакция','Новый снимок','Обе таблицы'],'Следующая транзакция: 1 и 4','Для обоих уровней новое чтение после завершения транзакции A видит подтверждённую бронь.'),
  ]};
}

const item = (name: string, state: string, tone: Tone='quiet') => cell(name,state,tone);
const rowLock: Variant = { label:'Строка', actors:['Списывает 4','Списывает 3'], resourceLabel:'Строки таблицы stock', frames:[
  moment(cell('—','Ещё не начал.'),cell('BEGIN','Открыл транзакцию раньше A.','active'),
    [item('Товар A · 5','Свободна'),item('Товар B · 8','Свободна')],['Сеанс B','BEGIN','Без блокировки строки'],'Порядок начала','Сам по себе BEGIN не резервирует товар. Запрос B на изменение ещё не поступил.'),
  moment(cell('UPDATE → qty − 4','Первым обновил товар A.','active'),cell('BEGIN','Транзакция открыта.'),
    [item('Товар A · 5 → 1','Удерживает сеанс A.','active'),item('Товар B · 8','Свободна')],['Сеанс A','Блокировка строки','Товар A'],'Первая запись','Внутри A новый остаток равен 1. Обычный SELECT другого сеанса пока видит 5.'),
  moment(cell('До COMMIT','Удерживает блокировку.','active'),cell('UPDATE → qty − 3','Ждёт завершения A.','wait'),
    [item('Товар A · 5 → 1','A удерживает, B ждёт.','wait'),item('Товар B · 8','Свободна')],['Сеанс B','Ожидание','Товар A занят'],'Конфликт на одной строке','В снимке команды B остаток равен 5 и подходит для списания трёх. При попытке изменить строку B встречает незавершённую запись A.',true),
  moment(cell('COMMIT','Остаток 1 зафиксирован.','done'),cell('Проверка WHERE','Проверяет новую версию.','active'),
    [item('Товар A · 1','Блокировка A снята.','done'),item('Товар B · 8','Свободна')],['Сеанс B','1 ≥ 3?','Условие ложно'],'Повторная проверка','В Read Committed после ожидания PostgreSQL заново проверяет условие на версии, которую зафиксировал A.'),
  moment(cell('Завершён','Списаны четыре единицы.','done'),cell('UPDATE 0; COMMIT','Ни одна строка не обновлена.','done'),
    [item('Товар A · 1','Итоговый остаток','done'),item('Товар B · 8','Остаток прежний')],['Сеанс B','0 строк','Остаток 1'],'Результат','RETURNING во втором сеансе не вернул строку. Приложение может сообщить, что товара недостаточно.'),
]};

const tableLock: Variant = { label:'Таблица', actors:['Пересчёт долей','Пополняет товар B'], resourceLabel:'Область действия блокировки', frames:[
  moment(cell('BEGIN','Начинает пересчёт.','active'),cell('—','Пополнение ещё не началось.'),
    [item('Таблица stock','Запись разрешена.'),item('Товар B · 8','Исходный остаток.')],['Сеанс A','BEGIN','Таблица свободна'],'До расчёта','Доли товаров зависят от общего остатка. На время расчёта состав и количества должны оставаться стабильными.'),
  moment(cell('LOCK TABLE stock','SHARE ROW EXCLUSIVE','active'),cell('—','Обычное чтение разрешено.'),
    [item('Таблица stock','Режим удерживает A.','active'),item('Товар B · 8','Виден читателям.')],['Сеанс A','Блокировка','Вся stock'],'До первого чтения','A получил табличную блокировку. Теперь другие транзакции не могут изменять строки stock до её освобождения.'),
  moment(cell('UPDATE → share','Считает доли по общему остатку.','active'),cell('UPDATE → qty + 1','Запись в stock ожидает.','wait'),
    [item('Таблица stock','A удерживает, B ждёт.','wait'),item('Товар B · 8','Обычный SELECT вернёт 8.')],['Сеанс B','Ожидание','Таблица занята'],'Область конфликта шире','Для UPDATE нужен табличный режим ROW EXCLUSIVE. Он несовместим с режимом A. Обычный SELECT третьего сеанса проходит.',true),
  moment(cell('COMMIT','Освободил таблицу.','done'),cell('UPDATE → qty + 1','Теперь может писать.','active'),
    [item('Таблица stock','Блокировка A снята.','done'),item('Товар B · 8 → 9','Изменение B до COMMIT.','active')],['Сеанс B','Запись разрешена','Товар B → 9'],'Продолжение записи','Пополнение выполняется после пересчёта. В своей транзакции B получает новый остаток 9.'),
  moment(cell('Завершён','Пересчёт зафиксирован.','done'),cell('COMMIT','Пополнение зафиксировано.','done'),
    [item('Таблица stock','Свободна'),item('Товар B · 9','Виден новым снимкам.','done')],['Сеанс B','COMMIT','Остаток 9'],'После освобождения','Гарантия стабильности действовала до COMMIT сеанса A. Позднейшие записи снова меняют остатки.'),
]};
export const transactionScenes = { mvcc:[snapshot(false),snapshot(true)], locks:[rowLock,tableLock] };
