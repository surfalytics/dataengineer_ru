// Главные разделы портала. Используются в двух местах:
// 1) плагин starlight-sidebar-topics (свой сайдбар у каждого раздела);
// 2) вкладки в шапке сайта (src/components/Header.astro).
// `match` — префиксы URL, по которым вкладка считается активной.

export const topics = [
  {
    label: 'Старт',
    link: '/start/',
    icon: 'rocket',
    match: ['/start/', '/about/'],
    items: [
      { label: 'С чего начать', items: [{ autogenerate: { directory: 'start' } }] },
      { label: 'О проекте', items: [{ autogenerate: { directory: 'about' } }] },
    ],
  },
  {
    label: 'База знаний',
    link: '/processing/sql/',
    icon: 'open-book',
    match: ['/processing/', '/tools/'],
    items: [
      { label: 'Обработка и аналитика', items: [{ autogenerate: { directory: 'processing' } }] },
      { label: 'Инструменты', items: [{ autogenerate: { directory: 'tools' } }] },
    ],
  },
  {
    label: 'Практика',
    link: '/practice/',
    icon: 'laptop',
    match: ['/practice/'],
    items: [
      { label: 'Обзор', link: '/practice/' },
      {
        label: 'Базовый минимум SQL',
        items: [
          'practice/sql',
          'practice/sql/setup',
          'practice/sql/datasets',
          { label: 'Основы', collapsed: true, items: [{ autogenerate: { directory: 'practice/sql/basic' } }] },
          { label: 'Средний уровень', collapsed: true, items: [{ autogenerate: { directory: 'practice/sql/intermediate' } }] },
          { label: 'Аналитические кейсы', collapsed: true, items: [{ autogenerate: { directory: 'practice/sql/analytics' } }] },
          { label: 'Продвинутый уровень', collapsed: true, items: [{ autogenerate: { directory: 'practice/sql/advanced' } }] },
        ],
      },
      { label: 'Базовый минимум CLI', items: [{ autogenerate: { directory: 'practice/cli' } }] },
      { label: 'Базовый минимум Python', items: [{ autogenerate: { directory: 'practice/python' } }] },
      { label: 'Базовый минимум статистики', items: [{ autogenerate: { directory: 'practice/stats' } }] },
      { label: 'Базовый минимум Git', items: [{ autogenerate: { directory: 'practice/git' } }] },
      { label: 'Базовый минимум Docker', items: [{ autogenerate: { directory: 'practice/docker' } }] },
      { label: 'Базовый минимум Dimensional Modeling', items: [{ autogenerate: { directory: 'practice/modeling' } }] },
    ],
  },
  {
    label: 'AI',
    link: '/ai/ai-tools/',
    icon: 'puzzle',
    match: ['/ai/'],
    items: [{ label: 'AI для инженера данных', items: [{ autogenerate: { directory: 'ai' } }] }],
  },
  {
    label: 'Карьера',
    link: '/career/job-search/',
    icon: 'analytics',
    match: ['/career/'],
    items: [{ label: 'Карьера', items: [{ autogenerate: { directory: 'career' } }] }],
  },
  {
    label: 'Конспекты книг',
    link: '/book-summaries/',
    icon: 'pencil',
    match: ['/book-summaries/'],
    items: [
      { label: 'Обзор', link: '/book-summaries/' },
      {
        label: 'Инжиниринг',
        items: [
          {
            label: 'Fundamentals of Data Engineering',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/fundamentals-of-data-engineering' } }],
          },
          {
            label: 'The Data Warehouse Toolkit',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/data-warehouse-toolkit' } }],
          },
          {
            label: 'Designing Data-Intensive Applications',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/designing-data-intensive-applications' } }],
          },
          {
            label: 'DuckDB: Up and Running',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/duckdb-up-and-running' } }],
          },
          {
            label: 'Data Pipelines with Apache Airflow',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/data-pipelines-with-apache-airflow' } }],
          },
          {
            label: 'Apache Iceberg: The Definitive Guide',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/apache-iceberg-the-definitive-guide' } }],
          },
          {
            label: 'Learning Spark',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/learning-spark' } }],
          },
          {
            label: 'Data Engineering Design Patterns',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/data-engineering-design-patterns' } }],
          },
          {
            label: 'Data Quality Fundamentals',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/data-quality-fundamentals' } }],
          },
          {
            label: 'Analytics Engineering with SQL and dbt',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/analytics-engineering-with-sql-and-dbt' } }],
          },
          {
            label: 'Practical Lakehouse Architecture',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/practical-lakehouse-architecture' } }],
          },
          {
            label: 'Redefining Data Engineering with AI',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/redefining-data-engineering-with-ai' } }],
          },
        ],
      },
      {
        label: 'AI и ML',
        items: [
          {
            label: 'AI Engineering',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/ai/ai-engineering' } }],
          },
          {
            label: 'Machines that Think',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/ai/machines-that-think' } }],
          },
          {
            label: 'Claude Code: Up and Running',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/ai/claude-code-up-and-running' } }],
          },
          {
            label: 'Claude AI Bible',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/ai/claude-ai-bible' } }],
          },
        ],
      },
      {
        label: 'Предпринимательство',
        items: [
          {
            label: "The Startup Owner's Manual",
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/entrepreneurship/startup-owners-manual' } }],
          },
          {
            label: 'The Mom Test',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/entrepreneurship/mom-test' } }],
          },
          {
            label: 'The Diary of a CEO',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/entrepreneurship/diary-of-a-ceo' } }],
          },
        ],
      },
      {
        label: 'Бизнес',
        items: [
          {
            label: 'Lean Analytics',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/lean-analytics' } }],
          },
          {
            label: 'Escaping the Build Trap',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/escaping-the-build-trap' } }],
          },
        ],
      },
      {
        label: 'Лидерство',
        items: [
          {
            label: "The Manager's Path",
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/managers-path' } }],
          },
          {
            label: 'Staff Engineer',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/staff-engineer' } }],
          },
          {
            label: "The Staff Engineer's Path",
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/staff-engineers-path' } }],
          },
          {
            label: 'Engineering Leadership: The Hard Parts',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/engineering-leadership-hard-parts' } }],
          },
          {
            label: 'Crafting Engineering Strategy',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/crafting-engineering-strategy' } }],
          },
          {
            label: "The Engineering Executive's Primer",
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/business/engineering-executives-primer' } }],
          },
        ],
      },
    ],
  },
  {
    label: 'Конспекты лекций',
    link: '/lecture-summaries/',
    icon: 'notes',
    match: ['/lecture-summaries/'],
    items: [
      { label: 'Обзор', link: '/lecture-summaries/' },
      {
        label: 'AI и ML',
        items: [
          {
            label: 'CME295: Transformers and Large Language Models',
            collapsed: true,
            items: [{ autogenerate: { directory: 'lecture-summaries/ai/stanford-cme295' } }],
          },
          // Курсы со значком «скоро»: пока есть только страница «О курсе». Значок убирают, когда выходит первая лекция.
          {
            label: 'CS336: Language Modeling from Scratch',
            badge: { text: 'скоро', variant: 'note' },
            collapsed: true,
            items: [{ autogenerate: { directory: 'lecture-summaries/ai/stanford-cs336' } }],
          },
          {
            label: 'CS329Z: Engineering AI Agents',
            badge: { text: 'скоро', variant: 'note' },
            collapsed: true,
            items: [{ autogenerate: { directory: 'lecture-summaries/ai/stanford-cs329z' } }],
          },
          {
            label: 'CS193T: Thinking with AI',
            badge: { text: 'скоро', variant: 'note' },
            collapsed: true,
            items: [{ autogenerate: { directory: 'lecture-summaries/ai/stanford-cs193t' } }],
          },
        ],
      },
      {
        label: 'Computer Science',
        items: [
          {
            label: 'CS50x: Introduction to Computer Science',
            badge: { text: 'скоро', variant: 'note' },
            collapsed: true,
            items: [{ autogenerate: { directory: 'lecture-summaries/cs/harvard-cs50x' } }],
          },
        ],
      },
    ],
  },
  {
    label: 'Подготовка к интервью',
    link: '/interview/',
    icon: 'open-book',
    match: ['/interview/'],
    items: [
      { label: 'Обзор', link: '/interview/' },
      { label: 'Вопросы с разбором', collapsed: true, items: [
        { label: 'Все темы', link: '/interview/questions/' },
        {
          "label": "SQL",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/sql/"
            },
            {
              "label": "Оконные функции",
              "collapsed": true,
              "items": [
                {
                  "label": "Типы и примеры",
                  "link": "/interview/questions/sql/windows/"
                },
                {
                  "label": "Группировка и окно",
                  "link": "/interview/questions/sql/windows/partition-by/"
                },
                {
                  "label": "Ранги при равенстве",
                  "link": "/interview/questions/sql/windows/ranking/"
                }
              ]
            },
            {
              "label": "CTE",
              "link": "/interview/questions/sql/cte/"
            },
            {
              "label": "WHERE и HAVING",
              "link": "/interview/questions/sql/aggregation/"
            },
            {
              "label": "Как убрать дубли",
              "link": "/interview/questions/sql/duplicates/"
            },
            {
              "label": "JOIN",
              "collapsed": true,
              "items": [
                {
                  "label": "Виды JOIN",
                  "link": "/interview/questions/sql/joins/"
                },
                {
                  "label": "Задача 1. Границы числа строк",
                  "link": "/interview/questions/sql/joins/bounds/"
                },
                {
                  "label": "Задача 2. JOIN USING (id)",
                  "link": "/interview/questions/sql/joins/using-id/"
                }
              ]
            },
            {
              "label": "Подзапросы",
              "link": "/interview/questions/sql/subqueries/"
            },
            {
              "label": "Порядок выполнения SELECT",
              "link": "/interview/questions/sql/query-order/"
            }
          ]
        },
        {
          "label": "Python",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/python/"
            },
            {
              "label": "Коллекции и хеширование",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/collections/"
                },
                {
                  "label": "Как устроен dict",
                  "link": "/interview/questions/python/collections/dict/"
                },
                {
                  "label": "Хешируемость ключа",
                  "link": "/interview/questions/python/collections/hashable-keys/"
                },
                {
                  "label": "Коллизии в dict",
                  "link": "/interview/questions/python/collections/collisions/"
                },
                {
                  "label": "Устройство list",
                  "link": "/interview/questions/python/collections/list/"
                },
                {
                  "label": "Кортеж и хешируемость",
                  "link": "/interview/questions/python/collections/tuple/"
                },
                {
                  "label": "Стек",
                  "link": "/interview/questions/python/collections/stack/"
                }
              ]
            },
            {
              "label": "Функции и декораторы",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/functions/"
                },
                {
                  "label": "Параметры и аргументы",
                  "link": "/interview/questions/python/functions/arguments/"
                },
                {
                  "label": "Распаковка аргументов",
                  "link": "/interview/questions/python/functions/unpacking/"
                },
                {
                  "label": "Области видимости",
                  "link": "/interview/questions/python/functions/scope/"
                },
                {
                  "label": "Декораторы с аргументами",
                  "link": "/interview/questions/python/functions/decorators/"
                },
                {
                  "label": "Декораторы классов",
                  "link": "/interview/questions/python/functions/class-decorators/"
                },
                {
                  "label": "Встроенные декораторы",
                  "link": "/interview/questions/python/functions/built-in-decorators/"
                }
              ]
            },
            {
              "label": "Итераторы и генераторы",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/iterators/"
                },
                {
                  "label": "Итераторы и генераторы",
                  "link": "/interview/questions/python/iterators/protocol/"
                },
                {
                  "label": "enumerate()",
                  "link": "/interview/questions/python/iterators/enumerate/"
                },
                {
                  "label": "zip()",
                  "link": "/interview/questions/python/iterators/zip/"
                }
              ]
            },
            {
              "label": "Типы, ссылки и память",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/objects/"
                },
                {
                  "label": "Динамическая и сильная типизация",
                  "link": "/interview/questions/python/objects/typing/"
                },
                {
                  "label": "Изменяемость и ссылки",
                  "link": "/interview/questions/python/objects/mutability/"
                },
                {
                  "label": "Равенство и идентичность",
                  "link": "/interview/questions/python/objects/equality/"
                },
                {
                  "label": "Неизменяемость строк",
                  "link": "/interview/questions/python/objects/strings/"
                },
                {
                  "label": "Почему присваивание не копирует список",
                  "link": "/interview/questions/python/objects/assignment/"
                },
                {
                  "label": "Поверхностная и глубокая копия",
                  "link": "/interview/questions/python/objects/copy/"
                },
                {
                  "label": "Циклические ссылки",
                  "link": "/interview/questions/python/objects/cycles/"
                },
                {
                  "label": "Освобождение памяти",
                  "link": "/interview/questions/python/objects/memory/"
                }
              ]
            },
            {
              "label": "Классы и методы",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/classes/"
                },
                {
                  "label": "Принципы ООП",
                  "link": "/interview/questions/python/classes/oop/"
                },
                {
                  "label": "Миксины",
                  "link": "/interview/questions/python/classes/mixins/"
                },
                {
                  "label": "Специальные методы",
                  "link": "/interview/questions/python/classes/dunder/"
                },
                {
                  "label": "classmethod и staticmethod",
                  "link": "/interview/questions/python/classes/method-types/"
                },
                {
                  "label": "Когда возвращают self",
                  "link": "/interview/questions/python/classes/return-self/"
                },
                {
                  "label": "Когда возвращают другой результат",
                  "link": "/interview/questions/python/classes/method-result/"
                },
                {
                  "label": "Контекстный менеджер",
                  "link": "/interview/questions/python/classes/context-managers/"
                }
              ]
            },
            {
              "label": "Потоки, процессы и asyncio",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/concurrency/"
                },
                {
                  "label": "GIL",
                  "link": "/interview/questions/python/concurrency/gil/"
                },
                {
                  "label": "Потоки и процессы",
                  "link": "/interview/questions/python/concurrency/threads-processes/"
                },
                {
                  "label": "Multiprocessing",
                  "link": "/interview/questions/python/concurrency/multiprocessing/"
                },
                {
                  "label": "Что такое асинхронность?",
                  "link": "/interview/questions/python/concurrency/asynchrony/"
                }
              ]
            },
            {
              "label": "Сортировки и инструменты",
              "collapsed": true,
              "items": [
                {
                  "label": "Все вопросы",
                  "link": "/interview/questions/python/algorithms/"
                },
                {
                  "label": "Сортировка в Python",
                  "link": "/interview/questions/python/algorithms/python-sort/"
                },
                {
                  "label": "Нижняя граница сортировки",
                  "link": "/interview/questions/python/algorithms/sort-bound/"
                },
                {
                  "label": "QuickSort, MergeSort и HeapSort",
                  "link": "/interview/questions/python/algorithms/sort-comparison/"
                },
                {
                  "label": "Линтеры",
                  "link": "/interview/questions/python/algorithms/linters/"
                }
              ]
            },
            {
              "label": "Задачи",
              "collapsed": true,
              "items": [
                {
                  "label": "Задача 1. Список по умолчанию",
                  "link": "/interview/questions/python/exercises/mutable-default/"
                },
                {
                  "label": "Задача 2. LEFT JOIN двух списков",
                  "link": "/interview/questions/python/exercises/left-join/"
                }
              ]
            }
          ]
        },
        {
          "label": "Теория БД",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/database-theory/"
            },
            {
              "label": "Транзакции",
              "collapsed": true,
              "items": [
                {
                  "label": "Обзор",
                  "link": "/interview/questions/database-theory/transactions/"
                },
                {
                  "label": "ACID",
                  "link": "/interview/questions/database-theory/transactions/acid/"
                },
                {
                  "label": "Уровни изоляции",
                  "link": "/interview/questions/database-theory/transactions/isolation/"
                },
                {
                  "label": "MVCC",
                  "link": "/interview/questions/database-theory/transactions/mvcc/"
                },
                {
                  "label": "Блокировки",
                  "link": "/interview/questions/database-theory/transactions/locks/"
                }
              ]
            },
            {
              "label": "План запроса",
              "link": "/interview/questions/database-theory/query-plan/"
            },
            {
              "label": "Партиционирование",
              "link": "/interview/questions/database-theory/partitioning/"
            },
            {
              "label": "Индексы",
              "collapsed": true,
              "items": [
                {
                  "label": "Теория и ограничения",
                  "link": "/interview/questions/database-theory/indexes/"
                },
                {
                  "label": "B-tree",
                  "link": "/interview/questions/database-theory/indexes/btree/"
                },
                {
                  "label": "Hash",
                  "link": "/interview/questions/database-theory/indexes/hash/"
                },
                {
                  "label": "GiST",
                  "link": "/interview/questions/database-theory/indexes/gist/"
                },
                {
                  "label": "SP-GiST",
                  "link": "/interview/questions/database-theory/indexes/spgist/"
                },
                {
                  "label": "GIN",
                  "link": "/interview/questions/database-theory/indexes/gin/"
                },
                {
                  "label": "BRIN",
                  "link": "/interview/questions/database-theory/indexes/brin/"
                }
              ]
            },
            {
              "label": "Типы физических джоинов",
              "collapsed": true,
              "items": [
                {
                  "label": "Обзор",
                  "link": "/interview/questions/database-theory/physical-joins/"
                },
                {
                  "label": "Hash Join",
                  "link": "/interview/questions/database-theory/physical-joins/hash-join/"
                },
                {
                  "label": "Merge Join",
                  "link": "/interview/questions/database-theory/physical-joins/merge-join/"
                },
                {
                  "label": "Nested Loop",
                  "link": "/interview/questions/database-theory/physical-joins/nested-loop/"
                }
              ]
            },
            {
              "label": "Оптимизация запроса",
              "link": "/interview/questions/database-theory/query-optimization/"
            },
            {
              "label": "WAL",
              "link": "/interview/questions/database-theory/wal/"
            },
            {
              "label": "VACUUM",
              "link": "/interview/questions/database-theory/vacuum/"
            }
          ]
        },
        {
          "label": "Airflow",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/airflow/"
            },
            {
              "label": "Компоненты Airflow 2 и 3",
              "link": "/interview/questions/airflow/components/"
            },
            {
              "label": "Executors",
              "link": "/interview/questions/airflow/executors/"
            },
            {
              "label": "Pool",
              "link": "/interview/questions/airflow/pools/"
            },
            {
              "label": "Max active tasks и Pool",
              "link": "/interview/questions/airflow/task-limits/"
            },
            {
              "label": "Catchup и расписание DAG",
              "link": "/interview/questions/airflow/scheduling/"
            },
            {
              "label": "Backfill",
              "link": "/interview/questions/airflow/backfill/"
            },
            {
              "label": "Идемпотентность и инкрементальная загрузка",
              "link": "/interview/questions/airflow/idempotency/"
            },
            {
              "label": "XCom",
              "link": "/interview/questions/airflow/xcom/"
            },
            {
              "label": "Python, Bash, Kubernetes и Spark",
              "link": "/interview/questions/airflow/operators/"
            },
            {
              "label": "Триггеры, сенсоры и зависимости DAG",
              "link": "/interview/questions/airflow/dependencies/"
            },
            {
              "label": "Наследование операторов",
              "link": "/interview/questions/airflow/custom-operators/"
            },
            {
              "label": "TaskFlow API",
              "link": "/interview/questions/airflow/taskflow/"
            },
            {
              "label": "Генераторы DAG",
              "link": "/interview/questions/airflow/dag-generation/"
            },
            {
              "label": "Генератор задач (Dynamic Task Mapping)",
              "link": "/interview/questions/airflow/task-mapping/"
            },
            {
              "label": "Паттерны загрузки данных",
              "link": "/interview/questions/airflow/loading-patterns/"
            },
            {
              "label": "Сколько DAG и executors было в проекте?",
              "link": "/interview/questions/airflow/scale/"
            }
          ]
        },
        {
          "label": "Spark",
          "collapsed": true,
          "items": [
            {
              "label": "Все вопросы",
              "link": "/interview/questions/spark/"
            },
            {
              "label": "Компоненты Spark",
              "link": "/interview/questions/spark/components/"
            },
            {
              "label": "Вкладки Spark UI",
              "link": "/interview/questions/spark/web-ui/"
            },
            {
              "label": "Job, Stage и Task",
              "link": "/interview/questions/spark/execution/"
            },
            {
              "label": "Lazy evaluation",
              "link": "/interview/questions/spark/lazy-evaluation/"
            },
            {
              "label": "MapReduce",
              "link": "/interview/questions/spark/map-reduce/"
            },
            {
              "label": "Shuffle",
              "link": "/interview/questions/spark/shuffle/"
            }
          ]
        },
        {
          "label": "ClickHouse",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/clickhouse/"
            },
            {
              "label": "Семейство MergeTree",
              "link": "/interview/questions/clickhouse/mergetree/"
            },
            {
              "label": "Ключ сортировки",
              "link": "/interview/questions/clickhouse/sorting/"
            }
          ]
        },
        {
          "label": "Kafka",
          "collapsed": true,
          "items": [
            {
              "label": "Все вопросы",
              "link": "/interview/questions/kafka/"
            },
            {
              "label": "Что такое Kafka",
              "link": "/interview/questions/kafka/what-is-kafka/"
            },
            {
              "label": "Компоненты Kafka",
              "link": "/interview/questions/kafka/components/"
            },
            {
              "label": "Топики и партиции",
              "link": "/interview/questions/kafka/partitions/"
            },
            {
              "label": "Ключ и порядок событий",
              "link": "/interview/questions/kafka/partition-key/"
            },
            {
              "label": "Группы потребителей",
              "link": "/interview/questions/kafka/consumer-groups/"
            },
            {
              "label": "Offset и его коммит",
              "link": "/interview/questions/kafka/offsets/"
            },
            {
              "label": "Ребалансировка группы",
              "link": "/interview/questions/kafka/rebalance/"
            },
            {
              "label": "Репликация, leader и ISR",
              "link": "/interview/questions/kafka/replication/"
            },
            {
              "label": "Гарантии доставки",
              "link": "/interview/questions/kafka/delivery-semantics/"
            },
            {
              "label": "Retention и compaction",
              "link": "/interview/questions/kafka/retention/"
            }
          ]
        },
        {
          "label": "Data modeling",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/data-modeling/"
            },
            {
              "label": "Факты и измерения",
              "link": "/interview/questions/data-modeling/dimensional/"
            },
            {
              "label": "История изменений",
              "link": "/interview/questions/data-modeling/scd/"
            }
          ]
        },
        {
          "label": "dbt",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/dbt/"
            },
            {
              "label": "Модели",
              "link": "/interview/questions/dbt/models/"
            },
            {
              "label": "Тесты",
              "link": "/interview/questions/dbt/tests/"
            }
          ]
        },
        {
          "label": "Data Quality",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/data-quality/"
            },
            {
              "label": "Проверки данных",
              "link": "/interview/questions/data-quality/checks/"
            },
            {
              "label": "Свежесть данных",
              "link": "/interview/questions/data-quality/freshness/"
            }
          ]
        },
        {
          "label": "Iceberg",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/iceberg/"
            },
            {
              "label": "Снапшоты",
              "link": "/interview/questions/iceberg/snapshots/"
            },
            {
              "label": "Эволюция схемы",
              "link": "/interview/questions/iceberg/schema/"
            }
          ]
        },
        {
          "label": "Flink",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/flink/"
            },
            {
              "label": "Время событий",
              "link": "/interview/questions/flink/event-time/"
            },
            {
              "label": "Состояние",
              "link": "/interview/questions/flink/state/"
            }
          ]
        },
        {
          "label": "Инфраструктура",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/infrastructure/"
            },
            {
              "label": "Контейнеры",
              "link": "/interview/questions/infrastructure/containers/"
            },
            {
              "label": "Сети",
              "link": "/interview/questions/infrastructure/network/"
            }
          ]
        },
        {
          "label": "Soft skills",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/soft-skills/"
            },
            {
              "label": "Коммуникация",
              "link": "/interview/questions/soft-skills/communication/"
            },
            {
              "label": "Разногласия в команде",
              "link": "/interview/questions/soft-skills/conflicts/"
            }
          ]
        },
        {
          "label": "Прочие",
          "collapsed": true,
          "items": [
            {
              "label": "Все подтемы",
              "link": "/interview/questions/other/"
            },
            {
              "label": "Проектирование систем",
              "link": "/interview/questions/other/system-design/"
            },
            {
              "label": "Оценка нагрузки",
              "link": "/interview/questions/other/estimates/"
            }
          ]
        },
      ] },
      { label: 'Карточки для повторения', collapsed: true, items: [
        { label: 'Все темы', link: '/interview/cards/' },
        { label: 'SQL', link: '/interview/cards/sql/' },
        { label: 'Python', link: '/interview/cards/python/' },
        { label: 'Теория БД', link: '/interview/cards/database-theory/' },
        { label: 'Airflow', link: '/interview/cards/airflow/' },
        { label: 'Spark', link: '/interview/cards/spark/' },
        { label: 'ClickHouse', link: '/interview/cards/clickhouse/' },
        { label: 'Kafka', link: '/interview/cards/kafka/' },
        { label: 'Data modeling', link: '/interview/cards/data-modeling/' },
        { label: 'dbt', link: '/interview/cards/dbt/' },
        { label: 'Data Quality', link: '/interview/cards/data-quality/' },
        { label: 'Iceberg', link: '/interview/cards/iceberg/' },
        { label: 'Flink', link: '/interview/cards/flink/' },
        { label: 'Инфраструктура', link: '/interview/cards/infrastructure/' },
        { label: 'Soft skills', link: '/interview/cards/soft-skills/' },
        { label: 'Прочие', link: '/interview/cards/other/' },
      ] },
    ],
  },
  {
    label: 'Библиотека',
    link: '/resources/books/',
    icon: 'document',
    match: ['/resources/', '/community/'],
    items: [
      { label: 'Книги и материалы', items: [{ autogenerate: { directory: 'resources' } }] },
      { label: 'Сообщество', items: [{ autogenerate: { directory: 'community' } }] },
    ],
  },
];
