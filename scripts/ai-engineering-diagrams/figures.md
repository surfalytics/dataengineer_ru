# Рисунки книги AI Engineering и наши схемы

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Исходные картинки из EPUB — в нашем репозитории нет (авторские права). Схемы собирает `chNN_diagrams.py` через `excb.py`.

## Обзор

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| — | Карта книги: 10 глав в четырёх блоках | `ch00-book-map.png` | наша схема (`ch00_diagrams.py`) |

## Глава 1

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Исходные картинки из EPUB в репозитории нет (авторские права). Схемы собирает `ch01_diagrams.py` через `excb.py`.
В книге 16 рисунков: 14 redrawn, 2 merged, 0 skipped. Наших собственных схем: 9.
Для графиков с данными значения прочитаны с графиков книги и округлены. Это сказано в тексте страницы.

### Рисунки книги

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 1-1 | GPT-4 режет фразу на 9 токенов (can't = can + 't) | `ch01-tokenization.png` | redrawn (скриншот токенизатора заменён блоками) |
| 1-2 | Autoregressive и masked языковые модели | `ch01-lm-types.png` | redrawn (пример фразы наш) |
| 1-3 | Multimodal модель выбирает следующий токен по токенам текста и картинки | `ch01-multimodal-next-token.png` | redrawn (пример наш: кот) |
| 1-4 | Типы задач benchmark Super-NaturalInstructions | `ch01-task-map.png` | redrawn (качественно: размер овала примерный) |
| 1-5 | Число компаний S&P 500, упомянувших AI в отчётах | `ch01-sp500-ai-mentions.png` | redrawn (значения подписаны на графике книги) |
| 1-6 | Звёзды GitHub: AI-инструменты против React, Vue, bitcoin | `ch01-github-stars.png` | redrawn (линии заменены столбцами конечных значений, примерно) |
| 1-7 | Доли восьми групп сценариев среди 205 приложений | `ch01-use-case-share.png` | redrawn (круговая диаграмма заменена столбцами, значения подписаны) |
| 1-8 | Доля компаний, которые вывели сценарий в production: внутренние выше внешних | `ch01-enterprise-willingness.png` | redrawn (значения подписаны) |
| 1-9 | McKinsey: сокращение времени задачи у разработчика | `ch01-coding-time-saved.png` | redrawn (диапазоны подписаны) |
| 1-10 | Duolingo: доля работы человека и AI на четырёх этапах | `ch01-duolingo-stages.png` | redrawn (длины столбцов прочитаны с рисунка) |
| 1-11 | MMLU и цена за миллион токенов, 2022–2024 | `ch01-mmlu-cost.png` | redrawn (12 из ~30 точек, координаты примерные, шкала цены логарифмическая) |
| 1-12 | Вакансии LinkedIn: ML engineer, Generative AI (скриншот) | `ch01-job-titles.png` | merged с 1-13 (скриншоты чужих вакансий заменены шаблоном «две модели») |
| 1-13 | Вакансии LinkedIn: отдельная роль AI engineer (скриншот) | `ch01-job-titles.png` | merged с 1-12 |
| 1-14 | Три слоя AI-стека и задачи слоёв | `ch01-ai-engineering-stack.png` | redrawn (файл с этим именем был в старой версии страницы, перезаписан) |
| 1-15 | Накопленное число AI-репозиториев по слоям (площадной график) | `ch01-repos-by-layer.png` | redrawn (4 момента времени: 2020, 2022, 2023, 2024; значения примерные) |
| 1-16 | Порядок работы: ML engineering (data, model, product), AI engineering (product, data, model) | `ch01-workflow-order.png` | redrawn |

### Наши схемы

| Идея | Наш файл |
|---|---|
| Главная схема главы: путь от языковой модели к AI engineering | `ch01-chapter-map.png` |
| Supervised и self-supervised обучение | `ch01-self-supervision.png` |
| Prompt engineering, RAG, finetuning: меняются ли веса | `ch01-adaptation-techniques.png` |
| Три оси AI-функции (критичная, проактивная, динамичная) | `ch01-product-dimensions.png` |
| Crawl-Walk-Run и пример бота поддержки | `ch01-crawl-walk-run.png` |
| Три «рва» AI-продукта | `ch01-moats.png` |
| Семь вопросов планирования | `ch01-planning-path.png` |
| Last mile: пример LinkedIn | `ch01-last-mile.png` |
| Training, pre-training, finetuning, post-training | `ch01-training-terms.png` |

## Глава 2

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Схемы собирает `ch02_diagrams.py` через `excb.py`. Значения для графиков прочитаны с графиков книги и округлены (это сказано в тексте страницы).

