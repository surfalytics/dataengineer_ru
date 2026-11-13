# Глоссарий: AI Engineering (Chip Huyen)

Единые слова для всех глав. Правила — в навыке `book-summary`, раздел «Translation guide».
Колонка «Как пишем»: термин в обратных кавычках = оставляем английским; обычное слово = пишем по-русски (английский в скобках при первом упоминании).
Ниже, после общих таблиц, идут новые термины каждой главы.

## Общие

| English | Как пишем | Пояснение при первом использовании |
|---|---|---|
| foundation model | `foundation model` | Большая универсальная модель, обученная на огромных данных. Её адаптируют под задачи |
| LLM | `LLM` | Большая языковая модель |
| AI engineering | `AI engineering` | Построение приложений на готовых foundation models |
| token | `токен` | Единица текста для модели: символ, слово или часть слова |
| prompt | `prompt` | Текст-инструкция и контекст, который мы отправляем модели |
| system prompt | `system prompt` | Общая инструкция для модели, задана разработчиком |
| context | контекст | Всё, что модель видит при ответе |
| context length | длина контекста | Максимум токенов, которые модель обрабатывает за раз |
| inference | `inference` | Расчёт ответа уже обученной моделью |
| training | обучение | Подбор параметров модели по данным |
| pre-training | `pre-training` | Первичное обучение на большом тексте: предсказывать следующий токен |
| post-training | `post-training` | Дообучение после pre-training: SFT, preference finetuning |
| finetuning | `finetuning` | Дообучение модели на своих данных |
| SFT | `SFT` | Supervised finetuning: учим по парам «инструкция — ответ» |
| RLHF | `RLHF` | Обучение с подкреплением на человеческих предпочтениях |
| preference data | данные о предпочтениях | Пары ответов и выбор, какой лучше |
| sampling | `sampling` | Выбор следующего токена по вероятностям |
| temperature | `temperature` | Параметр случайности sampling |
| hallucination | галлюцинация | Уверенный, но выдуманный ответ модели |
| embedding | `embedding` | Числовой вектор, передающий смысл данных |
| vector database | векторная база | Хранилище embeddings для поиска по сходству |
| parameter | параметр | Число внутри модели, подбирается при обучении |
| open-source model | открытая модель | Модель, веса которой доступны |
| model API | API модели | Модель как сервис |
| multimodal | мультимодальный | Работает с несколькими видами данных: текст, картинки, аудио |
| latency | задержка (`latency`) | Время от запроса до ответа |
| cost | стоимость | Деньги на вызов модели или на инфраструктуру |

## Оценка (главы 3–4)

| English | Как пишем | Пояснение |
|---|---|---|
| evaluation, eval | оценка (`evaluation`, `eval`) | Измерение качества системы |
| benchmark | `benchmark` | Стандартный набор задач для сравнения моделей |
| saturated benchmark | насыщенный `benchmark` | Модели набирают на нём почти максимум |
| exact evaluation | `exact evaluation` | Оценка с однозначным вердиктом |
| subjective evaluation | `subjective evaluation` | Оценка, где вердикт зависит от судьи |
| functional correctness | `functional correctness` | Система делает то, что должна. Для кода: проходит тесты |
| pass@k | `pass@k` | Доля задач, где хотя бы одно из `k` решений прошло все тесты |
| reference-based / reference-free | с эталоном / без эталона | Метрика требует эталонных ответов или нет |
| ground truth | эталон (`ground truth`) | Правильный ответ |
| exact match | `exact match` | Ответ точно совпадает с эталоном |
| lexical similarity | `lexical similarity` | Сходство по словам |
| semantic similarity | `semantic similarity` | Сходство по смыслу |
| edit distance | `edit distance` | Сколько правок превращают один текст в другой |
| n-gram | `n-gram` | Последовательность из n токенов |
| cosine similarity | `cosine similarity` | Мера сходства векторов |
| entropy | `entropy` | Информация на токен |
| cross entropy | `cross entropy` | Трудность предсказания токенов в данных |
| perplexity | `perplexity` | Экспонента от cross entropy |
| BPC / BPB | `BPC` / `BPB` | Биты на символ / на байт |
| data contamination | `data contamination` | Данные benchmark попали в обучающие данные |
| AI as a judge | `AI as a judge` | Модель оценивает ответы другой модели |
| AI judge | AI-судья (`AI judge`) | Модель плюс промпт, которые оценивают |
| self-bias / position bias / verbosity bias | `self-bias` / `position bias` / `verbosity bias` | Смещения судьи |
| reward model | `reward model` | Модель, оценивающая качество ответа |
| preference model | `preference model` | Модель, выбирающая лучший из двух ответов |
| comparative evaluation | `comparative evaluation` | Рейтинг по парным сравнениям |
| pointwise evaluation | `pointwise evaluation` | Оценка каждой модели отдельно |
| win rate | `win rate` | Доля побед в матчах |
| Elo, Bradley-Terry | `Elo`, `Bradley-Terry` | Алгоритмы рейтинга |
| guardrail | `guardrail` | Ограждение: проверка входа или выхода модели |
| A/B test | A/B-тест | Каждому пользователю показывают один из вариантов |

## Адаптация (главы 5–8)

| English | Как пишем | Пояснение |
|---|---|---|
| prompt engineering | `prompt engineering` | Подбор инструкций и контекста для модели |
| in-context learning | `in-context learning` | Модель учится на примерах прямо в prompt |
| few-shot / zero-shot | `few-shot` / `zero-shot` | С примерами в prompt / без примеров |
| chain of thought (CoT) | `chain of thought` | Просим модель рассуждать по шагам |
| prompt injection | `prompt injection` | Атака: вредная инструкция в данных |
| jailbreak | `jailbreak` | Обход ограничений модели |
| RAG | `RAG` | Retrieval-augmented generation: ответ с найденным контекстом |
| retrieval | поиск (`retrieval`) | Нахождение релевантных данных |
| chunk, chunking | `chunk`, `chunking` | Кусок документа, разбиение на куски |
| reranking | `reranking` | Пересортировка найденного |
| agent | агент (`agent`) | Система, которая планирует и использует инструменты |
| tool | инструмент (`tool`) | Функция или API, доступные агенту |
| planning | планирование | Агент строит план действий |
| memory | память | Хранение информации между шагами и сессиями |
| LoRA | `LoRA` | Дообучение малой части параметров |
| PEFT | `PEFT` | Parameter-efficient finetuning |
| quantization | `quantization` | Меньше бит на параметр |
| model merging | `model merging` | Слияние моделей |
| dataset engineering | `dataset engineering` | Создание и подготовка данных для модели |
| data synthesis | синтез данных | Создание данных моделью |
| distillation | `distillation` | Обучение малой модели на ответах большой |
| deduplication | дедупликация | Удаление повторов |
| data curation | подготовка данных (`data curation`) | Отбор, чистка, разметка |
| data augmentation | аугментация данных | Расширение данных преобразованиями |

