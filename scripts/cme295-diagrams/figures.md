# Рисунки курса CME295 и наши схемы

Статус: `redrawn` — перерисован по-нашему; `own` — наша схема; `skipped: причина`.
Слайды курса в репозиторий не копируем (авторские права). Схемы собирает `lecNN_diagrams.py` через `excb.py`.

## Обзор

| Лекция | Что на слайде | Идея | Наш файл | Статус |
|---|---|---|---|---|
| — | — | Карта курса: 7 лекций в трёх блоках | lec00-course-map.png (`lec00_diagrams.py`) | own |
| 1 | Схема трансформера из статьи | Энкодер и декодер | lec01-transformer.png | redrawn |
| 1 | Нет (наш рисунок) | Путь к трансформеру | lec01-roadmap.png | own |
| 1 | Формула внимания | query, key, value | lec01-qkv.png | own |
| 1 | Сеть Word2vec с одним скрытым слоем | Прокси-задача и скрытый вектор | lec01-word2vec.png | redrawn |
| 2 | Схемы encoder-only, decoder-only, сравнение с encoder-decoder | Три семейства трансформеров | lec02-families.png | redrawn |
| 2 | Схема sparse MoE, router, experts | Маршрутизация токена к top-k экспертам | lec02-moe.png | redrawn |
| 2 | Итоговые слайды про RoPE, SWA, GQA, pre-norm, RMSNorm | Что поменяли в блоке | lec02-block.png | own |
| 2 | Схемы greedy, sampling, температура | От logits до следующего токена | lec02-decoding.png | own |
| 2 | Графики законов масштабирования (Kaplan, Chinchilla) | Качество растёт с размером и данными | описано числами в тексте | skipped: числа в тексте и скрипте понятнее |
| 2 | Тепловая карта синусоидального position embedding | Сходство позиций | таблица значений скрипта lec02_rope.py | skipped: цифры в выводе скрипта |
| 2 | Beam search: дерево вариантов | k путей | описано в тексте | skipped: деталей мало |
| 2 | Окраска токенов по экспертам Mixtral | Разные токены идут к разным экспертам | описано в тексте | skipped: картинка из статьи |
| 3 | Слайды Pretraining, Paradigm for LLM training, Post-training | Все этапы обучения LLM | lec03-pipeline.png | redrawn |
| 3 | Слайды Pretraining overview, teacher forcing | Предсказание следующего токена за один проход | lec03-teacher-forcing.png | redrawn |
| 3 | Слайды LoRA | W0 заморожен, обучаем B и A | lec03-lora.png | redrawn |
| 3 | Слайды RLHF overview, Step 1, Step 2 | Два шага RLHF | lec03-rlhf.png | redrawn |
| 3 | Слайды Preference data (pointwise, pairwise, listwise) | Три формата данных | таблица в тексте | skipped: таблица проще |
| 3 | Слайды Reasoning timeline, скриншоты UI | Хронология и интерфейс | описано в тексте | skipped: скриншоты |
| 3 | Графики GRPO: качество и длина цепочки | Рост качества и длины рассуждений | описано в тексте | skipped: без реальных чисел |
| 4 | Три этапа обучения, схемы «Recap of last episode» | повтор прошлой лекции | — | skipped: повтор, есть в лекции 3 |
| 4 | Агент и среда, RL для LLM | соответствие понятий RL и LLM, цикл обучения | lec04-rl-loop.png | own |
| 4 | Четыре метода и их слабые места (по слайдам про проблемы и итоги) | карта лекции | lec04-roadmap.png | own |
| 4 | PPO против GRPO: схема моделей | какие модели участвуют, откуда преимущество | lec04-ppo-grpo.png | redrawn |
| 4 | GRPO credit system, On-policy distillation (пример про Teddy) | один итог на все токены против сигнала на токен | lec04-opd-credit.png | redrawn |
| 4 | Графики обрезки: цель от ρ при A>0 и A<0, рост длины ответа | поведение обрезки и длины | — | skipped: показано таблицей скрипта lec04_ppo_clip.py и числами в тексте |
| 4 | Формулы градиента политики, PPO, GRPO, KL, DPO | математика | — | skipped: формулы записаны текстом в блоках `text` |
| 5 | Оглавление лекции, два вопроса: «вместить» и «ускорить» | Карта лекции | lec05-map.png | own |
| 5 | Серия слайдов «Standard self-attention computation» и «Flash Attention in action» | Обычное внимание пишет S и P в HBM, FlashAttention считает блоками в SRAM | lec05-flash.png | redrawn |
| 5 | Слайды про DP, TP, PP, CP, EP | Пять видов параллелизма | lec05-parallelism.png | redrawn |
| 5 | Слайды «Speculative decoding» | Черновик, проверка, принять или отклонить | lec05-speculative.png | redrawn |
| 5 | Datasheet H200, схема GPU | HBM, SRAM, вычислительные блоки | lec05-flash.png (в тексте) | skipped: порядки величин даны в таблице |
| 5 | График roofline | Память против вычислений | — | skipped: считаем таблицей в `lec05_roofline.py` |
| 5 | Слайды про MHA, GQA, MQA, MLA | Сколько key и value хранить | — | skipped: считаем размер в `lec05_kvcache.py` |
| 6 | Нет (наш рисунок) | Карта лекции: ограничения LLM и что добавляют | lec06-map.png | own |
| 6 | Схема RAG из Super Study Guide, шаги Retrieve, Augment, Generate | База знаний, два шага поиска, ответ | lec06-rag.png | redrawn |
| 6 | Слайды про вызов инструмента (find teddy bear) | Три этапа вызова инструмента | lec06-tools.png | redrawn |
| 6 | Слайд цикла ReAct | Observe, plan, act, повтор | lec06-react.png | redrawn |
| 6 | График needle in a haystack | Качество падает на длинном входе | - | skipped: описан словами, цифр на слайде нет |
| 6 | Скриншоты model card, цены кэша | Цены токенов | - | skipped: скриншоты, цифры в тексте |
| 6 | Схема bi-encoder и cross-encoder | Раздельное и общее кодирование | - | skipped: идея в тексте и на диаграмме RAG |
| 7 | Setup, Challenges, Thought experiment | Пять способов оценки и их слабые места | lec07-map.png | own |
| 7 | Overview of LLM-as-a-Judge, Tune LLM-as-a-Judge | Вызов судьи и цикл настройки промпта | lec07-judge.png | redrawn |
| 7 | Failure modes (три шага цикла) | Что ломается на каждом шаге агента | lec07-agent.png | redrawn |
| 7 | Pareto frontier | Граница по качеству и цене | lec07-pareto.png | redrawn |
| 7 | Cohen's kappa, pass@k (формулы) | Формулы | текст страницы | skipped: формулы даны в тексте |
| 7 | Position, verbosity, self-enhancement bias | Три смещения судьи | таблица в тексте | skipped: таблица понятнее |
| 7 | Methodology (веса индекса Artificial Analysis) | Четыре области по 25% | таблица в тексте | skipped: таблица понятнее |
| 7 | MaxxBench, график METR, скриншоты, твиты | Результаты | текст страницы | skipped: скриншоты без идеи |

## Лекция 1

| Лекция | Что на слайде | Идея | Наш файл | Статус |
|---|---|---|---|---|
| 1 | Таймлайн: NLP до 2017, статья 2017, ChatGPT, агенты | Путь к трансформеру | lec01-roadmap.png (own: шаги представления токенов и их проблемы) | own |
| 1 | Слайды Tokenization: слова, символы, подслова | Три способа разбить текст | таблица в тексте | skipped: таблица понятнее |
| 1 | Слайды Word2vec: сеть V - d - V | Прокси-задача | описано шагами в тексте | skipped: числа даны в тексте |
| 1 | Слайды RNN | Hidden state | описано в тексте | skipped: деталей мало |
| 1 | Q, K, V и формула | Self-attention | lec01-qkv.png | redrawn |
| 1 | Архитектура трансформера из статьи | Энкодер, декодер, цикл генерации | lec01-transformer.png | redrawn |
| 1 | Контакты, логистика, обзор курса | — | — | skipped: логистика |