### Рисунки книги

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 2-1 | GPT-4 на MMLU по языкам: английский выше всех, телугу, маратхи, панджаби ниже | `ch02-lang-mmlu.png` | redrawn (11 языков и случайный выбор) |
| 2-2 | GPT-4 решает задачи Project Euler на разных языках, на бирманском и амхарском 0 | `ch02-lang-math.png` | redrawn (11 языков) |
| 2-3 | Темы сайтов в C4 (Washington Post) | `ch02-c4-domains.png` | redrawn (круговая диаграмма стала полосами) |
| 2-4 | Seq2seq (одно скрытое состояние) и transformer (attention) | `ch02-seq2seq-vs-transformer.png` | redrawn |
| 2-5 | Attention в действии (query, key, value) и конвейер MatMul, Scale, Mask, Softmax, MatMul из статьи Vaswani | `ch02-attention-qkv.png`, `ch02-attention-steps.png` | redrawn (две панели рисунка стали двумя схемами; пример перевода другой) |
| 2-6 | Из каких матриц состоит transformer и их размеры | `ch02-transformer-weights.png` | redrawn |
| 2-7 | Слои transformer, Mamba и блок Jamba | `ch02-architectures.png` | redrawn |
| 2-8 | Chinchilla: кривые потерь, оптимум параметров и токенов по FLOPs | `ch02-scaling-chinchilla.png` | redrawn как схема (три графика в логарифмической шкале пересказаны одним минимумом и цепочкой выводов; числа 63B и 1,4T взяты с графика) |
| 2-9 | Рост датасетов для обучения и запас данных в интернете | `ch02-data-stock.png` | redrawn (столбцы по годам, высота по логарифму) |
| 2-10 | Процесс: pre-training, SFT, RLHF | `ch02-model-training-stages.png` | redrawn |
| 2-11 | Мем: Шоггот со смайликом | `ch02-shoggoth.png` | redrawn как три простых блока (рисунок мема не копируем) |
| 2-12 | Типы запросов InstructGPT | `ch02-instructgpt-prompts.png` | redrawn (кольцевая диаграмма стала полосами) |
| 2-13 | Интерфейс разметчиков OpenAI: баллы 1–7, ранжирование | `ch02-labeler-flow.png` | redrawn как схема потока (скриншот не копируем) |
| 2-14 | Распределение вероятностей по словарю | `ch02-logits-probs.png` | merged с 2-15 |
| 2-15 | Вектор logits по словарю | `ch02-logits-probs.png` | redrawn (наши токены и числа) |
| 2-16 | Вероятности A и B при разных temperature | `ch02-temperature.png` | redrawn (кривая стала парами столбцов, значения посчитаны) |
| 2-17 | Logits, вероятности, logprobs | `ch02-logits-softmax-logprobs.png` | redrawn |
| 2-18 | Пример top-p | `ch02-top-p-example.png` | redrawn (с накопленными вероятностями) |
| 2-19 | Доля решённых задач при разном числе ответов (OpenAI) | `ch02-verifier-samples.png` | redrawn (точки кривой прочитаны с графика) |
| 2-20 | Скриншот guidance: выбор из списка и regex | `ch02-guidance-examples.png` | redrawn как схема с нашими примерами |
| 2-21 | Constrained sampling: фильтр logits | `ch02-constrained-sampling.png` | redrawn |
| 2-22 | Голова классификации поверх базовой модели | `ch02-classifier-head.png` | redrawn |
| 2-23 | Один prompt, две оценки эссе: 3/5 и 5/5 | `ch02-inconsistency.png` | redrawn (prompt пересказан по-русски) |
| 2-24 | Скриншот: LLaVA принимает шампунь за молоко | `ch02-snowballing.png` | redrawn как схема (пример 1; фото не копируем) |
| 2-25 | Snowballing: «9677 не простое» и выдуманное разложение | `ch02-snowballing.png` | redrawn (пример 2; тот же файл, что 2-24) |
| 2-26 | Метрики InstructGPT: токсичность, правдивость, галлюцинации, уместность | `ch02-instructgpt-quality.png` | redrawn |

Таблицы 2-1 и 2-2 (языки Common Crawl) стали графиком `ch02-cc-languages.png`. Таблицы 2-3 (CLIP), 2-4 (размерности Llama), 2-5 (токены обучения), 2-6 (примеры demonstration data) пересобраны в нашем виде прямо на странице. Таблица 2-7 пересказана текстом.

### Наши схемы (в книге таких нет)

| Идея | Наш файл |
|---|---|
| Главная карта: четыре решения и что видно в приложении | `ch02-chapter-map.png` |
| Языки Common Crawl: доля и недопредставленность (из таблиц 2-1, 2-2) | `ch02-cc-languages.png` |
| Число токенов на один текст: английский, хинди, бирманский (числа из текста) | `ch02-token-cost.png` |
| Multi-head attention: 4096 в 32 головы по 128 | `ch02-multihead.png` |
| Prefill, decode и KV cache | `ch02-prefill-decode.png` |
| Альтернативы transformer: RWKV и цепочка SSM | `ch02-ssm-family.png` |
| Mixture of Experts: router и два эксперта из восьми | `ch02-moe.png` |
| Расчёт стоимости обучения GPT-3 | `ch02-training-cost.png` |
| Pre-training и post-training: токен против ответа, 98% и 2% вычислений | `ch02-pre-vs-post.png` |
| Как считается loss reward model | `ch02-bradley-terry-loss.png` |
| Конвейер выбора токена: temperature, top-k, softmax, top-p | `ch02-sampling.png` |
| Best of N: несколько ответов и выбор лучшего | `ch02-best-of-n.png` |
| Пять способов получить формат: от prompt до finetuning | `ch02-structured-ladder.png` |
| Две гипотезы галлюцинаций и что помогает | `ch02-hallucination-hypotheses.png` |

