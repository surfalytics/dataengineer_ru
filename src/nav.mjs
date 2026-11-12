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
        label: 'Инженерия',
        items: [
          {
            label: 'Fundamentals of Data Engineering',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/fundamentals-of-data-engineering' } }],
          },
          {
            label: 'Designing Data-Intensive Applications',
            collapsed: true,
            items: [{ autogenerate: { directory: 'book-summaries/engineering/designing-data-intensive-applications' } }],
          },
        ],
      },
      // AI: добавить группу, когда появится первая книга (папка book-summaries/ai/).
      {
        label: 'Бизнес и Soft Skills',
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
