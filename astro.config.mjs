// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const GA_ID = 'G-WWHHQZ07HV';

export default defineConfig({
  site: 'https://dataengineer.ru',
  // base intentionally omitted — apex custom domain serves from root.
  // Default build.format 'directory' keeps clean content URLs (/processing/sql/).
  // Legacy `*.html` redirect keys emit as `<name>.html/index.html`; GitHub Pages
  // adds the trailing slash and serves the meta-refresh redirect from there.
  integrations: [
    starlight({
      title: 'Инжиниринг Данных',
      description: 'Русскоязычный портал об аналитике и инжиниринге данных.',
      defaultLocale: 'root',
      locales: {
        root: { label: 'Русский', lang: 'ru' },
      },
      logo: {
        src: './src/assets/surf2.svg',
        alt: 'Инжиниринг Данных',
        replacesTitle: false,
      },
      favicon: '/favicon.png',
      customCss: ['./src/styles/custom.css'],
      social: [
        { icon: 'telegram', label: 'Telegram', href: 'https://t.me/rockyourdata' },
        { icon: 'github', label: 'GitHub', href: 'https://github.com/surfalytics/dataengineer_ru' },
      ],
      editLink: {
        baseUrl: 'https://github.com/surfalytics/dataengineer_ru/edit/main/',
      },
      head: [
        // Google Analytics 4
        {
          tag: 'script',
          attrs: { async: true, src: `https://www.googletagmanager.com/gtag/js?id=${GA_ID}` },
        },
        {
          tag: 'script',
          content: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${GA_ID}');`,
        },
      ],
      sidebar: [
        { label: 'Обработка и аналитика', items: [{ autogenerate: { directory: 'processing' } }] },
        { label: 'Инструменты', items: [{ autogenerate: { directory: 'tools' } }] },
        { label: 'AI', items: [{ autogenerate: { directory: 'ai' } }] },
        { label: 'Карьера', items: [{ autogenerate: { directory: 'career' } }] },
        { label: 'Книги и Материалы', items: [{ autogenerate: { directory: 'resources' } }] },
        { label: 'Сообщество и Управление', items: [{ autogenerate: { directory: 'community' } }] },
        { label: 'О проекте', items: [{ autogenerate: { directory: 'about' } }] },
      ],
    }),
  ],
  redirects: {
    // Old Jekyll post URLs (/hard-skills/<date>-<slug>.html) -> new section URLs.
    '/hard-skills/2024-06-01-sql.html': '/processing/sql/',
    '/hard-skills/2024-06-02-dw.html': '/processing/dw/',
    '/hard-skills/2024-06-03-data_modelling.html': '/processing/data-modelling/',
    '/hard-skills/2024-06-04-data_quality.html': '/processing/data-quality/',
    '/hard-skills/2024-06-05-etl.html': '/processing/etl/',
    '/hard-skills/2024-07-01-spark.html': '/processing/spark/',
    '/hard-skills/2024-07-02-bigdata.html': '/processing/bigdata/',
    '/hard-skills/2024-07-03-streaming.html': '/processing/streaming/',
    '/hard-skills/2024-07-04-bi.html': '/processing/bi/',
    '/hard-skills/2024-07-05-dataviz.html': '/processing/dataviz/',
    '/hard-skills/2024-08-01-coding.html': '/tools/coding/',
    '/hard-skills/2024-08-02-data-tools.html': '/tools/cli-ide/',
    '/hard-skills/2024-08-03-api.html': '/tools/api/',
    '/hard-skills/2024-08-04-cloudcomputing.html': '/tools/cloud/',
    '/hard-skills/2024-08-05-devops.html': '/tools/devops/',
    '/hard-skills/2024-09-01-ai-tools.html': '/ai/ai-tools/',
    '/hard-skills/2024-09-02-claude-code-101.html': '/ai/claude-code-101/',
    // Old _pages / _others collection URLs.
    '/pages/books/': '/resources/books/',
    '/pages/whitepapers/': '/resources/whitepapers/',
    '/pages/career/': '/career/job-search/',
    '/pages/careertracks/': '/career/career-tracks/',
    '/pages/communities/': '/community/communities/',
    '/pages/management/': '/community/management/',
    '/others/about/': '/about/about/',
    '/others/contact/': '/about/contact/',
    '/others/services/': '/about/services/',
  },
});