Итого: рисунков в книге 26. Перерисовано 25, объединено 1 (2-14 вошёл в схему 2-15), пропущено 0. Наших схем 14. Всего файлов 39 (2-24 и 2-25 в одном файле, 2-5 в двух).

## Глава 3

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 3-1 | Рост числа статей об оценке LLM по месяцам | `ch03-eval-growth.png` | redrawn (значения прочитаны с графика) |
| 3-2 | Накопительное число open-source репозиториев по оценке | `ch03-eval-growth.png` | redrawn (панель справа) |
| 3-3 | Число репозиториев по темам: оценки меньше всего | `ch03-eval-tools-gap.png` | redrawn |
| 3-4 | Два языка с 2 и 4 токенами: entropy 1 и 2 | `ch03-entropy-squares.png` | redrawn |
| 3-5 | Верная подпись Fuyu получила низкий CIDEr | `ch03-fuyu-low-score.png` | redrawn вместо скриншота с фото |
| 3-6 | Архитектура CLIP | `ch03-clip.png` | redrawn |
| 3-7 | Скриншот: GPT-4 объясняет вердикт судьи | `ch03-ai-judge.png` | merged (выход «оценка + объяснение») |
| 3-8 | AI judge: шаблон промпта, модель, оценка | `ch03-ai-judge.png` | redrawn |
| 3-9 | PandaLM: два ответа и объяснённый вердикт | `ch03-pandalm.png` | redrawn (пример пересказан по-русски) |
| 3-10 | Скриншот ChatGPT: сравнить два ответа | `ch03-side-by-side-ui.png` | redrawn как схема интерфейса |
| — | Карта методов оценки | `ch03-evaluation-methods.png` | наша схема |
| — | Связь cross entropy, perplexity, BPC, BPB | `ch03-lm-metrics-relations.png` | наша схема |
| — | Что влияет на perplexity и для чего она | `ch03-perplexity-uses.png` | наша схема |
| — | Как считают pass@k | `ch03-pass-at-k.png` | наша схема |
| — | Три режима AI-судьи | `ch03-judge-modes.png` | наша схема |
| — | Три смещения судьи | `ch03-judge-biases.png` | наша схема |
| — | Три вида специализированных судей | `ch03-specialized-judges.png` | наша схема |
| — | Pointwise и comparative | `ch03-comparative-flow.png` | наша схема |

## Глава 4

В книге 10 рисунков и 7 таблиц. Все рисунки перерисованы. Диаграммы строит `ch04_diagrams.py` (модуль `excb.py`), файлы лежат в `public/assets/ai-engineering/`.

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 4-1 | SAFE: ответ делят на утверждения, делают самодостаточными, проверяют релевантность и поиском | `ch04-safe.png` | redrawn (свой пример про Python) |
| 4-2 | TruthfulQA: точность моделей, эксперты-люди 94% | `ch04-truthfulqa.png` | redrawn (столбцы, значения прочитаны с графика) |
| 4-3 | Политический компас моделей (левый/правый, авторитарный/либертарный) | `ch04-political-compass.png` | redrawn (четыре квадранта и только две модели, о которых говорит текст: на рисунке книги около 20 точек, их положение нельзя прочитать надёжно) |
| 4-4 | 10 крупнейших групп запросов в 1 млн разговоров LMSYS, ролевые игры на 8 месте | `ch04-lmsys-uses.png` | redrawn (столбцы, названия переведены и сокращены) |
| 4-5 | Workflow выбора модели: hard attributes, публичные benchmarks, свой eval, мониторинг | `ch04-selection-workflow.png` | redrawn |
| 4-6 | Inference service: модель за API | `ch04-inference-service.png` | redrawn |
| 4-7 | MMLU: разрыв между закрытыми и открытыми моделями | `ch04-open-vs-closed-mmlu.png` | redrawn (только лучшие модели на дату, не все точки) |
| 4-8 | a16z 2024: почему выбирают open source (контроль, настройка, цена) | `ch04-why-open.png` | redrawn (два столбца 100%) |
| 4-9 | GPT-3.5 и GPT-4, март и июнь 2023, четыре задачи | `ch04-gpt-drift.png` | redrawn (столбцы по четырём задачам рисунка) |
| 4-10 | GPT-3: разница score на чистых примерах и на всём benchmark (таблица на рисунке) | `ch04-contamination-gpt3.png` | redrawn (диаграмма относительной разницы по 13 benchmarks, подписана доля чистых примеров) |

Таблицы книги (не рисунки):

