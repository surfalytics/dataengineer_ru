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
