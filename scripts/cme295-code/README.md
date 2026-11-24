# Код курса CME295

Запуск из корня: `python3 -I scripts/cme295-code/<файл>.py`. Зависимости: `requirements.txt`.

## Лекция 1

Код и вывод на странице совпадают с файлами. Проверка: `python3 -I scripts/lecture-tools/check_code.py <страница.md> scripts/cme295-code --prefix lec01 --python <venv>/bin/python`.

| Лекция | Пример | Файл | Статус |
|---|---|---|---|
| 1 | BPE на маленьком корпусе | lec01_bpe.py | ok |
| 1 | Self-attention и causal mask на numpy | lec01_attention.py | ok |
| 1 | Задача 1: токенизатор по слияниям BPE | lec01_task1.py | ok |
| 1 | Задача 2: синусоидальный positional embedding | lec01_task2.py | ok |
| 1 | Задача 3: деление на sqrt(d_k) | lec01_task3.py | ok |

## Статус примеров

| Лекция | Пример | Файл | Статус |
|---|---|---|---|
| 1 | BPE на маленьком корпусе | lec01_bpe.py | ok |
| 1 | Self-attention и causal mask на numpy | lec01_attention.py | ok |
| 1 | Внимание для одного токена «teddy bear» | lec01_tiny_attention.py | ok |
| 1 | Задача 1: токенизатор по слияниям BPE | lec01_task1.py | ok |
| 1 | Задача 2: синусоидальный positional embedding | lec01_task2.py | ok |
| 1 | Задача 3: деление на sqrt(d_k) | lec01_task3.py | ok |
| 2 | Chinchilla: токены, параметры и бюджет | lec02_scaling.py | ok |
| 2 | Sparse MoE и load balancing loss на numpy | lec02_moe.py | ok |
| 2 | Синусоидальный embedding и RoPE: зависимость от разницы позиций | lec02_rope.py | ok |
| 2 | Размер KV-кэша для MHA, GQA, MQA | lec02_kv.py | ok |
| 2 | temperature, top-k, top-p, недетерминизм float | lec02_decoding.py | ok |
| 2 | LayerNorm и RMSNorm | lec02_norm.py | ok |
| 2 | Задача 1: токены на параметр | lec02_task1.py | ok |
| 2 | Задача 2: top-p руками | lec02_task2.py | ok |
| 2 | Задача 3: окно и число слоёв | lec02_task3.py | ok |
| 3 | Кросс-энтропия и bits per byte | lec03_loss.py | ok |
| 3 | LoRA: параметры и механика | lec03_lora.py | ok |
| 3 | Bradley-Terry и маленькая модель вознаграждения | lec03_reward.py | ok |
| 3 | Задача 1: SFT loss только по ответу | lec03_task1.py | ok |
| 3 | Задача 2: интерполяция позиций | lec03_task2.py | ok |
| 3 | Задача 3: DPO loss | lec03_task3.py | ok |
| 4 | Градиент политики и baseline на трёх ответах | lec04_policy_gradient.py | ok |
| 4 | Выборка по значимости и обрезка PPO | lec04_ppo_clip.py | ok |
| 4 | Преимущество по группе в GRPO и вес токена при нормализации | lec04_grpo.py | ok |
| 4 | Прямая и обратная KL, штраф по токенам в OPD | lec04_kl.py | ok |
| 4 | Задача 1: преимущество по группе | lec04_task1.py | ok |
| 4 | Задача 2: член цели PPO с обрезкой | lec04_task2.py | ok |
| 4 | Задача 3: KL в двух направлениях | lec04_task3.py | ok |
| 5 | FlashAttention: `softmax` по блокам равен обычному, устойчив в float16 | lec05_flash.py | ok |
| 5 | Память обучения и стадии ZeRO для 100 млрд параметров | lec05_memory.py | ok |
| 5 | Roofline: умножение матрицы при разном размере пачки | lec05_roofline.py | ok |
| 5 | Размер KV-кэша: MHA, GQA, MLA; запросы в памяти с PagedAttention | lec05_kvcache.py | ok |
| 5 | Спекулятивное декодирование сохраняет распределение целевой модели | lec05_speculative.py | ok |
| 5 | Задача 1: ZeRO для 70 млрд параметров на GPU по 80 ГБ | lec05_task1.py | ok |
| 5 | Задача 2: размер KV-кэша на 32 000 токенов | lec05_task2.py | ok |
| 5 | Задача 3: токены за проход и выигрыш спекулятивного декодирования | lec05_task3.py | ok |
| 6 | Семантический поиск, BM25 и гибрид | lec06_rag.py | ok |
| 6 | NDCG, RR, recall, precision | lec06_metrics.py | ok |
| 6 | Вызов инструментов: описание и три шага | lec06_tools.py | ok |
| 6 | Цикл ReAct с лимитом шагов | lec06_react.py | ok |
| 6 | Задача 1: фрагменты с перекрытием | lec06_task1.py | ok |
| 6 | Задача 2: порядок запроса и цена кэша | lec06_task2.py | ok |
| 6 | Задача 3: MRR и recall@3 | lec06_task3.py | ok |
| 7 | Доля совпадений и каппа Коэна | lec07_kappa.py | ok |
| 7 | pass@k: формула, симуляция, consensus@k | lec07_passk.py | ok |
| 7 | Position bias судьи и проверка обменом местами | lec07_judge.py | ok |
| 7 | Задача 1: pass@1 и pass@5 по набору задач | lec07_task1.py | ok |
| 7 | Задача 2: precision, recall и каппа судьи против человека | lec07_task2.py | ok |
| 7 | Задача 3: граница Парето | lec07_task3.py | ok |

### Заметки по лекциям

- Лекция 2: Проверка: `python3 -I scripts/lecture-tools/check_code.py <страница.md> scripts/cme295-code --prefix lec02 --python <venv>/bin/python`.
- Лекция 7: Запуск из корня: `python3 -I scripts/cme295-code/<файл>.py`. Нужен `numpy` (см. `requirements.txt`).