| Таблица | Что с ней сделано |
|---|---|
| 4-1 примеры TruthfulQA | Пересказаны словами в тексте (мифы про кашель, хруст пальцев, потепление, законы робототехники) |
| 4-2 инструкции IFEval | Сведены в свою таблицу по группам |
| 4-3 критерии выбора модели | Своя таблица для SQL-ассистента с нашими числами |
| 4-4 плюсы и минусы API и self-hosting | Своя схема `ch04-build-vs-buy.png` |
| 4-5 корреляции benchmarks | Пересказаны главные значения словами, матрица не копируется |
| 4-6 парадокс Симпсона | Свои числа (простые и сложные запросы), таблица и `ch04-simpson.png`, плюс SQL |
| 4-7 размер выборки OpenAI | Своя таблица и расчёт в `ch04_bootstrap_sample_size.py` |

Наши собственные диаграммы (в книге их нет):

| Идея | Наш файл | Статус |
|---|---|---|
| Главная карта главы: критерии, выбор модели, pipeline | `ch04-chapter-map.png` | own |
| Textual entailment: три исхода | `ch04-entailment.png` | own |
| IFEval и INFOBench: два способа проверить инструкцию | `ch04-instruction-following.png` | own |
| Model API и self-hosting по семи осям | `ch04-build-vs-buy.png` | own |
| Как загрязняются benchmarks и как это находят | `ch04-contamination-flow.png` | own |
| Оценка по компонентам: PDF в текст, текст в работодателя | `ch04-component-eval.png` | own |
| Несколько evaluation sets | `ch04-eval-sets.png` | own |
| Парадокс Симпсона на своих числах | `ch04-simpson.png` | own |
| Bootstrap: выборки с возвратом | `ch04-bootstrap.png` | own |
| Шаги evaluation pipeline (заменил старый файл с этим именем) | `ch04-evaluation-pipeline.png` | own |

## Глава 5

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Исходные картинки из EPUB в репозитории нет (авторские права). Схемы собирает `ch05_diagrams.py` через `excb.py`.
В книге 16 рисунков и 4 таблицы. Таблицы 5-1, 5-2, 5-3 и 5-4 пересказаны таблицами и кодом на странице.

### Рисунки книги

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 5-1 | Три части простого prompt для NER: описание задачи, пример, сама задача | `ch05-prompt-anatomy.png` | redrawn (пример заменён на русский) |
| 5-2 | Рост максимальной длины контекста с 1K до 2M токенов | `ch05-context-length.png` | redrawn (значения прочитаны с графика, шкала логарифмическая) |
| 5-3 | Пример prompt для теста NIAH: JSON с ключами и значениями | `ch05-niah.png` | redrawn (свои данные) |
| 5-4 | Точность по позиции документа с ответом: края лучше середины | `ch05-niah-results.png` | redrawn (две модели из шести, панель с 20 документами, значения прочитаны) |
| 5-5 | Скриншот: без роли оценка 2, с ролью учителя 4 | `ch05-persona.png` | redrawn как схема (пример по-русски) |
| 5-6 | CoT повышает долю решённых задач у больших моделей | `ch05-cot-gain.png` | redrawn (самая большая модель каждого семейства, значения прочитаны) |
| 5-7 | Скриншот: Claude пишет prompt для оценки эссе | `ch05-ai-writes-prompt.png` | redrawn как схема |
| 5-8 | Promptbreeder: мутации и отбор | `ch05-promptbreeder.png` | redrawn (пример мутации свой) |
| 5-9 | Опечатки в стандартном prompt LangChain | `ch05-tool-typos.png` | redrawn (две правки показаны текстом) |
| 5-10 | Модель косвенно выдаёт город пользователя | `ch05-context-leak.png` | redrawn (диалог по-русски) |
| 5-11 | PAIR: атакующая AI и целевая AI | `ch05-pair.png` | redrawn (тема примера заменена на нейтральную) |
| 5-12 | Indirect prompt injection через данные и инструменты | `ch05-indirect-injection.png` | redrawn |
| 5-13 | Атака повтором слова: модель выдаёт куски обучающих данных | `ch05-divergence-attack.png` | redrawn (выдуманные персональные данные не воспроизводим) |
| 5-14 | Почти-копии картинок из обучения Stable Diffusion | `ch05-diffusion-memorization.png` | redrawn как схема идеи (реальные фото и логотипы не показываем) |
| 5-15 | Скриншот: ложный отказ на запрос заполнить пропуск | `ch05-false-refusal.png` | redrawn как схема диалога |
| 5-16 | Иерархия инструкций: system, user, вывод модели, вывод tool | `ch05-instruction-hierarchy.png` | redrawn (пример по-русски) |

### Наши схемы

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| — | Карта главы: основы, приёмы, инструменты, защита (главная схема) | `ch05-chapter-map.png` | наша схема |
| — | Как system и user prompt склеиваются через chat template | `ch05-chat-template.png` | наша схема |
| — | Цепочка prompts для бота поддержки: плюсы и минусы | `ch05-prompt-chain.png` | наша схема |
| — | Prompt в Git и prompt catalog с закреплёнными версиями | `ch05-prompt-catalog.png` | наша схема |
| — | Три типа атак, цели и риски | `ch05-attack-map.png` | наша схема |
| — | Карта приёмов jailbreak: ручные, автоматические, через данные | `ch05-jailbreak-map.png` | наша схема |
| — | Три уровня защиты: модель, prompt, система | `ch05-defense-layers.png` | наша схема |
| — | Исходы запроса и формулы violation rate и false refusal rate | `ch05-violation-refusal.png` | наша схема |
| — | Защищённая система: фильтры, модель, проверка опасного SQL | `ch05-protected-pipeline.png` | наша схема |

