---
title: "Почему Executors могут падать при длительной загрузке?"
head:
  - tag: title
    content: "Падение executors при длительной загрузке в Spark | Инжиниринг Данных"
description: "Почему после нескольких итераций может упасть executor pod и как проверить, связано ли это с ростом нативной памяти и аренами glibc."
prev: {"label":"Как работает Dynamic Resource Allocation?","link":"/interview/questions/spark/dynamic-allocation/"}
next: false
tableOfContents: false
editUrl: false
---

Представь, что одно Spark-приложение загружает год данных по месяцам. Несколько месяцев обработаны успешно, а на очередной итерации кластер разрастается или падает executor pod с `OOMKilled`.

Сначала отдели две разные ситуации — на собеседовании и в проде это первый шаг диагностики:

| Что именно растёт между месяцами | Что проверить в первую очередь |
| --- | --- |
| **Стало больше executor pods** | Сверь вкладку **Executors** с числом живых pods. Проверь `spark.dynamicAllocation.maxExecutors` (или `spark.executor.instances` без динамики) и убедись, что все месяцы идут в одном `Application ID`. |
| **Pods столько же, растёт Java heap или память Python** | Проверь базовые утечки: забытые кеши без `unpersist()`, broadcast-переменные без `destroy()`, накопленные Python-списки или разрастающиеся планы. `maxExecutors` эти объекты не освободит. |
| **Pods столько же, Java heap после GC возвращается на место, но pod получает `OOMKilled`** | Значит, растёт память **вне Java heap**: нативные буферы, Python workers или страницы, которые удерживает нативный аллокатор **glibc malloc**. |

Если базовые причины исключены, а резидентная память процесса (RSS) после каждого месяца остаётся чуть выше и на очередном пике пробивает лимит контейнера, стоит проверить, как **glibc malloc** переиспользует память между итерациями.

## Что такое арена malloc?

Когда нескольким потокам одновременно нужна память, glibc может обслуживать их через разные **арены**. Это уменьшает конкуренцию за одну блокировку. Когда библиотека освобождает временный буфер, место снова доступно аллокатору. Однако на той же странице памяти могут оставаться занятые блоки. В результате часть страниц остаётся у процесса, и его резидентная память (RSS) после месяца может снизиться лишь частично. При следующем пике новые выделения могут увеличить её ещё сильнее.

По умолчанию предел числа арен glibc зависит от числа процессоров, которое обнаружила библиотека. На 64-битных системах он обычно составляет до восьми арен на обнаруженное ядро. Это **верхний предел**: арены создаются по мере необходимости. [Настройки аллокатора glibc](https://sourceware.org/glibc/manual/latest/html_node/Memory-Allocation-Tunables.html)

## Как здесь связаны CPU и Kubernetes?

В Spark на Kubernetes за CPU отвечают три разные настройки — их важно не путать:

- **`spark.executor.cores`** — сколько слотов задач планирует сам Spark внутри одного executor (на Kubernetes по умолчанию `1`).
- **`spark.kubernetes.executor.request.cores`** — CPU request pod, по которому планировщик Kubernetes ищет место на узле.
- **`spark.kubernetes.executor.limit.cores`** — потолок процессорного времени контейнера через cgroup-квоту.

Namespace Kubernetes сам по себе не определяет, сколько CPU видит процесс. Отдельно может быть ограничен набор доступных CPU (`cpuset`). Поэтому, даже если ты выдал executor `spark.executor.cores=2`, процесс внутри контейнера может видеть все логические ядра большого узла (например, 32 или 64) — и glibc поднимет верхний предел арен пропорционально числу ядер узла, а JVM может создать избыточно большие внутренние пулы потоков. У glibc и JVM свои механизмы определения этого числа. [CPU в Spark на Kubernetes](https://spark.apache.org/docs/4.1.1/running-on-kubernetes.html#spark-properties) · [Ресурсы контейнеров Kubernetes](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

Для приложения с небольшим бюджетом CPU можно задать следующие параметры в `spark-defaults.conf` до запуска в режиме `cluster`.

```properties
spark.executorEnv.MALLOC_ARENA_MAX                 4
spark.kubernetes.driverEnv.MALLOC_ARENA_MAX        4
spark.executor.extraJavaOptions                    -XX:ActiveProcessorCount=2
spark.driver.extraJavaOptions                      -XX:ActiveProcessorCount=2
```

- **`MALLOC_ARENA_MAX=4`** ограничивает число арен glibc четырьмя **на процесс**. В образе с glibc значения 2 и 4 можно сравнить на одинаковой загрузке. Меньшее число арен иногда снижает RSS ценой большей конкуренции потоков. У процесса с другим аллокатором (например, musl или jemalloc) эта настройка может не дать эффекта.
- **`-XX:ActiveProcessorCount=2`** задаёт JVM два активных процессора для расчёта размеров внутренних пулов, например потоков GC. Проверить видимое JVM число CPU можно через `Runtime.getRuntime().availableProcessors()`. Если JVM уже видит два процессора (например, по cgroup-лимиту), этот флаг не уменьшит её пулы дополнительно. Квоту контейнера (`limit.cores`), число слотов Spark (`spark.executor.cores`) и лимит арен glibc задают отдельно.
- **Почему `extraJavaOptions`, а не `JAVA_TOOL_OPTIONS`?** В Spark стандартный способ передать флаги JVM — `spark.executor.extraJavaOptions` и `spark.driver.extraJavaOptions`. Передача через переменную окружения `spark.executorEnv.JAVA_TOOL_OPTIONS` тоже работает (и действует на любой JVM-процесс внутри контейнера), но **перезаписывает** переменную `JAVA_TOOL_OPTIONS`, если она уже была задана в Docker-образе — в таком случае старые флаги нужно сохранить вручную. [Параметры JVM](https://docs.oracle.com/en/java/javase/17/docs/specs/man/java.html) · [Настройки среды выполнения Spark](https://spark.apache.org/docs/4.1.1/configuration.html#runtime-environment)

## Как проверить гипотезу?

1. Для одного и того же executor сопоставь после каждого месяца **занятую heap после GC**, RSS процессов Java и Python и расход памяти контейнера. В cgroup v2 `memory.current` показывает общий расход, а `memory.stat` помогает отделить анонимную память (`anon`) от файлового кеша (`file`). [Метрики cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
2. Если heap возвращается к исходному уровню, а RSS процесса и `anon` растут, проверь нативные буферы, Python workers и удержание страниц аллокатором. По одному графику RSS отличить фрагментацию от утечки нельзя.
3. Повтори загрузку на тех же данных и с теми же ресурсами, меняя по одному параметру. Сравни пик памяти, уровень после каждого месяца и время обработки. Так видно, помогло ли ограничение арен и сколько это стоило по времени.
