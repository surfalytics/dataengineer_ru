// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightSidebarTopics from 'starlight-sidebar-topics';
import sitemap from '@astrojs/sitemap';
import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { topics } from './src/nav.mjs';

const GA_ID = 'G-WWHHQZ07HV';
const SITE = 'https://dataengineer.ru';
const YM_ID = 114151925;

// Дата последнего коммита страницы для <lastmod> в sitemap (Яндекс по ней быстрее находит изменения).
// URL /processing/sql/ -> src/content/docs/processing/sql.md(x) или .../index.mdx.
function lastModified(url) {
  const p = new URL(url).pathname.replace(/^\/|\/$/g, '');
  const base = `src/content/docs/${p}`;
  const file = [`${base}.md`, `${base}.mdx`, `${base}/index.md`, `${base}/index.mdx`].find(existsSync);
  if (!file) return undefined;
  try {
    return execFileSync('git', ['log', '-1', '--format=%cI', '--', file], { encoding: 'utf8' }).trim() || undefined;
  } catch {
    return undefined;
  }
}

// Картинки в Markdown грузятся лениво: страница открывается быстрее.
// Первую картинку страницы не трогаем — она может быть на первом экране.
function rehypeLazyImages() {
  return (tree) => {
    let seen = 0;
    const walk = (node) => {
      if (node.type === 'element' && node.tagName === 'img') {
        node.properties ??= {};
        node.properties.decoding ??= 'async';
        if (seen++ > 0) node.properties.loading ??= 'lazy';
      }
      node.children?.forEach(walk);
    };
    walk(tree);
  };
}

export default defineConfig({
  site: SITE,
  markdown: {
    rehypePlugins: [rehypeLazyImages],
  },
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
      // Логотип "Дата Инженеръ" без плашки: чёрный для светлой темы, белый для тёмной.
      logo: {
        light: './src/assets/logo-light.svg',
        dark: './src/assets/logo-dark.svg',
        alt: 'Дата Инженеръ — Инжиниринг Данных',
        replacesTitle: true,
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
        // SEO: подтверждение прав в Яндекс Вебмастере (дублирует файл public/yandex_*.html).
        { tag: 'meta', attrs: { name: 'yandex-verification', content: '3e8b3a9a06bfb537' } },
        // SEO: Open Graph для сниппетов Яндекса, Telegram и VK.
        { tag: 'meta', attrs: { property: 'og:locale', content: 'ru_RU' } },
        { tag: 'meta', attrs: { property: 'og:image', content: `${SITE}/og-image.png` } },
        { tag: 'meta', attrs: { property: 'og:image:width', content: '1200' } },
        { tag: 'meta', attrs: { property: 'og:image:height', content: '630' } },
        { tag: 'meta', attrs: { name: 'twitter:image', content: `${SITE}/og-image.png` } },
        // SEO: структурированные данные о сайте (Schema.org), их читают Яндекс и Google.
        {
          tag: 'script',
          attrs: { type: 'application/ld+json' },
          content: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            name: 'Инжиниринг Данных',
            alternateName: 'Дата Инженеръ',
            url: `${SITE}/`,
            inLanguage: 'ru-RU',
            description: 'Русскоязычный портал об аналитике и инжиниринге данных.',
          }),
        },
        // Яндекс Метрика
        {
          tag: 'script',
          content: `(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})(window,document,'script','https://mc.yandex.ru/metrika/tag.js?id=${YM_ID}','ym');ym(${YM_ID},'init',{ssr:true,webvisor:true,clickmap:true,ecommerce:'dataLayer',referrer:document.referrer,url:location.href,accurateTrackBounce:true,trackLinks:true});`,
        },
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
      // Дата последнего изменения страницы из git.
      lastUpdated: true,
      components: {
        Header: './src/components/Header.astro',
      },
      // Каждый раздел (вкладка в шапке) получает свой сайдбар.
      plugins: [starlightSidebarTopics(topics.map(({ match, ...t }) => t))],
    }),
    // Свой sitemap вместо встроенного в Starlight: добавляет <lastmod> из git.
    sitemap({
      serialize(item) {
        const lastmod = lastModified(item.url);
        return lastmod ? { ...item, lastmod } : item;
      },
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
