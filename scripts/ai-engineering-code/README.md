# Код к конспекту AI Engineering

Только стандартная библиотека Python 3.10+ и DuckDB CLI (для SQL). Платных API нет.
Запуск из корня репозитория: `python3 scripts/ai-engineering-code/<файл>.py`.
Страницы глав собираются из шаблона командой `python3 scripts/ai-engineering-code/embed.py <шаблон.md> <страница.md>`: код и вывод на странице берутся из файлов и из настоящего запуска.
SQL-блоки на страницах проверяет `python3 scripts/kimball-diagrams/check_sql.py <страница.md>`.

Глава 7 использует `numpy`: `pip install -r scripts/ai-engineering-code/requirements-ch07.txt`. Остальные главы используют только стандартную библиотеку.

| Глава | Пример | Файл | Статус |
|---|---|---|---|
| 1 | Self-supervision на одном предложении, autoregressive и masked мини-модели, цена разметки | `ch01_language_models.py` | ok |
| 1 | Почему большим моделям нужно больше данных: bigram и trigram на разных объёмах | `ch01_model_size_data.py` | ok |
| 1 | Мини-BPE, правило «100 токенов ~ 75 слов», цена и время запроса к API (цены придуманы) | `ch01_tokens_cost.py` | ok |
| 1 | Crawl-Walk-Run: acceptance rate, ворота 95%, ложный «зелёный свет» на малой выборке | `ch01_crawl_walk_run.py` | ok |
| 1 | Build or buy и last mile в DuckDB (4 задания) | в `01-intro-ai-engineering.md` (`check_sql.py`) | ok |
| 2 | sampling: softmax, temperature, top-k, top-p, min-p, logprobs и underflow | `ch02_sampling.py` | ok |
| 2 | attention с нуля: Q, K, V, маска, головы, prefill и decode с KV cache | `ch02_attention.py` | ok |
| 2 | размер модели: параметры из размерностей, память, MoE, KV cache | `ch02_model_size.py` | ok |
| 2 | FLOPs, цена обучения GPT-3, правило 6·N·D, Chinchilla | `ch02_compute_scaling.py` | ok |
| 2 | игрушечный byte-level BPE: цена токенов на разных языках | `ch02_tokenizer.py` | ok |
| 2 | preference data: пары из ранга, loss Брэдли-Терри, reward model, best of N | `ch02_preference.py` | ok |
| 2 | test-time compute: средний logprob, self-consistency, best of N с verifier | `ch02_test_time_compute.py` | ok |
| 2 | structured outputs: маска logits, обрыв по токенам, защитный парсер | `ch02_structured_output.py` | ok |
| 3 | entropy, cross entropy, perplexity, BPC, BPB, мини-LM | `ch03_perplexity.py` | ok |
| 3 | functional correctness и pass@k | `ch03_functional_correctness.py` | ok |
| 3 | exact match, edit distance, n-gram, cosine | `ch03_similarity.py` | ok |
| 3 | AI judge: промпты и симуляция смещений | `ch03_judge_simulation.py` | ok |
| 3 | Elo и Bradley-Terry по матчам | `ch03_rating.py` | ok |
| 3 | матчи и win rate в DuckDB | в `03-evaluation-methodology.md` (check_sql.py) | ok |
| 4 | Проверки инструкций кодом (IFEval-стиль), чек-листы да/нет (INFOBench-стиль), формат против предметной области | `ch04_instruction_following.py` | ok |
| 4 | SAFE-стиль, SelfCheck-стиль и textual entailment на игрушечных данных | `ch04_factual_consistency.py` | ok |
| 4 | Расчёт: API или свой кластер, GPU и размер модели | `ch04_build_vs_buy.py` | ok |
| 4 | Hard attributes и пороги, среднее и mean win rate, корреляция benchmarks, свой leaderboard с весами | `ch04_model_selection.py` | ok |
| 4 | Data contamination: n-gram overlap, score на чистых примерах | `ch04_contamination.py` | ok |
| 4 | Bootstrap, размер evaluation set, шум и мощность теста | `ch04_bootstrap_sample_size.py` | ok |
| 4 | Мини-pipeline: компоненты, per turn и per task, цена проверок, журнал запуска | `ch04_pipeline.py` | ok |
| 4 | Таблица результатов оценки в DuckDB: срезы, доверительные интервалы, бизнес-соответствие, парадокс Симпсона | в `04-evaluate-ai-systems.md` (check_sql.py) | ok |
| 5 | тест `needle in a haystack`: стог из пар «ключ: значение», точность по позициям иглы | `ch05_niah_test.py` | ok |
| 5 | сборка `prompt` из частей, форматы few-shot, `chat template` Llama 2 и Llama 3, проверка итогового текста | `ch05_prompt_builder.py` | ok |
| 5 | разбор JSON-ответа, проверка по схеме, повтор с описанием ошибки | `ch05_structured_output.py` | ok |
| 5 | цепочка `prompts`: тип запроса и ответ, журнал шагов, цена и задержка, параллельность | `ch05_prompt_chain.py` | ok |
| 5 | игрушечный автоподбор `prompt` (мутации, `dev` и `test`, число вызовов) | `ch05_prompt_search.py` | ok |
| 5 | цена few-shot, повтора `system prompt`, длинного контекста и скрытых вызовов инструмента | `ch05_cost_estimate.py` | ok |
| 5 | `prompt catalog`: версии, метаданные, закрепление версий, разбор `.prompt`-файла | `ch05_prompt_catalog.py` | ok |
| 5 | стенд защиты от `prompt injection`: 9 атак, 6 безобидных запросов, пять слоёв, два показателя | `ch05_injection_harness.py` | ok |
| 6 | Стратегии chunking: символы, слова, предложения, рекурсивно, overlap, по токенам, размер и число vectors | `ch06_chunking.py` | ok |
| 6 | Term-based retrieval с нуля: токенизация, inverted index, TF-IDF, BM25 | `ch06_term_retrieval.py` | ok |
| 6 | Embedding-based retrieval на игрушечных embeddings: cosine, k-NN, многозначные слова, слабое место | `ch06_embedding_search.py` | ok |
| 6 | ANN: точный k-NN против IVF и LSH (recall и число проверок) | `ch06_ann_search.py` | ok |
| 6 | Общая библиотека для hybrid и оценки: корпус, BM25, embeddings, RRF | `ch06_retrieval_lib.py` | ok (библиотека, подключается) |
| 6 | Hybrid search, RRF, reranking, время и порядок в контексте | `ch06_hybrid_rerank.py` | ok |
| 6 | Оценка retrieval: precision, recall, MRR, MAP, NDCG для BM25, embeddings и hybrid | `ch06_retrieval_eval.py` | ok |
| 6 | Query rewriting и contextual retrieval | `ch06_query_context.py` | ok |
| 6 | Function calling: tools, tool_choice, проверка вызова, read/write и подтверждение | `ch06_function_calling.py` | ok |
| 6 | Агент: план, проверка плана, ReAct-трасса, reflection на SQLite, параллельные шаги | `ch06_agent_loop.py` | ok |
| 6 | Оценка агента: накопление ошибок, planning dataset, ablation, переходы, intent classifier | `ch06_agent_eval.py` | ok |
| 6 | Память: бюджет контекста, FIFO, long-term, summary, противоречия | `ch06_memory.py` | ok |
| 6 | Chunks, inverted index, BM25, RRF, метрики retrieval, лог агента и аудит write-действий в DuckDB (задания) | в `06-rag-and-agents.md` (`check_sql.py`: OK, 15 блоков) | ok |
| 7 | Помощник «prompt, RAG или finetuning»: правила главы на примерах (stdlib) | `ch07_finetune_or_rag.py` | ok |
| 7 | Калькулятор памяти: inference, полный finetuning, LoRA, QLoRA (stdlib) | `ch07_memory_calculator.py` | ok |
| 7 | Числовые форматы FP32/FP16/BF16/TF32 и quantization INT8/INT4 (stdlib) | `ch07_number_formats.py` | ok |
| 7 | LoRA на маленьких матрицах: факторизация, W' = W + (α/r)·A·B, ранги, multi-LoRA (numpy) | `ch07_lora_math.py` | ok |
| 7 | Model merging на игрушечных моделях: среднее, task vectors, SLERP, pruning, concatenation (numpy) | `ch07_model_merging.py` | ok |
| 7 | Ручки finetuning: learning rate, epochs, batch size, accumulation, prompt loss weight (numpy) | `ch07_training_knobs.py` | ok |
| 8 | quality x diversity, кривая «качество от объёма», подгонка кривой, бюджет | `ch08_quality_quantity.py` | ok |
| 8 | rule-based синтез, аугментация, perturbation, simulation | `ch08_synth_rules.py` | ok |
| 8 | синтез instruction data по плану тем и фильтры Self-Instruct | `ch08_instruction_synth.py` | ok |
| 8 | preference-пары от AI-судьи, обмен позиций против position bias | `ch08_pref_pairs.py` | ok |
| 8 | проверка синтетического кода: parser, linter, tests, repair, back-translation | `ch08_synth_verify.py` | ok |
| 8 | model collapse на игрушечной модели | `ch08_model_collapse.py` | ok |
| 8 | дедупликация: hash, shingles, MinHash, LSH, утечка train/test | `ch08_dedup.py` | ok |
| 8 | формат: few-shot в обучающие примеры, chat template, JSONL, проверка записей | `ch08_format.py` | ok |
| 8 | конвейер качества данных в DuckDB: inspect, очистка, PII, дубли, конфликты, утечка, разметчики | в `08-dataset-engineering.md` (check_sql.py) | ok |
| 9 | TTFT, TPOT, перцентили, throughput, goodput по журналу запросов | `ch09_latency_metrics.py` | ok |
| 9 | цена decode и prefill, batch API, prompt caching: калькулятор | `ch09_cost_calculator.py` | ok |
| 9 | MFU, MBU, потолок скорости decode, кейс PyTorch, игрушечная roofline-модель | `ch09_mfu_mbu.py` | ok |
| 9 | формула размера KV cache, приёмы сжатия, крошечный attention с кэшем и без | `ch09_kv_cache.py` | ok |
| 9 | speculative decoding: игрушечные модели, формула токенов за цикл, таблица ускорения | `ch09_speculative.py` | ok |
| 9 | static, dynamic и continuous batching в симуляции | `ch09_batching_sim.py` | ok |
| 9 | prefix cache: блоки по 16 токенов, порядок частей prompt, диалог | `ch09_prompt_cache.py` | ok |
| 9 | tensor, pipeline и replica parallelism, bin packing | `ch09_parallelism.py` | ok |
| 9 | журнал вызовов LLM в DuckDB: перцентили, goodput, цена, 4 задания | в `09-inference-optimization.md` (check_sql.py) | ok |
| 10 | маскирование PII и reverse map, output guardrail, retry и параллельные вызовы, false refusal rate | `ch10_guardrails.py` | ok |
| 10 | router по намерению, лимит контекста, мини-gateway (доступ, лимит токенов, fallback), экономия от router | `ch10_router_gateway.py` | ok |
| 10 | exact и semantic cache, порог похожести, утечка через кэш, LRU | `ch10_cache.py` | ok |
| 10 | весь игрушечный пайплайн: orchestrator, guardrails, router, кэш, mock-модель, trace | `ch10_pipeline.py` | ok |
| 10 | position bias, вырожденная петля обратной связи, «кошачий рай» | `ch10_feedback_loop.py` | ok |
| 10 | логи, метрики по дням, drift, trace, MTTD/MTTR/CFR, явная и неявная обратная связь в DuckDB | в `10-architecture-and-user-feedback.md` (check_sql.py) | ok |