## Глава 6

Исходник диаграмм: `scripts/ai-engineering-diagrams/ch06_diagrams.py` (модуль `excb.py`). Сборка: `python3 scripts/ai-engineering-diagrams/ch06_diagrams.py [имя ...]`.
Картинки: `public/assets/ai-engineering/<имя>.png`.

В книге 16 рисунков: 16 перерисованы, 0 объединены, 0 пропущены. Свои схемы: 9.

### Рисунки книги

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 6-1 | Схема «найти, потом прочитать»: retriever выбирает 5 страниц Wikipedia, reader отвечает | `ch06-retrieve-then-read.png` | redrawn |
| 6-2 | Базовая архитектура RAG: пользователь, retriever, внешняя память, generative model | `ch06-rag-architecture.png` | redrawn |
| 6-3 | Embedding-based retriever: индексация (splitter, embedding model, vector DB) и запрос | `ch06-rag-pipeline.png` | redrawn |
| 6-4 | Query rewriting: скриншот чата, где модель переписывает реплику «А Эмили Доу?» | `ch06-query-rewrite.png` | redrawn (схема вместо скриншота, примеры по-русски) |
| 6-5 | Contextual retrieval по Anthropic: контекст к chunk, два индекса | `ch06-contextual-retrieval.png` | redrawn |
| 6-6 | Мультимодальный RAG: база текстов, база картинок, retriever, модель | `ch06-multimodal-rag.png` | redrawn (картинку из мультфильма не рисуем, как и книга) |
| 6-7 | RAG с таблицей: text-to-SQL, выполнение SQL, generative model | `ch06-text-to-sql-rag.png` | redrawn |
| 6-8 | SWE-agent: LM agent, интерфейс «агент–компьютер», среда | `ch06-swe-agent.png` | redrawn |
| 6-9 | Разделение планирования и выполнения: Planner, Evaluator, Executor, Tools | `ch06-agent-loop.png` | redrawn |
| 6-10 | Function calling: скриншот кода (описание tools, запрос с tool_choice) | `ch06-function-calling.png` | redrawn (пошаговая схема вместо кода, пример «фунты в кг») |
| 6-11 | Четыре вида control flow: sequential, parallel, if, for loop | `ch06-control-flows.png` | redrawn |
| 6-12 | ReAct на примере HotpotQA: Thought, Act, Observation | `ch06-react-example.png` | redrawn (свой пример: поиск владельца таблицы) |
| 6-13 | Reflexion: задача, trajectory, evaluation, reflection, next trajectory; два примера | `ch06-reflexion.png` | redrawn (один пример с кодом; пример про кухню описан в тексте) |
| 6-14 | Распределение вызовов tools у ChatGPT и GPT-4 в Chameleon (график) | `ch06-tool-usage.png` | redrawn (значения прочитаны с графика и округлены) |
| 6-15 | Граф переходов между tools Chameleon (вероятности) | `ch06-tool-transitions.png` | redrawn (переходы с вероятностью ниже 0,05 не нарисованы; об этом сказано на схеме) |
| 6-16 | Иерархия памяти: internal knowledge, short-term, long-term | `ch06-memory-hierarchy.png` | redrawn |

### Наши схемы

| Идея | Наш файл | Где на странице |
|---|---|---|
| Главная карта главы: RAG, агенты, память | `ch06-rag-agents-map.png` | после «О чём глава» |
| Сравнение term-based и embedding-based поиска | `ch06-term-vs-embedding.png` | раздел сравнения |
| Context precision и recall на примере | `ch06-retrieval-metrics.png` | оценка retrieval |
| Hybrid search: последовательно и параллельно (RRF) | `ch06-hybrid-search.png` | hybrid search |
| Chunking: overlap и размер chunk | `ch06-chunking.png` | chunking |
| Агент Kitty Vogue: цепочка рассуждений и вызовов | `ch06-agent-example.png` | что такое агент |
| Накопление ошибок: 0,95 в степени числа шагов | `ch06-compound-errors.png` | что такое агент |
| Группы сбоев агента и что измерять | `ch06-agent-failures.png` | сбои агента |
| Бюджет контекста: short-term и long-term | `ch06-memory-budget.png` | память |

