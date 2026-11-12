---
title: "AI Engineering — конспект книги"
head:
  - tag: title
    content: "AI Engineering Chip Huyen: конспект | Инжиниринг Данных"
description: "Конспект книги AI Engineering (Chip Huyen) на русском. Foundation models, evaluation, prompt, RAG, агенты, finetuning, данные, inference: разбор 10 глав."
author: "Chip Huyen"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - ai
---

**AI Engineering: Building Applications with Foundation Models** — книга Chip Huyen (O'Reilly, декабрь 2024). Она учит строить приложения на готовых foundation models: от выбора модели и оценки качества до RAG, агентов, finetuning и архитектуры продукта. В книге 10 глав.

> Это собственный пересказ, а не перевод. За полным текстом, примерами и ссылками на исследования идите в оригинал. Схемы нарисованы заново по содержанию глав.

![Карта книги: 10 глав в четырёх блоках](/assets/ai-engineering/ch00-book-map.png)

## Зачем читать

- **Одна карта AI-стека.** Книга связывает prompt, RAG, finetuning, оценку и inference в одну систему.
- **Оценка — в центре.** Две главы про evaluation. Без оценки нельзя выбрать модель и понять, стало ли лучше.
- **Данные решают.** Глава про dataset engineering близка к работе дата-инженера: качество, дедупликация, синтетика.
- **Не про один продукт.** Модели меняются каждый месяц. Принципы остаются.
- **Решения про стоимость.** Latency, cost, build vs buy, когда finetune, а когда RAG.

## Как устроена книга

| Блок | Главы | О чём |
|---|---|---|
| Основы | 1–2 | Что такое AI engineering, как устроены foundation models |
| Оценка | 3–4 | Методы evaluation, выбор модели, пайплайн оценки |
| Адаптация модели | 5–8 | Prompt, RAG и агенты, finetuning, данные |
| Продакшен | 9–10 | Оптимизация inference, архитектура, обратная связь |

## Главные идеи

| Идея | Где разбирается |
|---|---|
| Порядок адаптации: prompt, потом RAG, потом finetuning | [Глава 7](/book-summaries/ai/ai-engineering/07-finetuning/) |
| Finetune для формы, RAG для фактов | [Глава 6](/book-summaries/ai/ai-engineering/06-rag-and-agents/), [глава 7](/book-summaries/ai/ai-engineering/07-finetuning/) |
| Сначала оценка, потом разработка (evaluation-driven development) | [Глава 4](/book-summaries/ai/ai-engineering/04-evaluate-ai-systems/) |
| Модель вероятностная, поэтому нужны sampling-настройки и проверки | [Глава 2](/book-summaries/ai/ai-engineering/02-understanding-foundation-models/) |
| Качество данных важнее их количества | [Глава 8](/book-summaries/ai/ai-engineering/08-dataset-engineering/) |
| Prefill и decode: две разные фазы inference | [Глава 9](/book-summaries/ai/ai-engineering/09-inference-optimization/) |
| Архитектура растёт шагами: context, guardrails, router, cache | [Глава 10](/book-summaries/ai/ai-engineering/10-architecture-and-user-feedback/) |

## Что изменилось к 2026 году

Книга написана в 2024 году. Главные идеи не устарели: оценка в центре, данные важнее модели, порядок prompt → RAG → finetuning. Устарели примеры моделей, цены и часть инструментов. В конце каждой главы есть раздел «Что изменилось к 2026 году».

| Тема | Что изменилось | Глава |
|---|---|---|
| Модели | Reasoning models и test-time compute. RL с проверяемой наградой (RLVR). MoE стал нормой | [2](/book-summaries/ai/ai-engineering/02-understanding-foundation-models/) |
| Оценка | MMLU насыщен. LMArena вместо LMSYS. Новые benchmarks для кода и агентов | [3](/book-summaries/ai/ai-engineering/03-evaluation-methodology/), [4](/book-summaries/ai/ai-engineering/04-evaluate-ai-systems/) |
| Контекст | Context engineering. Контекст 1M токенов. Structured output по JSON schema | [5](/book-summaries/ai/ai-engineering/05-prompt-engineering/) |
| Агенты | MCP стал стандартом. Coding agents. Agentic search рядом с vector RAG | [6](/book-summaries/ai/ai-engineering/06-rag-and-agents/) |
| Обучение | Reinforcement fine-tuning. Synthetic data с автоматической проверкой | [7](/book-summaries/ai/ai-engineering/07-finetuning/), [8](/book-summaries/ai/ai-engineering/08-dataset-engineering/) |
| Serving | FP8 и FP4, disaggregated prefill/decode, vLLM и SGLang | [9](/book-summaries/ai/ai-engineering/09-inference-optimization/) |
| Продакшен | AI gateways, OpenTelemetry для GenAI, онлайн-evals | [10](/book-summaries/ai/ai-engineering/10-architecture-and-user-feedback/) |

## Для кого

| Роль | Что получит |
|---|---|
| Data engineer, analytics engineer | Понимание, как данные и пайплайны работают внутри AI-продуктов |
| Разработчик AI-фич | Карту решений: модель, prompt, RAG, finetuning, оценка |
| Аналитик | Методы оценки качества и работы с feedback |
| Руководитель | Язык для обсуждения стоимости, рисков и сроков AI-проекта |

Нужны базовые знания Python и общее представление о машинном обучении. Глубокая математика не нужна.

## Как читать

- **Новичок.** Читайте по порядку. Главы 1, 2, 5 дают основу. Главу 9 оставьте на второй проход.
- **Analytics engineer.** Главы 3, 4, 8, 10: оценка, данные, feedback.
- **Data engineer.** Главы 6, 8, 9, 10: RAG-пайплайн, датасеты, serving, мониторинг.
- **Руководитель.** Главы 1, 4, 7, 10: планирование, оценка, build vs buy, архитектура.

Предлагаемый порядок:

1. Главы 1–2: что строим и на чём.
2. Главы 3–4: как измерять качество.
3. Главы 5–7: как адаптировать модель.
4. Глава 8: как готовить данные.
5. Главы 9–10: как запускать и улучшать в продакшене.

## Связь с другими конспектами

| | Fundamentals of Data Engineering | AI Engineering |
|---|---|---|
| Фокус | Жизненный цикл данных | Жизненный цикл AI-приложения |
| Вопрос | Как данные попадают к потребителю | Как из данных и модели собрать продукт |

Данные для RAG, finetuning и оценки приходят из тех самых пайплайнов. Начните с [конспекта Fundamentals of Data Engineering](/book-summaries/engineering/fundamentals-of-data-engineering/), если нужна база.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. Введение в AI engineering](/book-summaries/ai/ai-engineering/01-intro-ai-engineering/) | Foundation models, AI-стек, планирование приложения |
| [2. Как устроены foundation models](/book-summaries/ai/ai-engineering/02-understanding-foundation-models/) | Данные, архитектура, post-training, sampling |
| [3. Методология оценки](/book-summaries/ai/ai-engineering/03-evaluation-methodology/) | Perplexity, exact evaluation, AI as a judge |
| [4. Оценка AI-систем](/book-summaries/ai/ai-engineering/04-evaluate-ai-systems/) | Критерии, выбор модели, пайплайн оценки |
| [5. Prompt engineering](/book-summaries/ai/ai-engineering/05-prompt-engineering/) | Приёмы prompt, защита от атак |
| [6. RAG и агенты](/book-summaries/ai/ai-engineering/06-rag-and-agents/) | Retrieval, chunking, tools, planning, memory |
| [7. Finetuning](/book-summaries/ai/ai-engineering/07-finetuning/) | Когда нужен, память, LoRA, QLoRA |
| [8. Dataset engineering](/book-summaries/ai/ai-engineering/08-dataset-engineering/) | Качество данных, синтетика, обработка |
| [9. Оптимизация inference](/book-summaries/ai/ai-engineering/09-inference-optimization/) | Latency, KV cache, batching, quantization |
| [10. Архитектура и feedback](/book-summaries/ai/ai-engineering/10-architecture-and-user-feedback/) | Guardrails, router, cache, мониторинг, обратная связь |

Каждая страница содержит главную мысль, схему, ключевые термины, выводы для практики и вопросы для самопроверки.
