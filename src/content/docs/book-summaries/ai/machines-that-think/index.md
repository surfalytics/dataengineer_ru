---
title: "Machines that Think — конспект книги"
head:
  - tag: title
    content: "Machines that Think: конспект книги про LLM | Инжиниринг Данных"
description: "Конспект книги Machines that Think на русском. Как работают LLM, думают ли они, где ошибаются, что с этикой и как AI меняет работу. Разбор 8 глав."
author: "Rubén Castillo Sánchez"
sidebar:
  order: 0
  label: "Обзор книги"
tags:
  - books
  - ai
  - llm
---

**Machines that Think: What it really means for AI to think** — книга Rubén Castillo Sánchez (Manning, MEAP, версия 3, 2026). Она объясняет простым языком, как устроены большие языковые модели (LLM), в чём они сильны и где ошибаются. В версии 3 доступны 8 глав из 12. Главы 9–12 ещё не вышли.

> Это собственный пересказ, а не перевод. За полным текстом идите в оригинал. Схемы нарисованы заново по содержанию глав.

## Зачем читать

- **Это не учебник по коду.** Книга даёт ментальную модель: что внутри LLM и почему она ведёт себя именно так.
- **Понятно без математики.** Не нужен опыт в ML. Достаточно пользоваться ChatGPT или Claude.
- **Видно, где модель врёт.** Галлюцинации, зависимость от формулировки, jailbreak, пределы контекста.
- **Есть вопрос «думает ли машина».** Книга не даёт готового ответа. Она показывает, как о нём рассуждать.
- **Помогает решать на работе.** Когда доверять ответу, как считать цену, как проверять код от AI.

## Как устроена книга

| Часть | Главы | О чём |
|---|---|---|
| 1. Машины и люди | 1–5 | История идеи, язык и токены, нейросети, LLM, сравнение с мозгом |
| 2. Успехи и провалы | 6–9 | Ошибки LLM, этика и bias, влияние на работу и учёбу. Глава 9 ещё не вышла |
| 3. Будущее интеллекта | 10–12 | Ещё не вышли |

## Главные идеи

| Идея | Где разбирается |
|---|---|
| Гладкая речь не доказывает понимание | [Глава 1](/book-summaries/ai/machines-that-think/01-old-questions-new-machines/) |
| Машина собирает смысл из токенов и векторов | [Глава 2](/book-summaries/ai/machines-that-think/02-now-we-are-speaking/) |
| Нейросеть учится на ошибках: loss, backpropagation, gradient descent | [Глава 3](/book-summaries/ai/machines-that-think/03-inside-machine-brains/) |
| Transformer, масштаб и цена сделали LLM возможными | [Глава 4](/book-summaries/ai/machines-that-think/04-large-language-models/) |
| Похожее поведение не значит похожий механизм | [Глава 5](/book-summaries/ai/machines-that-think/05-back-to-humans/) |
| Надёжность даёт система вокруг модели, а не сама модель | [Глава 6](/book-summaries/ai/machines-that-think/06-all-that-glitters-is-not-smart/) |
| Этика модели — привычка из обучения. Bias идёт из данных | [Глава 7](/book-summaries/ai/machines-that-think/07-sure-i-can-be-unethical/) |
| Выгода от LLM в каждой области идёт вместе с новым риском | [Глава 8](/book-summaries/ai/machines-that-think/08-and-yet-it-works/) |

## Как читать

- **Новичок.** Читайте по порядку. Главы 1–4 дают основу.
- **Analytics engineer.** Главы 2, 6, 7: токены и embeddings, проверка ответов, bias по срезам.
- **Data engineer.** Главы 4, 6, 8: цена и контекст, prompt injection в пайплайнах, код от AI.
- **Руководитель.** Главы 1, 6, 8: ожидания, риски, влияние на команду.

## Связь с другими конспектами

| | AI Engineering | Machines that Think |
|---|---|---|
| Фокус | Как строить приложения на модели | Как модель устроена и почему так себя ведёт |
| Уровень | Практика: prompt, RAG, оценка | Понимание: токены, attention, ошибки, этика |

Сначала можно прочитать эту книгу для базы. Потом [AI Engineering](/book-summaries/ai/ai-engineering/) для практики.

## Разбор по главам

| Глава | Тема |
|---|---|
| [1. Старые вопросы, новые машины](/book-summaries/ai/machines-that-think/01-old-questions-new-machines/) | История ИИ, тест Тьюринга, Китайская комната |
| [2. Теперь мы говорим](/book-summaries/ai/machines-that-think/02-now-we-are-speaking/) | n-gram, токены, BPE, embeddings |
| [3. Как устроены нейросети](/book-summaries/ai/machines-that-think/03-inside-machine-brains/) | Нейрон, обучение, overfitting, CNN, RNN, attention |
| [4. Большие языковые модели](/book-summaries/ai/machines-that-think/04-large-language-models/) | Transformer, масштаб, LoRA, quantization, MoE |
| [5. Снова о человеке](/book-summaries/ai/machines-that-think/05-back-to-humans/) | Мозг и нейросеть, память, цели |
| [6. Не всё то золото, что блестит](/book-summaries/ai/machines-that-think/06-all-that-glitters-is-not-smart/) | Hallucination, jailbreak, context window |
| [7. Да, я могу быть неэтичным](/book-summaries/ai/machines-that-think/07-sure-i-can-be-unethical/) | Alignment, sycophancy, bias |
| [8. И всё-таки это работает](/book-summaries/ai/machines-that-think/08-and-yet-it-works/) | Экосистема, vibe coding, cognitive debt, наука |

Каждая страница содержит главную мысль, схему, ключевые термины, выводы для практики и вопросы для самопроверки.