## Глава 7

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Исходные картинки из EPUB — в репозитории нет (авторские права). Схемы собирает `ch07_diagrams.py` через `excb.py`.
Таблицы 7-1 … 7-7 книги не копируем: в тексте страницы они пересказаны в нашей форме (числа 7-3 посчитаны нашим скриптом).

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 7-1 | Как из Llama 2 получили Code Llama, Instruct и Python разными видами finetuning | `ch07-code-llama.png` | redrawn |
| 7-2 | Prompt с примерами в каждом запросе против finetuning на примерах | `ch07-prompt-vs-finetune.png` | redrawn |
| 7-3 | Путь адаптации: prompt, примеры, простой retrieval, затем сложный retrieval или finetuning | `ch07-adaptation-path.png` | redrawn (квадранты заменены двумя зонами) |
| 7-4 | Forward и backward pass: parameters, activations, loss, gradients | `ch07-forward-backward.png` | redrawn (одна ветка вместо трёх параллельных) |
| 7-5 | Память activations против памяти весов для моделей 22B–1T | `ch07-activation-memory.png` | redrawn (значения прочитаны с графика, округлены) |
| 7-6 | Форматы FP32, FP16, BF16, TF32: биты знака, range, precision | `ch07-number-formats.png` | redrawn |
| 7-7 | Partial finetuning против адаптеров: падение точности при разном числе trainable-параметров | `ch07-partial-vs-adapters.png` | redrawn (линейный график с лог-осью заменён столбцами, значения прочитаны) |
| 7-8 | Адаптеры Houlsby в блоке Transformer | `ch07-adapter-houlsby.png` | redrawn (упрощено до двух адаптеров и их внутренностей) |
| 7-9 | Hard prompt и soft prompt вместе | `ch07-soft-prompt.png` | redrawn |
| 7-10 | Число issues по методам PEFT в huggingface/peft | `ch07-peft-issues.png` | redrawn (значения прочитаны с графика) |
| 7-11 | LoRA: W, A, B и W' | `ch07-lora.png` | redrawn |
| 7-12 | Multi-LoRA serving: одна W и много адаптеров | `ch07-multi-lora.png` | redrawn (числа примера из текста книги) |
| 7-13 | Ensembling и model merging | `ch07-ensemble-vs-merge.png` | redrawn |
| 7-14 | Три подхода к слиянию: summing, layer stacking, concatenation | `ch07-merge-approaches.png` | redrawn |
| 7-15 | Слияние усреднением параметров | `ch07-merge-average.png` | redrawn (наши числа вместо чисел книги) |
| 7-16 | SLERP на сфере | `ch07-slerp.png` | redrawn (дуга из точек) |
| 7-17 | Качество при сохранении top-K% параметров task vector | `ch07-task-vector-pruning.png` | redrawn (значения прочитаны, ось от 50) |
| 7-18 | Sparse upcycling: из dense-блока в блок MoE | `ch07-moe-upcycling.png` | redrawn (без residual-связей) |
| 7-19 | Depthwise scaling: 32 слоя в 48 слоёв | `ch07-depth-scaling.png` | redrawn |
| 7-20 | Конкатенация двух адаптеров LoRA, ранг r1 + r2 | `ch07-lora-concat.png` | redrawn |
| — | Карта главы (главная схема) | `ch07-finetuning-map.png` | наша схема |
| — | Дерево решений: eval и prompt, затем тип ошибок | `ch07-finetune-or-not.png` | наша схема (перезаписан старый файл с той же идеей) |
| — | Память для модели 7B: полный finetuning, SGD, LoRA, QLoRA | `ch07-memory-breakdown.png` | наша схема (числа из `ch07_memory_calculator.py`) |
| — | Карта quantization: что, когда, пределы | `ch07-quantization-map.png` | наша схема |
| — | Дерево методов PEFT | `ch07-peft-map.png` | наша схема |
| — | Task vectors: сумма, среднее, вычитание | `ch07-task-vectors.png` | наша схема |
| — | Пути выбора базовой модели: progression и distillation | `ch07-tactics-paths.png` | наша схема (по тексту книги, рисунка в книге нет) |
| — | Шпаргалка: что видно на кривых loss и что делать | `ch07-loss-curves-guide.png` | наша схема |

Итого: 20 рисунков в книге, 20 redrawn, 0 merged, 0 skipped; 8 наших схем.

## Глава 8

Статус: `redrawn` — перерисован по-нашему; `merged`; `skipped: причина`. Схемы собирает `ch08_diagrams.py` через `excb.py`.
Значения для графиков прочитаны с рисунков книги и округлены.

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 8-1 | Качество 7B модели на трёх датасетах по 2000 примеров: качественный, разнообразный, оба | `ch08-quality-diversity.png` | redrawn (3,49 / 3,33 / 3,83) |
| 8-2 | SNLI после finetuning: на 100 примерах сильные модели впереди, на 550 000 все рядом | `ch08-snli-accuracy.png` | redrawn |
| 8-3 | Кривая «качество от объёма»: крутой участок и плато | `ch08-perf-vs-size.png` | redrawn на наших числах из `ch08_quality_quantity.py` |
| 8-4 | Число задач finetuning (0 – 1836) для моделей 8B, 62B, 540B | `ch08-task-diversity.png` | redrawn |
| 8-5 | Seed-задача и сгенерированная задача (Alpaca) | `ch08-alpaca-seed.png` | redrawn (тексты примеров наши) |
| 8-6 | Частые пары (глагол, существительное) у GPT-3 и GPT-4 | `ch08-verb-noun.png` | redrawn (верхние 8 пар из 25) |
| 8-7 | Распределение длины ответов GPT-3 и GPT-4 | `ch08-length-dist.png` | redrawn (логарифмическая шкала, значения приблизительные) |
| Table 8-1 | Смесь доменов Llama 3 на трёх этапах | `ch08-llama3-mix.png` | redrawn как полосы |
| Table 8-2, 8-3, 8-4 | Counterfactual, дубликаты, формат Items | в тексте страницы | rebuilt as our own tables (примеры наши) |
| — | Карта главы: curation, сбор, синтез, четыре шага обработки | `ch08-dataset-engineering.png` | наша схема |
| — | Шесть свойств качественных данных и нарушения | `ch08-quality-traits.png` | наша схема |
| — | Воронка сборки датасета (пример из книги) | `ch08-curation-funnel.png` | наша схема |
| — | Карта способов синтеза: rules, simulation, AI | `ch08-synthesis-methods.png` | наша схема |
| — | Пайплайн Llama 3 для синтетических данных по коду | `ch08-llama3-code-pipeline.png` | наша схема |
| — | Reverse instruction и расширение контекста | `ch08-bootstrap-loops.png` | наша схема |
| — | Model collapse: число выживших событий в игрушечной модели | `ch08-model-collapse.png` | наша схема (числа из `ch08_model_collapse.py`) |
| — | Distillation и student сильнее teacher | `ch08-distillation.png` | наша схема |
| — | Три способа дедупликации | `ch08-dedup-methods.png` | наша схема (числа из `ch08_dedup.py`) |
| — | Слои raw / cleaned / final и три совета по порядку шагов | `ch08-processing-order.png` | наша схема |
| — | Формат обучения и четыре prompt на inference | `ch08-format-mismatch.png` | наша схема |

