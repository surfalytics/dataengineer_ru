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
