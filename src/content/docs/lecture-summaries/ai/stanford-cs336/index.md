---
title: "Stanford CS336: Language Modeling from Scratch"
head:
  - tag: title
    content: "Stanford CS336 на русском: языковая модель с нуля | Инжиниринг Данных"
description: "Курс Stanford CS336 (весна 2026) о том, как построить LLM с нуля: токенизатор, трансформер, GPU, параллелизм, законы масштабирования, данные. 18 лекций."
author: "Percy Liang, Tatsunori Hashimoto"
sidebar:
  order: 0
  label: "О курсе"
tags:
  - lectures
  - llm
---

**Stanford CS336: Language Modeling from Scratch** — курс Stanford University весны 2026 года. Его ведут Percy Liang и Tatsunori Hashimoto. В курсе 17 лекций и одна гостевая. Курс учит строить `LLM` (большая языковая модель) с нуля, от данных до готовой модели.

> Конспект этого курса мы ещё готовим. Пока здесь описание курса и ссылки на видео. Основы уже разобраны в конспекте курса [CME295](/lecture-summaries/ai/stanford-cme295/): токены, механизм внимания (`attention`) и устройство трансформера (`transformer`).

## О чём курс

Авторы сравнивают его с курсами по операционным системам, где студенты пишут свою систему с нуля. В этом курсе студенты так же с нуля проходят весь путь создания языковой модели: сбор и очистку данных для предобучения (`pre-training`), сборку трансформера, обучение модели и оценку качества перед запуском.

Лекции идут крупными блоками. Сначала основы: токенизация (`tokenization`) и токенизатор (`tokenizer`), PyTorch и архитектура модели. Затем идёт блок о системах: как устроены GPU и TPU, как писать быстрые ядра (`kernels`) на Triton и как делить обучение между многими ускорителями. После этого курс разбирает законы масштабирования (`scaling law`) и `inference` (работа обученной модели). Последние лекции посвящены оценке, данным, `mid-training` (промежуточное обучение) и `post-training` (обучение после предобучения), в том числе `RL` (обучение с подкреплением) и выравниванию (`alignment`).

## Для кого

- Для тех, кто хочет понимать `LLM` на уровне кода, а не только пользоваться готовыми моделями.
- Курс очень практический. Авторы предупреждают, что кода в нём на порядок больше, чем в других курсах по AI, а готовых заготовок почти нет.
- Нужны уверенный Python, опыт с PyTorch и глубоким обучением, линейная алгебра, основы теории вероятностей и машинного обучения.

## Лекции

| № | Тема | Видео |
|---|---|---|
| 1 | Обзор курса и токенизация | [1 ч 19 мин](https://www.youtube.com/watch?v=JuoVZkPBiKk) |
| 2 | PyTorch и einops | [1 ч 17 мин](https://www.youtube.com/watch?v=kuYAsz7zspQ) |
| 3 | Архитектуры | [1 ч 29 мин](https://www.youtube.com/watch?v=lVynu4bo1rY) |
| 4 | Альтернативы механизму внимания | [1 ч 26 мин](https://www.youtube.com/watch?v=cKSwj_qZ8Jg) |
| 5 | GPU и TPU | [1 ч 19 мин](https://www.youtube.com/watch?v=izZba4UA7iY) |
| 6 | Ядра GPU, Triton и XLA | [1 ч 27 мин](https://www.youtube.com/watch?v=xnDHaNUvHBg) |
| 7 | Параллелизм, часть 1 | [1 ч 21 мин](https://www.youtube.com/watch?v=SzpOcwdIL0Y) |
| 8 | Параллелизм, часть 2 | [1 ч 20 мин](https://www.youtube.com/watch?v=6-cXp-aOmdg) |
| 9 | Законы масштабирования, часть 1 | [1 ч 18 мин](https://www.youtube.com/watch?v=Q15rhEWZPQ4) |
| 10 | Inference | [1 ч 26 мин](https://www.youtube.com/watch?v=EfM546A79aM) |
| 11 | Законы масштабирования, часть 2 | [1 ч 17 мин](https://www.youtube.com/watch?v=vTfEyOyzV9E) |
| 12 | Оценка моделей | [1 ч 19 мин](https://www.youtube.com/watch?v=JpAxdTWQJxM) |
| 13 | Данные: источники и наборы данных | [1 ч 22 мин](https://www.youtube.com/watch?v=-qm0ln33G24) |
| 14 | Данные, часть 2 | [1 ч 25 мин](https://www.youtube.com/watch?v=5sxHosTLPF8) |
| 15 | Mid-training и post-training | [1 ч 20 мин](https://www.youtube.com/watch?v=2oH6PWPrYFo) |
| 16 | Post-training: RLVR | [1 ч 16 мин](https://www.youtube.com/watch?v=dIFAi87Ws4E) |
| 17 | Выравнивание и мультимодальность | [1 ч 18 мин](https://www.youtube.com/watch?v=26FtD08ZpOU) |
| — | Гостевая лекция: Dan Fu | [1 ч 12 мин](https://www.youtube.com/watch?v=9EEm4iMAF5s) |

## Источник

- Видео: [плейлист на YouTube](https://www.youtube.com/playlist?list=PLoROMvodv4rMqXOcazWaTUHhq-yembLCV), канал Stanford Online.
- Программа, слайды и задания: [сайт курса](https://cs336.stanford.edu/).