Примечание: старый файл `public/assets/ai-engineering/ch08-dataset-pipeline.png` (из прошлой версии страницы) больше не используется.

## Глава 9

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Исходные картинки из EPUB в репозитории нет (авторские права). Схемы собирает `ch09_diagrams.py` через `excb.py`.
Итого: 19 рисунков книги (19 redrawn, 0 merged, 0 skipped) и 6 наших схем.

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 9-1 | Простой inference service: приложения, inference server с моделями, железо | `ch09-inference-service.png` | redrawn |
| 9-2 | Roofline: memory-bound и compute-bound зоны | `ch09-roofline.png` | redrawn (схема без масштаба, добавлены точки decode и prefill) |
| 9-3 | Два шага inference: prefill и decode | `ch09-inference-phases.png` | redrawn (пример на русском, старый файл заменён) |
| 9-4 | Goodput: запросы, которые уложились в SLO | `ch09-goodput.png` | redrawn (свои 10 запросов, честный подсчёт 3 из 10: в рисунке книги по значениям выходит 2) |
| 9-5 | MBU падает с ростом числа пользователей (Llama 2-70B) | `ch09-mbu-users.png` | redrawn (значения прочитаны с графика и округлены) |
| 9-6 | Вычислительные примитивы: scalar, vector, tensor | `ch09-compute-primitives.png` | redrawn |
| 9-7 | Иерархия памяти ускорителя: SRAM, HBM, CPU DRAM | `ch09-memory-hierarchy.png` | redrawn (пирамида заменена тремя ступенями) |
| 9-8 | Одна модель у разных провайдеров inference: качество чуть различается | `ch09-provider-quality.png` | redrawn (значения прочитаны с графика и округлены, ось с 20) |
| 9-9 | Speculative decoding: предложить, проверить, принять | `ch09-speculative-decoding.png` | redrawn (русский пример вместо английского) |
| 9-10 | Inference with reference: два примера копирования из входа | `ch09-inference-with-reference.png` | redrawn (скриншот статьи заменён схемой с русскими примерами) |
| 9-11 | Medusa: головы предсказывают токены вперёд, дерево кандидатов | `ch09-medusa.png` | redrawn (русский пример) |
| 9-12 | KV cache: K и V прошлых токенов лежат в кэше | `ch09-kv-cache.png` | redrawn (вместо перевода «How are you» общий пример генерации) |
| 9-13 | FlashAttention: слияние операций в один kernel | `ch09-flashattention.png` | redrawn (значения прочитаны с графика и округлены) |
| 9-14 | Кейс PyTorch: рост throughput Llama-7B | `ch09-pytorch-case.png` | redrawn (значения из графика книги) |
| 9-15 | Static и dynamic batching | `ch09-static-dynamic-batching.png` | redrawn |
| 9-16 | Обычный и continuous batching | `ch09-continuous-batching.png` | redrawn |
| 9-17 | Prompt cache: общее начало prompt берём из кэша | `ch09-prompt-cache.png` | redrawn (русский пример) |
| 9-18 | Tensor parallelism для умножения матриц | `ch09-tensor-parallelism.png` | redrawn |
| 9-19 | Pipeline parallelism на четырёх устройствах | `ch09-pipeline-parallelism.png` | redrawn (пустые клетки простоя выделены нами) |
| — | Карта оптимизации inference: уровни модели и сервиса, железо | `ch09-inference-map.png` | наша схема (главная) |
| — | Хронология запроса: TTFT, TPOT, формула latency | `ch09-latency-timeline.png` | наша схема |
| — | TTFT глазами пользователя: скрытые шаги агента | `ch09-user-ttft.png` | наша схема |
| — | Формула размера KV cache и пример Llama 2 13B | `ch09-kv-cache-size.png` | наша схема |
| — | Multi-head, grouped-query, multi-query, cross-layer attention | `ch09-attention-kv-sharing.png` | наша схема |
| — | Prefill и decode вместе и раздельно | `ch09-disaggregated-serving.png` | наша схема |