## Продакшен (главы 9–10)

| English | Как пишем | Пояснение |
|---|---|---|
| prefill / decode | `prefill` / `decode` | Две фазы inference |
| TTFT / TPOT | `TTFT` / `TPOT` | Время до первого токена / на следующий токен |
| throughput | `throughput` | Токены в секунду по сервису |
| goodput | `goodput` | Запросы в секунду, уложившиеся в SLO |
| KV cache | `KV cache` | Кэш key и value прошлых токенов |
| batching | `batching` | Обработка нескольких запросов вместе |
| speculative decoding | `speculative decoding` | Малая модель предлагает токены, большая проверяет |
| prompt caching | `prompt caching` | Повторное использование обработки общей части prompt |
| router | `router` | Выбирает модель под запрос |
| gateway | `gateway` | Единая точка доступа к моделям |
| cache (exact / semantic) | кэш | Хранение прошлых ответов |
| observability | `observability` | Логи, метрики, трассировки |
| user feedback | обратная связь пользователей | Явные и неявные сигналы качества |

## Новые термины главы 1

| English | Как пишем | Пояснение |
|---|---|---|
| language model | языковая модель (`language model`) | Хранит статистику языка: насколько вероятен токен в контексте |
| tokenization | `tokenization` | Разбиение текста на токены |
| vocabulary | словарь (`vocabulary`) | Множество всех токенов, с которыми работает модель |
| masked language model | `masked` модель | Заполняет пропуск по токенам слева и справа. Пример: BERT |
| autoregressive language model | `autoregressive` модель | Предсказывает следующий токен по предыдущим. Её же называют `causal` |
| generative AI | `generative AI` | AI, который создаёт открытые выходы из конечного словаря |
| completion | `completion` | Продолжение текста; предсказание по вероятностям |
| completion machine | машина дописывания (`completion machine`) | Образ языковой модели: получает текст и дописывает его |
| supervision | `supervision` | Обучение на размеченных людьми данных |
| self-supervision | `self-supervision` | Метки берутся из самих данных (следующий токен) |
| unsupervised | `unsupervised` | Обучение без меток. Не то же, что self-supervision |
| BOS / EOS | `<BOS>` / `<EOS>` | Специальные токены начала и конца последовательности |
| natural language supervision | `natural language supervision` | Вариант self-supervision: пары (картинка, подпись) из интернета. Так учили CLIP |
| LMM | `LMM` | Large multimodal model: генеративная мультимодальная модель |
| general-purpose model | универсальная модель | Подходит для многих задач. Противоположность модели под одну задачу |
| task-specific model | модель под задачу | Меньше и дешевле, но решает одну задачу |
| build or buy | `build or buy` | Решение: строить свою модель или брать готовую |
| model adaptation | адаптация модели | Подгонка модели под задачу: prompt-based техники или finetuning |
| AI interface | `AI interface` | Интерфейс, через который пользователи работают с AI-приложением |
| context construction | построение контекста (`context construction`) | Подбор данных и инструментов, которые передают модели вместе с prompt |
| human-in-the-loop | `human-in-the-loop` | Человек участвует в решениях AI |
| Crawl-Walk-Run | `Crawl-Walk-Run` | Постепенный рост автоматизации: человек обязателен, AI с сотрудниками, AI с клиентами |
| acceptance rate | `acceptance rate` | Доля подсказок AI, принятых человеком без правок |
| usefulness threshold | порог полезности (`usefulness threshold`) | Минимальное качество, при котором продукт полезен |
| last mile | `last mile` | Последние проценты качества, которые занимают больше всего времени |
| defensibility / moat | защита продукта (`defensibility`, `moat`) | Что мешает конкурентам повторить продукт: технология, данные, дистрибуция |
| distribution | дистрибуция (`distribution`) | Умение донести продукт до пользователей |
| data flywheel | маховик данных (`data flywheel`) | Больше пользователей, больше данных, лучше продукт, больше пользователей |
| business continuity | непрерывность бизнеса (`business continuity`) | Компания может обанкротиться, если не внедрит AI |
| exposure | подверженность (`exposure`) | Доля задач профессии, время на которые AI сокращает минимум на 50% |
| IDP | `IDP` | Intelligent data processing: интеллектуальная обработка данных |
| product copilot | `product copilot` | AI, который проводит клиента через сложные задачи в продукте |
| talk-to-your-docs | `talk-to-your-docs` | Диалог с вашими документами |
| modeling and training | моделирование и обучение (`modeling and training`) | Разработка архитектуры модели, её обучение и finetuning |
| inference optimization | оптимизация `inference` | Ускорение и удешевление работы модели |
| traditional ML | традиционный ML | Все ML-модели до foundation models |
| commodity | товар (`commodity`) | Модели стали взаимозаменяемыми, поэтому отличаются данными |

## Новые термины главы 2

