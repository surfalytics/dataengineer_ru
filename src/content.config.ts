import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({
    loader: docsLoader(),
    schema: docsSchema({
      extend: z.object({
        // Курация ресурсов: теги для поиска/фильтрации.
        tags: z.array(z.string()).optional(),
        // Учебный трек (дорожная карта) для навигации по пути обучения.
        track: z.string().optional(),
        author: z.string().optional(),
        pubDate: z.coerce.date().optional(),
      }),
    }),
  }),
};