## Глава 10

Статус: `redrawn` — перерисован по-нашему; `merged` — идея вошла в другую схему; `skipped: причина`.
Исходные картинки из EPUB в репозитории нет (авторские права). Схемы собирает `ch10_diagrams.py` через `excb.py`.
В книге 21 рисунок: 19 перерисованы, 2 объединены, 0 пропущены. Наших схем 13.

### Рисунки книги

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| 10-1 | Простейшая архитектура: запрос, Model API, ответ | `ch10-arch-simple.png` | redrawn |
| 10-2 | Архитектура с блоком сбора контекста | `ch10-arch-context.png` | redrawn |
| 10-3 | Маскирование и демаскирование PII через reverse map | `ch10-pii-mask.png` | redrawn (пример по-русски) |
| 10-4 | Архитектура с input и output guardrails и scorers | `ch10-arch-guardrails.png` | redrawn |
| 10-5 | Архитектура с router в блоке Model API | `ch10-arch-router.png` | redrawn |
| 10-6 | Model gateway: приложения, единый API, провайдеры | `ch10-gateway-fan.png` | redrawn |
| 10-7 | Архитектура: gateway заменяет Model API | `ch10-arch-gateway.png` | redrawn |
| 10-8 | Архитектура с кэшами (кэш запросов и кэш поиска) | `ch10-arch-cache.png` | redrawn |
| 10-9 | Цикл агента: ответ возвращается в сбор контекста | `ch10-agent-loop.png` | redrawn как схема цикла с проверкой «задача решена?» |
| 10-10 | Итоговая архитектура с write actions | `ch10-architecture.png` | redrawn (главная схема главы, с номерами шагов, monitoring и orchestrator) |
| 10-11 | Скриншот LangSmith: trace запроса агента | `ch10-trace-tree.png` | redrawn как временная шкала шагов с придуманными числами |
| 10-12 | Скриншот ChatGPT: пользователь перефразирует запрос | `ch10-rephrase-example.png` | redrawn (другой пример) |
| 10-13 | Скриншот ChatGPT: «лучше, хуже, так же» после перегенерации | `ch10-regen-compare.png` | redrawn как схема процесса |
| 10-14 | Inpainting в DALL-E: правка выбранной области | `ch10-inpainting.png` | redrawn как схема процесса |
| 10-15 | Скриншот ChatGPT: два полных ответа рядом | `ch10-side-by-side.png` | redrawn (левая половина) |
| 10-16 | Скриншот Gemini: начала нескольких версий | `ch10-side-by-side.png` | merged (правая половина той же схемы) |
| 10-17 | Скриншот Google Photos: «тот же человек?» | `ch10-photo-uncertain.png` | redrawn как схема процесса |
| 10-18 | Скриншот Midjourney: U1-U4, V1-V4, заново | `ch10-midjourney.png` | redrawn как схема действий и сигналов |
| 10-19 | Скриншот GitHub Copilot: подсказка и Tab | `ch10-copilot.png` | redrawn как схема процесса |
| 10-20 | Скриншот ChatGPT: выбор между ответами на вопрос по статистике | `ch10-feedback-ui-traps.png` | redrawn (ловушка 1) |
| 10-21 | Скриншот Luma: сердитое эмодзи на месте пяти звёзд | `ch10-feedback-ui-traps.png` | merged (ловушка 2 той же схемы) |

Таблица 10-1 (группы жалоб из датасета FITS) пересказана таблицей в тексте страницы, а не рисунком.

### Наши схемы (нет в книге)

| Figure | Идея | Наш файл | Статус |
|---|---|---|---|
| — | Router разводит запросы по пяти путям | `ch10-router-intents.png` | наша схема |
| — | Output guardrails: сбои и политики | `ch10-output-guardrails.png` | наша схема |
| — | Как работает кэш: exact, semantic, запись | `ch10-cache-flow.png` | наша схема |
| — | Утечка данных через кэш и исправление | `ch10-cache-leak.png` | наша схема |
| — | Monitoring и observability | `ch10-monitoring-vs-observability.png` | наша схема |
| — | Метрики, логи, traces и разбор сбоя | `ch10-metrics-logs-traces.png` | наша схема |
| — | Три источника drift | `ch10-drift.png` | наша схема |
| — | Orchestrator: компоненты и chaining | `ch10-orchestrator.png` | наша схема |
| — | Явный и неявный feedback, зачем он нужен | `ch10-feedback-types.png` | наша схема |
| — | Карта сигналов диалога | `ch10-feedback-signals.png` | наша схема |
| — | Когда собирать feedback | `ch10-feedback-when.png` | наша схема |
| — | Четыре смещения feedback | `ch10-feedback-biases.png` | наша схема |
| — | Вырожденная петля обратной связи | `ch10-feedback-loop.png` | наша схема |