| English | Как пишем | Пояснение |
|---|---|---|
| Common Crawl | Common Crawl | Некоммерческий архив страниц интернета. Главный источник данных для обучения LLM |
| C4 (Colossal Clean Crawled Corpus) | `C4` | Очищенная часть Common Crawl от Google |
| low-resource language | язык с малым числом данных (`low-resource`) | Язык, на котором в обучающих данных мало текста |
| domain-specific model | доменная модель (`domain-specific model`) | Модель для одной области: биология, медицина, чертежи |
| seq2seq | `seq2seq` | Архитектура «последовательность в последовательность»: encoder читает вход, decoder пишет выход |
| RNN | `RNN` | Рекуррентная сеть. Читает токены по одному, по порядку |
| encoder / decoder | `encoder` / `decoder` | Часть, которая читает вход / часть, которая пишет выход |
| hidden state | скрытое состояние (`hidden state`) | Вектор, в котором RNN хранит всё, что прочитала |
| attention | `attention` | Механизм: при каждом новом токене модель сама решает, на какие прошлые токены смотреть |
| transformer | `transformer` | Архитектура на attention. Сейчас основа почти всех LLM |
| query / key / value | `query` / `key` / `value` | Три вектора attention: что ищем / чем помечен токен / что в нём лежит |
| multi-head attention | `multi-head attention` | Attention, который считают несколькими «головами» параллельно |
| transformer block | блок `transformer` | Один слой: модуль attention и модуль MLP |
| MLP / feedforward layer | `MLP` / слой `feedforward` | Несколько линейных слоёв с нелинейной функцией между ними |
| activation function | функция активации (`ReLU`, `GELU`) | Нелинейная функция между линейными слоями |
| d_model, d_ff | `d_model`, `d_ff` | Размерность модели (скрытая) и размерность слоя feedforward |
| positional embedding | `positional embedding` | Вектор, который сообщает модели позицию токена |
| unembedding layer / model head | `unembedding layer` / `model head` | Последний слой: вектор модели в вероятности токенов |
| prefill / decode | `prefill` / `decode` | Две фазы inference: прочитать prompt параллельно / писать ответ по одному токену |
| KV cache | `KV cache` | Кэш векторов key и value прошлых токенов |
| SSM (state space model) | `SSM` | Семейство архитектур, у которых цена растёт линейно с длиной текста |
| Mamba, Jamba, RWKV, S4, H3 | Mamba, Jamba, RWKV, S4, H3 | Названия альтернатив transformer |
| MoE (mixture of experts) | `MoE` | Модель из групп параметров («экспертов»). На токен работают только несколько |
| sparse / dense model | разреженная / плотная модель | Много параметров равны нулю или не используются на токен / используются все |
| FLOP / FLOPs / FLOP/s | `FLOP`, `FLOPs`, `FLOP/s` | Операция с плавающей точкой / число операций (работа) / операций в секунду (скорость) |
| utilization | загрузка (`utilization`) | Какую долю пиковой мощности железа реально используем |
| epoch | эпоха | Один проход по всему датасету |
| training tokens | токены обучения | Сколько токенов модель прочитала при обучении (датасет × эпохи) |
| scaling law | `scaling law` | Закон: как качество зависит от размера модели, данных и вычислений |
| compute-optimal | `compute-optimal` | Лучшая модель при фиксированном бюджете вычислений |
| Chinchilla scaling law | `Chinchilla` | Правило: токенов обучения примерно в 20 раз больше, чем параметров |
| inverse scaling | `inverse scaling` | Случай, когда большая модель хуже малой |
| hyperparameter | гиперпараметр | Настройка, которую задаёт человек, а не обучение |
| scaling extrapolation | `scaling extrapolation` | Подбор гиперпараметров большой модели по опытам на малых |
| emergent ability | эмерджентная способность (`emergent ability`) | Умение, которое появляется только у больших моделей |
| demonstration data | `demonstration data` | Пары (prompt, хороший ответ) для SFT |
| behavior cloning | `behavior cloning` | Модель копирует поведение из примеров |
| comparison data | `comparison data` | Тройки (prompt, победивший ответ, проигравший ответ) |
| DPO | `DPO` | Direct Preference Optimization: проще RLHF, без отдельной reward model и RL |
| RLAIF | `RLAIF` | RL на предпочтениях, которые даёт другая модель |
| PPO | `PPO` | Proximal Policy Optimization: алгоритм RL, который чаще всего используют в RLHF |
| best of N | `best of N` | Сгенерировать N ответов, выбрать лучший |
| test-time compute | `test-time compute` | Больше вычислений на запрос: несколько ответов, поиск лучшего |
| beam search | `beam search` | Поиск по лучам: на каждом шаге держим несколько лучших кандидатов |
| self-consistency | `self-consistency` | Выбор самого частого ответа из нескольких |
| verifier | `verifier` | Модель или правило, которое проверяет ответ |
| logit | `logit` | Число для каждого токена до softmax. Не вероятность |
| softmax | `softmax` | Функция, которая превращает logits в вероятности |
| greedy sampling | `greedy sampling` | Всегда брать самый вероятный токен |
| top-k / top-p (nucleus) / min-p | `top-k` / `top-p` / `min-p` | Способы ограничить набор токенов, из которых выбираем |
| logprobs | `logprobs` | Логарифмы вероятностей токенов |
| underflow | `underflow` | Число настолько мало, что компьютер округляет его до нуля |
| stop token / stop condition | `stop token` / условие остановки | Токен или правило, после которого генерация заканчивается |
| structured outputs | `structured outputs` | Ответ в заданном формате: JSON, SQL, регулярное выражение |
| semantic parsing | `semantic parsing` | Перевод текста на человеческом языке в машинный формат (например, text-to-SQL) |
| JSON mode | режим JSON (`JSON mode`) | Режим API: модель обещает валидный JSON |
| constrained sampling | `constrained sampling` | Sampling только из токенов, которые разрешает грамматика |
| grammar | грамматика | Правила, какой токен можно на каждом шаге формата |
| post-processing | `post-processing` | Скрипт чинит типичные ошибки в ответе модели |
| probabilistic / deterministic | вероятностный / детерминированный | Ответ случаен / ответ всегда одинаков |
| inconsistency | несогласованность (`inconsistency`) | Разные ответы на один и тот же или почти такой же prompt |
| seed | `seed` | Начальное число генератора случайных чисел |
| self-delusion / snowballing hallucination | самообман / `snowballing` | Модель верит своей же ошибке и нагромождает новые |
| reward model, preference model | `reward model`, `preference model` | Уже есть в общем глоссарии: модель, которая оценивает ответ |

## Новые термины главы 4

| English | Как пишем | Пояснение |
|---|---|---|
| evaluation-driven development | `evaluation-driven development` | Сначала критерии оценки, потом разработка (по аналогии с test-driven development) |
| domain-specific capability | domain-specific capability (предметные навыки) | Умение модели в вашей области: код, SQL, язык, право |
| generation capability | generation capability (способность генерировать) | Качество самого сгенерированного текста: факты, безопасность, связность |
| fluency / coherence | беглость (`fluency`) / связность (`coherence`) | Грамматика и естественность текста / логика и структура |
| faithfulness / relevance | верность исходному тексту (`faithfulness`) / релевантность (`relevance`) | Насколько перевод точен / насколько изложение сфокусировано на главном |
| factual consistency | `factual consistency` | Ответ не противоречит контексту (local) или общим знаниям (global) |
| SelfCheckGPT | `SelfCheckGPT` | Проверка фактов: несколько ответов модели на один вопрос, расхождение значит галлюцинацию |
| SAFE | `SAFE` | Проверка фактов: ответ делят на утверждения и подтверждают поиском |
| textual entailment, NLI | `textual entailment` | Следует ли гипотеза из посылки: следует, противоречит, нейтрально |
| safety | безопасность (`safety`) | Отсутствие вреда в ответах: токсичность, hate speech, стереотипы, предвзятость |
| instruction-following | `instruction-following` (следование инструкциям) | Умение выполнять инструкции по формату, длине, стилю, содержанию |
| role-playing | ролевая игра (`role-playing`) | Модель играет персонажа или персону |
| time to first token (TTFT) | `TTFT` | Время до первого токена |
| P90 | `P90` | 90-й процентиль: 90% запросов быстрее этого значения |
| TPM | `TPM` | Токенов в минуту: масштаб нагрузки |
| Pareto optimization | `Pareto optimization` | Оптимизация сразу по нескольким целям |
| hard / soft attributes | hard / soft attributes (жёсткие / мягкие свойства) | Что нельзя менять / что можно улучшить |
| open weight / open model | `open weight` / `open model` | Веса открыты без данных / открыты веса и данные |
| model API / inference service | `model API` / `inference service` | Интерфейс к модели / сервис, запускающий модель |
| data lineage | `data lineage` | Происхождение данных, на которых обучена модель |
| model distillation | `model distillation` | Малая модель учится на ответах большой |
| evaluation harness | `evaluation harness` | Инструмент, который запускает модель на многих benchmarks |
| leaderboard | `leaderboard` | Рейтинг моделей по набору benchmarks |
| mean win rate | `mean win rate` | Доля случаев, когда модель лучше другой, усреднённая по сценариям |
| n-gram overlapping | `n-gram overlapping` | Поиск загрязнения по общим цепочкам из n токенов |
| dirty / clean samples | «грязные» / «чистые» примеры | Примеры benchmark, которые есть / которых нет в training data |
| turn-based / task-based evaluation | `turn-based` / `task-based evaluation` | Оценка каждого ответа / оценка решения задачи |
| evaluation guideline, rubric | `evaluation guideline`, `rubric` | Критерии, шкала и примеры оценки |
| usefulness threshold | `usefulness threshold` (порог полезности) | Минимальный балл, при котором приложение полезно |
| stickiness / engagement | удержание (`stickiness`) / вовлечённость (`engagement`) | Метрики DAU, WAU, MAU / число разговоров и длительность визита |
| slicing | `slicing` | Оценка по подмножествам данных |
| Simpson's paradox | парадокс Симпсона (`Simpson's paradox`) | Общий итог противоположен итогам по группам |
| bootstrap | `bootstrap` | Выборки с возвратом для проверки стабильности оценки |
| logprobs | `logprobs` | Логарифмы вероятностей токенов: показывают уверенность модели |
| instruction data | `instruction data` | Данные вида «инструкция — ответ» для finetuning |

## Новые термины главы 5

| English | Как пишем | Пояснение |
|---|---|---|
| user prompt | `user prompt` | Часть `prompt` с вводом пользователя и данными |
| chat template | `chat template` | Формат склейки `system prompt` и `user prompt` в один текст со служебными токенами. Свой у каждой модели |
| prompt template (приложения) | шаблон `prompt` | Текст с местами для данных, который пишет разработчик приложения. Не то же, что `chat template` |
| shot | `shot` | Один пример в `prompt` |
| prompt robustness | устойчивость к `prompt` (`prompt robustness`) | Насколько мало меняется ответ при мелких изменениях `prompt`: «5» и «пять», пустая строка, регистр |
| persona | роль (`persona`) | Роль, которую модель играет в ответе, например учитель первого класса |
| needle in a haystack, NIAH | `needle in a haystack` (NIAH) | Тест: спрятать факт (иглу) в длинном `prompt` (стоге сена) и просить найти |
| RULER | RULER | Набор тестов для оценки работы модели с длинными `prompt` |
| context construction | `context construction` | Сбор нужного контекста для запроса: поиск по данным, веб-поиск |
| intent classification | `intent classification` | Определение типа запроса пользователя |
| prompt chaining, decomposition | цепочка `prompts` (`prompt chaining`) | Разбиение сложной задачи на подзадачи, у каждой свой `prompt` |
| self-critique | самокритика (`self-critique`) | Просьба к модели проверить собственный ответ |
| prompt optimization tool | инструмент автоподбора `prompt` | DSPy, OpenPrompt и подобные: сами ищут `prompt`, который максимизирует метрику |
| Promptbreeder, TextGrad | Promptbreeder, TextGrad | Инструменты автоподбора `prompt` с помощью AI |
| mutation, mutator | мутация, мутатор | Изменение `prompt` по правилу в эволюционном поиске |
| prompt catalog | `prompt catalog` | Хранилище `prompts` с явными версиями, метаданными и списком потребителей |
| prompt extraction | `prompt extraction` | Атака: вытащить `prompt` приложения, включая `system prompt` |
| reverse prompt engineering | `reverse prompt engineering` | Попытка выяснить закрытый `prompt` по ответам приложения |
| indirect prompt injection | `indirect prompt injection` | Вредная команда лежит в данных, которые модель читает через `tool` |
| passive phishing / active injection | пассивный фишинг / активная инъекция | Вредную нагрузку оставляют в публичных местах / шлют её цели прямо |
| obfuscation | обфускация | Приём jailbreak: опечатки, смесь языков, странные символы |
| DAN | DAN | Известный `jailbreak` через ролевую игру: «делай что угодно прямо сейчас» |
| PAIR | `PAIR` | Автоматическая атака: AI-атакующий улучшает `prompt` по ответам цели |
| information extraction | `information extraction` | Атака: достать данные обучения или приватный контекст модели |
| factual probing | `factual probing` | Исследование того, что знает модель, фразами с пропуском |
| LAMA | LAMA | Бенчмарк реляционных знаний модели (Meta AI, 2019) |
| memorization | запоминание (`memorization`) | Модель хранит куски обучающих данных и может выдать их дословно |
| divergence attack, repeated token attack | атака дрейфом, атака повторяющимися токенами | Просьба повторять слово бесконечно: модель сбивается и выдаёт обучающие данные |
| regurgitation | дословное воспроизведение (`regurgitation`) | Модель выдаёт защищённый текст из обучения без атак |
| instruction hierarchy | `instruction hierarchy` | Приоритет инструкций: system, user, вывод модели, вывод `tool` |
| borderline request | пограничный запрос | Запрос, на который возможен и безопасный, и небезопасный ответ |
| red team, red teaming | `red team`, `red teaming` | Группа, которая ищет новые атаки на свою систему, и сама практика |
| violation rate | `violation rate` | Доля успешных атак среди всех попыток |
| false refusal rate | `false refusal rate` | Доля лишних отказов на безобидные запросы |
| sandbox, isolation | изоляция (`sandbox`) | Запуск сгенерированного кода в среде, отделённой от основной машины |
| human approval | согласие человека | Опасная команда (`DELETE`, `DROP`, `UPDATE`) выполняется только после одобрения |
| out-of-scope topics | запретные темы | Темы, на которые приложение не должно отвечать |

## Новые термины главы 6

| English | Как пишем | Пояснение |
|---|---|---|
| retriever | `retriever` | Часть RAG, которая находит данные во внешней памяти |
| generator | `generator` | Часть RAG, которая пишет ответ по найденным данным |
| external memory | внешняя память (`external memory`) | Хранилище, откуда RAG берёт данные: база, прошлые чаты, интернет |
| indexing / querying | индексация / запрос (`indexing`, `querying`) | Подготовка данных для быстрого поиска / поиск по запросу |
| term-based retrieval | `term-based retrieval` | Поиск по словам (лексический): TF-IDF, BM25 |
| embedding-based retrieval | `embedding-based retrieval` | Поиск по смыслу через embeddings и vector search |
| sparse / dense | `sparse` / `dense` | Разреженные / плотные vectors. Книга делит поиск иначе: по способу, а не по типу vectors |
| TF, IDF, TF-IDF | `TF`, `IDF`, `TF-IDF` | Частота термина в документе; обратная частота документов с термином; их произведение |
| BM25 | `BM25` | Вариант TF-IDF с поправкой на длину документа |
| inverted index | `inverted index` | Словарь «термин → документы, где он есть» |
| Elasticsearch | Elasticsearch | Система term-based поиска на базе Lucene |
| tokenization | токенизация | Разбиение запроса на термины |
| k-NN / ANN | `k-NN` / `ANN` | Точный перебор ближайших соседей / приближённый поиск |
| LSH, HNSW, IVF, product quantization, Annoy | `LSH`, `HNSW`, `IVF`, `product quantization`, `Annoy` | Алгоритмы ANN: хэширование в корзины, многослойный граф, кластеры k-means, сжатие vectors, случайные деревья |
| hybrid search | `hybrid search` | Term-based и embedding-based поиск вместе |
| RRF | `RRF` | Reciprocal rank fusion: слияние рангов, балл = сумма 1/(k + rank) |
| query rewriting | `query rewriting` | Переписывание запроса, чтобы он был понятен без контекста диалога |
| contextual retrieval | `contextual retrieval` | Добавление к chunk контекста для облегчения поиска |
| context precision / context recall | `context precision` / `context recall` | Доля релевантных среди найденных / доля найденных среди всех релевантных |
| NDCG, MAP, MRR | `NDCG`, `MAP`, `MRR` | Ранговые метрики поиска |
| MTEB, BEIR | MTEB, BEIR | Benchmarks для embeddings и для retrieval |
| evaluation set (retrieval) | `evaluation set` | Тестовые запросы и документы с метками релевантности |
| multimodal RAG | мультимодальный `RAG` | RAG, где в контексте не только текст, но и картинки и другое |
| text-to-SQL | text-to-SQL | Модель превращает вопрос и схему таблиц в SQL |
| environment | среда (`environment`) | То, где агент работает: игра, интернет, компьютер |
| action | действие (`action`) | Что агент может делать в среде |
| tool inventory | `tool inventory` | Набор инструментов, доступных агенту |
| read-only action / write action | `read-only` / `write action` | Действие, которое читает данные / действие, которое меняет данные или мир |
| knowledge augmentation | расширение знаний (`knowledge augmentation`) | Инструменты, которые дают агенту контекст |
| capability extension | расширение возможностей (`capability extension`) | Инструменты, которые закрывают слабости модели |
| code interpreter | `code interpreter` | Инструмент, который выполняет код, написанный моделью |
| web browsing | веб-просмотр (`web browsing`) | Любые инструменты, которые ходят в интернет |
| function calling | `function calling` | Модель возвращает имя функции и аргументы, вызывает функцию ваш код |
| tool_choice (required / none / auto) | `tool_choice` | Режим использования tools: обязательно / запрещено / решает модель |
| plan / planner | план / `planner` | Последовательность шагов; компонент, который её строит |
| executor | `executor` | Компонент, который выполняет шаги плана |
| evaluator | `evaluator` | Компонент, который проверяет план и результат |
| plan validation | проверка плана (`validation`) | Проверка плана до выполнения: эвристики или AI judge |
| task decomposition | декомпозиция задачи | Разбиение задачи на посильные шаги |
| multi-agent system | мультиагентная система | Система из нескольких компонентов-агентов (planner, evaluator, executor) |
| intent classifier | `intent classifier` | Определяет намерение пользователя; может пометить запрос как `IRRELEVANT` |
| human in the loop | человек в цикле | Человек подтверждает или выполняет часть шагов плана |
| backtracking | возврат (`backtracking`) | Вернуться на шаг назад и выбрать другое действие |
| hierarchical planning | иерархическое планирование | Сначала план верхнего уровня, потом детальные планы |
| control flow | `control flow` (поток управления) | Порядок выполнения шагов: sequential, parallel, if, for |
| reflection | `reflection` | Оценка плана или результата и исправление ошибок |
| ReAct | ReAct | Паттерн: мысль, действие, наблюдение по кругу |
| Reflexion | Reflexion | Паттерн: evaluator и self-reflection после неудачи, потом новая траектория |
| trajectory | траектория (`trajectory`) | План или цепочка действий агента |
| ablation study | `ablation study` | Убрать один компонент и посмотреть, как изменилось качество |
| tool transition | переход между tools | Вероятность, что после tool X агент вызовет tool Y |
| skill manager | `skill manager` | Хранит новые навыки агента для повторного использования (Voyager) |
| planning dataset | `planning dataset` | Набор пар (задача, tool inventory) для проверки планов агента |
| failure modes (agent) | сбои агента (`failure modes`) | Сбои планирования, сбои инструментов, неэффективность |
| goal failure | `goal failure` | План не решает задачу или нарушает условия (бюджет, время) |
| internal knowledge | `internal knowledge` | Знания в весах модели |
| short-term memory | `short-term memory` | Контекст модели: быстрый, ограниченный, не живёт между задачами |
| long-term memory | `long-term memory` | Внешнее хранилище: живёт между задачами, данные можно удалять |
| memory management / memory retrieval | `memory management` / `memory retrieval` | Что хранить и удалять / как достать нужное |
| FIFO | `FIFO` | Первым вошёл, первым вышел |
| summary (memory) | `summary` | Краткое изложение диалога для сжатия памяти |

## Новые термины главы 7

| English | Как пишем | Пояснение |
|---|---|---|
| transfer learning | `transfer learning` | Перенос знания с одной задачи на другую |
| feature-based transfer | `feature-based transfer` | Перенос через признаки (embeddings), которые извлекла другая модель |
| sample efficiency | `sample efficiency` | Умение учиться на малом числе примеров |
| continued pre-training, self-supervised finetuning | `continued pre-training` | Самообучение на сырых текстах области после pre-training |
| infilling finetuning | `infilling finetuning` | Дообучение заполнять пропуск в тексте или коде |
| long-context finetuning | `long-context finetuning` | Дообучение, чтобы расширить длину контекста |
| catastrophic forgetting | `catastrophic forgetting` | Модель забывает старую задачу при обучении новой |
| trainable / frozen parameter | `trainable` и `frozen` параметры | Обновляемый и замороженный параметр |
| forward pass / backward pass | `forward pass` / `backward pass` | Прямой проход считает ответ, обратный обновляет веса |
| backpropagation | `backpropagation` | Обратное распространение ошибки |
| loss | `loss` | Потеря: разница между ответом и ожидаемым ответом |
| gradient | `gradient` | Вклад параметра в loss |
| optimizer, optimizer states | `optimizer`, `optimizer states` | Алгоритм обновления весов и его хранимые значения (SGD, Adam) |
| activations | `activations` | Промежуточные значения прямого прохода |
| gradient checkpointing | `gradient checkpointing` | Не хранить activations, а пересчитывать |
| FP32, FP16, BF16, TF32 | `FP32`, `FP16`, `BF16`, `TF32` | Форматы чисел с плавающей запятой |
| INT8, INT4 | `INT8`, `INT4` | Целочисленные форматы |
| range, precision (exponent, mantissa) | `range`, `precision` | Диапазон и точность формата |
| PTQ | `PTQ` | Post-training quantization |
| QAT | `QAT` | Quantization-aware training |
| mixed precision, AMP | `mixed precision`, `AMP` | Смешанная точность; автоматический выбор точности во frameworks |
| full finetuning | `full finetuning` | Обновляются все параметры |
| partial finetuning | `partial finetuning` | Обновляется часть параметров |
| adapter | `adapter` | Малый обучаемый модуль в модели |
| soft prompt / hard prompt | `soft prompt` / `hard prompt` | Обучаемые векторы на входе / текстовый prompt |
| prefix tuning, P-tuning, prompt tuning | `prefix tuning`, `P-tuning`, `prompt tuning` | Варианты soft prompt, различаются местом вставки |
| LoRA rank, alpha | `rank` (`r`), `α` | Размер «узкого места» LoRA и коэффициент вклада добавки |
| multi-LoRA serving | `multi-LoRA serving` | Одна базовая модель и много адаптеров |
| QLoRA, NF4, paged optimizer | `QLoRA`, `NF4`, `paged optimizer` | LoRA с 4-битными весами; формат NF4; optimizer, который выгружает данные на CPU |
| intrinsic dimension | `intrinsic dimension` | Сколько параметров реально нужно для новой задачи |
| low-rank factorization | низкоранговая факторизация | Разложение матрицы на произведение малых |
| ensembling | `ensembling` | Объединение ответов нескольких моделей |
| task vector, task arithmetic | `task vector`, `task arithmetic` | Дообученная минус базовая; сложение и вычитание таких векторов |
| SLERP | `SLERP` | Сферическая линейная интерполяция |
| TIES, DARE | `TIES`, `DARE` | Методы очистки task vectors перед слиянием |
| layer stacking, frankenmerging, passthrough | `layer stacking` | Слияние постановкой слоёв друг на друга |
| depthwise scaling | `depthwise scaling` | Увеличение модели в глубину |
| MoE, sparse upcycling, router | `MoE`, `sparse upcycling`, `router` | Модель с экспертами; её получение из обычной модели; выбор эксперта |
| federated learning | `federated learning` | Устройства учат копии модели на своих данных, потом их сливают |
| CPU offloading | `CPU offloading` | Часть памяти выгружается с GPU на CPU |
| learning rate, scheduler | `learning rate`, `learning rate scheduler` | Размер шага обучения и правило его изменения |
| batch size, gradient accumulation | `batch size`, `gradient accumulation` | Примеров на шаг; накопление gradients за несколько batch |
| epoch | `epoch` | Один проход по обучающим данным |
| overfitting | `overfitting` | Модель запоминает обучающие данные |
| prompt loss weight | `prompt loss weight` | Вклад токенов prompt в loss относительно токенов ответа |
| semantic parsing | `semantic parsing` | Превращение естественного языка в структурированный формат |

## Новые термины главы 8

| English | Как пишем | Пояснение |
|---|---|---|
| data-centric AI / model-centric AI | `data-centric AI` / `model-centric AI` | Улучшаем качество через данные / через саму модель |
| data labeler, dataset creator, data quality engineer | разметчик, создатель датасетов, инженер качества данных | Роли, которые появились в AI-командах |
| annotation, annotator | разметка, разметчик | Ручное или AI-добавление меток и ответов к данным |
| annotation guidelines | правила разметки (`annotation guidelines`) | Документ: что такое хороший ответ, чем оценка 3 отличается от 4 |
| quality / coverage / quantity | `quality` / `coverage` / `quantity` | Три критерия данных: чистота, разнообразие, объём |
| data diversity | разнообразие данных (`data diversity`) | То же, что coverage: данные покрывают разные запросы |
| data mix | смесь данных (`data mix`) | Доли доменов в обучающих данных на одном этапе |
| diminishing returns | `diminishing returns` | Убывающая отдача: каждая новая порция данных помогает меньше |
| ossification | «окостенение» (`ossification`) | Веса после pre-training хуже подстраиваются под данные finetuning |
| annealing | `annealing` | Конец обучения с малым learning rate на малом объёме лучших данных |
| weak supervision, semi-supervision, active learning | слабая разметка, полуавтоматическая разметка, активное обучение | Способы уменьшить число размеченных данных |
| data acquisition strategy | стратегия получения данных | Как получить датасет с нужными свойствами при заданном бюджете |
| data flywheel | `data flywheel` (маховик данных) | Данные пользователей улучшают продукт, продукт привлекает больше пользователей |
| single-turn / multi-turn | `single-turn` / `multi-turn` | Один обмен репликами / диалог из нескольких |
| tool use | `tool use` | Работа модели с инструментами и API |
| procedural generation | `procedural generation` (процедурная генерация) | Данные создаёт алгоритм, а не человек |
| rule-based synthesis | `rule-based` синтез | Данные из шаблонов и правил |
| perturbation | `perturbation` (возмущение) | Добавление шума к данным |
| counterfactual augmentation | контрфактическая аугментация | Замена гендерных и других слов на парные, чтобы ослабить смещение |
| simulation, Sim2Real | симуляция (`simulation`), `Sim2Real` | Виртуальная среда вместо опыта в мире / перенос обратно в мир |
| self-play | `self-play` | Модель учится, играя сама с собой |
| back-translation | `back-translation` | Перевод туда и обратно для проверки; для кода: код, объяснение, код |
| reverse instruction | `reverse instruction` | Из готового хорошего текста создаём инструкцию, которая его вызывает |
| instruction synthesis | `instruction synthesis` | Синтез пар (инструкция, ответ) |
| AI verifier | `AI verifier` | AI judge или scorer, проверяющий синтетические данные |
| model collapse | `model collapse` | Деградация при рекурсивном обучении на данных модели |
| data lineage | `data lineage` (происхождение данных) | Откуда пришли данные и как менялись |
| teacher / student | `teacher` / `student` | Большая модель-учитель / малая модель-ученик |
| data processing | обработка данных (`data processing`) | Inspect, deduplicate, clean and filter, format |
| inter-annotator disagreement | расхождение между разметчиками | Насколько по-разному размечают один пример |
| shingle | `shingle` | «Окно» из n слов подряд |
| Jaccard similarity | `Jaccard similarity` | Доля общих элементов двух наборов |
| MinHash | `MinHash` | Короткая подпись набора, оценивающая Jaccard |
| LSH | `LSH` | Locality-sensitive hashing: похожие подписи попадают в одну корзину |
| Bloom filter | `Bloom filter` | Компактная структура: «возможно есть» или «точно нет» |
| bucket | `bucket` (корзина) | Группа объектов с одинаковым hash |
| identity resolution | `identity resolution` | Понять, что две записи это один человек или объект |
| active learning / importance sampling / data pruning | `active learning` / `importance sampling` / `data pruning` | Способы выбрать самые полезные примеры |
| PII | `PII` | Персональные данные |
| chat template | `chat template` | Шаблон записи диалога в токены модели |
| JSONL | `JSONL` | Файл, где каждая строка это один JSON-объект |

## Новые термины главы 9

| English | Как пишем | Пояснение |
|---|---|---|
| inference server / inference service | `inference server` / `inference service` | Сервер, который хранит модели и запускает их; сервис, который ещё принимает и маршрутизирует запросы |
| compute-bound | `compute-bound` | Время задачи ограничено вычислениями |
| memory-bandwidth-bound / memory-bound | `memory-bandwidth-bound` | Время задачи ограничено скоростью передачи данных из памяти. В конспекте `memory-bound` в смысле «нехватка памяти» не используем, пишем `OOM` или «не хватает памяти» |
| out-of-memory | `OOM` | Ошибка: памяти не хватило |
| arithmetic intensity | `arithmetic intensity` | Сколько операций приходится на один байт, прочитанный из памяти |
| roofline | `roofline` | График, где видно, упирается операция в вычисления или в память |
| online API / batch API | online API / batch API | API для малой задержки / API для низкой цены с долгим ожиданием |
| streaming mode | `streaming` | Режим, где токены возвращаются по мере генерации |
| percentile (p50, p90, p95, p99) | перцентиль (`p50`, `p95`, `p99`) | Задержка, в которую укладывается заданная доля запросов |
| TBT / ITL | `TBT` / `ITL` | Другие названия `TPOT`: время между токенами / межтокенная задержка |
| time to publish | `time to publish` | Время до первого токена, который видит пользователь |
| TPS / RPS / RPM | `TPS` / `RPS` / `RPM` | Токены / запросы в секунду / запросы в минуту |
| SLO | `SLO` | Целевое значение метрики, которое мы обещаем |
| GPU utilization | `GPU utilization` | Доля времени, когда GPU занят. Не показывает эффективность |
| FLOP/s | `FLOP/s` | Операции с плавающей запятой в секунду |
| MFU / MBU | `MFU` / `MBU` | Доля использованных FLOP/s / пропускной способности памяти |
| accelerator | ускоритель (`accelerator`) | Чип для ускорения определённых вычислений |
| GPU / TPU / CPU | `GPU` / `TPU` / `CPU` | Видеочип общего назначения для параллельных вычислений / чип Google для тензоров / центральный процессор |
| tensor core | `tensor cores` | Блоки GPU для матричных и тензорных вычислений |
| HBM / SRAM / DRAM | `HBM` / `SRAM` / `DRAM` | Быстрая стековая память GPU / самая быстрая память на кристалле / системная память |
| TDP | `TDP` | Тепловая мощность, которую должна отводить система охлаждения |
| CUDA / Triton / ROCm | CUDA / Triton / ROCm | Языки для программирования GPU: NVIDIA / OpenAI / AMD |
| pruning | `pruning` | Удаление или обнуление наименее полезных параметров |
| weight-only quantization | `weight-only quantization` | Снижение точности только весов модели |
| draft model / target model | `draft model` / `target model` | Малая быстрая модель, которая предлагает токены / большая модель, которая проверяет |
| speculative decoding | `speculative decoding` | Draft-модель предлагает токены, target-модель проверяет параллельно |
| inference with reference | `inference with reference` | Черновик токенов берут из входа |
| parallel decoding, Lookahead, Medusa, Jacobi decoding | `parallel decoding`, `Lookahead decoding`, `Medusa`, `Jacobi decoding` | Генерация нескольких токенов сразу и проверка их согласованности |
| KV cache | `KV cache` | Сохранённые key и value векторы прошлых токенов |
| local attention | `local attention` | Attention только по окну ближайших токенов |
| cross-layer attention | `cross-layer attention` | Соседние слои делят key и value |
| multi-query / grouped-query attention | `multi-query attention` / `grouped-query attention` | Головы делят key и value: все вместе / по группам |
| PagedAttention, vLLM | `PagedAttention`, vLLM | Хранение KV cache блоками; inference framework |
| FlashAttention | `FlashAttention` | Kernel, который сливает операции attention |
| kernel | `kernel` | Код, оптимизированный под конкретный чип |
| compiler, lowering | `compiler`, `lowering` | Инструмент, который переводит код модели в kernels; сам перевод |
| vectorization / parallelization / loop tiling / operator fusion | `vectorization` / `parallelization` / `loop tiling` / `operator fusion` | Приёмы ускорения kernels |
| torch.compile, XLA, TVM, TensorRT | `torch.compile`, XLA, TVM, TensorRT | Компиляторы и frameworks для inference |
| static / dynamic / continuous batching | `static batching` / `dynamic batching` / `continuous batching` | Batch ждёт заполнения / ждёт заполнения или окно времени / принимает новые запросы по мере выхода готовых (`in-flight batching`) |
| prefill/decode disaggregation | разделение `prefill` и `decode` | Шаги работают на разных инстансах |
| prompt caching (prefix cache, context cache) | `prompt caching` | Повторное использование обработки общего начала prompt |
| replica / tensor / pipeline parallelism | `replica parallelism` / `tensor parallelism` / `pipeline parallelism` | Копии модели / деление операции между устройствами / деление модели на стадии |
| context / sequence parallelism | `context parallelism` / `sequence parallelism` | Деление входной последовательности / деление операторов |
| micro-batch | `micro-batch` | Часть batch в pipeline parallelism |
| bin packing | `bin packing` | Задача упаковки копий моделей в GPU разного размера |
| goodput | `goodput` | Запросы в секунду, которые уложились в SLO (в `glossary.md` уже есть) |

## Новые термины главы 10

| English | Как пишем | Пояснение |
|---|---|---|
| input guardrails | `input guardrails` | Защита на входе: PII, вредные prompt |
| output guardrails | `output guardrails` | Защита на выходе: формат, безопасность, политика при сбое |
| PII | `PII` | Персональные данные: телефоны, номера документов, банковские счета |
| PII reverse map | `PII reverse map` | Таблица «плейсхолдер — исходное значение» для демаскирования ответа |
| false refusal rate | `false refusal rate` | Доля нормальных запросов, которые система заблокировала |
| retry | `retry` | Повторный вызов модели при сбое |
| stream completion | `stream completion` | Режим, где токены сразу идут пользователю, не дожидаясь конца ответа |
| intent classifier | `intent classifier` | Маленькая модель, которая предсказывает намерение пользователя |
| fallback | `fallback` | Запасной путь при сбое или rate limit |
| rate limit | `rate limit` | Лимит числа запросов, который ставит провайдер API |
| exact cache | `exact cache` | Кэш для точно совпадающих запросов |
| semantic cache | `semantic cache` | Кэш по похожести embeddings запросов |
| similarity threshold | порог похожести (`similarity threshold`) | Значение похожести, с которого запрос считается «тем же» |
| eviction policy | политика вытеснения (`eviction policy`) | Правило, что выбросить из кэша: `LRU`, `LFU`, `FIFO` |
| hit rate | `hit rate` | Доля запросов, закрытых из кэша |
| read-only actions | `read-only actions` | Действия, которые только читают данные: поиск, SQL, web search |
| write actions | `write actions` | Действия, которые меняют внешний мир: письмо, заказ, перевод |
| context construction | сбор контекста | Блок, который строит контекст для запроса (retrieval, tools) |
| tool gateway | `tool gateway` | Единый доступ к инструментам, как model gateway для моделей |
| monitoring | `monitoring` | Слежение за внешними результатами системы |
| instrumentation | `instrumentation` | Оснащение системы сбором данных о её работе |
| log | лог (`log`) | Журнал событий, записи только добавляются |
| trace | `trace` | Связанные события одного запроса: полный путь по шагам |
| span | `span` | Один шаг trace с временем и токенами |
| drift | `drift` | Незаметное изменение prompt, поведения пользователей или модели |
| MTTD, MTTR, CFR | `MTTD`, `MTTR`, `CFR` | Время обнаружения, время исправления, доля неудачных изменений |
| north star | `north star` | Главная метрика продукта (DAU, подписки) |
| orchestrator | `orchestrator` | Компонент, который задаёт компоненты и порядок шагов пайплайна |
| chaining | `chaining` | Соединение шагов в цепочку (композиция функций) |
| explicit feedback | `explicit feedback` | Явная обратная связь: лайки, звёзды, ответы на вопросы |
| implicit feedback | `implicit feedback` | Неявная обратная связь: выводится из слов и действий |
| natural language feedback | `natural language feedback` | Обратная связь из содержания сообщений |
| regeneration | `regeneration` | Просьба пользователя сгенерировать ответ заново |
| inpainting | `inpainting` | Правка выбранной области картинки по подсказке |
| data flywheel | `data flywheel` | Маховик данных: больше пользователей, больше данных, лучше продукт |
| data donation | `data donation` | Пользователь делится данными о взаимодействии вместе с отзывом |
| response bias | `response bias` | Явный feedback смещён: чаще отвечают недовольные |
| leniency bias | `leniency bias` | Люди оценивают добрее, чем думают |
| recency bias | `recency bias` | Человек предпочитает вариант, который увидел последним |
| degenerate feedback loop | `degenerate feedback loop` | Модель усиливает свои смещения через обратную связь |
| exposure bias, popularity bias, filter bubble | `exposure bias`, `popularity bias`, `filter bubble` | Популярное показывают чаще и поэтому оно остаётся популярным |
| sycophancy | `sycophancy` | Подхалимство: модель говорит то, что хочет услышать пользователь |
| exploration | `exploration` | Часть показов делается случайной, чтобы проверять новое |
