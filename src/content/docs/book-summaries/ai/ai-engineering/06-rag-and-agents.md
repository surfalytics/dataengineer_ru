---
title: "AI Engineering, глава 6: RAG и агенты"
head:
  - tag: title
    content: "RAG и AI-агенты: поиск, tools, planning, memory | Инжиниринг Данных"
description: "Подробный конспект главы 6 AI Engineering на русском: RAG, BM25, embeddings, hybrid search, chunking, агенты, tools, planning, memory."
sidebar:
  order: 6
  label: "6. RAG и агенты"
tags:
  - books
  - ai
  - rag
  - agents
---

**Главная мысль:** Модель отвечает хорошо, только если у неё есть нужный контекст. Без него она чаще ошибается и выдумывает. В главе два способа построить контекст для каждого запроса. `RAG` ищет данные во внешней памяти и кладёт их в prompt. Агент идёт дальше: он сам вызывает инструменты, планирует шаги и проверяет результат. Оба способа меняют только вход модели, а не саму модель.

## О чём глава

Чтобы решить задачу, модели нужны две вещи: инструкция, как решать, и информация для решения. Человек без нужных сведений чаще даёт неверный ответ. Модель так же: если ей не хватает контекста, она чаще ошибается и галлюцинирует. В приложении инструкции одинаковы для всех запросов. А контекст у каждого запроса свой.

В [главе 5](/book-summaries/ai/ai-engineering/05-prompt-engineering/) мы учились писать инструкции. Эта глава про второе: как собрать подходящий контекст для каждого запроса. Автор называет два главных способа:

- **`RAG`** (`retrieval-augmented generation`): модель получает релевантные данные из внешних источников.
- **Агенты** (`agents`): модель сама использует инструменты (`tools`), например веб-поиск или API новостей, чтобы собрать информацию.

`RAG` в основном строит контекст. Агентный подход умеет больше. Инструменты закрывают слабые места модели и расширяют её возможности. Главное: они дают модели возможность действовать в реальном мире и автоматизировать многие дела. Оба подхода быстро завоевали воображение: появилось много демо и продуктов, и многие уверены, что это и есть будущее.

Что внутри главы:

- `RAG`: идея, архитектура и зачем он нужен при длинном контексте;
- алгоритмы поиска: term-based (`BM25`) и embedding-based (vector search), их сравнение и hybrid search;
- как улучшить поиск: `chunking`, `reranking`, переписывание запроса, contextual retrieval;
- как оценивать retrieval и как выбирать решение для поиска;
- `RAG` для картинок и для таблиц (text-to-SQL);
- агенты: что это такое, инструменты, планирование, reflection, выбор инструментов;
- сбои агента и как их оценивать;
- память (`memory`) для `RAG` и агентов;
- практика: код на Python и SQL в DuckDB, который воспроизводит идеи главы.

Следующая [глава 7](/book-summaries/ai/ai-engineering/07-finetuning/) покажет другой путь: менять не вход модели, а саму модель.

![Карта главы 6: контекст для запроса строят RAG, агенты и память; у каждого направления свои подтемы](/assets/ai-engineering/ch06-rag-agents-map.png)

Как читать схему. Сверху общая задача: собрать контекст для запроса. Слева `RAG`: как искать, как улучшать поиск и как работать не только с текстом. В центре агенты: инструменты, планирование и сбои. Справа память: знания в весах, контекст и внешнее хранилище. Пунктирная стрелка показывает, что `RAG` — частный случай агента: retriever здесь просто один из инструментов.

## RAG: найти данные и дать их модели

### Что такое RAG и откуда он взялся

`RAG` — это приём, который улучшает ответ модели с помощью информации, найденной во внешнем хранилище. Хранилищем (`external memory`) может быть внутренняя база данных, прошлые чаты пользователя или интернет.

Идею «сначала найти, потом сгенерировать» впервые показали в работе Chen et al. (2017) «Reading Wikipedia to Answer Open-Domain Questions». Система там сначала выбирает пять страниц Wikipedia, самых подходящих к вопросу. Потом модель читает эти страницы и формирует ответ. Авторы назвали модель «читателем документов» (`document reader`). Это была рекуррентная сеть `LSTM`. До появления архитектуры transformer в 2018 году `LSTM` была главной архитектурой глубокого обучения для текста.

![Схема «найти, потом прочитать»: вопрос, document retriever выбирает страницы Wikipedia, document reader выдаёт ответ](/assets/ai-engineering/ch06-retrieve-then-read.png)

Как читать схему. Слева вопрос. Retriever берёт из всей Wikipedia пять страниц. Reader читает только их и выдаёт короткий ответ. Так модели не нужно держать в голове всю энциклопедию.

Сам термин `retrieval-augmented generation` ввели Lewis et al. (2020) в работе «Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks». Они предложили `RAG` для задач, где знаний слишком много, чтобы подать их в модель целиком. С `RAG` в модель попадает только то, что retriever нашёл самым релевантным запросу. Авторы заметили, что доступ к нужной информации помогает модели давать более подробные ответы и реже галлюцинировать.

> **Заметка автора.** Примерно тогда же вышла ещё одна работа Facebook: Petroni et al. (2020), «How Context Affects Language Models' Factual Predictions». Она показала, что добавление системы поиска к предобученной языковой модели сильно улучшает ответы на фактические вопросы.

Пример. Пользователь спрашивает: «Сможет ли принтер Acme fancy-printer-A300 напечатать 100 страниц?» Модель ответит лучше, если получит технические характеристики этого принтера. Без них она будет гадать.

Удобно думать о `RAG` так: вместо одного контекста для всех запросов мы собираем отдельный контекст для каждого. Это помогает и с пользовательскими данными. Данные конкретного пользователя можно класть в контекст только тех запросов, которые к нему относятся.

> **Пояснение.** Для data engineer это знакомая мысль. Контекст — это то, что в классическом ML называют признаками. Автор прямо пишет: построение контекста для foundation model — это аналог `feature engineering` для классической модели. Цель та же: дать модели информацию, нужную, чтобы обработать вход.

### Зачем RAG, если контекст моделей растёт

В первые годы foundation models `RAG` был одним из самых частых приёмов. Главная его цель была в том, чтобы обойти ограничение длины контекста. Многие считают, что достаточно длинный контекст убьёт `RAG`. Автор с этим не согласен, и у него два аргумента.

**Первый аргумент: данных всегда больше.** Какой бы длинный контекст ни был у модели, найдутся приложения, которым нужно ещё больше. Объём данных растёт: люди создают и добавляют новые данные и редко что-то удаляют. Длина контекста тоже растёт, но не так быстро, как аппетит приложений.

> **Заметка автора.** Автор сравнивает это с законом Паркинсона: «работа заполняет всё время, отпущенное на неё». Его теория такая: контекст приложения расширяется, пока не заполнит предел, который поддерживает модель.

**Второй аргумент: длинный контекст модель использует не всегда хорошо.** Об этом говорилось в главе 2, в разделе про длину контекста. Чем длиннее контекст, тем вероятнее, что модель сосредоточится не на той части. Кроме того, каждый лишний токен стоит денег и может добавить задержку (`latency`). `RAG` позволяет для каждого запроса взять только самое нужное. Входных токенов становится меньше, а качество ответа растёт.

Обе линии развиваются параллельно: одни работают над длиной контекста, другие учат модели лучше его использовать. Автор не удивится, если провайдер встроит в модель механизм поиска или внимания, который сам выделяет важные части контекста.

> **Заметка автора.** Anthropic советует для моделей Claude: если ваша база знаний меньше 200 000 токенов (около 500 страниц), можно положить её в prompt целиком, без `RAG`. Автор хотел бы, чтобы другие провайдеры дали похожие рекомендации про выбор между `RAG` и длинным контекстом.

## Архитектура RAG

В системе `RAG` два компонента:

- **`Retriever`** достаёт информацию из внешней памяти;
- **`Generator`** (генеративная модель) пишет ответ по найденной информации.

Пользователь отправляет запрос. Он идёт и в retriever, и в generator. Retriever находит в памяти нужный контекст и передаёт его generator. Generator видит запрос и найденный контекст и пишет ответ.

![Базовая архитектура RAG: пользователь, retriever с внешней памятью, generative model и ответ](/assets/ai-engineering/ch06-rag-architecture.png)

Как читать схему. Внешняя память подключена к retriever. Запрос пользователя идёт по двум дорожкам: к retriever, чтобы найти данные, и напрямую к generative model. Найденный контекст тоже идёт к generative model. Ответ возвращается пользователю.

В оригинальной работе Lewis et al. retriever и генеративную модель обучали вместе. Сейчас компоненты часто обучают отдельно. Многие команды собирают `RAG` из готовых retriever и модели. Но дообучение всей системы целиком может заметно улучшить её качество.

**Успех `RAG` зависит от качества retriever.** У retriever две главные функции:

- **индексация** (`indexing`): подготовка данных так, чтобы потом их можно было быстро найти;
- **запрос** (`querying`): отправка запроса и получение релевантных данных.

То, как вы индексируете данные, зависит от того, как вы будете их искать.

Теперь пример. Пусть внешняя память — база документов компании: заметки, договоры, протоколы встреч. Один документ может занимать 10 токенов, а может миллион. Если извлекать документы целиком, контекст может стать сколь угодно длинным. Поэтому каждый документ режут на небольшие части — `chunks`. Как резать, мы разберём позже. Пока считаем, что документы уже разбиты на удобные куски. Задача — для каждого запроса найти куски, самые релевантные ему. Часто нужна небольшая обработка, чтобы объединить найденные куски с prompt в итоговый prompt. Его и получает generative model.

> **Заметка автора.** В этой главе слово «документ» означает и «документ», и «chunk». Технически chunk документа — тоже документ. Так автор согласует терминологию книги с классической терминологией NLP и информационного поиска (`information retrieval`, IR).

## Алгоритмы поиска (retrieval)

Поиск — не изобретение `RAG`. Это очень старая идея: автоматизировать поиск информации пытались ещё в 1920-е годы. Поиск лежит в основе поисковых систем, рекомендательных систем, анализа логов и многого другого. Многие алгоритмы, созданные для классических систем поиска, подходят и для `RAG`.

> **Заметка автора.** Первые описания информационного поиска есть в патентах Эмануэля Гольдберга 1920-х годов: он описал «статистическую машину» для поиска документов на микрофильмах.

Область информационного поиска (`information retrieval`) большая, у неё есть целая индустрия. На нескольких страницах её не описать. Поэтому автор показывает только общие очертания. Дополнительные материалы лежат в GitHub-репозитории книги.

> **Заметка автора.** Строго говоря, `retrieval` обычно ограничен одной базой или одной системой, а `search` (поиск) может идти по разным системам. В главе автор использует эти слова как синонимы.

Суть поиска проста: оценить, насколько каждый документ подходит запросу. Алгоритмы отличаются тем, как считают эту оценку релевантности (`relevance score`). Сначала два самых распространённых механизма: term-based и embedding-based.

### Sparse и dense: почему книга делит иначе

В литературе алгоритмы часто делят на `sparse` и `dense`. Книга выбрала другое деление: term-based и embedding-based. Вот почему.

- **Sparse retriever** хранит данные в разреженных векторах: у большинства элементов значение 0. Term-based поиск считается разреженным, потому что каждый термин можно записать как one-hot вектор: везде 0, кроме одной единицы. Длина вектора равна размеру словаря. Единица стоит на месте, которое соответствует номеру термина в словаре. Например, при словаре `{"food": 0, "banana": 1, "slug": 2}` векторы слов будут `[1, 0, 0]`, `[0, 1, 0]` и `[0, 0, 1]`.
- **Dense retriever** хранит данные в плотных векторах: у большинства элементов значение не 0. Embedding-based поиск обычно называют dense, потому что embeddings чаще всего плотные.

Но бывают и разреженные embeddings. Например, `SPLADE` (Sparse Lexical and Expansion, Formal et al., 2021) берёт embeddings от BERT и с помощью регуляризации обнуляет большинство значений. Разреженность делает операции эффективнее.

При делении на sparse и dense `SPLADE` попадает в одну группу с term-based алгоритмами. Но по принципу работы, сильным и слабым сторонам он гораздо ближе к dense embedding retrieval. Деление на term-based и embedding-based избегает этой ошибки в классификации.

### Term-based retrieval

Самый простой способ найти релевантные документы — искать по ключевым словам. Такой подход иногда называют лексическим поиском (`lexical retrieval`). Например, по запросу «AI engineering» система найдёт все документы, где есть эта фраза. У подхода две проблемы.

**Проблема 1: термин может встречаться во многих документах.** Тогда в контекст модели все они не влезут. Нужна эвристика, как выбрать. Простая идея: брать документы, где термин встречается чаще всего. Логика такая: чем чаще слово в документе, тем документ релевантнее этому слову. Частоту термина в документе называют **`term frequency`** (`TF`).

**Проблема 2: запрос может быть длинным, а термины в нём неравноценны.** Возьмём запрос «easy recipes for vietnamese food to cook at home». В нём несколько терминов, и информативны из них не все. Слова «vietnamese» и «recipes» говорят много, а «for» и «at» почти ничего. Нужен способ найти важные термины.

Идея: чем больше документов содержат термин, тем он менее информативен. Служебные слова есть почти в каждом документе. Поэтому важность термина обратно пропорциональна числу документов с ним. Эту метрику называют **`inverse document frequency`** (`IDF`). Чтобы её посчитать, считаем документы с термином и делим общее число документов на это число. Если документов 10, а термин есть в 5 из них, то IDF равна 10 / 5 = 2. Чем выше IDF, тем термин важнее.

> **Пояснение.** На практике от этого отношения берут логарифм: так редкие термины не получают огромный вес. Именно так IDF записана в формуле ниже и в нашем коде.

**`TF-IDF`** объединяет обе метрики. Обозначим:

- `t₁, t₂, …, t_q` — термины запроса `Q`;
- `f(t, D)` — сколько раз термин `t` встречается в документе `D`;
- `N` — число всех документов, `C(t)` — число документов, содержащих `t`;
- `IDF(t) = log(N / C(t))`.

Тогда наивный балл документа `D` для запроса `Q`:

```text
Score(D, Q) = сумма по всем терминам запроса: IDF(tᵢ) × f(tᵢ, D)
```

Читать так: для каждого слова запроса берём его вес `IDF` и умножаем на то, сколько раз слово встречается в документе. Потом складываем. Документы с высоким баллом идут первыми.

Две популярные реализации term-based поиска — Elasticsearch и BM25.

**Elasticsearch** (Shay Banon, 2010) построен на Lucene. Он хранит данные в структуре **inverted index** (инвертированный индекс). Это словарь: термин → документы, где он встречается. Благодаря ему документы с нужным термином находятся быстро. В индексе можно хранить и дополнительное: частоту термина и число документов с ним. Это нужно для расчёта TF-IDF. Вот упрощённый пример индекса (наши данные):

| Термин | Документов | (номер документа, частота термина) |
|---|---|---|
| pipeline | 3 | (2, 4), (7, 1), (9, 6) |
| airflow | 2 | (2, 3), (9, 1) |
| retry | 4 | (1, 2), (2, 1), (7, 5), (9, 2) |

По термину `airflow` сразу видно: он есть в документах 2 и 9, в первом три раза, во втором один. Просматривать все документы не нужно.

**Okapi BM25** — «25-е поколение алгоритма Best Matching». Его придумали Robertson и коллеги в 1980-х. Балл BM25 — это вариация TF-IDF. Главное отличие: BM25 нормализует частоту термина по длине документа. Длинные документы чаще содержат любой термин, и у них выше сырая частота. Без поправки длинные документы выигрывали бы без причины.

> **Пояснение.** В нашем коде используется стандартная форма BM25: `IDF × tf × (k1 + 1) / (tf + k1 × (1 − b + b × длина / средняя длина))`. Параметр `k1` ограничивает рост от повторов одного слова. Параметр `b` включает поправку на длину. Типичные значения: `k1 = 1,5`, `b = 0,75`.

BM25 и его варианты (BM25+, BM25F) до сих пор широко применяют. Они служат отличной базой (`baseline`), с которой сравнивают более сложные алгоритмы, например embedding-based поиск.

> **Заметка автора.** Aravind Srinivas, CEO Perplexity, написал в Twitter: «Трудно реально улучшить BM25 или полнотекстовый поиск». Тем, кто хочет глубже понять BM25, автор советует работу самих авторов: «The Probabilistic Relevance Framework: BM25 and Beyond» (Robertson и Zaragoza, 2009).

**Токенизация.** Есть процесс, о котором автор пока не сказал: токенизация, то есть разбиение запроса на термины. Проще всего разбить на слова. Но так составные термины теряют смысл. Например, «hot dog» превращается в «hot» и «dog», и ни одно слово не сохраняет смысл исходного термина. Выход: считать частые n-grams отдельными терминами. Если биграмма «hot dog» часто встречается, она становится одним термином.

Кроме того, обычно приводят текст к нижнему регистру, убирают знаки препинания и стоп-слова (`the`, `and`, `is`). Решения для term-based поиска часто делают это сами. Токенизацию умеют и классические пакеты NLP: NLTK, spaCy, Stanford CoreNLP.

**Поиск по пересечению n-grams.** В главе 3 мы мерили лексическое сходство двух текстов по пересечению n-grams. Можно ли искать документы по пересечению n-grams с запросом? Да. Но подход работает лучше всего, когда запрос и документы примерно одной длины. Если документы намного длиннее запроса, они почти наверняка содержат n-grams запроса. Тогда у многих документов будет похожий высокий балл, и настоящие релевантные документы трудно отличить от слабых.

Ниже пример на Python. Мы строим inverted index, считаем IDF, наивный TF-IDF и BM25 и проверяем сильные и слабые стороны term-based поиска.

<details>
<summary>Код: ch06_term_retrieval.py</summary>

```python
"""Глава 6: term-based retrieval с нуля: токенизация, inverted index, TF-IDF и BM25.
Показывает: как строится inverted index, как считают TF, IDF и итоговый балл, чем BM25
отличается от наивного TF-IDF (нормализация по длине документа), сильные стороны
(точный код ошибки) и слабые стороны (синонимы, многозначные слова) term-based поиска.
Запуск: python3 -I scripts/ai-engineering-code/ch06_term_retrieval.py   (только стандартная библиотека)"""
import math
import re
from collections import Counter, defaultdict

DOCS = {
    "d1": "Transformer architecture: self-attention lets a neural network weigh every token against every other token.",
    "d2": "A power transformer changes the voltage of electricity between two circuits using coils.",
    "d3": "Transformers is a film series about robots that turn into cars.",
    "d4": "Error EADDRNOTAVAIL (99) means the address you try to bind is not available on this machine.",
    "d5": "How to reset your password: click Forgot password on the login page and follow the email link.",
    "d6": "I cannot sign in to my account after changing the phone number.",
    "d7": "Refund policy: you can return a product within 30 days and get your money back.",
    "d8": "Our delivery takes three to five days. Express delivery arrives the next day.",
    "d9": "Hot dog recipe for beginners: grill the sausage and warm the bun.",
    "d10": "Embedding models turn text into vectors so that similar meaning gives close vectors.",
    "d11": "BM25 ranks documents by term frequency, inverse document frequency and document length.",
    "d12": "Vector database stores embeddings and finds nearest neighbors quickly.",
}
STOP = {"a", "the", "of", "to", "in", "on", "is", "and", "you", "your", "how", "can", "i", "my", "that", "so", "by",
        "for", "this", "into", "it", "an", "or", "with", "every", "other", "our", "after", "about", "against"}


def tokenize(text):
    """Нижний регистр, только слова и числа, без стоп-слов."""
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


print("== 1. Токенизация и inverted index")
tokens = {d: tokenize(t) for d, t in DOCS.items()}
print("d1 ->", tokens["d1"])
index = defaultdict(dict)  # term -> {doc: частота term в doc}
for d, toks in tokens.items():
    for term, f in Counter(toks).items():
        index[term][d] = f
for term in ("transformer", "vectors", "delivery", "eaddrnotavail"):
    print(f"{term:14s} документов: {len(index[term])}  (doc, частота): {sorted(index[term].items())}")

N = len(DOCS)


def idf_naive(term):
    """IDF по книге: log(N / C(t)), C(t) — число документов с термином."""
    return math.log(N / len(index[term])) if term in index else 0.0


def tfidf_score(query, doc):
    """Наивный TF-IDF: сумма IDF(t) * f(t, D) по терминам запроса."""
    f = Counter(tokens[doc])
    return sum(idf_naive(t) * f[t] for t in tokenize(query))


print("\n== 2. IDF: редкие термины важнее частых")
for term in ("days", "transformer", "vectors", "eaddrnotavail"):
    print(f"IDF({term}) = log({N}/{len(index[term])}) = {idf_naive(term):.2f}")

AVG_LEN = sum(len(t) for t in tokens.values()) / N


def idf_bm25(term):
    n = len(index.get(term, {}))
    return math.log(1 + (N - n + 0.5) / (n + 0.5))


def bm25_score(query, doc, k1=1.5, b=0.75):
    """BM25: насыщение частоты (k1) и нормализация по длине документа (b)."""
    f = Counter(tokens[doc])
    length = len(tokens[doc])
    score = 0.0
    for t in tokenize(query):
        if f[t]:
            tf = f[t] * (k1 + 1) / (f[t] + k1 * (1 - b + b * length / AVG_LEN))
            score += idf_bm25(t) * tf
    return score


def search(query, scorer, k=3):
    scored = sorted(((scorer(query, d), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [(d, round(s, 2)) for s, d in scored[:k] if s > 0]


print("\n== 3. Поиск: TF-IDF и BM25")
for q in ("transformer architecture neural network", "vector nearest neighbors", "EADDRNOTAVAIL (99)"):
    print(f"запрос: {q!r}")
    print("  TF-IDF:", search(q, tfidf_score))
    print("  BM25  :", search(q, bm25_score))

print("\n== 4. Длинный документ: BM25 гасит эффект длины")
short = "refund policy refund"
long_ = "refund " + " ".join(["lorem"] * 60) + " refund"
tokens["s"], tokens["l"] = tokenize(short), tokenize(long_)
for t in ("s", "l"):
    for term, f in Counter(tokens[t]).items():
        index[term][t] = f
N += 2
AVG_LEN = sum(len(t) for t in tokens.values()) / len(tokens)
print(f"короткий документ: длина {len(tokens['s'])}, refund встречается 2 раза")
print(f"длинный документ : длина {len(tokens['l'])}, refund встречается 2 раза")
print(f"TF-IDF: короткий {tfidf_score('refund', 's'):.2f}, длинный {tfidf_score('refund', 'l'):.2f}  (одинаково, длина не учтена)")
print(f"BM25  : короткий {bm25_score('refund', 's'):.2f}, длинный {bm25_score('refund', 'l'):.2f}  (длинный документ получает меньше)")
N -= 2

print("\n== 5. Слабое место: нет общих слов — нет результата")
for q in ("I lost access to my profile", "how fast will my order arrive"):
    print(f"запрос: {q!r} -> BM25: {search(q, bm25_score)}")
print("«profile» и «access» не встречаются в d5/d6, «arrive» не равно «arrives». Term-based поиск не знает синонимов.")

print("\n== 6. Токены из нескольких слов: «hot dog»")
print("по словам      :", tokenize("hot dog recipe"))
bigram_terms = {"hot dog"}


def tokenize_with_bigrams(text):
    words = [t for t in re.findall(r"[a-z0-9]+", text.lower())]
    out, i = [], 0
    while i < len(words):
        if i + 1 < len(words) and f"{words[i]} {words[i + 1]}" in bigram_terms:
            out.append(f"{words[i]} {words[i + 1]}")
            i += 2
        else:
            if words[i] not in STOP:
                out.append(words[i])
            i += 1
    return out


print("с bigram-токеном:", tokenize_with_bigrams("hot dog recipe"))
print("Частый bigram считаем одним термином, иначе «hot» и «dog» теряют смысл.")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_term_retrieval.py`. Реальный вывод:

```text
== 1. Токенизация и inverted index
d1 -> ['transformer', 'architecture', 'self', 'attention', 'lets', 'neural', 'network', 'weigh', 'token', 'token']
transformer    документов: 2  (doc, частота): [('d1', 1), ('d2', 1)]
vectors        документов: 1  (doc, частота): [('d10', 2)]
delivery       документов: 1  (doc, частота): [('d8', 2)]
eaddrnotavail  документов: 1  (doc, частота): [('d4', 1)]

== 2. IDF: редкие термины важнее частых
IDF(days) = log(12/2) = 1.79
IDF(transformer) = log(12/2) = 1.79
IDF(vectors) = log(12/1) = 2.48
IDF(eaddrnotavail) = log(12/1) = 2.48

== 3. Поиск: TF-IDF и BM25
запрос: 'transformer architecture neural network'
  TF-IDF: [('d1', 9.25), ('d2', 1.79)]
  BM25  : [('d1', 7.74), ('d2', 1.57)]
запрос: 'vector nearest neighbors'
  TF-IDF: [('d12', 7.45)]
  BM25  : [('d12', 6.82)]
запрос: 'EADDRNOTAVAIL (99)'
  TF-IDF: [('d4', 4.97)]
  BM25  : [('d4', 4.11)]

== 4. Длинный документ: BM25 гасит эффект длины
короткий документ: длина 3, refund встречается 2 раза
длинный документ : длина 62, refund встречается 2 раза
TF-IDF: короткий 3.08, длинный 3.08  (одинаково, длина не учтена)
BM25  : короткий 2.75, длинный 0.91  (длинный документ получает меньше)

== 5. Слабое место: нет общих слов — нет результата
запрос: 'I lost access to my profile' -> BM25: []
запрос: 'how fast will my order arrive' -> BM25: []
«profile» и «access» не встречаются в d5/d6, «arrive» не равно «arrives». Term-based поиск не знает синонимов.

== 6. Токены из нескольких слов: «hot dog»
по словам      : ['hot', 'dog', 'recipe']
с bigram-токеном: ['hot dog', 'recipe']
Частый bigram считаем одним термином, иначе «hot» и «dog» теряют смысл.
```

Что видно в выводе:

- Блок 1: токены документа и inverted index. По термину `delivery` сразу видны документ и частота (2 раза в `d8`).
- Блок 2: IDF. Термин `vectors` есть в одном документе из двенадцати, его IDF `2,48`. Термин `transformer` есть в двух, его IDF `1,79`. Чем реже термин, тем он важнее.
- Блок 3: запросы с точными словами работают хорошо. Код ошибки `EADDRNOTAVAIL (99)` находит ровно `d4`. Это сильная сторона term-based поиска.
- Блок 4: документ из 3 токенов и документ из 62 токенов содержат `refund` по 2 раза. Наивный TF-IDF даёт им одинаковый балл. BM25 даёт длинному документу балл заметно ниже. Это и есть поправка на длину.
- Блок 5: запрос «I lost access to my profile» не находит ничего: в документах нет этих слов. Запрос про заказ тоже: `arrive` не равно `arrives`. Term-based поиск не знает синонимов и форм слова.
- Блок 6: «hot dog» как один термин. Так токенизация сохраняет смысл.

### Embedding-based retrieval

Term-based поиск считает релевантность на уровне слов, а не смысла. Как мы видели в главе 3, внешний вид текста не всегда отражает смысл. Из-за этого в выдачу попадают документы, не связанные с намерением пользователя. Запрос «transformer architecture» вернёт документы про электрический трансформатор или про фильм «Трансформеры».

**Embedding-based retriever** (его ещё называют семантическим, `semantic retrieval`) пытается упорядочить документы по тому, насколько их смысл близок запросу.

При embedding-based поиске у индексации появляется ещё одна функция: превращение исходных кусков данных в embeddings. База, где лежат полученные embeddings, называется **vector database** (векторная база). Запрос потом состоит из двух шагов:

1. **Embedding model.** Превращаем запрос в embedding той же моделью, которой индексировали данные.
2. **Retriever.** Берём `k` кусков, чьи embeddings ближе всего к embedding запроса. Число `k` зависит от случая: от приложения, от generative model и от запроса.

![Embedding-based retriever: индексация (splitter, embedding model, vector database) и запрос (embedding запроса, поиск k ближайших, generative model)](/assets/ai-engineering/ch06-rag-pipeline.png)

Как читать схему. Верхняя рамка — индексация, она идёт заранее: документы режутся на chunks, каждый chunk превращается в vector и записывается в vector database. Нижняя рамка — работа на каждый запрос: запрос превращается в vector той же моделью, retriever ищет k ближайших vectors, найденные chunks уходят в generative model вместе с запросом. Важно, что модель embeddings в обеих рамках одна и та же.

Эта схема упрощена. В реальных системах есть и другие компоненты: например, reranker, который заново упорядочивает все найденные кандидаты, и кеши, чтобы уменьшить задержку.

> **Заметка автора.** У workflow поиска для `RAG` много общих шагов с классической рекомендательной системой.

Здесь снова появляются embeddings, о которых говорилось в главе 3. Напомним: embedding — это вектор, который старается сохранить важные свойства исходных данных. Если модель embeddings плохая, retriever не работает.

Ещё одна новая деталь — векторные базы. Хранить vectors — простая часть. Сложная часть — векторный поиск (`vector search`). При embedding-запросе vector database должна найти в базе vectors, ближайшие к запросу, и вернуть их. Vectors нужно индексировать и хранить так, чтобы поиск был быстрым и эффективным.

Как и многое другое в генеративных приложениях, vector search придумали не для генеративного AI. Он нужен во всех приложениях с embeddings: поиск, рекомендации, организация данных, информационный поиск, кластеризация, обнаружение мошенничества.

Обычно vector search — это задача поиска ближайших соседей (`nearest neighbor search`): для запроса найти `k` ближайших vectors. Наивное решение — **k-NN** (k nearest neighbors). Оно работает так:

1. Считаем сходство между embedding запроса и всеми vectors в базе, например через `cosine similarity`.
2. Сортируем все vectors по сходству.
3. Возвращаем `k` vectors с наибольшим сходством.

Такое решение даёт точный результат, но считает много и работает медленно. Его нужно использовать только для небольших наборов данных.

Для больших наборов используют **ANN** (`approximate nearest neighbor`, приближённый поиск ближайших соседей). Алгоритм не гарантирует точный ответ, но находит почти тех же соседей намного быстрее. Из-за важности задачи алгоритмов и библиотек много: `FAISS` (Facebook AI Similarity Search; Johnson et al., 2017), `ScaNN` (Google; Sun et al., 2020), `Annoy` (Spotify; Bernhardsson, 2013) и `Hnswlib` (Hierarchical Navigable Small World; Malkov и Yashunin, 2016).

Большинство разработчиков приложений не будут писать vector search сами. Поэтому автор даёт короткий обзор подходов. Он пригодится, когда вы будете выбирать решение. В общем, vector databases организуют vectors в корзины, деревья или графы. Алгоритмы отличаются эвристикой, с помощью которой они повышают шанс, что похожие vectors окажутся рядом. Vectors также можно квантовать (хранить с меньшей точностью) или делать разреженными. Квантованные и разреженные vectors дешевле обрабатывать. Подробнее о vector search рассказывает серия статей компании Zilliz. Главные алгоритмы:

- **`LSH`** (locality-sensitive hashing; Indyk и Motwani, 1999). Мощный и универсальный алгоритм, который работает не только с vectors. Он хэширует похожие vectors в одни и те же корзины (`buckets`), чтобы ускорить поиск. Платит за скорость частью точности. Реализован в FAISS и Annoy.
- **`HNSW`** (Hierarchical Navigable Small World; Malkov и Yashunin, 2016). Строит многослойный граф: узлы — vectors, рёбра соединяют похожие vectors. Поиск ближайшего соседа идёт по рёбрам графа. Реализация авторов открыта. Алгоритм есть в FAISS и Milvus.
- **`Product quantization`** (Jégou et al., 2011). Делит каждый vector на несколько подвекторов и заменяет vector более простым представлением меньшей размерности. Расстояния считают по этому короткому представлению, и это намного быстрее. Ключевая часть FAISS, поддерживается почти всеми популярными библиотеками vector search.
- **`IVF`** (Inverted File Index; Sivic и Zisserman, 2003). Группирует похожие vectors в кластеры методом k-means. Число кластеров обычно выбирают так, чтобы в среднем на кластер приходилось от 100 до 10 000 vectors. При запросе IVF находит центры кластеров, ближайшие к embedding запроса, и vectors из этих кластеров становятся кандидатами. Вместе с product quantization образует основу FAISS.
- **`Annoy`** (Approximate Nearest Neighbors Oh Yeah; Bernhardsson, 2013). Подход на деревьях. Строит несколько бинарных деревьев; каждое делит vectors на группы по случайному признаку, например проводит случайную линию и делит vectors по сторонам от неё. При поиске деревья обходят и собирают возможных соседей. Spotify открыл код.

Есть и другие алгоритмы, например SPTAG (Microsoft) и FLANN (Fast Library for Approximate Nearest Neighbors).

Хотя vector databases появились как отдельная категория вместе с `RAG`, любая база, которая умеет хранить vectors, может считаться vector database. Многие классические базы получили или получают поддержку хранения vectors и vector search.

Ниже две программы. Первая показывает embedding-based поиск на игрушечных embeddings: как документ превращается в vector, как считается cosine similarity, как точный k-NN находит документы без общих слов, как контекст разрешает многозначное слово и чего не умеет такой поиск. Вторая сравнивает точный перебор с двумя приближёнными алгоритмами, `IVF` и `LSH`, которые мы написали с нуля.

> **Пояснение.** Настоящая embedding model обучена на больших данных, и её vectors имеют сотни чисел. В нашем примере её заменяет маленький словарь «смысловых осей». Это модель идеи («близкий смысл — близкие vectors»), а не настоящая модель. В production вместо функции `embed()` вызывают настоящую модель.

<details>
<summary>Код: ch06_embedding_search.py</summary>

```python
"""Глава 6: embedding-based retrieval на игрушечных embeddings.
Настоящая embedding model обучена на больших данных. Здесь мы заменяем её словарём «понятий»:
каждое слово несёт вес в нескольких смысловых осях, текст = сумма слов. Это модель идеи
(близкий смысл -> близкие vectors), а не настоящая embedding model. В production вместо
функции embed() вызывают настоящую модель.
Показывает: embedding текста, cosine similarity, k-NN перебором, поиск без общих слов,
разбор многозначного слова по контексту, слабое место (редкий код ошибки), цену хранения vectors.
Запуск: python3 -I scripts/ai-engineering-code/ch06_embedding_search.py   (только стандартная библиотека)"""
import math
import re

DOCS = {
    "d1": "Transformer architecture: self-attention lets a neural network weigh every token against every other token.",
    "d2": "A power transformer changes the voltage of electricity between two circuits using coils.",
    "d3": "Transformers is a film series about robots that turn into cars.",
    "d4": "Error EADDRNOTAVAIL (99) means the address you try to bind is not available on this machine.",
    "d5": "How to reset your password: click Forgot password on the login page and follow the email link.",
    "d6": "I cannot sign in to my account after changing the phone number.",
    "d7": "Refund policy: you can return a product within 30 days and get your money back.",
    "d8": "Our delivery takes three to five days. Express delivery arrives the next day.",
    "d9": "Hot dog recipe for beginners: grill the sausage and warm the bun.",
    "d10": "Embedding models turn text into vectors so that similar meaning gives close vectors.",
    "d11": "BM25 ranks documents by term frequency, inverse document frequency and document length.",
    "d12": "Vector database stores embeddings and finds nearest neighbors quickly.",
}
AXES = ["account", "money", "shipping", "ml", "electric", "film", "food", "system", "search"]
LEX = {  # слово -> веса по осям смысла (ручной словарь, учебный)
    "password": {"account": 1}, "login": {"account": 1}, "sign": {"account": .8}, "account": {"account": 1},
    "profile": {"account": .9}, "access": {"account": .8}, "forgot": {"account": .6}, "reset": {"account": .6},
    "email": {"account": .3}, "credentials": {"account": 1}, "lost": {"account": .3}, "phone": {"account": .2},
    "refund": {"money": 1}, "money": {"money": 1}, "cash": {"money": 1}, "return": {"money": .6},
    "product": {"money": .3}, "back": {"money": .3}, "policy": {"money": .2},
    "delivery": {"shipping": 1}, "order": {"shipping": .6}, "arrive": {"shipping": 1}, "arrives": {"shipping": 1},
    "fast": {"shipping": .5}, "days": {"shipping": .4}, "express": {"shipping": .8}, "day": {"shipping": .2},
    "transformer": {"ml": .4, "electric": .4, "film": .2}, "transformers": {"film": .6, "ml": .2},
    "architecture": {"ml": .8}, "neural": {"ml": 1}, "network": {"ml": .5, "system": .3}, "attention": {"ml": .7},
    "token": {"ml": .7}, "self": {"ml": .2}, "models": {"ml": .6}, "text": {"ml": .3},
    "embedding": {"ml": .6, "search": .5}, "embeddings": {"ml": .6, "search": .5},
    "vector": {"search": .6, "ml": .4}, "vectors": {"search": .6, "ml": .4}, "database": {"search": .6},
    "nearest": {"search": 1}, "neighbors": {"search": 1}, "find": {"search": .7}, "finds": {"search": .7},
    "similar": {"search": .3, "ml": .3}, "meaning": {"search": .3, "ml": .3}, "bm25": {"search": 1},
    "term": {"search": .7}, "frequency": {"search": .7}, "documents": {"search": .7}, "document": {"search": .7},
    "ranks": {"search": .7},
    "voltage": {"electric": 1}, "electricity": {"electric": 1}, "circuits": {"electric": 1}, "coils": {"electric": 1},
    "power": {"electric": .8},
    "film": {"film": 1}, "series": {"film": .6}, "robots": {"film": .6, "ml": .1}, "cars": {"film": .3},
    "error": {"system": .8}, "address": {"system": .8}, "bind": {"system": .8}, "available": {"system": .4},
    "machine": {"system": .4},
    "hot": {"food": 1}, "dog": {"food": .6}, "recipe": {"food": 1}, "sausage": {"food": 1}, "grill": {"food": 1},
    "bun": {"food": 1}, "warm": {"food": .5}, "beginners": {"food": .2},
}


def words(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def embed(text):
    """Учебный embedding: сумма смысловых весов слов, потом нормировка до длины 1."""
    v = [0.0] * len(AXES)
    for w in words(text):
        for axis, weight in LEX.get(w, {}).items():
            v[AXES.index(axis)] += weight
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm else v


def cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def knn(query, k=3):
    """Точный k-NN: считаем сходство со всеми vectors, сортируем, берём k лучших."""
    q = embed(query)
    scored = sorted(((cosine(q, VECTORS[d]), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [(d, round(s, 2)) for s, d in scored[:k] if s > 0]


print("== 1. Индексация: каждый документ -> vector")
VECTORS = {d: embed(t) for d, t in DOCS.items()}
print("оси:", AXES)
for d in ("d5", "d8", "d1"):
    nz = {a: round(x, 2) for a, x in zip(AXES, VECTORS[d]) if x}
    print(f"{d}: {nz}")

print("\n== 2. Запрос: тот же embed(), потом k ближайших (точный k-NN)")
for q in ("I lost access to my profile", "how fast will my order arrive", "can I get cash back for a product"):
    print(f"запрос: {q!r}")
    print("  k-NN:", knn(q))
print("Общих слов с d5, d6, d8, d7 почти нет, но по смыслу они найдены: слова из одной смысловой оси лежат рядом.")

print("\n== 3. Многозначное слово: контекст решает")
for q in ("transformer", "transformer architecture neural network", "transformer voltage coils"):
    print(f"запрос: {q!r}")
    print("  k-NN:", knn(q))
print("Одно слово «transformer»: d1 (нейросеть) и d2 (электрика) получают одинаковое сходство 0,73. Контекстные слова решают спор.")

print("\n== 4. Слабое место: редкий точный код")
q = "EADDRNOTAVAIL (99)"
print(f"запрос: {q!r}; vector запроса: {embed(q)}")
print("  k-NN:", knn(q), "(vector нулевой: игрушечная модель не знает этот токен, все сходства равны 0)")
print("запрос: 'error address bind' ->", knn("error address bind", 2))
print("Настоящая модель даст «размытый» vector про сетевые ошибки. Точный код она находит ненадёжно. Для этого есть term-based поиск.")

print("\n== 5. Сколько стоит хранить и обновлять vectors")
docs_per_day, dim, bytes_per_float = 100_000_000, 1536, 4
per_second = docs_per_day / 86_400
storage_gb = docs_per_day * dim * bytes_per_float / 1e9
print(f"Пересчёт 100 млн документов в день = {per_second:.0f} embeddings в секунду, всё время")
print(f"100 млн vectors по {dim} чисел float32 = {storage_gb:.0f} GB только на vectors (без индекса)")
print(f"Те же vectors в 1 байт на число (quantization) = {storage_gb / 4:.0f} GB")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_embedding_search.py`. Реальный вывод:

```text
== 1. Индексация: каждый документ -> vector
оси: ['account', 'money', 'shipping', 'ml', 'electric', 'film', 'food', 'system', 'search']
d5: {'account': 1.0}
d8: {'shipping': 1.0}
d1: {'ml': 0.99, 'electric': 0.08, 'film': 0.04, 'system': 0.06}

== 2. Запрос: тот же embed(), потом k ближайших (точный k-NN)
запрос: 'I lost access to my profile'
  k-NN: [('d5', 1.0), ('d6', 1.0)]
запрос: 'how fast will my order arrive'
  k-NN: [('d8', 1.0), ('d7', 0.12)]
запрос: 'can I get cash back for a product'
  k-NN: [('d7', 0.99)]
Общих слов с d5, d6, d8, d7 почти нет, но по смыслу они найдены: слова из одной смысловой оси лежат рядом.

== 3. Многозначное слово: контекст решает
запрос: 'transformer'
  k-NN: [('d1', 0.73), ('d2', 0.73), ('d10', 0.52)]
запрос: 'transformer architecture neural network'
  k-NN: [('d1', 1.0), ('d10', 0.77), ('d2', 0.22)]
запрос: 'transformer voltage coils'
  k-NN: [('d2', 1.0), ('d1', 0.24), ('d10', 0.13)]
Одно слово «transformer»: d1 (нейросеть) и d2 (электрика) получают одинаковое сходство 0,73. Контекстные слова решают спор.

== 4. Слабое место: редкий точный код
запрос: 'EADDRNOTAVAIL (99)'; vector запроса: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  k-NN: [] (vector нулевой: игрушечная модель не знает этот токен, все сходства равны 0)
запрос: 'error address bind' -> [('d4', 1.0), ('d1', 0.06)]
Настоящая модель даст «размытый» vector про сетевые ошибки. Точный код она находит ненадёжно. Для этого есть term-based поиск.

== 5. Сколько стоит хранить и обновлять vectors
Пересчёт 100 млн документов в день = 1157 embeddings в секунду, всё время
100 млн vectors по 1536 чисел float32 = 614 GB только на vectors (без индекса)
Те же vectors в 1 байт на число (quantization) = 154 GB
```

Что видно в выводе:

- Блок 2: запросы «I lost access to my profile» и «how fast will my order arrive» почти не имеют общих слов с найденными документами, но находятся по смыслу. Слова одной смысловой оси лежат рядом.
- Блок 3: слово «transformer» неоднозначно: `d1` (нейросеть) и `d2` (электрика) получают одинаковое сходство 0,73. Контекстные слова («architecture neural network» или «voltage coils») решают спор.
- Блок 4: слабое место. Игрушечная модель не знает токен `EADDRNOTAVAIL`, поэтому vector нулевой и найти нечего. Настоящая модель дала бы размытый vector «про сетевые ошибки». Точный код ошибки embedding-based поиск находит ненадёжно.
- Блок 5: цифры хранения. 100 млн vectors по 1536 чисел `float32` занимают около 614 GB только на сами vectors, без индекса. Квантование до одного байта на число уменьшает это в четыре раза.

<details>
<summary>Код: ch06_ann_search.py</summary>

```python
"""Глава 6: поиск ближайших соседей: точный перебор (k-NN) против приближённого (ANN).
Мы пишем два простых ANN-алгоритма с нуля: IVF (кластеры k-means) и LSH (случайные гиперплоскости)
и меряем две вещи: recall (какую долю настоящих соседей нашли) и число проверенных vectors
(это замена скорости: чем меньше проверок, тем быстрее). Данные — случайные кластеры с фиксированным seed.
Запуск: python3 -I scripts/ai-engineering-code/ch06_ann_search.py   (только стандартная библиотека)"""
import math
import random

rng = random.Random(7)
DIM, N_CLUSTERS, PER_CLUSTER, K = 16, 20, 100, 5

print("== 0. Данные")
centers = [[rng.uniform(-10, 10) for _ in range(DIM)] for _ in range(N_CLUSTERS)]
data = [[c + rng.gauss(0, 4.0) for c in center] for center in centers for _ in range(PER_CLUSTER)]
queries = [[c + rng.gauss(0, 4.0) for c in rng.choice(centers)] for _ in range(60)]
print(f"vectors в базе: {len(data)}, размерность: {DIM}, запросов: {len(queries)}, ищем k = {K}")


def top_k(q, candidate_ids, k=K):
    return sorted(candidate_ids, key=lambda i: math.dist(q, data[i]))[:k]


print("\n== 1. Точный перебор (k-NN): проверяет каждый vector")
truth = [set(top_k(q, range(len(data)))) for q in queries]
print(f"проверено vectors на запрос: {len(data)} (все); recall = 1.00 по определению")

print("\n== 2. IVF: делим vectors на кластеры k-means, при запросе смотрим только ближайшие кластеры")


def kmeans(points, k, iters=8):
    cents = [points[i][:] for i in rng.sample(range(len(points)), k)]
    for _ in range(iters):
        groups = [[] for _ in range(k)]
        for p in points:
            groups[min(range(k), key=lambda j: math.dist(p, cents[j]))].append(p)
        for j, g in enumerate(groups):
            if g:
                cents[j] = [sum(x) / len(g) for x in zip(*g)]
    return cents


cents = kmeans(data, N_CLUSTERS)
cells = [[] for _ in range(N_CLUSTERS)]
for i, p in enumerate(data):
    cells[min(range(N_CLUSTERS), key=lambda j: math.dist(p, cents[j]))].append(i)
print(f"кластеров: {N_CLUSTERS}, размеры от {min(map(len, cells))} до {max(map(len, cells))}")
build_ivf = (8 + 1) * len(data) * N_CLUSTERS  # 8 итераций k-means + финальное распределение: расстояний до центров
print(f"построение индекса: около {build_ivf} вычислений расстояния")
print(f"{'nprobe':>7} {'recall':>8} {'проверено vectors':>18}")
for nprobe in (1, 2, 4, 8):
    hit, checked = 0, 0
    for q, t in zip(queries, truth):
        near = sorted(range(N_CLUSTERS), key=lambda j: math.dist(q, cents[j]))[:nprobe]
        cand = [i for j in near for i in cells[j]]
        hit += len(set(top_k(q, cand)) & t)
        checked += len(cand) + N_CLUSTERS  # плюс сравнение с центрами кластеров
    print(f"{nprobe:>7} {hit / (K * len(queries)):>8.2f} {checked / len(queries):>18.0f}")
print("Больше кластеров на запрос -> выше recall, но больше проверок. Это и есть компромисс ANN.")

print("\n== 3. LSH: хэш по знакам проекций на случайные гиперплоскости, похожие vectors попадают в одну корзину")


def lsh_index(n_planes, seed):
    r = random.Random(seed)
    planes = [[r.gauss(0, 1) for _ in range(DIM)] for _ in range(n_planes)]

    def sig(p):
        return tuple(sum(a * b for a, b in zip(pl, p)) > 0 for pl in planes)

    buckets = {}
    for i, p in enumerate(data):
        buckets.setdefault(sig(p), []).append(i)
    return sig, buckets


print(f"{'planes':>7} {'tables':>7} {'построение':>11} {'recall':>8} {'проверено vectors':>18}")
for n_planes, n_tables in ((10, 1), (6, 1), (6, 4), (6, 8)):
    tables = [lsh_index(n_planes, 100 + t) for t in range(n_tables)]
    hit, checked = 0, 0
    for q, t in zip(queries, truth):
        cand = set()
        for sig, buckets in tables:
            cand.update(buckets.get(sig(q), []))
        hit += len(set(top_k(q, cand)) & t)
        checked += len(cand)
    build = len(data) * n_planes * n_tables  # проекций на плоскости при построении
    print(f"{n_planes:>7} {n_tables:>7} {build:>11} {hit / (K * len(queries)):>8.2f} {checked / len(queries):>18.0f}")
print("Меньше гиперплоскостей и больше таблиц -> выше recall, но больше проверок.")
print("На этих данных IVF достигает высокого recall за меньшее число проверок, чем LSH, но строить его дороже (k-means).")
print("Это компромисс «индекс против запроса»: подробный индекс строится дольше, зато запросы быстрее и точнее.")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_ann_search.py`. Реальный вывод:

```text
== 0. Данные
vectors в базе: 2000, размерность: 16, запросов: 60, ищем k = 5

== 1. Точный перебор (k-NN): проверяет каждый vector
проверено vectors на запрос: 2000 (все); recall = 1.00 по определению

== 2. IVF: делим vectors на кластеры k-means, при запросе смотрим только ближайшие кластеры
кластеров: 20, размеры от 37 до 195
построение индекса: около 360000 вычислений расстояния
 nprobe   recall  проверено vectors
      1     0.94                121
      2     0.99                224
      4     1.00                429
      8     1.00                841
Больше кластеров на запрос -> выше recall, но больше проверок. Это и есть компромисс ANN.

== 3. LSH: хэш по знакам проекций на случайные гиперплоскости, похожие vectors попадают в одну корзину
 planes  tables  построение   recall  проверено vectors
     10       1       20000     0.15                 12
      6       1       12000     0.28                 75
      6       4       48000     0.72                241
      6       8       96000     0.92                381
Меньше гиперплоскостей и больше таблиц -> выше recall, но больше проверок.
На этих данных IVF достигает высокого recall за меньшее число проверок, чем LSH, но строить его дороже (k-means).
Это компромисс «индекс против запроса»: подробный индекс строится дольше, зато запросы быстрее и точнее.
```

Что видно в выводе:

- Точный k-NN проверяет все 2000 vectors на каждый запрос. Это эталон: его recall равен 1.
- `IVF` смотрит только ближайшие кластеры. При `nprobe = 1` проверяется около 120 vectors из 2000, а recall уже 0,94. Больше кластеров дают recall выше, но проверок больше.
- `LSH` строит индекс дешевле (меньше вычислений при построении), но на тех же данных ему нужно больше проверок для близкого recall. Одна таблица с 6 плоскостями даёт recall 0,28. Восемь таблиц дают 0,92, но проверок уже около 380.
- Это компромисс «индекс против запроса», о котором автор говорит в следующем разделе: подробный индекс строится дольше и занимает больше места, зато запросы быстрее и точнее.

### Сравнение term-based и embedding-based retrieval

Поиск существует давно, и готовых зрелых решений много. Поэтому и term-based, и embedding-based поиск запустить довольно просто. У каждого подхода свои плюсы и минусы.

![Сравнение term-based и embedding-based поиска: как ищут, скорость, сильные и слабые стороны, их объединение в hybrid search](/assets/ai-engineering/ch06-term-vs-embedding.png)

Как читать схему. Слева term-based: быстрый и дешёвый, силён на точных терминах, но не понимает смысл. Справа embedding-based: понимает смысл и живые запросы, его можно дообучать, но он дороже и может «размыть» редкий код. Жёлтый овал посередине — hybrid search: он берёт сильные стороны обоих.

**Скорость.** Term-based поиск, как правило, намного быстрее и при индексации, и при запросе. Извлечь термины быстрее, чем построить embeddings. Найти документы по термину дешевле, чем искать ближайших соседей.

**Качество.** Term-based поиск работает без проблем. Решения вроде Elasticsearch и BM25 успешно держат множество приложений поиска. Но простота означает и меньше «ручек», которыми можно улучшить результат. К тому же из-за многозначности терминов он может найти не те документы.

Embedding-based поиск со временем можно заметно улучшить, и он способен обойти term-based. Модель embeddings и retriever можно дообучить отдельно, вместе или вместе с generative model. Он позволяет задавать более естественные запросы, потому что смотрит на смысл, а не на слова. Но при превращении данных в embeddings ключевые слова, например точные коды ошибок (`EADDRNOTAVAIL (99)`) или названия продуктов, могут «размыться». Из-за этого такие вещи потом труднее найти. Ограничение можно снять, если сочетать embedding-based и term-based поиск. Об этом ниже.

**Стоимость.** Embeddings стоят денег. Это особенно заметно, если данные часто меняются и embeddings приходится часто пересчитывать. Представьте, что нужно каждый день строить embeddings для 100 миллионов документов. В зависимости от выбранной vector database дорогими могут стать и хранение vectors, и поиск по ним. Автор говорит, что расходы компании на vector databases нередко составляют пятую часть, а иногда и половину расходов на API моделей.

| | Term-based | Embedding-based |
|---|---|---|
| Скорость запроса | Намного выше | Embedding запроса и vector search могут быть медленными |
| Качество | Обычно сильное, но трудно улучшить. Из-за многозначности терминов находит не те документы | После дообучения может обойти term-based. Понимает естественные запросы |
| Стоимость | Намного дешевле | Embeddings, хранение и vector search бывают дорогими |

Решать, оправдан ли выигрыш в качестве у semantic retrieval, нужно, сравнив его с ценой и задержкой, особенно на этапе запроса. Основная часть задержки `RAG` приходится на генерацию ответа, особенно длинного. Поэтому добавка от embedding запроса и vector search в сумме может оказаться совсем небольшой. Но она всё равно влияет на то, как пользователь воспринимает продукт.

**Компромисс между индексацией и запросом.** В системах поиска всегда есть компромисс между индексом и запросом. Чем подробнее индекс, тем точнее запрос, но тем дольше строится индекс и тем больше он занимает места. Представьте индекс потенциальных клиентов. Добавьте поля (имя, компания, почта, телефон, интересы) — найти нужных людей станет проще, но индекс строится дольше и занимает больше места.

В общем, подробный индекс вроде `HNSW` даёт высокую точность и быстрые запросы, но требует много времени и места при построении. Простой индекс вроде `LSH` строится быстрее и занимает меньше памяти, зато запросы медленнее и менее точны. Это то, что мы видели в нашем примере с `IVF` и `LSH`.

Сайт **ANN-Benchmarks** сравнивает разные ANN-алгоритмы на нескольких наборах данных по четырём главным метрикам. Они учитывают этот компромисс:

- **`Recall`**: какую долю настоящих ближайших соседей нашёл алгоритм;
- **`Query per second` (QPS)**: сколько запросов алгоритм обрабатывает в секунду. Важно для приложений с большим трафиком;
- **время построения** (`build time`): сколько времени нужно, чтобы построить индекс. Особенно важно, если индекс приходится часто обновлять (данные меняются);
- **размер индекса** (`index size`): сколько места занимает индекс. Важно для масштабирования и требований к хранению.

Для оценки retrieval есть ещё `BEIR` (Benchmarking IR; Thakur et al., 2021). Это среда оценки, которая подключает системы поиска к 14 популярным benchmarks по retrieval.

### Как оценивать качество retrieval

Качество retriever оценивают по качеству данных, которые он находит. Две метрики часто используют в системах оценки `RAG`:

- **`Context precision`** (она же `context relevance`): какая доля всех найденных документов релевантна запросу;
- **`Context recall`**: какая доля всех документов, релевантных запросу, была найдена.

![Context precision и context recall на примере: из 5 найденных документов 3 релевантны, всего в базе 4 релевантных](/assets/ai-engineering/ch06-retrieval-metrics.png)

Как читать схему. Retriever вернул 5 документов. Из них 3 по делу, поэтому precision равна 3/5 = 0,6. Во всей базе по запросу есть 4 релевантных документа, retriever нашёл 3, поэтому recall равен 3/4 = 0,75. Внизу напоминание: порядок в выдаче измеряют другими метриками, а recall считать дороже, чем precision.

Чтобы посчитать эти метрики, нужен **evaluation set**: список тестовых запросов и набор документов. Для каждого тестового запроса вы отмечаете каждый тестовый документ как релевантный или нет. Разметку делают люди или AI judge. Потом считаете precision и recall retriever на этом наборе.

В production некоторые фреймворки для `RAG` поддерживают только precision и не поддерживают recall. Чтобы посчитать recall для запроса, нужно разметить релевантность **всех** документов в базе. Precision считать проще: достаточно сравнить найденные документы с запросом, и это может сделать AI judge.

Если вам важен порядок найденных документов (релевантные должны быть первыми), используйте ранговые метрики: `NDCG` (normalized discounted cumulative gain), `MAP` (mean average precision) и `MRR` (mean reciprocal rank).

> **Пояснение.** `MRR` берёт ранг первого верного документа и усредняет `1 / ранг` по запросам. Если верный документ первый, получается 1, если второй, то 0,5. `MAP` усредняет precision в позициях, где стоят релевантные документы. `NDCG` награждает верные документы тем сильнее, чем выше они стоят, и сравнивает результат с идеальным порядком. Все три считаются в нашем коде и в SQL ниже.

Для semantic retrieval нужно оценивать и качество самих embeddings. Как говорилось в главе 3, embeddings можно оценивать независимо: они хороши, если у похожих документов embeddings ближе. Их можно оценивать и по тому, насколько хорошо они работают на конкретных задачах. Benchmark `MTEB` (Muennighoff et al., 2023) оценивает embeddings на широком наборе задач: поиск, классификация, кластеризация.

Качество retriever стоит оценивать и в составе всей системы `RAG`. В конце концов retriever хорош, если помогает системе создавать качественные ответы. Как оценивать ответы генеративных моделей, мы разбирали в главах 3 и 4. Итог: качество `RAG` нужно проверять и по компонентам, и сквозным образом (`end-to-end`). Для этого:

1. оцените качество поиска;
2. оцените итоговые ответы `RAG`;
3. оцените embeddings (для embedding-based поиска).

Ниже программа, которая считает все эти метрики на маленьком размеченном наборе и сравнивает три retriever: BM25, игрушечные embeddings и hybrid с RRF. Кирпичики (база документов, BM25, embeddings, RRF) лежат в общем файле `ch06_retrieval_lib.py`. Его же использует программа про hybrid search, поэтому мы покажем его один раз здесь.

<details>
<summary>Код: ch06_retrieval_lib.py</summary>

```python
"""Глава 6: общие кирпичики для примеров hybrid search и оценки retrieval.
Здесь: учебная база документов, токенизация, BM25 (term-based), игрушечные embeddings (semantic),
cosine similarity и слияние рангов RRF. Это библиотека, а не самостоятельный скрипт:
её подключают ch06_hybrid_rerank.py и ch06_retrieval_eval.py.
Подробное объяснение каждой части: ch06_term_retrieval.py (BM25) и ch06_embedding_search.py (embeddings)."""
import math
import re
from collections import Counter

DOCS = {
    "d1": "Transformer architecture: self-attention lets a neural network weigh every token against every other token.",
    "d2": "A power transformer changes the voltage of electricity between two circuits using coils.",
    "d3": "Transformers is a film series about robots that turn into cars.",
    "d4": "Error EADDRNOTAVAIL (99) means the address you try to bind is not available on this machine.",
    "d5": "How to reset your password: click Forgot password on the login page and follow the email link.",
    "d6": "I cannot sign in to my account after changing the phone number.",
    "d7": "Refund policy: you can return a product within 30 days and get your money back.",
    "d8": "Our delivery takes three to five days. Express delivery arrives the next day.",
    "d9": "Hot dog recipe for beginners: grill the sausage and warm the bun.",
    "d10": "Embedding models turn text into vectors so that similar meaning gives close vectors.",
    "d11": "BM25 ranks documents by term frequency, inverse document frequency and document length.",
    "d12": "Vector database stores embeddings and finds nearest neighbors quickly.",
}
STOP = {"a", "the", "of", "to", "in", "on", "is", "and", "you", "your", "how", "can", "i", "my", "that", "so", "by",
        "for", "this", "into", "it", "an", "or", "with", "every", "other", "our", "after", "about", "against"}


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


# ---------- term-based: BM25 ----------
TOKENS = {d: tokenize(t) for d, t in DOCS.items()}
N = len(DOCS)
AVG_LEN = sum(map(len, TOKENS.values())) / N
DF = Counter(t for toks in TOKENS.values() for t in set(toks))  # в скольких документах есть термин


def bm25(query, doc, k1=1.5, b=0.75):
    f, length, score = Counter(TOKENS[doc]), len(TOKENS[doc]), 0.0
    for t in tokenize(query):
        if f[t]:
            idf = math.log(1 + (N - DF[t] + 0.5) / (DF[t] + 0.5))
            score += idf * f[t] * (k1 + 1) / (f[t] + k1 * (1 - b + b * length / AVG_LEN))
    return score


def term_search(query):
    """Полный рейтинг по BM25. В выдачу попадают только документы с общими терминами."""
    scored = sorted(((bm25(query, d), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [d for s, d in scored if s > 0]


# ---------- embedding-based: игрушечные embeddings ----------
AXES = ["account", "money", "shipping", "ml", "electric", "film", "food", "system", "search"]
LEX = {
    "password": {"account": 1}, "login": {"account": 1}, "sign": {"account": .8}, "account": {"account": 1},
    "profile": {"account": .9}, "access": {"account": .8}, "forgot": {"account": .6}, "reset": {"account": .6},
    "email": {"account": .3}, "credentials": {"account": 1}, "lost": {"account": .3}, "phone": {"account": .2},
    "refund": {"money": 1}, "money": {"money": 1}, "cash": {"money": 1}, "return": {"money": .6},
    "product": {"money": .3}, "back": {"money": .3}, "policy": {"money": .2},
    "delivery": {"shipping": 1}, "order": {"shipping": .6}, "arrive": {"shipping": 1}, "arrives": {"shipping": 1},
    "fast": {"shipping": .5}, "days": {"shipping": .4}, "express": {"shipping": .8}, "day": {"shipping": .2},
    "transformer": {"ml": .4, "electric": .4, "film": .2}, "transformers": {"film": .6, "ml": .2},
    "architecture": {"ml": .8}, "neural": {"ml": 1}, "network": {"ml": .5, "system": .3}, "attention": {"ml": .7},
    "token": {"ml": .7}, "self": {"ml": .2}, "models": {"ml": .6}, "text": {"ml": .3},
    "embedding": {"ml": .6, "search": .5}, "embeddings": {"ml": .6, "search": .5},
    "vector": {"search": .6, "ml": .4}, "vectors": {"search": .6, "ml": .4}, "database": {"search": .6},
    "nearest": {"search": 1}, "neighbors": {"search": 1}, "find": {"search": .7}, "finds": {"search": .7},
    "similar": {"search": .3, "ml": .3}, "meaning": {"search": .3, "ml": .3}, "bm25": {"search": 1},
    "term": {"search": .7}, "frequency": {"search": .7}, "documents": {"search": .7}, "document": {"search": .7},
    "ranks": {"search": .7},
    "voltage": {"electric": 1}, "electricity": {"electric": 1}, "circuits": {"electric": 1}, "coils": {"electric": 1},
    "power": {"electric": .8},
    "film": {"film": 1}, "series": {"film": .6}, "robots": {"film": .6, "ml": .1}, "cars": {"film": .3},
    "error": {"system": .8}, "address": {"system": .8}, "bind": {"system": .8}, "available": {"system": .4},
    "machine": {"system": .4},
    "hot": {"food": 1}, "dog": {"food": .6}, "recipe": {"food": 1}, "sausage": {"food": 1}, "grill": {"food": 1},
    "bun": {"food": 1}, "warm": {"food": .5}, "beginners": {"food": .2},
}


def embed(text):
    v = [0.0] * len(AXES)
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        for axis, weight in LEX.get(w, {}).items():
            v[AXES.index(axis)] += weight
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm else v


def cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


VECTORS = {d: embed(t) for d, t in DOCS.items()}


def dense_search(query):
    """Рейтинг по cosine similarity. В выдачу попадают документы с положительным сходством."""
    q = embed(query)
    scored = sorted(((cosine(q, VECTORS[d]), d) for d in DOCS), key=lambda x: (-x[0], x[1]))
    return [d for s, d in scored if s > 0]


# ---------- слияние рангов ----------
def rrf(rankings, k=60):
    """Reciprocal rank fusion: score(D) = сумма 1 / (k + rank_i(D)) по всем рейтингам."""
    score = Counter()
    for ranking in rankings:
        for rank, d in enumerate(ranking, 1):
            score[d] += 1 / (k + rank)
    return sorted(score, key=lambda d: (-score[d], d)), score
```

</details>

<details>
<summary>Код: ch06_retrieval_eval.py</summary>

```python
"""Глава 6: оценка retrieval на маленьком размеченном наборе.
Показывает: context precision, context recall, MRR, MAP, NDCG, и сравнение трёх retrievers:
term-based (BM25), embedding-based (игрушечные embeddings) и hybrid (RRF).
Для каждого запроса мы заранее разметили, какие документы релевантны (в реальности это делают люди или AI judge).
Запуск: python3 -I scripts/ai-engineering-code/ch06_retrieval_eval.py
(нужен соседний файл ch06_retrieval_lib.py; только стандартная библиотека)"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch06_retrieval_lib import dense_search, rrf, term_search  # noqa: E402

# evaluation set: запрос -> множество релевантных документов (разметили все 12 документов под каждый запрос)
EVAL = {
    "transformer architecture neural network": {"d1"},
    "EADDRNOTAVAIL (99)": {"d4"},
    "I lost access to my profile": {"d5", "d6"},
    "how fast will my order arrive": {"d8"},
    "can I get cash back for a product": {"d7"},
    "find nearest vectors in a database": {"d12"},
    "how do search engines rank documents": {"d11"},
    "transformer": {"d1"},  # нужен документ про нейросети, но слово неоднозначно
    "tasty dinner with bread": {"d9"},  # ни одного общего слова, и словарь игрушечной модели его не знает
}
K = 3


def precision(found, relevant):
    """Context precision: какая доля найденных документов релевантна."""
    return sum(d in relevant for d in found) / len(found) if found else 0.0


def recall(found, relevant):
    """Context recall: какая доля всех релевантных документов найдена. Нужна разметка всей базы."""
    return sum(d in relevant for d in found) / len(relevant)


def reciprocal_rank(found, relevant):
    """1 / ранг первого релевантного документа (0, если его нет). Среднее по запросам = MRR."""
    for rank, d in enumerate(found, 1):
        if d in relevant:
            return 1 / rank
    return 0.0


def average_precision(found, relevant):
    """AP: средняя precision в позициях, где стоит релевантный документ. Среднее по запросам = MAP."""
    hits, total = 0, 0.0
    for rank, d in enumerate(found, 1):
        if d in relevant:
            hits += 1
            total += hits / rank
    return total / len(relevant)


def ndcg(found, relevant):
    """NDCG с бинарной релевантностью: награда 1/log2(rank+1), делим на идеальный порядок."""
    dcg = sum(1 / math.log2(r + 1) for r, d in enumerate(found, 1) if d in relevant)
    ideal = sum(1 / math.log2(r + 1) for r in range(1, min(len(relevant), len(found)) + 1))
    return dcg / ideal if ideal else 0.0


RETRIEVERS = {
    "BM25": term_search,
    "embeddings": dense_search,
    "hybrid RRF": lambda q: rrf([term_search(q), dense_search(q)])[0],
}


def evaluate(search, k=K):
    rows = []
    for q, rel in EVAL.items():
        found = search(q)[:k]
        rows.append((precision(found, rel), recall(found, rel), reciprocal_rank(found, rel),
                     average_precision(found, rel), ndcg(found, rel)))
    return [sum(col) / len(rows) for col in zip(*rows)]


print(f"== 1. Что нашёл каждый retriever (top-{K}); релевантные документы в скобках")
for q, rel in EVAL.items():
    print(f"запрос: {q!r}  (релевантно: {sorted(rel)})")
    for name, search in RETRIEVERS.items():
        print(f"  {name:11s} {search(q)[:K]}")

print(f"\n== 2. Метрики по retrievers (среднее по {len(EVAL)} запросам, k = {K})")
print(f"{'retriever':11s} {'precision':>10} {'recall':>7} {'MRR':>6} {'MAP':>6} {'NDCG':>6}")
for name, search in RETRIEVERS.items():
    p, r, mrr, ap, nd = evaluate(search)
    print(f"{name:11s} {p:>10.2f} {r:>7.2f} {mrr:>6.2f} {ap:>6.2f} {nd:>6.2f}")
print("Документы и запросы подобраны так, чтобы показать сильные и слабые стороны каждого метода.")
print("Hybrid не проваливается там, где проваливается один из retrievers. Но последний запрос не нашёл никто.")

print("\n== 3. Как меняются precision и recall, если брать больше документов (hybrid RRF)")
print(f"{'k':>3} {'precision':>10} {'recall':>7}")
for k in (1, 2, 3, 5, 8):
    p, r, *_ = evaluate(RETRIEVERS["hybrid RRF"], k)
    print(f"{k:>3} {p:>10.2f} {r:>7.2f}")
print("Больше k -> recall растёт, precision падает. Модели в контекст лучше давать мало, но точных документов.")

print("\n== 4. Один запрос подробно: «I lost access to my profile», k = 3")
q, rel = "I lost access to my profile", EVAL["I lost access to my profile"]
for name, search in RETRIEVERS.items():
    f = search(q)[:3]
    print(f"{name:11s} найдено {f}: precision {precision(f, rel):.2f}, recall {recall(f, rel):.2f}, "
          f"RR {reciprocal_rank(f, rel):.2f}, NDCG {ndcg(f, rel):.2f}")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_retrieval_eval.py`. Реальный вывод:

```text
== 1. Что нашёл каждый retriever (top-3); релевантные документы в скобках
запрос: 'transformer architecture neural network'  (релевантно: ['d1'])
  BM25        ['d1', 'd2']
  embeddings  ['d1', 'd10', 'd2']
  hybrid RRF  ['d1', 'd2', 'd10']
запрос: 'EADDRNOTAVAIL (99)'  (релевантно: ['d4'])
  BM25        ['d4']
  embeddings  []
  hybrid RRF  ['d4']
запрос: 'I lost access to my profile'  (релевантно: ['d5', 'd6'])
  BM25        []
  embeddings  ['d5', 'd6']
  hybrid RRF  ['d5', 'd6']
запрос: 'how fast will my order arrive'  (релевантно: ['d8'])
  BM25        []
  embeddings  ['d8', 'd7']
  hybrid RRF  ['d8', 'd7']
запрос: 'can I get cash back for a product'  (релевантно: ['d7'])
  BM25        ['d7']
  embeddings  ['d7']
  hybrid RRF  ['d7']
запрос: 'find nearest vectors in a database'  (релевантно: ['d12'])
  BM25        ['d12', 'd10']
  embeddings  ['d12', 'd11', 'd10']
  hybrid RRF  ['d12', 'd10', 'd11']
запрос: 'how do search engines rank documents'  (релевантно: ['d11'])
  BM25        ['d11']
  embeddings  ['d11', 'd12', 'd10']
  hybrid RRF  ['d11', 'd12', 'd10']
запрос: 'transformer'  (релевантно: ['d1'])
  BM25        ['d1', 'd2']
  embeddings  ['d1', 'd2', 'd10']
  hybrid RRF  ['d1', 'd2', 'd10']
запрос: 'tasty dinner with bread'  (релевантно: ['d9'])
  BM25        []
  embeddings  []
  hybrid RRF  []

== 2. Метрики по retrievers (среднее по 9 запросам, k = 3)
retriever    precision  recall    MRR    MAP   NDCG
BM25              0.50    0.67   0.67   0.67   0.67
embeddings        0.43    0.78   0.78   0.78   0.78
hybrid RRF        0.54    0.89   0.89   0.89   0.89
Документы и запросы подобраны так, чтобы показать сильные и слабые стороны каждого метода.
Hybrid не проваливается там, где проваливается один из retrievers. Но последний запрос не нашёл никто.

== 3. Как меняются precision и recall, если брать больше документов (hybrid RRF)
  k  precision  recall
  1       0.89    0.83
  2       0.61    0.89
  3       0.54    0.89
  5       0.49    0.89
  8       0.49    0.89
Больше k -> recall растёт, precision падает. Модели в контекст лучше давать мало, но точных документов.

== 4. Один запрос подробно: «I lost access to my profile», k = 3
BM25        найдено []: precision 0.00, recall 0.00, RR 0.00, NDCG 0.00
embeddings  найдено ['d5', 'd6']: precision 1.00, recall 1.00, RR 1.00, NDCG 1.00
hybrid RRF  найдено ['d5', 'd6']: precision 1.00, recall 1.00, RR 1.00, NDCG 1.00
```

Что видно в выводе:

- Блок 1: каждый retriever ошибается по-разному. BM25 не находит ничего по запросам без общих слов («I lost access to my profile»). Embeddings не находят код `EADDRNOTAVAIL (99)`: игрушечная модель его не знает. Запрос «tasty dinner with bread» не находит никто: общих слов нет, а словарь модели про такие слова не знает.
- Блок 2: средние метрики. Hybrid RRF получает самые высокие recall, MRR, MAP, NDCG и precision. Он не провалился на тех запросах, на которых провалился один из retriever.
- Блок 3: чем больше `k`, тем выше recall и ниже precision. Поэтому в контекст модели лучше давать мало, но точных документов.
- Данные игрушечные: документы и запросы подобраны, чтобы показать сильные и слабые стороны. Настоящие числа вы получите только на своих данных.

### Hybrid search: объединяем подходы

У разных алгоритмов поиска разные сильные стороны, поэтому retriever в production обычно объединяет несколько подходов. Сочетание term-based и embedding-based поиска называют **гибридным поиском** (`hybrid search`).

![Два способа hybrid search: последовательно (дешёвый retriever, потом reranker) и параллельно (несколько retrievers и слияние рангов RRF)](/assets/ai-engineering/ch06-hybrid-search.png)

Как читать схему. В верхней рамке алгоритмы идут друг за другом: дешёвый поиск даёт кандидатов, точный выбирает лучших. В нижней рамке они работают одновременно, а потом их рейтинги сливаются в один по формуле `RRF`.

**Последовательно.** Сначала дешёвый и менее точный retriever, например term-based, отбирает кандидатов. Потом более точный, но дорогой механизм, например k-NN, выбирает лучших из этих кандидатов. Второй шаг называют `reranking` (пересортировка).

Пример. По запросу «transformer» можно взять все документы со словом «transformer», будь они про электрическое устройство, архитектуру нейросетей или фильм. Потом vector search выберет из них те, что действительно относятся к запросу про нейросети. Другой пример: запрос «Кто отвечает за большую часть продаж клиенту X?». Сначала берём все документы с ключевым словом X. Потом vector search ищет среди них контекст для вопроса «Кто отвечает за большую часть продаж?».

**Параллельно (ансамбль).** Напомним: retriever ранжирует документы по релевантности запросу. Можно взять несколько retrievers, чтобы они одновременно искали кандидатов, а потом объединить их рейтинги в один финальный.

Алгоритм объединения рейтингов называется **`reciprocal rank fusion`** (`RRF`, взаимное слияние рангов; Cormack et al., 2009). Каждый документ получает балл по рангу в рейтинге retriever. Первое место даёт 1/1 = 1. Второе даёт 1/2 = 0,5. Чем выше ранг, тем выше балл. Итоговый балл документа — сумма баллов по всем retrievers. Если один retriever поставил документ первым, а другой вторым, итог 1 + 0,5 = 1,5.

Этот пример сильно упрощает RRF, но показывает суть. Настоящая формула для документа `D`:

```text
Score(D) = сумма по i от 1 до n: 1 / (k + rᵢ(D))
```

- `n` — число рейтингов, каждый построен своим retriever;
- `rᵢ(D)` — ранг документа `D` у retriever `i`;
- `k` — константа. Она защищает от деления на ноль и регулирует влияние документов с низкими рангами. Типичное значение `k = 60`.

> **Пояснение.** Чем больше `k`, тем меньше разница между первым и вторым местом. При `k = 0` первое место в 2 раза лучше второго. При `k = 60` разница всего около 1,6%: `1/61` против `1/62`.

## Как улучшить retrieval

Многое зависит от задачи. Но есть тактики, которые повышают шанс найти нужные документы. Автор разбирает четыре: стратегию chunking, reranking, переписывание запроса и contextual retrieval.

### Стратегия chunking

То, как нужно индексировать данные, зависит от того, как вы будете искать. В предыдущих разделах мы разбирали алгоритмы поиска и стратегии индексации к ним. При этом мы считали, что документы уже разбиты на удобные куски. Теперь о самом разбиении. Это важное решение: выбранная стратегия `chunking` заметно влияет на качество поиска.

Проще всего делить документы на куски одинаковой длины по какой-то единице. Обычные единицы: символы, слова, предложения и абзацы. Например, можно резать по 2048 символов или по 512 слов. Можно резать так, чтобы в каждом chunk было заданное число предложений (скажем, 20) или абзацев (каждый абзац — отдельный chunk).

**Рекурсивное разбиение.** Можно резать рекурсивно, используя всё более мелкие единицы, пока каждый chunk не уложится в максимальный размер. Сначала делим документ на разделы. Если раздел слишком длинный, делим на абзацы. Если абзац всё ещё длинный, делим на предложения. Так реже обрываются связные фрагменты текста.

**Разбиение по структуре.** Для некоторых документов подходят специальные способы. Есть splitter'ы для разных языков программирования. Документы формата «вопрос-ответ» можно делить на пары, и каждая пара станет chunk. Китайский текст может требовать другой разбивки, чем английский.

**Overlap.** Если резать документ на куски без пересечения, граница может пройти через важный контекст, и информация потеряется. Возьмём фразу «Я оставил жене записку». Если разрезать её на «Я оставил жене» и «записку», ни одна часть не передаёт главное. Overlap (перекрытие) гарантирует, что важная информация на границе попадёт хотя бы в один chunk. Например, при размере chunk 2048 символов перекрытие можно задать в 20 символов.

![Chunking: без overlap смысл порван, с overlap ключевая часть сохранена; компромисс между маленьким и большим chunk](/assets/ai-engineering/ch06-chunking.png)

Как читать схему. Вверху две пары chunks для фразы «Я оставил жене записку на столе». Слева без overlap: ни один chunk не говорит, что именно оставили. Справа с overlap в два слова: первый chunk содержит главное. Внизу компромисс размера: меньше chunks дают разнообразие, но теряют общий смысл и дороже; большие chunks несут больше смысла, но в контекст их влезает меньше.

**Ограничения по размеру.** Размер chunk не должен превышать максимальную длину контекста generative model. При embedding-based подходе он не должен превышать и предел контекста модели embeddings.

**Chunking по токенам.** Документы можно делить и в токенах, определённых tokenizer'ом generative model. Допустим, вы используете Llama 3. Сначала обрабатываете документы tokenizer'ом Llama 3, потом режете по границам токенов. Так проще работать с моделями дальше по цепочке. Минус: если вы перейдёте на другую generative model с другим tokenizer, данные придётся индексировать заново.

**Размер chunk.** Какую бы стратегию вы ни выбрали, размер chunk важен.

- Меньший chunk даёт больше разнообразия. В контекст влезает больше кусков: если уменьшить chunk вдвое, их влезет вдвое больше. Больше разных кусков могут дать модели более широкую информацию, и ответ может получиться лучше.
- Но маленькие chunks могут терять важную информацию. Представьте документ, который в целом говорит о теме X, но X явно упомянута только в первой половине. Если разрезать его на два chunks, вторая половина может не найтись, и модель не сможет её использовать.
- Маленькие chunks увеличивают объём вычислений. Особенно заметно это при embedding-based поиске. Chunk вдвое меньше — вдвое больше chunks, вдвое больше embeddings, которые нужно создать и хранить. Пространство vector search вдвое больше, и запросы могут замедлиться.

Универсально лучшего размера chunk и размера overlap нет. Нужно экспериментировать.

<details>
<summary>Код: ch06_chunking.py</summary>

```python
"""Глава 6: стратегии chunking — как резать документы перед индексацией.
Показывает: фиксированные куски (символы, слова, предложения), overlap, рекурсивное
разбиение, разбиение по структуре (пары «вопрос-ответ»), chunking по токенам и то,
как размер chunk влияет на число chunks (и на число vectors).
Запуск: python3 -I scripts/ai-engineering-code/ch06_chunking.py   (только стандартная библиотека)"""
import random
import re

print("== 1. Overlap: фраза не рвётся посередине")
phrase = "Я оставил жене записку на столе".split()


def word_chunks(words, size, overlap=0):
    """Куски по `size` слов; соседние куски делят `overlap` слов."""
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step) if words[i:i + size]]


print("без overlap  :", word_chunks(phrase, 3, 0))
print("overlap = 1  :", word_chunks(phrase, 4, 1))
print("overlap = 2  :", word_chunks(phrase, 4, 2))
print("Без overlap ни один кусок не говорит, что оставили записку жене. С overlap первый кусок несёт ключевое.")

print("\n== 2. Разные единицы: символы, слова, предложения, абзацы")
doc = """Загрузка данных идёт каждую ночь. Сначала Airflow запускает задачу extract. Она читает новые заказы из PostgreSQL.

Потом идёт очистка. Мы убираем дубликаты и пустые строки. Даты приводим к UTC.

Последний шаг — запись в витрину. Таблица orders_daily обновляется инкрементально. Если шаг упал, Airflow повторяет его три раза.

Алерты уходят в Slack. Дежурный смотрит на них утром. Если упала загрузка, он запускает backfill."""


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def char_chunks(text, size, overlap=0):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]


paragraphs = [p.strip() for p in doc.split("\n\n")]
print(f"символов в документе: {len(doc)}, слов: {len(doc.split())}, предложений: {len(sentences(doc))}, абзацев: {len(paragraphs)}")
for size in (120, 60):
    parts = char_chunks(doc, size)
    cut = sum(not p.rstrip().endswith((".", "!", "?")) for p in parts)
    print(f"по {size} символов: кусков {len(parts)}, оборваны посреди предложения: {cut}")
print("по 3 предложения: кусков", len([" ".join(sentences(doc)[i:i + 3]) for i in range(0, len(sentences(doc)), 3)]))
print("по абзацу: кусков", len(paragraphs))

print("\n== 3. Рекурсивное разбиение: от крупных единиц к мелким")


def recursive_split(text, max_len, seps=("\n\n", ". ", " ")):
    """Режем по самому крупному разделителю. Если кусок всё ещё длиннее max_len, берём следующий."""
    if len(text) <= max_len:
        return [text.strip()]
    for sep in seps:
        parts = text.split(sep)
        if len(parts) > 1:
            out, buf = [], ""
            for part in parts:
                piece = part if part.endswith((".", "!", "?")) or sep != ". " else part + "."
                if len(buf) + len(piece) + 1 <= max_len:
                    buf = (buf + " " + piece).strip()
                else:
                    if buf:
                        out.append(buf)
                    buf = piece
                    if len(buf) > max_len:  # кусок всё ещё велик: спускаемся ниже
                        out.extend(recursive_split(buf, max_len, seps[seps.index(sep) + 1:] or (" ",)))
                        buf = ""
            if buf:
                out.append(buf)
            return [o for o in out if o]
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


rec = recursive_split(doc, 100)
for i, c in enumerate(rec, 1):
    print(f"[{i}] ({len(c):3d} симв.) {c}")
print("все куски не длиннее 100:", all(len(c) <= 100 for c in rec))

print("\n== 4. Структура документа: пары «вопрос-ответ»")
faq = """В: Как сбросить пароль?
О: Нажмите «Забыли пароль» на странице входа. Мы пришлём ссылку на почту.
В: Как удалить аккаунт?
О: Напишите в поддержку. Удаление занимает до 7 дней."""
pairs = re.findall(r"В: (.+?)\nО: (.+?)(?=\nВ: |\Z)", faq, flags=re.S)
for q, a in pairs:
    print(f"chunk = вопрос + ответ: «{q}» -> «{a[:30]}…»")

print("\n== 5. Chunking по токенам: смена tokenizer требует переиндексации")


def tok_a(text):  # «токенизатор» A: слово = токен
    return re.findall(r"\w+|[^\w\s]", text)


def tok_b(text):  # «токенизатор» B: слово режется на куски по 4 символа
    out = []
    for t in re.findall(r"\w+|[^\w\s]", text):
        out.extend(t[i:i + 4] for i in range(0, len(t), 4))
    return out


for name, tk in (("A", tok_a), ("B", tok_b)):
    toks = tk(doc)
    chunks = [toks[i:i + 32] for i in range(0, len(toks), 32)]
    print(f"tokenizer {name}: токенов {len(toks)}, кусков по 32 токена {len(chunks)}")
print("Границы кусков у A и B разные. Сменили модель с другим tokenizer — пересчитайте chunks и embeddings.")

print("\n== 6. Размер chunk и число vectors")
rng = random.Random(42)
pool = ["Таблица обновляется каждую ночь.", "Дубликаты удаляются по ключу заказа.", "Ошибка пишется в лог.",
        "Алерт приходит в Slack.", "Витрина читает только чистые данные.", "Backfill запускают вручную.",
        "Схема проверяется перед записью.", "Партиции создаются по дате."]
big = " ".join(rng.choice(pool) for _ in range(600))
words = big.split()
print(f"слов в большом документе: {len(words)}")
print(f"{'размер chunk (слов)':>20} {'chunks':>8} {'vectors в базе':>15}")
for size in (200, 100, 50, 25):
    n = len(word_chunks(words, size, 0))
    print(f"{size:>20} {n:>8} {n:>15}")
print("Размер chunk вдвое меньше -> chunks вдвое больше: больше embeddings, больше хранение, дольше поиск.")
print("Зато в контекст модели влезает вдвое больше разных кусков.")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_chunking.py`. Реальный вывод:

```text
== 1. Overlap: фраза не рвётся посередине
без overlap  : ['Я оставил жене', 'записку на столе']
overlap = 1  : ['Я оставил жене записку', 'записку на столе']
overlap = 2  : ['Я оставил жене записку', 'жене записку на столе', 'на столе']
Без overlap ни один кусок не говорит, что оставили записку жене. С overlap первый кусок несёт ключевое.

== 2. Разные единицы: символы, слова, предложения, абзацы
символов в документе: 424, слов: 62, предложений: 12, абзацев: 4
по 120 символов: кусков 4, оборваны посреди предложения: 3
по 60 символов: кусков 8, оборваны посреди предложения: 7
по 3 предложения: кусков 4
по абзацу: кусков 4

== 3. Рекурсивное разбиение: от крупных единиц к мелким
[1] ( 75 симв.) Загрузка данных идёт каждую ночь. Сначала Airflow запускает задачу extract.
[2] ( 38 симв.) Она читает новые заказы из PostgreSQL.
[3] ( 78 симв.) Потом идёт очистка. Мы убираем дубликаты и пустые строки. Даты приводим к UTC.
[4] ( 82 симв.) Последний шаг — запись в витрину. Таблица orders_daily обновляется инкрементально.
[5] ( 46 симв.) Если шаг упал, Airflow повторяет его три раза.
[6] ( 97 симв.) Алерты уходят в Slack. Дежурный смотрит на них утром. Если упала загрузка, он запускает backfill.
все куски не длиннее 100: True

== 4. Структура документа: пары «вопрос-ответ»
chunk = вопрос + ответ: «Как сбросить пароль?» -> «Нажмите «Забыли пароль» на стр…»
chunk = вопрос + ответ: «Как удалить аккаунт?» -> «Напишите в поддержку. Удаление…»

== 5. Chunking по токенам: смена tokenizer требует переиндексации
tokenizer A: токенов 76, кусков по 32 токена 3
tokenizer B: токенов 124, кусков по 32 токена 4
Границы кусков у A и B разные. Сменили модель с другим tokenizer — пересчитайте chunks и embeddings.

== 6. Размер chunk и число vectors
слов в большом документе: 2489
 размер chunk (слов)   chunks  vectors в базе
                 200       13              13
                 100       25              25
                  50       50              50
                  25      100             100
Размер chunk вдвое меньше -> chunks вдвое больше: больше embeddings, больше хранение, дольше поиск.
Зато в контекст модели влезает вдвое больше разных кусков.
```

Что видно в выводе:

- Блок 1: без overlap фраза рвётся на «Я оставил жене» и «записку на столе». С overlap первый кусок несёт «Я оставил жене записку».
- Блок 2: резка по символам рвёт предложения (оборваны 3 из 4 кусков при 120 символах, 7 из 8 при 60). Резка по предложениям и абзацам не рвёт.
- Блок 3: рекурсивное разбиение. Сначала делим по абзацам, длинные абзацы режем по предложениям. Все куски не длиннее 100 символов, предложения целы.
- Блок 4: для пар «вопрос-ответ» chunk равен паре.
- Блок 5: два «токенизатора» дают разное число токенов и разные границы кусков. Сменили модель с другим tokenizer — нужно пересчитать chunks и embeddings.
- Блок 6: размер chunk вдвое меньше даёт вдвое больше chunks и vectors.

### Reranking

Исходный рейтинг документов от retriever можно сделать точнее с помощью `reranking`. Он особенно полезен, когда нужно сократить число найденных документов: чтобы уложиться в контекст модели или уменьшить число входных токенов.

Типичный паттерн мы уже видели в разделе про hybrid search: дешёвый, но менее точный retriever ищет кандидатов, а более точный, но дорогой механизм переставляет их.

Документы можно ранжировать и по времени, отдавая больший вес свежим данным. Это полезно для приложений, где время критично: агрегатор новостей, чат с вашей почтой (бот, который отвечает на вопросы про ваши письма), анализ фондового рынка.

Ранжирование контекста отличается от обычного поискового ранжирования. В поиске критична точная позиция: первое место или пятое. При reranking контекста порядок документов всё ещё важен, потому что от него зависит, насколько хорошо модель их обработает. Как говорилось в разделе про длину контекста и эффективность контекста, модели лучше понимают документы в начале и в конце контекста. Но пока документ вообще попал в контекст, влияние порядка слабее, чем влияние позиции в поисковой выдаче.

Ниже программа с hybrid search, `RRF`, последовательным reranking, reranking по времени и порядком документов в контексте. Она использует файл `ch06_retrieval_lib.py`.

<details>
<summary>Код: ch06_hybrid_rerank.py</summary>

```python
"""Глава 6: hybrid search, слияние рангов RRF и reranking.
Показывает: как RRF складывает рейтинги term-based и embedding-based retrievers, последовательную схему
«дешёвый поиск -> точный reranking», reranking по времени и порядок документов в контексте.
Запуск: python3 -I scripts/ai-engineering-code/ch06_hybrid_rerank.py
(нужен соседний файл ch06_retrieval_lib.py; только стандартная библиотека)"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch06_retrieval_lib import DOCS, VECTORS, cosine, dense_search, embed, rrf, term_search  # noqa: E402

print("== 1. RRF руками")
# Документ A: 1-й в одном рейтинге и 2-й в другом. Упрощённая версия без k: 1/1 + 1/2 = 1,5
print("упрощённо (без k): 1/1 + 1/2 =", 1 / 1 + 1 / 2)
for k in (0, 60):
    s_a = 1 / (k + 1) + 1 / (k + 2)  # A: ранг 1 и ранг 2
    s_b = 1 / (k + 3) + 1 / (k + 1)  # B: ранг 3 и ранг 1
    print(f"k = {k:2d}: A = {s_a:.4f}, B = {s_b:.4f}")
print("k = 60 сглаживает разницу между рангами: первое место уже не «в разы» лучше второго.")

print("\n== 2. Hybrid search: term-based + embedding-based -> RRF")
queries = {
    "EADDRNOTAVAIL (99)": "точный код: embedding не знает токен",
    "I lost access to my profile": "нет общих слов: BM25 ничего не находит",
    "transformer architecture": "оба метода находят",
}
for q, note in queries.items():
    term, dense = term_search(q), dense_search(q)
    fused, score = rrf([term, dense])
    print(f"запрос: {q!r} ({note})")
    print("  BM25 :", term[:3])
    print("  dense:", dense[:3])
    print("  RRF  :", [(d, round(score[d], 4)) for d in fused[:3]])
print("Один retriever подстраховывает другой: код ошибки находит BM25, перефразированный вопрос находит embedding.")

print("\n== 3. Последовательно: дешёвый retriever берёт кандидатов, reranker выбирает лучших")
query = "transformer for text models"
cands = term_search(query)  # шаг 1: BM25, дёшево
print("кандидаты BM25:", cands)
q = embed(query)
reranked = sorted(cands, key=lambda d: -cosine(q, VECTORS[d]))  # шаг 2: точнее и дороже, смотрит на смысл
print("после reranking по смыслу:", [(d, round(cosine(q, VECTORS[d]), 2)) for d in reranked])
print("d2 (про электрический трансформатор) ушёл вниз: BM25 видел только слово «transformer».")

print("\n== 4. Reranking по времени: свежее важнее")
news = [  # (id, релевантность запросу, возраст в днях)
    ("n1", 0.90, 400), ("n2", 0.80, 3), ("n3", 0.75, 10), ("n4", 0.70, 1), ("n5", 0.60, 90),
]
HALF_LIFE = 14  # через 14 дней вес падает вдвое
rows = [(i, rel, age, rel * 0.5 ** (age / HALF_LIFE)) for i, rel, age in news]
print(f"{'id':>3} {'relevance':>10} {'возраст':>8} {'с учётом времени':>17}")
for i, rel, age, adj in sorted(rows, key=lambda r: -r[3]):
    print(f"{i:>3} {rel:>10.2f} {age:>6} дн {adj:>17.3f}")
print("По одной релевантности первым был бы n1 (ему 400 дней). С учётом времени первый n2.")

print("\n== 5. Порядок в контексте: самое важное — в начало и в конец")


def order_for_context(ranked):
    """Модели лучше видят начало и конец контекста. Лучший документ в начало, второй — в конец."""
    front, back = [], []
    for i, d in enumerate(ranked):
        (front if i % 2 == 0 else back).append(d)
    return front + back[::-1]


ranked = ["r1", "r2", "r3", "r4", "r5"]
print("по рангу        :", ranked)
print("для контекста   :", order_for_context(ranked))
print("Важно: сам документ должен попасть в контекст. Порядок влияет слабее, чем ранг в поисковой выдаче.")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_hybrid_rerank.py`. Реальный вывод:

```text
== 1. RRF руками
упрощённо (без k): 1/1 + 1/2 = 1.5
k =  0: A = 1.5000, B = 1.3333
k = 60: A = 0.0325, B = 0.0323
k = 60 сглаживает разницу между рангами: первое место уже не «в разы» лучше второго.

== 2. Hybrid search: term-based + embedding-based -> RRF
запрос: 'EADDRNOTAVAIL (99)' (точный код: embedding не знает токен)
  BM25 : ['d4']
  dense: []
  RRF  : [('d4', 0.0164)]
запрос: 'I lost access to my profile' (нет общих слов: BM25 ничего не находит)
  BM25 : []
  dense: ['d5', 'd6']
  RRF  : [('d5', 0.0164), ('d6', 0.0161)]
запрос: 'transformer architecture' (оба метода находят)
  BM25 : ['d1', 'd2']
  dense: ['d1', 'd10', 'd2']
  RRF  : [('d1', 0.0328), ('d2', 0.032), ('d10', 0.0161)]
Один retriever подстраховывает другой: код ошибки находит BM25, перефразированный вопрос находит embedding.

== 3. Последовательно: дешёвый retriever берёт кандидатов, reranker выбирает лучших
кандидаты BM25: ['d10', 'd1', 'd2']
после reranking по смыслу: [('d1', 0.97), ('d10', 0.74), ('d2', 0.37)]
d2 (про электрический трансформатор) ушёл вниз: BM25 видел только слово «transformer».

== 4. Reranking по времени: свежее важнее
 id  relevance  возраст  с учётом времени
 n2       0.80      3 дн             0.690
 n4       0.70      1 дн             0.666
 n3       0.75     10 дн             0.457
 n5       0.60     90 дн             0.007
 n1       0.90    400 дн             0.000
По одной релевантности первым был бы n1 (ему 400 дней). С учётом времени первый n2.

== 5. Порядок в контексте: самое важное — в начало и в конец
по рангу        : ['r1', 'r2', 'r3', 'r4', 'r5']
для контекста   : ['r1', 'r3', 'r5', 'r4', 'r2']
Важно: сам документ должен попасть в контекст. Порядок влияет слабее, чем ранг в поисковой выдаче.
```

Что видно в выводе:

- Блок 1: при `k = 60` у документов с рангами (1, 2) и (3, 1) почти одинаковый балл: 0,0325 и 0,0323. Первое место уже не «в разы» лучше второго.
- Блок 2: hybrid работает на разных типах запросов. Код `EADDRNOTAVAIL (99)` находит BM25, перефразированный вопрос находит embedding, а для запроса, где оба метода справляются, RRF ставит выше то, что нравится обоим.
- Блок 3: последовательная схема. BM25 берёт трёх кандидатов, и в них `d2` (про электрический трансформатор). Reranking по смыслу опускает его на последнее место.
- Блок 4: с учётом времени новость `n2` (3 дня) обгоняет `n1` (400 дней), хотя `n1` релевантнее по баллу. Период полураспада здесь 14 дней.
- Блок 5: функция `order_for_context` кладёт лучший документ в начало, второй в конец.

### Переписывание запроса (query rewriting)

`Query rewriting` (переписывание запроса) также называют переформулировкой, нормализацией запроса и иногда расширением запроса. Возьмём диалог:

```text
Пользователь: Когда Джон Доу в последний раз что-то у нас покупал?
AI: Джон в последний раз купил шляпу Fruity Fedora у нас две недели назад, 3 января 2030.
Пользователь: А Эмили Доу?
```

Последний вопрос «А Эмили Доу?» без контекста неоднозначен. Если отправить его в поиск как есть, скорее всего вернутся нерелевантные документы. Запрос нужно переписать так, чтобы он отражал настоящий вопрос. Новый запрос должен быть понятен сам по себе. Здесь: «Когда Эмили Доу в последний раз что-то у нас покупала?»

![Переписывание запроса: диалог с неполной последней репликой превращается в самостоятельный вопрос для поиска](/assets/ai-engineering/ch06-query-rewrite.png)

Как читать схему. Слева диалог, последняя реплика («А Эмили Доу?») красная: в поиск её отправлять нельзя. Модель-переписчик получает весь диалог и инструкцию переписать последнюю реплику. Результат — самостоятельный вопрос, он и идёт в retriever.

Переписывание запросов придумали не для `RAG`. В классических поисковых системах оно давно делается эвристиками. В AI-приложениях запрос может переписывать другая модель с промптом вроде «Перепиши последнюю реплику пользователя так, чтобы она отражала, о чём он на самом деле спрашивает». В книге показан скриншот, как ChatGPT с таким промптом переписал запрос про Эмили.

Переписывание бывает сложным, особенно если нужно разрешить личность (`identity resolution`) или привлечь другие знания. Если пользователь спрашивает «А его жена?», нужно сначала запросить у базы, кто его жена. Если этих сведений нет, модель-переписчик должна понять, что запрос не решить, а не выдумать имя. Иначе придёт неверный ответ.

### Contextual retrieval

Идея `contextual retrieval`: добавить к каждому chunk релевантный контекст, чтобы его было проще найти. Вот способы.

- **Метаданные.** Простой приём: дополнить chunk метаданными вроде тегов и ключевых слов. В e-commerce товар можно дополнить описанием и отзывами. Картинки и видео можно искать по названиям и подписям.
- **Сущности.** Метаданные могут содержать сущности, автоматически извлечённые из chunk. Если в документе есть код ошибки `EADDRNOTAVAIL (99)`, добавьте его в метаданные: система найдёт документ по этому слову, даже когда документ превращён в embeddings.
- **Вопросы, на которые отвечает chunk.** В поддержке клиентов к каждой статье можно добавить связанные вопросы. Статью «Как сбросить пароль?» можно дополнить вопросами «Как сбросить пароль?», «Я забыл пароль», «Не могу войти» и даже «Помогите, не могу найти аккаунт».
- **Контекст исходного документа.** Если документ разрезан на chunks, некоторым chunks не хватает контекста, чтобы retriever понял, о чём они. Тогда к chunk добавляют контекст оригинала: например, название и краткое содержание документа.

> **Заметка автора.** Некоторые команды рассказывали автору, что их системы поиска лучше всего работают, когда данные организованы в формате «вопрос-ответ».

Anthropic использует для этого AI-модели: модель пишет короткий контекст (обычно 50–100 токенов), который объясняет chunk и его связь с исходным документом. Prompt, который Anthropic использует, по смыслу такой: модели дают весь документ и один chunk и просят дать краткий контекст, который поместит chunk в общий документ, чтобы улучшить поиск этого chunk. Ответ должен содержать только этот контекст и ничего больше.

Сгенерированный контекст дописывают в начало chunk, и поисковый алгоритм индексирует уже расширенный chunk.

![Contextual retrieval по Anthropic: каждый chunk и документ идут в LLM, контекст дописывается к chunk, расширенный chunk индексируется в vector database и в term index](/assets/ai-engineering/ch06-contextual-retrieval.png)

Как читать схему. Документ режется на chunks. Для каждого chunk модель получает документ целиком и сам chunk и пишет короткое описание, где chunk стоит. Описание и chunk склеиваются. Склеенный текст идёт в оба индекса: через embedding model в vector database и через TF-IDF/BM25 в term index.

Ниже программа с mock-переписчиком запроса и с примерами contextual retrieval (контекст документа, метаданные, типовые вопросы). Переписчик здесь — простое правило. В реальной системе его заменяет вызов модели.

<details>
<summary>Код: ch06_query_context.py</summary>

```python
"""Глава 6: query rewriting и contextual retrieval на простом BM25.
Показывает: почему реплика диалога «А Эмили Доу?» нельзя отправлять в поиск как есть, как работает
переписывание запроса (здесь rewriter — простое правило; в реальной системе это вызов модели с промптом
«перепиши последний вопрос так, чтобы он был понятен без диалога»), как rewriter отказывается решать то, чего не знает,
и как контекст, дописанный к chunk (метаданные, коды, вопросы, описание места в документе), возвращает chunk в выдачу.
Запуск: python3 -I scripts/ai-engineering-code/ch06_query_context.py   (только стандартная библиотека)"""
import math
import re
from collections import Counter

STOP = {"a", "the", "of", "to", "in", "on", "is", "and", "from", "for", "us", "did", "was", "how", "about", "what", "when",
        "time", "by", "with", "it", "an", "that", "this", "at", "her", "she", "they"}


def tok(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.toks = {d: tok(t) for d, t in docs.items()}
        self.avg = sum(map(len, self.toks.values())) / len(docs)
        self.df = Counter(t for ts in self.toks.values() for t in set(ts))

    def search(self, q, k=3):
        n, out = len(self.docs), []
        for d, ts in self.toks.items():
            f, s = Counter(ts), 0.0
            for t in tok(q):
                if f[t]:
                    idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                    s += idf * f[t] * (self.k1 + 1) / (f[t] + self.k1 * (1 - self.b + self.b * len(ts) / self.avg))
            if s > 0:
                out.append((round(s, 2), d))
        return [d for s, d in sorted(out, key=lambda x: (-x[0], x[1]))][:k]


print("== 1. Query rewriting: реплика диалога без контекста")
PURCHASES = {
    "p1": "John Doe last bought a Fruity Fedora hat two weeks ago.",
    "p2": "Emily Doe last bought a Tabby Tie three days ago.",
    "p3": "Emily Doe asked support about the delivery of her order.",
    "p4": "Emily Doe changed her email address and phone number.",
}
index = BM25(PURCHASES)
dialog = ["When was the last time John Doe bought something from us?",
          "John last bought a Fruity Fedora hat from us two weeks ago.",
          "How about Emily Doe?"]
raw = dialog[-1]
print(f"запрос как есть: {raw!r} -> найдено {index.search(raw)}")


def rewrite(history, last):
    """MOCK-rewriter: берёт шаблон предыдущего вопроса пользователя и подставляет новое имя.
    Если в реплике нет имени, которое можно подставить, честно говорит, что вопрос не решается."""
    names = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", last)
    if not names:
        return "CANNOT_RESOLVE"
    prev_question = next(m for m in reversed(history) if m.endswith("?"))
    return re.sub(r"[A-Z][a-z]+ [A-Z][a-z]+", names[0], prev_question)


new_q = rewrite(dialog[:-1], raw)
print(f"после rewriting: {new_q!r} -> найдено {index.search(new_q)}")
print("Без rewriting среди документов Эмили нет приоритета: вопрос о покупке потерялся. После rewriting покупка первая.")

print("\n== 2. Rewriter не должен выдумывать")
for last in ("How about Emily Doe?", "What about his wife?"):
    r = rewrite(dialog[:-1], last)
    print(f"{last!r} -> {r!r}")
print("Для «his wife» имени в запросе нет. Rewriter возвращает CANNOT_RESOLVE и не придумывает имя.")
print("Сначала нужно спросить базу, кто жена этого клиента, и только потом переписывать запрос.")

print("\n== 3. Contextual retrieval: chunk без контекста не находится")
chunks = {
    "c1": "It grew by 3% over the previous quarter.",
    "c2": "They hired 40 engineers and opened a new office.",
    "c3": "Error EADDRNOTAVAIL (99) appeared in the nightly job logs.",
    "c4": "Customers can try again after five minutes.",
}
# Контекст пишет модель по паре (документ, chunk). Здесь он записан руками, как мог бы ответить rewriter.
CONTEXT = {
    "c1": "From the ACME Q2 2030 report, section on revenue growth.",
    "c2": "From the ACME Q2 2030 report, section on hiring and offices.",
    "c3": "From the infrastructure incident log of Q2 2030.",
    "c4": "From the help center article about account lockout after wrong passwords.",
}
query = "ACME Q2 2030 revenue growth"
plain = BM25(chunks)
print(f"запрос: {query!r}")
print("chunks как есть        ->", plain.search(query) or "[]  (в chunk нет ни названия компании, ни слов «revenue growth»)")
with_context = {c: f"{CONTEXT[c]} {t}" for c, t in chunks.items()}
print("+ контекст документа   ->", BM25(with_context).search(query))
print("\n== 4. Метаданные и вопросы к chunk")
meta = dict(chunks)
meta["c3"] += " keywords: EADDRNOTAVAIL, cannot assign requested address, bind error"
meta["c4"] += " questions: I forgot my password. I cannot log in. Why is my account locked?"
for q in ("cannot assign requested address", "I forgot my password", "why is my account locked"):
    print(f"{q!r:36s} без: {plain.search(q) or '[]'}   с метаданными: {BM25(meta).search(q) or '[]'}")
print("Ключевые слова и типовые вопросы в метаданных дают поиску зацепки. Они же помогают после превращения chunk в embedding.")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_query_context.py`. Реальный вывод:

```text
== 1. Query rewriting: реплика диалога без контекста
запрос как есть: 'How about Emily Doe?' -> найдено ['p3', 'p4', 'p2']
после rewriting: 'When was the last time Emily Doe bought something from us?' -> найдено ['p2', 'p1', 'p3']
Без rewriting среди документов Эмили нет приоритета: вопрос о покупке потерялся. После rewriting покупка первая.

== 2. Rewriter не должен выдумывать
'How about Emily Doe?' -> 'When was the last time Emily Doe bought something from us?'
'What about his wife?' -> 'CANNOT_RESOLVE'
Для «his wife» имени в запросе нет. Rewriter возвращает CANNOT_RESOLVE и не придумывает имя.
Сначала нужно спросить базу, кто жена этого клиента, и только потом переписывать запрос.

== 3. Contextual retrieval: chunk без контекста не находится
запрос: 'ACME Q2 2030 revenue growth'
chunks как есть        -> []  (в chunk нет ни названия компании, ни слов «revenue growth»)
+ контекст документа   -> ['c1', 'c2', 'c3']

== 4. Метаданные и вопросы к chunk
'cannot assign requested address'    без: []   с метаданными: ['c3', 'c4']
'I forgot my password'               без: []   с метаданными: ['c4']
'why is my account locked'           без: []   с метаданными: ['c4']
Ключевые слова и типовые вопросы в метаданных дают поиску зацепки. Они же помогают после превращения chunk в embedding.
```

Что видно в выводе:

- Блок 1: «А Эмили Доу?» как есть находит три документа про Эмили, но вопрос о покупке потерялся: нужный документ не первый. После переписывания документ о покупке стоит первым.
- Блок 2: переписчик не выдумывает. На «What about his wife?» он возвращает `CANNOT_RESOLVE`, потому что в реплике нет имени, которое можно подставить.
- Блок 3: chunk «It grew by 3%…» без контекста не находится по запросу «ACME Q2 2030 revenue growth»: в нём нет ни компании, ни слов о выручке. С контекстом, который написала бы модель, он стоит первым.
- Блок 4: ключевые слова и типовые вопросы в метаданных дают term-based поиску зацепки: запрос «I cannot log in» без них ничего не находил.

## Как выбрать решение для поиска

Вот факторы, которые стоит учесть при оценке решения для retrieval:

- Какие механизмы запроса оно поддерживает? Поддерживает ли hybrid search?
- Если это vector database: какие модели embeddings и алгоритмы vector search она поддерживает?
- Насколько она масштабируется и по объёму хранимых данных, и по трафику запросов? Подходит ли она вашим паттернам трафика?
- Сколько времени занимает индексация данных? Сколько данных можно обработать пачкой за раз (добавить или удалить)?
- Какова задержка запроса для разных алгоритмов запроса?
- Если решение управляемое (`managed`): какая ценовая модель? Оплата идёт за объём документов и vectors или за объём запросов?

> **Заметка автора.** В список не вошли функции, которые обычно связаны с корпоративными решениями: управление доступом, соответствие требованиям (`compliance`), разделение плоскостей данных и управления и так далее.

## RAG не только для текста

До сих пор мы говорили о текстовых системах `RAG`, где внешние данные — текстовые документы. Но внешние источники могут быть и мультимодальными, и табличными.

### Мультимодальный RAG

Если generator мультимодальный, его контекст можно дополнять не только текстом, но и картинками, видео, аудио из внешних источников. Автор берёт для примеров картинки, но их можно заменить любой другой модальностью. По запросу retriever находит и тексты, и картинки, релевантные запросу. На вопрос «Какого цвета дом в мультфильме Pixar «Вверх»?» retriever может достать картинку этого дома, чтобы модели было проще ответить.

![Мультимодальный RAG: retriever ищет и в базе текстов, и в базе картинок и передаёт найденное мультимодальной модели](/assets/ai-engineering/ch06-multimodal-rag.png)

Как читать схему. У retriever две базы: тексты и картинки. Он находит и фрагмент текста, и картинку и отдаёт их мультимодальной модели вместе с вопросом. Реальную картинку из мультфильма книга не использует по авторским правам, и мы тоже её не рисуем.

Если у картинок есть метаданные (названия, теги, подписи), их можно искать по метаданным: картинка найдётся, если подпись релевантна запросу.

Если нужно искать картинки по содержимому, нужен способ сравнивать картинки с запросами. Когда запросы текстовые, нужна мультимодальная модель embeddings, которая создаёт embeddings и для картинок, и для текста. Допустим, вы взяли `CLIP` (Radford et al., 2021). Retriever тогда работает так:

1. Создаёте CLIP-embeddings для всех данных, и текстовых, и картинок, и храните их в vector database.
2. Создаёте CLIP-embedding для запроса.
3. Ищете в vector database все картинки и тексты, чьи embeddings близки к embedding запроса.

### RAG с табличными данными

Большинство приложений работают не только с неструктурированными данными (текст, картинки), но и с табличными. Многим запросам нужна информация из таблиц. Workflow для дополнения контекста табличными данными заметно отличается от классического workflow `RAG`.

Пусть вы работаете в интернет-магазине Kitty Vogue, который продаёт одежду для кошек. Заказы лежат в таблице `Sales`: номер заказа, время, id и название товара, цена за штуку, число единиц и сумма.

Чтобы ответить на «Сколько единиц Fruity Fedora продали за последние 7 дней?», система должна запросить таблицу по всем заказам Fruity Fedora и сложить единицы. Допустим, таблицу можно запрашивать через SQL. Запрос примерно такой:

```text
SELECT SUM(units) AS total_units_sold
FROM Sales
WHERE product_name = 'Fruity Fedora'
  AND timestamp >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
```

> **Пояснение.** Это запрос из книги в диалекте MySQL, мы показываем его как пример и не запускаем. Рабочий вариант для DuckDB есть в разделе практики ниже.

Чтобы выполнить такой workflow, система должна уметь составлять и выполнять SQL. Нужны три шага:

1. **Text-to-SQL.** По запросу пользователя и схемам таблиц определить, какой нужен SQL-запрос. Text-to-SQL — пример семантического разбора (`semantic parsing`), о котором шла речь в главе 2.
2. **Выполнение SQL.** Выполнить запрос.
3. **Генерация.** Сформировать ответ по результату SQL и исходному запросу пользователя.

![RAG с таблицами: text-to-SQL пишет запрос, его выполняют, результат идёт в generative model вместе с вопросом](/assets/ai-engineering/ch06-text-to-sql-rag.png)

Как читать схему. Вопрос пользователя идёт в text-to-SQL. Модель видит схему таблицы `Sales` и пишет SQL. Запрос выполняется на таблице. Результат (число) идёт в generative model вместе с исходным вопросом, а она формулирует ответ человеческим языком.

Если таблиц много и их схемы не помещаются в контекст модели, на шаге text-to-SQL может понадобиться промежуточный шаг: предсказать, какие таблицы нужны для запроса. Преобразование текста в SQL может делать та же модель, что пишет итоговый ответ, или специальная text-to-SQL модель.

В этом разделе видно, как инструменты вроде retriever и SQL executor позволяют моделям обрабатывать больше запросов и давать более качественные ответы. А могла бы модель ещё больше улучшиться, если бы получила доступ к другим инструментам? Использование инструментов — ключевая особенность агентного подхода, и ему посвящён следующий раздел.

## Агенты

Многие считают умных агентов конечной целью AI. Классический учебник Stuart Russell и Peter Norvig «Artificial Intelligence: A Modern Approach» (1995) определяет область искусственного интеллекта как «изучение и разработку рациональных агентов».

Небывалые способности foundation models открыли дверь для агентных приложений, которые раньше нельзя было представить. Наконец можно строить автономных умных агентов: ассистентов, коллег и коучей. Они могут помочь сделать сайт, собрать данные, спланировать поездку, провести маркетинговое исследование, вести клиентский аккаунт, автоматизировать ввод данных, подготовиться к собеседованию, провести собеседование с кандидатами, договориться о сделке и многое другое. Возможностей кажется бесконечно много, а потенциальная экономическая ценность таких агентов огромна.

> **Предупреждение автора.** Агенты на основе AI — это новая область. У неё нет устоявшейся теории, по которой их можно определять, строить и оценивать. Этот раздел — попытка собрать каркас из существующей литературы. Он будет меняться вместе с развитием области. По сравнению с остальной книгой этот раздел более экспериментальный.

Раздел начинается с обзора агентов. Затем идут два аспекта, которые определяют способности агента: инструменты и планирование. У агентов с их новыми способами работы появляются и новые виды сбоев. Раздел заканчивается тем, как оценивать агентов, чтобы эти сбои ловить. Хотя агенты новы, они опираются на идеи, которые уже встречались в книге: самокритику, цепочку рассуждений (`chain of thought`) и структурированные выводы.

### Что такое агент

Слово «агент» используют во многих технических контекстах: software agent, intelligent agent, user agent, conversational agent, reinforcement learning agent. Что же такое агент здесь?

**Агент — это всё, что может воспринимать свою среду и действовать в ней.** Значит, агента определяют две вещи: **среда** (`environment`), в которой он работает, и **набор действий** (`actions`), которые он может выполнять.

> **Заметка автора.** В «Artificial Intelligence: A Modern Approach» агент определён как нечто, что воспринимает среду с помощью сенсоров и воздействует на неё с помощью исполнительных механизмов.

Среду определяет сценарий использования. Если агента делают для игры (Minecraft, Go, Dota), то игра и есть среда. Если агент собирает документы из интернета, среда — интернет. Если агент — кухонный робот, среда — кухня. Среда агента для беспилотного автомобиля — дорожная система и прилегающие территории.

Набор действий агента расширяют **инструменты** (`tools`), к которым у него есть доступ. Многие знакомые генеративные приложения — это агенты с доступом к хотя бы простым инструментам. ChatGPT — агент: он ищет в интернете, выполняет код на Python и создаёт картинки. Системы `RAG` — тоже агенты. Их инструменты — поиск по тексту, поиск по картинкам и выполнение SQL.

Между средой агента и его набором инструментов сильная зависимость. Среда определяет, какие инструменты агент потенциально может использовать. Если среда — шахматы, единственные возможные действия — допустимые ходы. В обратную сторону: набор инструментов ограничивает среду, в которой агент может работать. Если единственное действие робота — плавать, он сможет работать только в воде.

![SWE-agent: модель-агент, интерфейс «агент–компьютер» с удобными командами и среда — компьютер с terminal и файловой системой](/assets/ai-engineering/ch06-swe-agent.png)

Как читать схему. Внутри рамки SWE-agent: модель («мозг») и интерфейс. Интерфейс даёт модели небольшой набор команд: навигация по репозиторию, поиск и просмотр файлов, правка строк. Команды идут в среду, то есть в компьютер с terminal и файловой системой. Результат возвращается модели в удобной для неё форме.

Это визуализация SWE-agent (Yang et al., 2024), агента на базе GPT-4. Его среда — компьютер с terminal и файловой системой. Его действия: навигация по репозиторию, поиск файлов, просмотр файлов и редактирование строк.

Агент должен выполнять задачи, которые обычно пользователь формулирует во входе. В AI-агенте **AI — это мозг**. Он обрабатывает полученную информацию, включая задачу и обратную связь от среды, планирует цепочку действий для выполнения задачи и определяет, выполнена ли она.

Вернёмся к `RAG` с табличными данными из примера Kitty Vogue. Это простой агент с тремя действиями: генерация ответа, генерация SQL и выполнение SQL. На запрос «Спрогнозируй выручку по Fruity Fedora на ближайшие три месяца» агент мог бы пройти такую последовательность:

1. Подумать, как решить задачу. Он может решить, что для прогноза нужны продажи за последние пять лет. Обратите внимание: рассуждения агента показываются как промежуточный результат.
2. Вызвать генерацию SQL-запроса, чтобы получить продажи за пять лет.
3. Вызвать выполнение SQL.
4. Подумать, что вернул инструмент и как это поможет прогнозу. Агент может заключить, что данных мало для надёжного прогноза: например, есть пропуски. Тогда он решает, что нужна ещё информация о прошлых маркетинговых кампаниях.
5. Вызвать генерацию SQL для запроса про кампании.
6. Вызвать выполнение SQL.
7. Решить, что новой информации достаточно для прогноза, и составить его.
8. Решить, что задача выполнена.

![Пример агента Kitty Vogue: цепочка рассуждений и вызовов инструментов от задачи до прогноза](/assets/ai-engineering/ch06-agent-example.png)

Как читать схему. Фиолетовые блоки — рассуждения агента, синие — вызовы инструментов. Первая строка идёт слева направо: задача, рассуждение и первый запрос данных. Потом агент видит, что данных мало, и (вторая строка, справа налево) просит ещё данные. Когда данных хватает, он генерирует ответ и решает, что задача выполнена.

По сравнению с другими сценариями использования агентам нужны более мощные модели по двум причинам.

- **Накопление ошибок** (`compound mistakes`). Чтобы выполнить задачу, агенту часто нужно несколько шагов, а общая точность падает с числом шагов. Если точность модели на шаг 95%, то после 10 шагов она составит около 60%, а после 100 шагов всего около 0,6%.
- **Ставки выше.** С доступом к инструментам агенты могут выполнять более значимые задачи, но любой сбой может иметь более тяжёлые последствия.

![Накопление ошибок агента: доля успешных запусков при точности 95% на шаг падает с числом шагов](/assets/ai-engineering/ch06-compound-errors.png)

Как читать схему. Это наш график, а не из книги: мы посчитали `0,95` в степени числа шагов. После одного шага остаётся 95%, после 10 шагов около 60%, после 100 шагов меньше 1%. Красный столбик — случай из книги: 100 шагов.

Задача на много шагов стоит времени и денег.

> **Заметка автора.** В первые дни агентов жаловались, что агенты годятся только на то, чтобы тратить ваш кредит на API.

Но если агент может работать автономно, он способен сэкономить много человеческого времени, и стоимость окупается. Успех агента в среде зависит от инструментов, к которым у него есть доступ, и от силы его AI-планировщика. Сначала разберём виды инструментов.

### Инструменты (tools)

Системе не нужен доступ к внешним инструментам, чтобы быть агентом. Но без внешних инструментов способности агента ограничены. Модель обычно умеет только одно действие: LLM генерирует текст, генератор картинок создаёт картинки. Внешние инструменты делают агента намного мощнее.

Инструменты помогают агенту воспринимать среду и воздействовать на неё. Действия, которые позволяют воспринимать среду, называют **read-only** (только чтение). Действия, которые позволяют воздействовать на среду, называют **write actions** (действия записи).

Набор инструментов агента называют **tool inventory**. Он определяет, что агент может делать, поэтому важно подумать, какие и сколько инструментов ему дать. Больше инструментов — больше возможностей. Но чем больше инструментов, тем труднее их понять и правильно использовать. Подходящий набор находят экспериментами, о чём ниже в разделе про выбор инструментов.

В зависимости от среды возможны разные инструменты. Автор выделяет три категории: расширение знаний (то есть построение контекста), расширение возможностей и инструменты, которыми агент воздействует на среду.

#### Расширение знаний (knowledge augmentation)

Автор надеется, что книга уже убедила вас: правильный контекст очень важен для качества ответа. Большая категория инструментов — те, что расширяют знания агента. Некоторые мы уже разобрали: текстовый и картиночный retriever и SQL executor. Другие возможные инструменты: поиск людей во внутреннем справочнике, API склада со статусом товаров, поиск в Slack, чтение почты.

Многие такие инструменты дополняют модель частными процессами и информацией компании. Но они могут дать и доступ к публичной информации, особенно из интернета.

**Веб-просмотр** (`web browsing`) был одной из первых и самых ожидаемых функций чат-ботов вроде ChatGPT. Просмотр интернета не даёт модели устареть. Модель устарела, когда данные, на которых она обучена, больше не актуальны. Если обучающие данные модели закончились неделю назад, она не ответит на вопросы, где нужна информация этой недели, пока её не дадут в контексте. Без просмотра интернета модель не скажет вам о погоде, новостях, ближайших событиях, курсах акций, статусе рейса и так далее.

Автор использует «веб-просмотр» как общий термин для всех инструментов, которые ходят в интернет: браузеры и конкретные API (поисковые API, API новостей, GitHub, соцсети вроде X, LinkedIn и Reddit).

Просмотр интернета даёт доступ к свежим данным, лучшим ответам и меньшему числу галлюцинаций. Но он может открыть агента и для грязи интернета. Выбирайте интернет-API осознанно.

#### Расширение возможностей (capability extension)

Вторая категория — инструменты, которые закрывают встроенные ограничения моделей. Это простые способы повысить качество работы модели.

Например, модели известны тем, что плохо считают. Если спросить модель, сколько будет 199 999 разделить на 292, она, скорее всего, ошибётся. Но для модели с калькулятором это тривиально. Вместо того чтобы учить модель арифметике, намного экономнее просто дать ей инструмент.

Другие простые инструменты, которые заметно усиливают модель: календарь, конвертер часовых поясов, конвертер единиц (например, фунты в килограммы) и переводчик, который работает с языками, которых модель не знает.

Сложнее, но мощнее **code interpreter**. Вместо того чтобы учить модель понимать код, можно дать ей интерпретатор: она выполнит код, вернёт результаты или разберёт ошибки. Так агент становится помощником программиста, аналитиком данных и даже научным ассистентом, который пишет код для экспериментов и сообщает результаты. Но автоматическое выполнение кода несёт риск атак через внедрение кода (`code injection`), о чём говорилось в разделе про защитный prompt engineering в [главе 5](/book-summaries/ai/ai-engineering/05-prompt-engineering/). Чтобы защитить себя и пользователей, нужны правильные меры безопасности.

Внешние инструменты могут сделать модель, которая работает с одним видом данных, мультимодальной. Модель, которая умеет генерировать только текст, может использовать модель «текст в картинку» как инструмент, и тогда система создаёт и текст, и картинки. На текстовый запрос AI-планировщик агента решает: вызвать генерацию текста, картинки или обе. Так ChatGPT создаёт и текст, и картинки: для картинок он использует DALL-E. Агенты могут также использовать code interpreter для диаграмм и графиков, компилятор LaTeX для формул и браузер для страниц из HTML.

Так же модель, которая принимает только текст, может обрабатывать картинки с помощью инструмента подписи к изображению (`image captioning`) и аудио с помощью инструмента транскрибации. OCR (оптическое распознавание символов) позволяет ей читать PDF.

Использование инструментов может заметно повысить качество модели по сравнению с одним prompt или finetuning. Chameleon (Lu et al., 2023) показывает, что агент на GPT-4 с набором из 13 инструментов превосходит GPT-4 без инструментов на нескольких benchmarks. Инструменты этого агента: поиск знаний, генератор запросов, подпись к изображению, детектор текста и поиск Bing. На ScienceQA (benchmark по научным вопросам) Chameleon улучшает лучший опубликованный результат на 11,37%. На TabMWP (Tabular Math Word Problems; Lu et al., 2022), benchmark по математике по таблицам, он улучшает точность на 17%.

#### Действия записи (write actions)

До сих пор речь шла о read-only действиях, которые позволяют модели читать из источников данных. Но инструменты могут выполнять и **write actions**: они вносят изменения в источники данных. SQL executor может получить таблицу (чтение), но может и изменить или удалить её (запись). API почты может прочитать письмо и ответить на него. API банка может показать баланс и выполнить перевод.

Write actions позволяют системе делать больше. С ними можно автоматизировать весь процесс привлечения клиентов: исследовать потенциальных клиентов, найти их контакты, написать письма, отправить первые письма, прочитать ответы, напомнить о себе, извлечь заказы, обновить базы данных новыми заказами и так далее.

Но мысль о том, что AI получит возможность автоматически менять нашу жизнь, пугает. Как нельзя дать стажёру право удалять вашу production-базу, так нельзя разрешать ненадёжному AI делать банковские переводы. Доверие к способностям системы и к её мерам безопасности критично. Нужно быть уверенным, что система защищена от злоумышленников, которые могут попытаться заставить её выполнить вредные действия.

Автор рассказывает: когда он говорит с группой людей об автономных AI-агентах, кто-то обязательно вспоминает беспилотные автомобили: «А что, если кто-то взломает машину и тебя похитят?» Пример с автомобилем кажется очень сильным из-за физического присутствия. Но AI-система может навредить и без присутствия в физическом мире. Она может манипулировать фондовым рынком, красть авторские права, нарушать приватность, усиливать предвзятость, распространять дезинформацию и пропаганду и многое другое (см. защитный prompt engineering в главе 5).

Все эти опасения обоснованы, и каждая организация, которая хочет использовать AI, должна всерьёз относиться к безопасности. Но это не значит, что AI-системы никогда не должны получать возможность действовать в реальном мире. Если мы можем доверить машине, которая везёт нас в космос, то автор надеется, что когда-нибудь мер безопасности хватит и для доверия автономным AI-системам. К тому же люди тоже ошибаются. Автор лично доверял бы беспилотному автомобилю больше, чем случайному незнакомцу за рулём.

Как правильные инструменты делают людей намного продуктивнее (представьте бизнес без Excel или небоскрёб без кранов), так и модели с инструментами решают намного больше задач. Многие провайдеры уже поддерживают использование инструментов в своих моделях. Эту функцию часто называют **вызовом функций** (`function calling`). Автор ожидает, что вызов функций с широким набором инструментов станет обычным для большинства моделей.

> **Пояснение.** Для data engineer правило простое: read-инструменты можно давать агенту смело (с ограничением доступа), а write-инструменты нужно запускать только с проверкой параметров, подтверждением человека и журналом вызовов. Пример такой защиты есть в нашем коде `ch06_function_calling.py` ниже.

### Планирование (planning)

В центре агента на foundation model стоит модель, которая решает задачу. Задачу определяют цель и ограничения. Например: спланировать двухнедельную поездку из Сан-Франциско в Индию с бюджетом 5000 $. Цель — двухнедельная поездка. Ограничение — бюджет.

Сложные задачи требуют планирования. Результат планирования — **план** (`plan`): дорожная карта шагов, нужных для выполнения задачи. Чтобы планировать эффективно, модель должна понять задачу, рассмотреть разные варианты её выполнения и выбрать самый перспективный.

Кто был на планёрке, тот знает: планировать трудно. Планирование — важная вычислительная задача, и она хорошо изучена. Чтобы описать её полностью, нужно несколько томов, поэтому автор коснётся только поверхности.

#### Как устроено планирование агента

Задачу можно разбить многими способами, но не все ведут к успеху. Среди верных разбиений одни эффективнее других. Возьмём вопрос: «Сколько компаний без выручки привлекли не менее 1 миллиарда долларов?» Его можно решить по-разному. Для примера возьмём два варианта:

1. Найти все компании без выручки, а затем отфильтровать их по сумме привлечённых денег.
2. Найти все компании, привлёкшие не менее 1 миллиарда, а затем отфильтровать их по выручке.

Второй вариант эффективнее. Компаний без выручки намного больше, чем компаний с привлечёнными миллиардами. Если вариантов только два, умный агент должен выбрать второй.

**Планирование отдельно от выполнения.** Планирование можно совместить с выполнением в одном prompt. Например, попросить модель думать шаг за шагом (prompt с цепочкой рассуждений) и выполнять шаги в том же prompt. Но что если модель составит план из 1000 шагов, который даже не достигает цели? Без присмотра агент может выполнять такие шаги часами и тратить время и деньги на вызовы API, пока вы не заметите, что он застрял.

Чтобы не выполнять бесплодные планы, **планирование нужно отделить от выполнения**. Сначала вы просите агента составить план. Выполнять его начинают только после того, как план **проверен** (`validated`). Проверять план можно по-разному:

- **Эвристиками.** Простая эвристика: отбросить планы с недопустимыми действиями. Если план требует поиска в Google, а у агента нет доступа к Google, план недопустим. Другая простая эвристика: отбросить планы длиннее `X` шагов.
- **AI judge.** Можно попросить модель оценить, выглядит ли план разумно и как его улучшить.

Если проверка сочла план плохим, просим planner составить другой. Если план хороший, выполняем. Если в плане есть внешние инструменты, вызывается функция. Результаты выполнения нужно оценить снова. Составленный план не обязательно охватывает всю задачу: это может быть небольшой план для подзадачи. Весь процесс показан на схеме.

![Цикл агента: Planner строит план, Evaluator проверяет его, Executor вызывает tools, результаты оцениваются, при неудаче строится новый план](/assets/ai-engineering/ch06-agent-loop.png)

Как читать схему. Запрос идёт в Planner, он выдаёт план. Evaluator проверяет план: если плох, Planner строит новый (пунктирная стрелка). Если хорош, Executor выполняет шаги и вызывает tools. Результаты tools возвращаются в Evaluator, и он решает: цель достигнута или нужен новый план.

Теперь в системе три компонента: один создаёт планы, второй проверяет планы, третий выполняет планы. Если считать каждый компонент агентом, получится **мультиагентная система** (`multi-agent system`).

> **Заметка автора.** Большинство агентных workflows настолько сложны, что включают несколько компонентов. Поэтому большинство агентов — мультиагентные.

Чтобы ускорить процесс, можно не строить планы по очереди, а создать несколько планов параллельно и попросить evaluator выбрать самый перспективный. Это ещё один компромисс между задержкой и стоимостью: одновременное создание нескольких планов стоит дороже.

**Intent classifier.** Для планирования нужно понимать намерение за задачей: чего пользователь хочет добиться этим запросом? Чтобы помогать агентам планировать, часто используют `intent classifier` (классификатор намерений). Как показано в главе 5 в разделе о разбиении сложных задач на простые подзадачи, классификация намерений может идти через отдельный prompt или через обученную для этого модель-классификатор. Этот механизм тоже можно считать ещё одним агентом мультиагентной системы.

Знание намерения помогает выбрать правильные инструменты. Например, если вопрос в службу поддержки про оплату, агенту может понадобиться инструмент, который достаёт последние платежи пользователя. А если вопрос про сброс пароля, агенту может понадобиться поиск по документации.

> **Совет автора.** Некоторые запросы могут быть вне компетенции агента. Intent classifier должен уметь пометить такой запрос как `IRRELEVANT`, чтобы агент вежливо отказал, а не тратил вычисления (FLOPs) на поиск невозможных решений.

До сих пор мы считали, что агент автоматизирует все три фазы: составление плана, проверку плана и выполнение. В реальности человек может вмешаться в каждую фазу, чтобы помочь процессу и снизить риски. Эксперт может составить план, проверить план или выполнить его части. Например, для сложной задачи, где агент не справляется с полным планом, эксперт может составить план верхнего уровня, а агент его расширит. Если в плане есть рискованные операции (обновить базу данных, влить изменение кода), система перед выполнением может запросить явное одобрение человека или передать такие операции людям. Для этого нужно чётко определить, какую степень автоматизации агент может иметь для каждого действия.

Итого, решение задачи обычно состоит из таких процессов. Reflection агенту не обязателен, но может заметно повысить его качество:

1. **Генерация плана** (`plan generation`): составить план выполнения задачи. План — последовательность посильных действий, поэтому процесс называют ещё декомпозицией задачи (`task decomposition`).
2. **Reflection и исправление ошибок:** оценить составленный план. Если план плох, составить новый.
3. **Выполнение** (`execution`): выполнить действия плана. Часто это вызов конкретных функций.
4. **Reflection и исправление ошибок:** получив результаты действий, оценить их и решить, достигнута ли цель. Найти и исправить ошибки. Если цель не достигнута, составить новый план.

Некоторые из этих приёмов вы уже видели в книге. Когда вы просите модель «думай шаг за шагом», вы просите её разложить задачу на части. Когда просите «проверь, что твой ответ верный», вы просите её сделать reflection.

#### Могут ли foundation models планировать

Открытый вопрос: насколько хорошо foundation models умеют планировать. Многие исследователи считают, что модели на основе авторегрессионных языковых моделей планировать не могут. Главный AI-учёный Meta Yann LeCun прямо говорит, что авторегрессионные LLM не умеют планировать (2023). В статье «Can LLMs Really Reason and Plan?» Kambhampati (2023) утверждает: LLM хороши в извлечении знаний, но не в планировании. По его словам, работы, которые приписывают LLM способность планировать, путают общее знание о планировании, извлечённое из LLM, с планами, которые можно выполнить. «Планы, полученные из LLM, могут выглядеть разумными для неспециалиста, но на выполнении дают сбои и ошибки.»

Хотя признаков того, что LLM плохо планируют, много, неясно, в чём причина: мы не умеем правильно использовать LLM, или LLM принципиально не способны планировать.

**Планирование — это по сути поиск.** Вы перебираете разные пути к цели, предсказываете результат (награду) каждого пути и выбираете путь с самым перспективным результатом. Часто оказывается, что пути к цели нет вообще.

Поиск часто требует **возврата** (`backtracking`). Представьте шаг, где возможны два действия: A и B. После действия A вы попадаете в неперспективное состояние, и нужно вернуться на шаг назад и выполнить действие B.

Некоторые утверждают, что авторегрессионная модель умеет генерировать только действия вперёд. Вернуться и придумать другие действия она не может. Из этого они делают вывод, что такие модели не планируют. Но это не обязательно так. Если модель, пройдя путь с действием A, видит, что он бесперспективен, она может поменять путь на действие B и тем самым как бы вернуться. Модель может также в любой момент начать сначала и выбрать другой путь.

Возможно, LLM планируют плохо ещё и потому, что им не дают нужных инструментов для планирования. Чтобы планировать, нужно знать не только доступные действия, но и **возможный результат каждого действия**. Простой пример: вы хотите подняться на гору. Можно повернуть направо или налево, развернуться или идти прямо. Но если при повороте направо вы упадёте с обрыва, вы, возможно, не станете рассматривать это действие. Технически: действие переводит вас из одного состояния в другое, и чтобы решить, делать ли действие, нужно знать итоговое состояние.

Значит, недостаточно просить модель только сгенерировать последовательность действий, как делает популярный приём с цепочкой рассуждений. В статье «Reasoning with Language Model is Planning with World Model» (Hao et al., 2023) авторы утверждают: LLM, которая содержит столько информации о мире, способна предсказывать результат каждого действия. LLM может использовать это предсказание, чтобы строить связные планы.

Даже если AI не умеет планировать сам, он может быть частью планировщика. LLM можно дополнить инструментом поиска и системой отслеживания состояния, чтобы помочь ему в планировании.

> **Сбоку: FM-планировщик против RL-планировщика.** Агент — центральное понятие в обучении с подкреплением (`RL`, reinforcement learning). Википедия определяет RL как область, которая изучает, как умный агент должен действовать в динамической среде, чтобы максимизировать накопленную награду. RL-агенты и FM-агенты во многом похожи: обоих определяют среда и действия. Главное отличие — как работает планировщик. В RL-агенте планировщик обучают алгоритмом RL, и это может занять много времени и ресурсов. В FM-агенте планировщик — сама модель. Её умение планировать можно улучшить через prompt или finetuning, и это обычно требует меньше времени и ресурсов. Ничто не мешает FM-агенту использовать алгоритмы RL, чтобы стать лучше. Автор предполагает, что в долгой перспективе FM-агенты и RL-агенты сольются.

#### Генерация плана

Самый простой способ превратить модель в генератор планов — prompt engineering. Представьте, что вы делаете агента, который помогает клиентам Kitty Vogue узнавать о товарах. Вы даёте ему три внешних инструмента: найти товары по цене, найти топ-товары, получить информацию о товаре. Ниже пример prompt для генерации плана (по смыслу, он только для иллюстрации, в production prompts сложнее):

```text
SYSTEM PROMPT
Предложи план решения задачи. Тебе доступны 5 действий:
get_today_date()
fetch_top_products(start_date, end_date, num_products)
fetch_product_info(product_name)
generate_query(task_history, tool_output)
generate_response(query)

План — это последовательность допустимых действий.

Примеры
Задача: «Расскажи про Fruity Fedora»
План: [fetch_product_info, generate_query, generate_response]

Задача: «Какой товар лучше всего продавался на прошлой неделе?»
План: [fetch_top_products, generate_query, generate_response]

Задача: {ВВОД ПОЛЬЗОВАТЕЛЯ}
План:
```

В примере два момента.

- Формат плана — список функций, параметры которых агент выводит сам. Это лишь один из многих способов структурировать поток управления агента.
- Функция `generate_query` берёт текущую историю задачи и последний вывод инструмента и создаёт запрос для генератора ответа. После каждого шага вывод инструмента добавляется в историю задачи.

Для запроса «Какова цена самого продаваемого товара за прошлую неделю?» сгенерированный план может выглядеть так:

```text
1. get_time()
2. fetch_top_products()
3. fetch_product_info()
4. generate_query()
5. generate_response()
```

Вы спросите: «А параметры каждой функции?» Точные параметры предсказать трудно, потому что их часто выводят из предыдущих выводов инструментов. Если первый шаг `get_time()` вернул «2030-09-13», агент может вывести, что следующий шаг нужно вызвать с такими параметрами:

```text
fetch_top_products(
    start_date="2030-09-07",
    end_date="2030-09-13",
    num_products=1
)
```

Часто информации для точных значений параметров не хватает. Например, пользователь спросил: «Какова средняя цена самых продаваемых товаров?» Ответы на два вопроса неясны. Сколько товаров из бестселлеров он хочет рассмотреть? Нужны бестселлеры за последнюю неделю, за месяц или за всё время? Значит, модели часто приходится угадывать, и догадки могут быть неверными.

Последовательность действий и их параметры генерирует модель, поэтому они могут быть выдуманы (галлюцинации). Галлюцинация может привести к вызову несуществующей функции или существующей функции с неверными параметрами. Приёмы, которые улучшают качество модели вообще, улучшают и её планирование. Вот несколько способов, как заставить агента планировать лучше:

- написать лучший prompt с большим числом примеров;
- лучше описать инструменты и их параметры, чтобы модель понимала их лучше;
- переписать сами функции и упростить их, например разбить сложную функцию на две простых;
- взять более сильную модель (в целом сильные модели планируют лучше);
- дообучить модель (finetune) на генерацию планов.

##### Вызов функций (function calling)

Многие провайдеры моделей поддерживают использование инструментов и тем самым превращают модели в агентов. **Инструмент — это функция.** Поэтому вызов инструмента часто называют вызовом функции. API разных моделей работают по-разному, но в общем вызов функции устроен так:

1. **Создайте tool inventory.** Объявите все инструменты, которые хотите использовать. Каждый инструмент описывается точкой входа (например, именем функции), параметрами и документацией: что функция делает и какие параметры ей нужны.
2. **Укажите, какие инструменты агент может использовать.** Для разных запросов нужны разные инструменты. Во многих API можно передать список объявленных инструментов для каждого запроса. В некоторых можно ещё управлять использованием инструментов настройкой:
   - `required`: модель обязана использовать хотя бы один инструмент;
   - `none`: модель не должна использовать инструменты;
   - `auto`: модель сама решает, какие инструменты использовать.

В книге вызов функции показан псевдокодом, чтобы он подходил для нескольких API. Для конкретного API смотрите его документацию.

![Function calling шаг за шагом: объявляем tools, отправляем запрос, модель возвращает вызов, наш код вызывает функцию, результат идёт в модель](/assets/ai-engineering/ch06-function-calling.png)

Как читать схему. Верхний ряд — пять шагов. Нижний ряд — пример для запроса «Сколько кг в 40 фунтах?». Важный момент: модель только выбирает функцию и аргументы. Саму функцию вызывает наш код. Жёлтый блок напоминает режимы `tool_choice`, красный — что значения параметров нужно проверять.

На запрос пользователя агент, объявленный так, автоматически выбирает, какие инструменты использовать и с какими параметрами. Некоторые API с вызовом функций гарантируют, что генерируются только допустимые функции, хотя они не могут гарантировать правильные значения параметров.

Например, на запрос «Сколько килограммов в 40 фунтах?» агент может решить, что ему нужен инструмент `lbs_to_kg` со значением параметра 40. Ответ модели выглядит примерно так: причина завершения `tool_calls`, у сообщения нет текста, а в списке вызовов функция `lbs_to_kg` с аргументами `{"lbs": 40}`. По этому ответу вы вызываете `lbs_to_kg(lbs=40)` и используете вывод для ответа пользователю.

> **Совет автора.** Работая с агентами, всегда спрашивайте систему, какие значения параметров она использует в каждом вызове функции. Проверяйте, что они верны.

Ниже программа с mock-моделью. Она показывает описание инструментов, режимы `tool_choice`, проверку вызова до выполнения (неверный инструмент, неверные параметры, неверные значения), разделение read и write и подтверждение человеком. В реальной системе функцию `mock_model()` заменяет вызов API модели с теми же `tools` и `tool_choice`. Пример такого вызова лежит в конце файла в комментарии.

<details>
<summary>Код: ch06_function_calling.py</summary>

```python
"""Глава 6: function calling и проверки безопасности при вызове tools.
Показывает: описание tools (имя, параметры, документация), режимы tool_choice (required / none / auto),
ответ модели с tool_calls, проверку вызова перед выполнением (неверный tool, неверные параметры),
разделение read- и write-действий и подтверждение человеком.
Модель здесь — mock: простая функция с правилами. В реальной системе вместо mock_model()
вы вызываете API модели с теми же tools и tool_choice (пример блока API — в конце файла, в комментарии).
Запуск: python3 -I scripts/ai-engineering-code/ch06_function_calling.py   (только стандартная библиотека)"""
import json
import re

print("== 1. Описываем tools (как в API: имя, описание, параметры)")


def lbs_to_kg(lbs):
    return round(lbs * 0.45359237, 2)


def ft_to_meters(ft):
    return round(ft * 0.3048, 2)


def delete_orders(order_ids):
    return f"удалено заказов: {len(order_ids)}"


TOOLS = {
    "lbs_to_kg": dict(fn=lbs_to_kg, access="read", description="Convert from pounds to kilograms",
                      params={"lbs": "number"}),
    "ft_to_meters": dict(fn=ft_to_meters, access="read", description="Convert from feet to meters",
                         params={"ft": "number"}),
    "delete_orders": dict(fn=delete_orders, access="write", description="Delete orders by id",
                          params={"order_ids": "list"}),
}
for name, t in TOOLS.items():
    print(f"{name}({', '.join(f'{p}: {ty}' for p, ty in t['params'].items())}) [{t['access']}] — {t['description']}")

print("\n== 2. Mock-модель: по запросу решает, какой tool вызвать, и отдаёт имя и аргументы строкой JSON")


def mock_model(query, tool_names, tool_choice="auto"):
    """Возвращает словарь в форме ответа API: finish_reason + tool_calls или текст."""
    if tool_choice == "none":
        return {"finish_reason": "stop", "content": "Отвечаю без tools: примерно 18 кг.", "tool_calls": []}
    call = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:pounds|lbs)", query)
    if m and "lbs_to_kg" in tool_names:
        call = {"name": "lbs_to_kg", "arguments": json.dumps({"lbs": float(m.group(1))})}
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:feet|ft)", query)
    if m and "ft_to_meters" in tool_names:
        call = {"name": "ft_to_meters", "arguments": json.dumps({"ft": float(m.group(1))})}
    if call is None and tool_choice == "required":
        call = {"name": tool_names[0], "arguments": json.dumps({})}  # обязаны вызвать хоть что-то
    if call is None:
        return {"finish_reason": "stop", "content": "Tool не нужен.", "tool_calls": []}
    return {"finish_reason": "tool_calls", "content": None, "tool_calls": [{"function": call, "type": "function"}]}


for choice in ("auto", "none", "required"):
    r = mock_model("How many kg are 40 pounds?", ["lbs_to_kg", "ft_to_meters"], choice)
    print(f"tool_choice={choice:8s} -> finish_reason={r['finish_reason']}, tool_calls={r['tool_calls']}")
r = mock_model("Say hello", ["lbs_to_kg", "ft_to_meters"], "required")
print("required без подходящего tool -> модель вынуждена вызвать tool с пустыми аргументами:", r["tool_calls"][0]["function"])

print("\n== 3. Проверяем вызов ДО выполнения")


def validate_call(call):
    """Возвращает список проблем. Пустой список — вызов допустим."""
    name, args = call["name"], json.loads(call["arguments"])
    if name not in TOOLS:
        return [f"invalid tool: {name!r} нет в списке tools"]
    problems = []
    expected = TOOLS[name]["params"]
    for p in expected:
        if p not in args:
            problems.append(f"пропущен параметр {p!r}")
    for p, v in args.items():
        if p not in expected:
            problems.append(f"лишний параметр {p!r}")
        elif expected[p] == "number" and not isinstance(v, (int, float)):
            problems.append(f"параметр {p!r} должен быть числом, пришло {v!r}")
        elif expected[p] == "list" and not isinstance(v, list):
            problems.append(f"параметр {p!r} должен быть списком")
    return problems


cases = {
    "верный вызов": {"name": "lbs_to_kg", "arguments": '{"lbs": 40}'},
    "invalid tool": {"name": "bing_search", "arguments": '{"q": "weather"}'},
    "valid tool, invalid params": {"name": "lbs_to_kg", "arguments": '{"lbs": 40, "extra": 1}'},
    "неверный тип": {"name": "lbs_to_kg", "arguments": '{"lbs": "forty"}'},
    "valid tool, wrong value": {"name": "lbs_to_kg", "arguments": '{"lbs": 100}'},
}
for label, call in cases.items():
    print(f"{label:28s} -> {validate_call(call) or 'схема в порядке'}")
print("Последний случай (lbs=100 вместо 40) схема не поймает: значение выбрала модель. Его проверяют отдельно:")
query = "How many kg are 40 pounds?"
numbers_in_query = {float(x) for x in re.findall(r"\d+(?:\.\d+)?", query)}
args = json.loads(cases["valid tool, wrong value"]["arguments"])
print(f"  числа в запросе: {sorted(numbers_in_query)}; аргумент lbs = {args['lbs']} -> "
      f"{'ok' if args['lbs'] in numbers_in_query else 'подозрительно: такого числа нет в запросе'}")

print("\n== 4. Read и write: write-действия идут через подтверждение человека")
AUDIT_LOG = []


def run_tool(call, approve=None):
    problems = validate_call(call)
    if problems:
        return f"отклонено: {problems}"
    tool = TOOLS[call["name"]]
    args = json.loads(call["arguments"])
    if tool["access"] == "write" and not (approve and approve(call)):
        AUDIT_LOG.append((call["name"], args, "ждёт подтверждения"))
        return "write-действие не выполнено: нужно подтверждение человека"
    AUDIT_LOG.append((call["name"], args, "выполнено"))
    return tool["fn"](**args)


print("read :", run_tool({"name": "lbs_to_kg", "arguments": '{"lbs": 40}'}))
delete_call = {"name": "delete_orders", "arguments": '{"order_ids": [1, 2, 3]}'}
print("write без подтверждения:", run_tool(delete_call))
print("write с подтверждением  :", run_tool(delete_call, approve=lambda c: True))
print("журнал вызовов:")
for entry in AUDIT_LOG:
    print("  ", entry)

print("\n== 5. Полный цикл: запрос -> tool_calls -> выполнение -> ответ")
r = mock_model("How many kg are 40 pounds?", ["lbs_to_kg", "ft_to_meters"], "auto")
call = r["tool_calls"][0]["function"]
result = run_tool(call)
print(f"модель выбрала {call['name']}({call['arguments']}); результат: {result}")
print(f"ответ пользователю: «40 фунтов — это около {result} кг»")

# --- Как это выглядит с настоящей моделью (в этом файле не выполняется, нужен ключ API): ---
# response = model_client.chat.completions.create(
#     model=MODEL_NAME, messages=[{"role": "user", "content": query}],
#     tools=[lbs_to_kg_declaration, ft_to_meters_declaration], tool_choice="auto")
# call = response.choices[0].message.tool_calls[0].function   # имя и аргументы
# result = run_tool({"name": call.name, "arguments": call.arguments})
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_function_calling.py`. Реальный вывод:

```text
== 1. Описываем tools (как в API: имя, описание, параметры)
lbs_to_kg(lbs: number) [read] — Convert from pounds to kilograms
ft_to_meters(ft: number) [read] — Convert from feet to meters
delete_orders(order_ids: list) [write] — Delete orders by id

== 2. Mock-модель: по запросу решает, какой tool вызвать, и отдаёт имя и аргументы строкой JSON
tool_choice=auto     -> finish_reason=tool_calls, tool_calls=[{'function': {'name': 'lbs_to_kg', 'arguments': '{"lbs": 40.0}'}, 'type': 'function'}]
tool_choice=none     -> finish_reason=stop, tool_calls=[]
tool_choice=required -> finish_reason=tool_calls, tool_calls=[{'function': {'name': 'lbs_to_kg', 'arguments': '{"lbs": 40.0}'}, 'type': 'function'}]
required без подходящего tool -> модель вынуждена вызвать tool с пустыми аргументами: {'name': 'lbs_to_kg', 'arguments': '{}'}

== 3. Проверяем вызов ДО выполнения
верный вызов                 -> схема в порядке
invalid tool                 -> ["invalid tool: 'bing_search' нет в списке tools"]
valid tool, invalid params   -> ["лишний параметр 'extra'"]
неверный тип                 -> ["параметр 'lbs' должен быть числом, пришло 'forty'"]
valid tool, wrong value      -> схема в порядке
Последний случай (lbs=100 вместо 40) схема не поймает: значение выбрала модель. Его проверяют отдельно:
  числа в запросе: [40.0]; аргумент lbs = 100 -> подозрительно: такого числа нет в запросе

== 4. Read и write: write-действия идут через подтверждение человека
read : 18.14
write без подтверждения: write-действие не выполнено: нужно подтверждение человека
write с подтверждением  : удалено заказов: 3
журнал вызовов:
   ('lbs_to_kg', {'lbs': 40}, 'выполнено')
   ('delete_orders', {'order_ids': [1, 2, 3]}, 'ждёт подтверждения')
   ('delete_orders', {'order_ids': [1, 2, 3]}, 'выполнено')

== 5. Полный цикл: запрос -> tool_calls -> выполнение -> ответ
модель выбрала lbs_to_kg({"lbs": 40.0}); результат: 18.14
ответ пользователю: «40 фунтов — это около 18.14 кг»
```

Что видно в выводе:

- Блок 2: в режиме `auto` модель вызывает `lbs_to_kg` с `{"lbs": 40.0}`. В режиме `none` она отвечает текстом без вызова. В режиме `required` вызов обязателен: даже когда подходящего инструмента нет, модель вынуждена вызвать хоть какой-то, и аргументы пустые. Поэтому `required` нужно применять осознанно.
- Блок 3: проверка схемы ловит неверный инструмент (`bing_search`), лишний параметр и неверный тип. Но вызов с `lbs = 100` вместо 40 схему проходит: значение выбрала модель. Его проверяют отдельно, например сверяя с числами в запросе.
- Блок 4: write-вызов `delete_orders` без подтверждения не выполняется. С подтверждением выполняется. Каждый вызов попадает в журнал, и по нему видно, что было сделано и что ждало подтверждения.
- Блок 5: полный цикл: модель выбрала функцию, наш код выполнил её, получилось 18,14 кг.

##### Гранулярность планирования

План — это дорожная карта шагов. У дорожной карты может быть разная детализация. Чтобы спланировать год, квартальный план точнее годового, месячный план точнее квартального, а недельный точнее месячного.

Между планированием и выполнением есть компромисс. Подробный план труднее составить, но легче выполнить. План верхнего уровня составить проще, но выполнить труднее. Обойти компромисс можно **иерархическим планированием** (`hierarchical planning`). Сначала planner составляет план верхнего уровня, например план на каждый квартал. Потом тот же или другой planner для каждого квартала составляет план на каждый месяц.

Все примеры планов выше используют точные имена функций, то есть очень детальны. У такого подхода есть проблема: набор инструментов агента со временем меняется. Функцию `get_time()` могут переименовать в `get_current_time()`. Тогда придётся обновить prompt и все примеры. Точные имена функций мешают и переиспользовать planner в разных сценариях с разными API инструментов. Если вы раньше дообучили модель генерировать планы под старый набор инструментов, придётся дообучать её заново под новый.

Чтобы этого избежать, планы можно составлять на более естественном языке, выше уровня имён функций конкретной области. Например, для вопроса «Какова цена самого продаваемого товара за прошлую неделю?»:

```text
1. get current date
2. retrieve the best-selling product last week
3. retrieve product information
4. generate query
5. generate response
```

На естественном языке plan generator устойчивее к изменениям в API инструментов. Если модель обучали в основном на естественном языке, ей, вероятно, легче понимать и создавать планы на естественном языке, и галлюцинирует она меньше.

Минус подхода: нужен переводчик, который превращает каждое действие на естественном языке в исполняемые команды.

> **Заметка автора.** Chameleon (Lu et al., 2023) называет такой переводчик генератором программ (`program generator`).

Но перевод намного проще, чем планирование, и с ним справятся более слабые модели с меньшим риском галлюцинаций. В нашем коде `ch06_agent_loop.py` ниже переводчик — функция `execute()`.

##### Сложные планы и control flow

Все примеры планов выше были последовательными: следующее действие всегда выполняется после предыдущего. Порядок выполнения действий называют **потоком управления** (`control flow`). Последовательный поток — только один из видов. Бывают ещё параллельный, `if` и цикл `for`.

![Четыре вида control flow: sequential, parallel, if и for loop с примерами из задач данных](/assets/ai-engineering/ch06-control-flows.png)

Как читать схему. Каждая рамка — один вид потока. У всех жёлтый блок «решение о порядке»: именно он определяет, что делать дальше. Sequential: B после A. Parallel: B и C одновременно. If: B или C по условию. For loop: повторять A, пока условие не выполнится.

- **Sequential** (последовательно): задача B выполняется после завершения задачи A, вероятно потому, что B зависит от A. Например, SQL-запрос можно выполнить только после того, как он переведён из естественного языка.
- **Parallel** (параллельно): задачи A и B выполняются одновременно. Например, на запрос «Найди самые продаваемые товары дешевле 100 долларов» агент может сначала найти 100 бестселлеров, а потом одновременно узнать цену каждого из них.
- **If** (условие): выполняется задача B или C, в зависимости от результата предыдущего шага. Например, агент сначала проверяет отчёт о прибыли NVIDIA, а по отчёту решает, продавать акции NVIDIA или покупать.
- **For loop** (цикл): повторять задачу A, пока не выполнится условие. Например, генерировать случайные числа, пока не найдётся простое.

В обычной разработке условия потоков управления заданы точно. В агентах потоки управления определяют AI-модели. Планы с непоследовательным потоком управления труднее создавать и переводить в исполняемые команды.

Когда вы оцениваете фреймворк для агентов, проверьте, какие потоки управления он поддерживает. Например, если системе нужно просмотреть десять сайтов, может ли она делать это одновременно? Параллельное выполнение заметно уменьшает задержку, которую видит пользователь.

#### Reflection и исправление ошибок

Даже лучшие планы нужно постоянно проверять и корректировать, чтобы повысить шансы на успех. Reflection не обязателен, чтобы работать как агент, но он нужен, чтобы добиваться успеха.

Reflection полезен на многих этапах задачи:

- после получения запроса: оценить, выполним ли запрос;
- после первого составления плана: оценить, разумен ли план;
- после каждого шага выполнения: оценить, не сбился ли агент с пути;
- после выполнения всего плана: оценить, выполнена ли задача.

Reflection и исправление ошибок — два разных механизма, которые работают вместе. Reflection даёт выводы, которые помогают обнаружить и исправить ошибки.

Reflection может делать тот же агент с помощью prompt на самокритику. Или отдельный компонент, например специальный scorer: модель, которая выдаёт для каждого результата конкретный балл.

**ReAct.** Чередование мышления и действия впервые предложила работа ReAct (Yao et al., 2022), и теперь это обычный паттерн агентов. Авторы используют термин «рассуждение» (`reasoning`) для обоих процессов: и планирования, и reflection. На каждом шаге агента просят объяснить своё рассуждение (планирование), выполнить действие и проанализировать наблюдение (reflection). Так повторяют, пока агент не решит, что задача выполнена. Обычно агента просят выдавать результат в формате, на примерах:

```text
Thought 1: …
Act 1: …
Observation 1: …

… [продолжать, пока reflection не решит, что задача выполнена] …

Thought N: …
Act N: Finish [ответ на запрос]
```

В книге показан пример агента на ReAct, который отвечает на вопрос из HotpotQA (Yang et al., 2018), benchmark для многошаговых вопросов. Мы нарисовали свой пример в духе data engineering: найти владельца таблицы.

![Пример ReAct: цепочка Мысль, Действие, Наблюдение; после неудачного поиска агент уточняет запрос и находит ответ](/assets/ai-engineering/ch06-react-example.png)

Как читать схему. Фиолетовое — мысли, синее — действия, жёлтое — наблюдения. Цепочка идёт змейкой: первая строка слева направо, вторая справа налево, третья снова слева направо. Поиск `stg_orders` ничего не нашёл. В мысли 3 агент учитывает наблюдение, меняет запрос на `stg_orders_v2` и находит владельца. Последнее действие `Finish` завершает задачу.

Reflection можно реализовать и в мультиагентной среде: один агент планирует и выполняет действия, а другой оценивает результат после каждого шага или после серии шагов.

> **Заметка автора.** Это напоминает метод агента actor-critic (Konda и Tsitsiklis, 1999) из reinforcement learning.

Если ответ агента не выполнил задачу, можно попросить агента подумать, почему так вышло и как исправиться. На основе этого предложения агент создаёт новый план. Так агенты учатся на своих ошибках. Например, в задаче генерации кода evaluator может заметить, что сгенерированный код проваливает треть тестов. Агент размышляет и приходит к выводу: причина в том, что он не учёл массивы, где все числа отрицательные. Тогда он генерирует новый код, который учитывает такие массивы.

**Reflexion** (Shinn et al., 2023) идёт именно этим путём. В этом фреймворке reflection разделён на два модуля: evaluator, который оценивает результат, и модуль self-reflection, который анализирует, что пошло не так. Авторы называют план «траекторией» (`trajectory`). На каждом шаге после оценки и самоанализа агент предлагает новую траекторию.

![Reflexion: задача, первая попытка (trajectory), оценка результата, self-reflection, новая попытка; пример с функцией проверки скобок](/assets/ai-engineering/ch06-reflexion.png)

Как читать схему. Верхняя строка — пять этапов: задача, trajectory, evaluation, self-reflection, next trajectory. Нижняя строка — пример с кодом. Агент написал функцию, считающую только число скобок. Собственные тесты упали. Self-reflection нашёл причину: не учтён порядок скобок. Новая версия кода это исправляет. В книге есть и второй пример, про робота на кухне: действие «взять сковороду с конфорки 1» не дало результата, и после reflection агент берёт сковороду с конфорки 2.

По сравнению с планированием reflection относительно проще реализовать, и она может дать удивительно хороший прирост качества. Минус подхода — задержка и стоимость. Мысли, наблюдения и иногда действия могут занимать много токенов, а это повышает стоимость и задержку, которую видит пользователь, особенно в задачах со многими промежуточными шагами. Чтобы агенты следовали формату, авторы ReAct и Reflexion использовали в prompt много примеров. Это увеличивает стоимость входных токенов и уменьшает контекст, доступный для другой информации.

Ниже мини-агент магазина Kitty Vogue с настоящей базой SQLite. Планировщик и text-to-SQL в нём mock, а всё остальное настоящее: проверка плана до запуска, translator, трасса в стиле ReAct, разбор ошибки SQL (reflection) и ограничение числа шагов. В реальной системе функции `planner()` и `text_to_sql()` заменяют вызовами модели.

<details>
<summary>Код: ch06_agent_loop.py</summary>

```python
"""Глава 6: цикл агента: план -> проверка плана -> выполнение tools -> наблюдение -> reflection.
Мини-агент магазина «Kitty Vogue» работает с настоящей базой SQLite (в памяти). Планировщик и text-to-SQL
здесь mock (простые правила), всё остальное — настоящее: SQL, проверка плана, журнал шагов, разбор ошибки.
В реальной системе planner() и text_to_sql() заменяют вызовами модели.
Показывает: план на естественном языке и translator, проверку плана до запуска, трассу в стиле ReAct,
reflection и исправление ошибки SQL, параллельные шаги (разница в latency) и ограничение числа шагов.
Запуск: python3 -I scripts/ai-engineering-code/ch06_agent_loop.py   (только стандартная библиотека)"""
import difflib
import random
import sqlite3
from datetime import date, timedelta

TODAY = date(2030, 9, 13)  # «сегодня» зафиксировано, чтобы вывод не менялся
rng = random.Random(3)
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE sales (order_id INT, sold_on TEXT, product TEXT, price REAL, units INT)")
PRICES = {"Fruity Fedora": 18.0, "Meow Mix Seasoning": 10.99, "Purr & Shake": 25.0, "Tabby Tie": 7.5, "Whisker Scarf": 12.0}
weights = {"Fruity Fedora": 5, "Meow Mix Seasoning": 3, "Purr & Shake": 2, "Tabby Tie": 1, "Whisker Scarf": 1}
for oid in range(1, 301):
    product = rng.choices(list(weights), weights=list(weights.values()))[0]
    day = TODAY - timedelta(days=rng.randint(0, 19))
    db.execute("INSERT INTO sales VALUES (?, ?, ?, ?, ?)", (oid, day.isoformat(), product, PRICES[product], rng.randint(1, 3)))
print(f"в таблице sales строк: {db.execute('SELECT count(*) FROM sales').fetchone()[0]}, «сегодня»: {TODAY}")

# ---------------------------------------------------------------- tools
CALLS = []  # журнал всех вызовов: имя, аргументы, результат


def tool(fn):
    def wrapper(*a, **kw):
        out = fn(*a, **kw)
        CALLS.append((fn.__name__, a or kw, out))
        return out
    wrapper.__name__ = fn.__name__
    return wrapper


@tool
def get_today_date():
    return TODAY.isoformat()


@tool
def run_sql(query):
    return db.execute(query).fetchall()  # при ошибке SQL бросит исключение — его увидит reflection


@tool
def fetch_product_info(product_name):
    return {"product": product_name, "price": PRICES[product_name]}


def text_to_sql(question, hint=None):
    """MOCK: шаблонный text-to-SQL. Первая попытка нарочно ошибается в имени колонки."""
    col = "product" if hint else "product_name"
    if "top product" in question:
        return f"SELECT {col}, SUM(units) AS u FROM sales WHERE sold_on >= '{(TODAY - timedelta(days=6)).isoformat()}' GROUP BY {col} ORDER BY u DESC LIMIT 1"
    return (f"SELECT SUM(units) FROM sales WHERE {col} = 'Fruity Fedora' "
            f"AND sold_on >= '{(TODAY - timedelta(days=7)).isoformat()}'")


# ---------------------------------------------------------------- planner (mock) + проверка плана
KNOWN_ACTIONS = {"get current date", "find top product of the last week", "get product info",
                 "count units sold", "generate response"}
MAX_STEPS = 6


def planner(task, attempt):
    """MOCK-планировщик. Первый план содержит действие, которого нет в списке tools."""
    if "price of the top product" in task:
        if attempt == 0:
            return ["search the web for prices", "get product info", "generate response"]  # плохой план
        return ["get current date", "find top product of the last week", "get product info", "generate response"]
    return ["count units sold", "generate response"]


def validate_plan(plan):
    problems = [f"нет такого действия: {a!r}" for a in plan if a not in KNOWN_ACTIONS]
    if len(plan) > MAX_STEPS:
        problems.append(f"слишком много шагов: {len(plan)} > {MAX_STEPS}")
    return problems


print("\n== 1. Планирование отделено от выполнения: сначала проверяем план")
task = "What is the price of the top product of the last week?"
for attempt in range(3):
    plan = planner(task, attempt)
    problems = validate_plan(plan)
    print(f"попытка {attempt + 1}: {plan}")
    if not problems:
        print("  план годен, выполняем")
        break
    print("  отклонён:", problems)

# ---------------------------------------------------------------- executor + reflection
print("\n== 2. Выполнение плана: мысль -> действие -> наблюдение (стиль ReAct)")
state = {}


def execute(action):
    """Translator: переводит шаг плана на естественном языке в вызов функции с параметрами из state."""
    if action == "get current date":
        state["today"] = get_today_date()
        return "today", state["today"]
    if action == "find top product of the last week":
        rows = run_sql(text_to_sql("top product", hint="schema"))
        state["top"] = rows[0][0]
        return "run_sql(top product)", rows
    if action == "get product info":
        state["info"] = fetch_product_info(state["top"])
        return f"fetch_product_info({state['top']!r})", state["info"]
    if action == "generate response":
        return "generate_response", f"Цена самого продаваемого товара ({state['top']}) — ${state['info']['price']}"


for i, step in enumerate(plan, 1):
    act, obs = execute(step)
    print(f"Мысль {i}: нужно выполнить шаг «{step}»")
    print(f"Действие {i}: {act}")
    print(f"Наблюдение {i}: {obs}")

print("\n== 3. Reflection: первая попытка SQL падает, агент разбирает ошибку и исправляет запрос")
question = "How many units of Fruity Fedora were sold in the last 7 days?"
hint, evaluator_verdict = None, None
for attempt in range(1, 4):
    sql = text_to_sql(question, hint)
    print(f"Попытка {attempt}. SQL: {sql}")
    try:
        result = run_sql(sql)
        print(f"  результат: {result} -> evaluator: цель достигнута")
        break
    except sqlite3.OperationalError as e:
        print(f"  ошибка выполнения: {e}")
        print("  evaluator: цель не достигнута")
        schema = [r[1] for r in db.execute("PRAGMA table_info(sales)")]
        missing = str(e).split(": ")[-1]
        close = difflib.get_close_matches(missing, schema, n=1, cutoff=0.5)
        print(f"  reflection: колонки {missing!r} нет. Колонки таблицы: {schema}. Ближайшая по написанию: {close}.")
        hint = "use real column names"
print("Без reflection агент остановился бы на первой ошибке или решил бы, что всё хорошо.")

print("\n== 4. Control flow: параллельные шаги снижают latency")
LATENCY_MS = 300  # условное время одного вызова tool
top5 = [r[0] for r in db.execute("SELECT product FROM sales GROUP BY product ORDER BY SUM(units) DESC LIMIT 5")]
print(f"шаг A: найти top-5 товаров -> {top5}")
print(f"шаги B..F: цена каждого из {len(top5)} товаров (независимые вызовы)")
print(f"  последовательно: {len(top5) * LATENCY_MS} мс, параллельно: {LATENCY_MS} мс (по условной задержке {LATENCY_MS} мс на вызов)")
under_15 = [p for p in top5 if PRICES[p] < 15]
print(f"запрос «топ-товары дешевле $15» -> {under_15}")

print("\n== 5. Цикл с условием и ограничение числа шагов")
n, steps = 0, 0
is_prime = lambda x: x > 1 and all(x % d for d in range(2, int(x ** 0.5) + 1))  # noqa: E731
r2 = random.Random(11)
while steps < MAX_STEPS * 5:  # жёсткий предел: агент не должен крутиться бесконечно
    steps += 1
    n = r2.randint(2, 40)
    if is_prime(n):
        break
print(f"генерируем числа, пока не получим простое: нашли {n}, шагов: {steps}")
print(f"предел шагов агента: {MAX_STEPS * 5}. Без предела ошибка планировщика сжигает деньги на API.")

print("\n== 6. Журнал вызовов (его нужно хранить и смотреть при разборе сбоев)")
print(f"всего вызовов tools: {len(CALLS)}")
for name, args, out in CALLS[:4]:
    print(f"  {name}: {str(out)[:60]}")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_agent_loop.py`. Реальный вывод:

```text
в таблице sales строк: 300, «сегодня»: 2030-09-13

== 1. Планирование отделено от выполнения: сначала проверяем план
попытка 1: ['search the web for prices', 'get product info', 'generate response']
  отклонён: ["нет такого действия: 'search the web for prices'"]
попытка 2: ['get current date', 'find top product of the last week', 'get product info', 'generate response']
  план годен, выполняем

== 2. Выполнение плана: мысль -> действие -> наблюдение (стиль ReAct)
Мысль 1: нужно выполнить шаг «get current date»
Действие 1: today
Наблюдение 1: 2030-09-13
Мысль 2: нужно выполнить шаг «find top product of the last week»
Действие 2: run_sql(top product)
Наблюдение 2: [('Fruity Fedora', 101)]
Мысль 3: нужно выполнить шаг «get product info»
Действие 3: fetch_product_info('Fruity Fedora')
Наблюдение 3: {'product': 'Fruity Fedora', 'price': 18.0}
Мысль 4: нужно выполнить шаг «generate response»
Действие 4: generate_response
Наблюдение 4: Цена самого продаваемого товара (Fruity Fedora) — $18.0

== 3. Reflection: первая попытка SQL падает, агент разбирает ошибку и исправляет запрос
Попытка 1. SQL: SELECT SUM(units) FROM sales WHERE product_name = 'Fruity Fedora' AND sold_on >= '2030-09-06'
  ошибка выполнения: no such column: product_name
  evaluator: цель не достигнута
  reflection: колонки 'product_name' нет. Колонки таблицы: ['order_id', 'sold_on', 'product', 'price', 'units']. Ближайшая по написанию: ['product'].
Попытка 2. SQL: SELECT SUM(units) FROM sales WHERE product = 'Fruity Fedora' AND sold_on >= '2030-09-06'
  результат: [(104,)] -> evaluator: цель достигнута
Без reflection агент остановился бы на первой ошибке или решил бы, что всё хорошо.

== 4. Control flow: параллельные шаги снижают latency
шаг A: найти top-5 товаров -> ['Fruity Fedora', 'Meow Mix Seasoning', 'Purr & Shake', 'Tabby Tie', 'Whisker Scarf']
шаги B..F: цена каждого из 5 товаров (независимые вызовы)
  последовательно: 1500 мс, параллельно: 300 мс (по условной задержке 300 мс на вызов)
запрос «топ-товары дешевле $15» -> ['Meow Mix Seasoning', 'Tabby Tie', 'Whisker Scarf']

== 5. Цикл с условием и ограничение числа шагов
генерируем числа, пока не получим простое: нашли 37, шагов: 2
предел шагов агента: 30. Без предела ошибка планировщика сжигает деньги на API.

== 6. Журнал вызовов (его нужно хранить и смотреть при разборе сбоев)
всего вызовов tools: 4
  get_today_date: 2030-09-13
  run_sql: [('Fruity Fedora', 101)]
  fetch_product_info: {'product': 'Fruity Fedora', 'price': 18.0}
  run_sql: [(104,)]
```

Что видно в выводе:

- Блок 1: первый план содержит действие `search the web for prices`, которого нет в списке. Проверка отклоняет его до запуска. Второй план годен.
- Блок 2: трасса выполнения. Параметры берутся из предыдущих шагов: дата из `get_today_date` дала окно «последние 7 дней» для запроса про топ-товар.
- Блок 3: reflection. Первый SQL падает: колонки `product_name` нет. Агент смотрит схему, находит ближайшее по написанию имя `product` и пробует снова. Evaluator после второй попытки видит результат и считает цель достигнутой.
- Блок 4: пять независимых вызовов за ценой товаров: последовательно 1500 мс, параллельно 300 мс. Это и есть выигрыш control flow `parallel`. Числа условные: мы задали задержку 300 мс на вызов.
- Блок 5: цикл с условием и жёсткий предел числа шагов. Без предела ошибка планировщика сжигает деньги на API.
- Блок 6: журнал вызовов. Его нужно сохранять: по нему разбирают сбои.

#### Выбор инструментов

Инструменты часто играют решающую роль в успехе задачи, поэтому их выбирать нужно внимательно. Что вы дадите агенту, зависит не только от среды и задачи, но и от AI-модели, которая им управляет.

Надёжного руководства по выбору лучших инструментов нет. В литературе по агентам очень разные наборы. Toolformer (Schick et al., 2023) дообучил GPT-J, чтобы он освоил пять инструментов. Chameleon (Lu et al., 2023) использует 13 инструментов. Gorilla (Patil et al., 2023) пытается заставить агентов выбрать правильный вызов API из 1645 API.

Больше инструментов даёт агенту больше возможностей. Но чем их больше, тем труднее эффективно ими пользоваться. Это похоже на людей: большой набор инструментов освоить труднее. К тому же больше инструментов значит больше описаний инструментов, которые могут не влезть в контекст модели.

Как и многие решения при разработке AI-приложений, выбор инструментов требует экспериментов и анализа. Вот что можно сделать:

- сравнить, как агент работает с разными наборами инструментов;
- провести **ablation study** (исследование с удалением): убрать один инструмент из набора и посмотреть, насколько упадёт качество агента. Если инструмент можно убрать без падения качества, уберите его;
- найти инструменты, на которых агент часто ошибается. Если инструмент оказался слишком сложным для агента (даже с длинными prompts и finetuning модель не учится им пользоваться), поменяйте инструмент;
- построить распределение вызовов инструментов, чтобы видеть, какие используются чаще всего, а какие реже всего.

На графике книги показано, как различается использование инструментов у GPT-4 и ChatGPT в Chameleon (Lu et al., 2023).

![Доля программ Chameleon, где вызван каждый tool: ChatGPT и GPT-4 на ScienceQA и TabMWP](/assets/ai-engineering/ch06-tool-usage.png)

Как читать схему. Это столбчатый график, мы нарисовали его по значениям, прочитанным с графика книги (округлены). Каждая пара столбиков — один инструмент: синий — ChatGPT, фиолетовый — GPT-4. Значение — доля программ, где инструмент был вызван. Верхний блок — ScienceQA, нижний — TabMWP.

Эксперименты Lu et al. (2023) показывают две вещи:

- **Разные задачи требуют разных инструментов.** ScienceQA (научные вопросы) гораздо сильнее опирается на инструменты поиска знаний, чем TabMWP (математика по таблицам). На ScienceQA поиск знаний вызывают в 72–81% программ, на TabMWP только в 16–25%. А на TabMWP главный инструмент — генератор программ (около 71–72%).
- **У разных моделей разные предпочтения.** GPT-4 использует более широкий набор инструментов, чем ChatGPT. ChatGPT, видимо, чаще выбирает подпись к изображению, а GPT-4 — поиск знаний.

> **Совет автора.** Когда оцениваете фреймворк для агентов, смотрите, какие planners и инструменты он поддерживает. Разные фреймворки могут специализироваться на разных категориях инструментов. AutoGPT, например, фокусируется на API соцсетей (Reddit, X и Wikipedia), а Composio — на корпоративных API (Google Apps, GitHub и Slack). Ваши потребности со временем изменятся, поэтому проверьте, как легко расширить агента новыми инструментами.

**Новые инструменты из старых.** Люди становятся продуктивнее не только за счёт имеющихся инструментов, но и за счёт того, что из простых инструментов делают всё более мощные. Может ли AI создавать новые инструменты из исходных?

Chameleon (Lu et al., 2023) предлагает изучать переходы между инструментами (`tool transition`): какова вероятность, что после инструмента X агент вызовет инструмент Y? Если два инструмента часто используют вместе, их можно объединить в более крупный инструмент. Если агент знает эту информацию, он сам может объединять первые инструменты, чтобы строить всё более сложные.

![Граф переходов между инструментами Chameleon: числа на стрелках — вероятность, что после одного tool будет вызван другой](/assets/ai-engineering/ch06-tool-transitions.png)

Как читать схему. Каждый блок — инструмент, стрелка — переход, число — вероятность. Например, после `knowledge_retrieval` агент всегда идёт в `solution_generator` (1,0). Граф начинается в START и заканчивается в END. Редкие переходы с вероятностью ниже 0,05 мы не рисовали, значения прочитаны с графика книги.

Voyager (Wang et al., 2023) предлагает **skill manager** — менеджер навыков. Он отслеживает новые навыки (инструменты), которые приобретает агент, чтобы использовать их потом. Каждый навык — это программа. Когда skill manager решает, что новый навык полезен (например, он успешно помог агенту выполнить задачу), он добавляет его в библиотеку навыков (по сути это аналог tool inventory). Позже навык можно достать для других задач.

### Сбои агента и оценка агента

Оценка — это поиск сбоев. Чем сложнее задача, тем больше мест, где агент может сломаться. Помимо сбоев, общих для всех AI-приложений (главы 3 и 4), у агентов есть свои уникальные сбои. Их вызывают планирование, выполнение инструментов и эффективность. Одни из них заметить легче, чем другие.

Чтобы оценить агента, нужно определить его виды сбоев и измерить, как часто случается каждый.

> **Заметка автора.** Автор сделал простой benchmark, который иллюстрирует эти сбои. Он лежит в GitHub-репозитории книги. Есть и готовые benchmarks и leaderboards для агентов: Berkeley Function Calling Leaderboard, AgentOps Evaluation Harness и TravelPlanner.

![Сбои агента: сбои планирования, сбои инструментов и неэффективность; что измерять в каждой группе](/assets/ai-engineering/ch06-agent-failures.png)

Как читать схему. Три колонки — три группы сбоев. В красных блоках перечислены конкретные сбои. В зелёных блоках под ними — что делать, чтобы их измерить: метрики планов, тесты каждого инструмента и сравнение эффективности с базой.

#### Сбои планирования

Планирование трудное и может провалиться многими способами. Самый частый сбой — неправильное использование инструментов. Агент может составить план с одной или несколькими такими ошибками:

- **Неверный инструмент** (`invalid tool`). Например, план содержит `bing_search`, но этого инструмента нет в наборе агента.
- **Верный инструмент, неверные параметры** (`valid tool, invalid parameters`). Например, агент вызывает `lbs_to_kg` с двумя параметрами. Инструмент в наборе есть, но принимает только один параметр, `lbs`.
- **Верный инструмент, неверные значения параметров** (`valid tool, wrong values`). Например, агент вызывает `lbs_to_kg` с одним параметром `lbs`, но передаёт 100, а нужно 120.

Другой вид сбоя планирования — **цель не достигнута** (`goal failure`). Это бывает, когда план не решает задачу или решает её, но нарушает условия. Представьте, что вы просите спланировать двухнедельную поездку из Сан-Франциско в Ханой с бюджетом 5000 $. Агент может спланировать поездку в Хошимин. Или двухнедельную поездку в Ханой, которая сильно превышает бюджет.

Ограничение, которое часто упускают при оценке агентов, — **время**. Часто время работы агента не важно: вы поручаете задачу и вас нужно лишь известить, когда она готова. Но во многих случаях агент становится менее полезным со временем. Например, вы просите агента подготовить заявку на грант, а он заканчивает её после дедлайна — толку мало.

Интересный вид сбоя планирования возникает из-за **ошибок в reflection**. Агент уверен, что выполнил задачу, хотя это не так. Например, вы просите расселить 50 человек в 30 гостиничных номеров. Агент расселяет только 40 и настаивает, что задача выполнена.

Чтобы проверить агента на сбои планирования, можно создать **planning dataset**. В нём каждый пример — кортеж `(task, tool inventory)`. Пусть агент составит для каждой задачи `K` планов. Посчитайте метрики:

- сколько из всех созданных планов валидны;
- сколько планов в среднем нужно составить агенту для задачи, чтобы получить валидный;
- сколько из всех вызовов инструментов валидны;
- как часто вызывается неверный инструмент;
- как часто верный инструмент вызывается с неверными параметрами;
- как часто верный инструмент вызывается с неверными значениями параметров.

Проанализируйте результаты агента и поищите закономерности. На каких типах задач агент ошибается чаще? Есть ли у вас гипотеза, почему? На каких инструментах модель часто ошибается? Некоторые инструменты агенту использовать труднее. Способность агента пользоваться трудным инструментом можно улучшить лучшим prompt, большим числом примеров или finetuning. Если ничего не помогает, подумайте, не заменить ли инструмент на более простой.

#### Сбои инструментов

Сбой инструмента — это когда выбран правильный инструмент, но его вывод неверен. Один вид сбоя: инструмент просто выдаёт неверный результат. Например, генератор подписи к изображению даёт неверное описание, а генератор SQL — неверный SQL.

Если агент составляет только планы верхнего уровня, а перевод каждого запланированного действия в исполняемые команды делает модуль-переводчик, ошибки могут быть из-за перевода.

Сбои инструментов бывают и потому, что у агента нет доступа к нужным инструментам. Очевидный пример: задача — получить из интернета текущие курсы акций, а доступа в интернет у агента нет.

Сбои инструментов зависят от инструмента. Каждый инструмент нужно тестировать независимо. Всегда печатайте каждый вызов инструмента и его вывод, чтобы их можно было проверить и оценить. Если у вас есть переводчик, сделайте для него benchmarks.

Чтобы обнаружить отсутствие инструментов, нужно знать, какие инструменты должны использоваться. Если ваш агент часто проваливается в определённой области, возможно, ему не хватает инструментов для неё. Поработайте с экспертами предметной области и посмотрите, какие инструменты использовали бы они.

#### Эффективность

Агент может составить хороший план и использовать нужные инструменты, но работать неэффективно. Что отслеживать, чтобы оценить эффективность:

- сколько шагов агенту в среднем нужно, чтобы выполнить задачу;
- сколько в среднем стоит выполнение задачи;
- сколько обычно занимает каждое действие. Есть ли действия, которые особенно долгие или дорогие?

Сравнивайте эти показатели с базой (`baseline`), которой может быть другой агент или человек-оператор. Сравнивая AI-агентов с людьми, помните: люди и AI действуют по-разному. Что эффективно для человека, может быть неэффективно для AI, и наоборот. Например, человеку неэффективно открывать 100 веб-страниц, а AI-агенту, который может открыть все страницы сразу, это тривиально.

Ниже программа, которая считает то, о чём говорит автор. Ошибки накапливаются. Planning dataset и метрики планов. Ablation инструментов. Частота и переходы инструментов (пары для слияния). Сравнение агента с человеком. И `intent classifier` с классом `IRRELEVANT`. Планировщик в ней mock и ошибается с заданными вероятностями, а код оценки — настоящий: он классифицирует каждый вызов и считает метрики, как вы считали бы по логам реального агента. Числа на этих данных получены из нашего mock и ничего не доказывают про настоящие модели.

<details>
<summary>Код: ch06_agent_eval.py</summary>

```python
"""Глава 6: как оценивать агента: накопление ошибок, planning dataset, метрики сбоев планирования,
ablation tools, переходы между tools, эффективность и intent classifier с классом IRRELEVANT.
Планировщик здесь — mock, он нарочно ошибается с заданными вероятностями (seed фиксирован).
Настоящая часть — код оценки: он классифицирует каждый вызов и считает метрики, как вы считали бы по логам реального агента.
Запуск: python3 -I scripts/ai-engineering-code/ch06_agent_eval.py   (только стандартная библиотека)"""
import random
from collections import Counter, defaultdict

print("== 1. Ошибки накапливаются: точность на шаг -> успех всей задачи")
print(f"{'на шаг':>7} {'5 шагов':>9} {'10 шагов':>9} {'20 шагов':>9} {'100 шагов':>10}")
for p in (0.90, 0.95, 0.99):
    print(f"{p:>7.2f} " + " ".join(f"{p ** n:>{w}.1%}" for n, w in ((5, 9), (10, 9), (20, 9), (100, 10))))
print("При 95% на шаг 10 шагов дают около 60%, а 100 шагов — около 0,6%.")

# ---------------------------------------------------------------- planning dataset
INVENTORY = {  # tool inventory: имя -> список параметров
    "get_today_date": [],
    "fetch_top_products": ["start_date", "end_date", "num_products"],
    "fetch_product_info": ["product_name"],
    "lbs_to_kg": ["lbs"],
}
# planning dataset: (задача, ожидаемые вызовы с правильными значениями параметров)
DATASET = [
    ("price of the best-selling product last week", [("get_today_date", {}), ("fetch_top_products", {"start_date": "09-07", "end_date": "09-13", "num_products": 1}), ("fetch_product_info", {"product_name": "Fruity Fedora"})]),
    ("what is today's date", [("get_today_date", {})]),
    ("info about Fruity Fedora", [("fetch_product_info", {"product_name": "Fruity Fedora"})]),
    ("convert 40 lbs to kg", [("lbs_to_kg", {"lbs": 40})]),
    ("top 3 products last week", [("get_today_date", {}), ("fetch_top_products", {"start_date": "09-07", "end_date": "09-13", "num_products": 3})]),
    ("weight of the top product in kg", [("get_today_date", {}), ("fetch_top_products", {"start_date": "09-07", "end_date": "09-13", "num_products": 1}), ("lbs_to_kg", {"lbs": 2})]),
]
K = 5  # сколько планов просим у агента на каждую задачу
# mock: вероятности ошибок на вызов (сложные tools с несколькими параметрами ошибаются чаще)
P_ERR = {"get_today_date": (0.02, 0.0, 0.0), "fetch_top_products": (0.05, 0.15, 0.25),
         "fetch_product_info": (0.05, 0.05, 0.10), "lbs_to_kg": (0.03, 0.05, 0.10)}  # (invalid tool, bad params, wrong value)
rng = random.Random(2024)


def mock_plan(expected):
    """Агент пытается воспроизвести ожидаемый план, но иногда ломает вызов."""
    plan = []
    for name, args in expected:
        r = rng.random()
        p_tool, p_param, p_value = P_ERR[name]
        if r < p_tool:
            plan.append(("bing_search", {"q": name}))                       # invalid tool
        elif r < p_tool + p_param:
            plan.append((name, {**args, "extra": 1}))                       # valid tool, invalid params
        elif r < p_tool + p_param + p_value and args:
            k = next(iter(args))
            plan.append((name, {**args, k: "WRONG" if isinstance(args[k], str) else args[k] + 1}))  # wrong value
        else:
            plan.append((name, dict(args)))
    return plan


def classify_call(call, expected_call):
    name, args = call
    if name not in INVENTORY:
        return "invalid tool"
    if set(args) != set(INVENTORY[name]):
        return "valid tool, invalid params"
    if call != expected_call:
        return "valid tool, wrong values"
    return "ok"


print("\n== 2. Planning dataset: K планов на задачу, считаем метрики")
call_kinds, by_tool, plan_ok, attempts_to_valid, unsolved = Counter(), defaultdict(Counter), 0, [], 0
for task, expected in DATASET:
    first_valid = None
    for i in range(1, K + 1):
        plan = mock_plan(expected)
        kinds = [classify_call(c, e) for c, e in zip(plan, expected)]
        for (_, exp_call), kind in zip(zip(plan, expected), kinds):
            call_kinds[kind] += 1
            by_tool[exp_call[0]][kind] += 1  # ошибку записываем на tool, который агент должен был вызвать
        if all(k == "ok" for k in kinds):
            plan_ok += 1
            first_valid = first_valid or i
    if first_valid:
        attempts_to_valid.append(first_valid)
    else:
        unsolved += 1
total_plans, total_calls = len(DATASET) * K, sum(call_kinds.values())
print(f"планов всего: {total_plans}, валидных: {plan_ok} ({plan_ok / total_plans:.0%})")
print(f"среднее число планов до первого валидного (по решённым задачам): {sum(attempts_to_valid) / len(attempts_to_valid):.2f}; задач без валидного плана: {unsolved}")
print(f"вызовов всего: {total_calls}, валидных: {call_kinds['ok']} ({call_kinds['ok'] / total_calls:.0%})")
for kind in ("invalid tool", "valid tool, invalid params", "valid tool, wrong values"):
    print(f"  {kind:28s} {call_kinds[kind]:>3} ({call_kinds[kind] / total_calls:.0%})")
print("ошибки по tools (где модели труднее всего):")
for name, c in sorted(by_tool.items(), key=lambda x: -(sum(x[1].values()) - x[1]["ok"])):
    bad = sum(c.values()) - c["ok"]
    print(f"  {name:20s} ошибок {bad:>2} из {sum(c.values()):>2} вызовов")
print("Tool с самой высокой долей ошибок — кандидат на упрощение: лучше описание, больше примеров или другой tool.")

print("\n== 3. Ablation: убираем tool и смотрим, падает ли качество")
# для каждой задачи: какие наборы tools достаточны (альтернативные способы решить)
TASKS = {
    "цена хита недели": [{"get_today_date", "fetch_top_products", "fetch_product_info"}, {"sql_executor"}],
    "дата": [{"get_today_date"}],
    "инфо о товаре": [{"fetch_product_info"}, {"sql_executor"}],
    "фунты в кг": [{"lbs_to_kg"}, {"calculator"}],
    "топ-3 за неделю": [{"get_today_date", "fetch_top_products"}, {"sql_executor"}],
    "курс валют": [{"web_search"}],
}
ALL_TOOLS = set().union(*[s for sets in TASKS.values() for s in sets]) | {"image_captioner"}


def pass_rate(tools):
    return sum(any(s <= tools for s in sets) for sets in TASKS.values()) / len(TASKS)


base = pass_rate(ALL_TOOLS)
print(f"все tools: {base:.0%} задач решаются")
for t in sorted(ALL_TOOLS):
    rate = pass_rate(ALL_TOOLS - {t})
    verdict = "можно убрать" if rate == base else f"нужен (качество падает на {base - rate:.0%})"
    print(f"  без {t:20s}: {rate:.0%} -> {verdict}")
print("image_captioner не нужен ни одной задаче: лишний tool только занимает место в контексте.")

print("\n== 4. Какие tools вызывают чаще и какие идут друг за другом")
TRACES = [["get_today_date", "fetch_top_products", "fetch_product_info"]] * 5 + [["fetch_product_info"]] * 3 + \
         [["get_today_date", "fetch_top_products"]] * 3 + [["lbs_to_kg"]] * 2
calls = Counter(t for tr in TRACES for t in tr)
print("частота вызовов:", dict(calls.most_common()))
pairs = Counter((a, b) for tr in TRACES for a, b in zip(tr, tr[1:]))
nexts = Counter(a for tr in TRACES for a in tr[:-1])
for (a, b), n in pairs.most_common():
    print(f"  после {a} -> {b}: вероятность {n / nexts[a]:.2f}")
print("Пара get_today_date -> fetch_top_products идёт всегда вместе: её можно слить в один tool «топ товаров за неделю».")

print("\n== 5. Эффективность: сравнение агента с человеком")
runs = {"агент": [(6, 0.12, 40), (9, 0.20, 65), (5, 0.10, 35), (14, 0.35, 110)],
        "человек": [(8, 0.0, 600), (6, 0.0, 480), (7, 0.0, 520), (9, 0.0, 700)]}  # (шагов, $, секунд)
for who, rs in runs.items():
    n = len(rs)
    print(f"{who:8s}: шагов {sum(r[0] for r in rs) / n:.1f}, цена ${sum(r[1] for r in rs) / n:.2f}, время {sum(r[2] for r in rs) / n:.0f} с")
print("Цифры условные. Агент быстрее, но платит за API. Человек медленнее, зато без прямой цены. Сравнивайте обе оси.")
print("И помните: что просто человеку, может быть дорого агенту, и наоборот.")

print("\n== 6. Intent classifier: сначала понять, чего хотят, и отсеять чужие запросы")


def classify_intent(query):
    q = query.lower()
    if any(w in q for w in ("invoice", "payment", "charge")):
        return "billing"
    if any(w in q for w in ("password", "login", "sign in")):
        return "account"
    return "IRRELEVANT"


TOOLS_BY_INTENT = {"billing": ["fetch_recent_payments"], "account": ["search_docs"], "IRRELEVANT": []}
for q in ("Why was I charged twice?", "How do I reset my password?", "Write a poem about the sea"):
    intent = classify_intent(q)
    action = "вежливо отказать, не тратя вычисления" if intent == "IRRELEVANT" else f"дать агенту tools {TOOLS_BY_INTENT[intent]}"
    print(f"{q!r:36s} -> {intent:10s} -> {action}")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_agent_eval.py`. Реальный вывод:

```text
== 1. Ошибки накапливаются: точность на шаг -> успех всей задачи
 на шаг   5 шагов  10 шагов  20 шагов  100 шагов
   0.90     59.0%     34.9%     12.2%       0.0%
   0.95     77.4%     59.9%     35.8%       0.6%
   0.99     95.1%     90.4%     81.8%      36.6%
При 95% на шаг 10 шагов дают около 60%, а 100 шагов — около 0,6%.

== 2. Planning dataset: K планов на задачу, считаем метрики
планов всего: 30, валидных: 18 (60%)
среднее число планов до первого валидного (по решённым задачам): 1.17; задач без валидного плана: 0
вызовов всего: 55, валидных: 42 (76%)
  invalid tool                   1 (2%)
  valid tool, invalid params     1 (2%)
  valid tool, wrong values      11 (20%)
ошибки по tools (где модели труднее всего):
  fetch_top_products   ошибок  9 из 15 вызовов
  lbs_to_kg            ошибок  3 из 10 вызовов
  fetch_product_info   ошибок  1 из 10 вызовов
  get_today_date       ошибок  0 из 20 вызовов
Tool с самой высокой долей ошибок — кандидат на упрощение: лучше описание, больше примеров или другой tool.

== 3. Ablation: убираем tool и смотрим, падает ли качество
все tools: 100% задач решаются
  без calculator          : 100% -> можно убрать
  без fetch_product_info  : 100% -> можно убрать
  без fetch_top_products  : 100% -> можно убрать
  без get_today_date      : 83% -> нужен (качество падает на 17%)
  без image_captioner     : 100% -> можно убрать
  без lbs_to_kg           : 100% -> можно убрать
  без sql_executor        : 100% -> можно убрать
  без web_search          : 83% -> нужен (качество падает на 17%)
image_captioner не нужен ни одной задаче: лишний tool только занимает место в контексте.

== 4. Какие tools вызывают чаще и какие идут друг за другом
частота вызовов: {'get_today_date': 8, 'fetch_top_products': 8, 'fetch_product_info': 8, 'lbs_to_kg': 2}
  после get_today_date -> fetch_top_products: вероятность 1.00
  после fetch_top_products -> fetch_product_info: вероятность 1.00
Пара get_today_date -> fetch_top_products идёт всегда вместе: её можно слить в один tool «топ товаров за неделю».

== 5. Эффективность: сравнение агента с человеком
агент   : шагов 8.5, цена $0.19, время 62 с
человек : шагов 7.5, цена $0.00, время 575 с
Цифры условные. Агент быстрее, но платит за API. Человек медленнее, зато без прямой цены. Сравнивайте обе оси.
И помните: что просто человеку, может быть дорого агенту, и наоборот.

== 6. Intent classifier: сначала понять, чего хотят, и отсеять чужие запросы
'Why was I charged twice?'           -> billing    -> дать агенту tools ['fetch_recent_payments']
'How do I reset my password?'        -> account    -> дать агенту tools ['search_docs']
'Write a poem about the sea'         -> IRRELEVANT -> вежливо отказать, не тратя вычисления
```

Что видно в выводе:

- Блок 1: при 95% на шаг 10 шагов дают около 60%, а 100 шагов около 0,6%. При 99% на шаг 100 шагов дают только 36,6%.
- Блок 2: из 30 планов валидны 18. Из 55 вызовов 42 валидны. Самый частый сбой — неверные значения параметров (11 вызовов, 20%). Больше всего ошибок у `fetch_top_products`: у него три параметра, и он «трудный» по нашей конструкции. Такой инструмент — кандидат на упрощение.
- Блок 3: ablation показывает, какие инструменты нужны. Без `get_today_date` и без `web_search` качество падает, потому что запасного способа решить эти задачи нет. `image_captioner` не нужен ни одной задаче. Для остальных есть запасной путь (`sql_executor`, `calculator`), поэтому при удалении по одному качество не падает. Поэтому ablation нужно читать вместе с логом реальных запросов.
- Блок 4: `get_today_date` всегда идёт перед `fetch_top_products`. Такую пару можно слить в один инструмент.
- Блок 5: условное сравнение с человеком. Агент быстрее, но платит за API.
- Блок 6: `intent classifier` отсеивает «Write a poem about the sea» как `IRRELEVANT`, и агент не тратит на неё вычисления.

## Память (memory)

Под **памятью** понимают механизмы, которые позволяют модели хранить и использовать информацию. Память особенно полезна для приложений, которым нужно много знаний, таких как `RAG`, и для многошаговых приложений, таких как агенты. Системе `RAG` нужна память для расширенного контекста, который может расти за несколько ходов по мере поиска новой информации. Агентной системе нужна память, чтобы хранить инструкции, примеры, контекст, наборы инструментов, планы, выводы инструментов, рассуждения и многое другое. Хотя `RAG` и агенты предъявляют к памяти повышенные требования, она полезна любому AI-приложению, которому нужно что-то хранить.

У AI-модели обычно три главных механизма памяти:

- **Внутреннее знание** (`internal knowledge`). Сама модель — механизм памяти, потому что хранит знания из данных, на которых обучена. Это её внутреннее знание. Оно не меняется, пока не обновят саму модель. Модель может обращаться к нему при любом запросе.
- **Краткосрочная память** (`short-term memory`). Контекст модели — тоже механизм памяти. Предыдущие сообщения диалога можно добавить в контекст, и модель использует их для следующих ответов. Контекст можно считать краткосрочной памятью, потому что он не сохраняется между задачами (запросами). Доступ к нему быстрый, но ёмкость ограничена. Поэтому в нём хранят информацию, самую важную для текущей задачи.
- **Долгосрочная память** (`long-term memory`). Внешние источники данных, к которым модель обращается через поиск, например в системе `RAG`, — тоже память. Её можно считать долгосрочной, потому что она сохраняется между задачами. В отличие от внутреннего знания модели, информацию из долгосрочной памяти можно удалять без обновления модели.

У человека похожие механизмы памяти. Как дышать — это ваше внутреннее знание: вы обычно не забываете, как дышать, если вы не в серьёзной беде. Кратковременная память содержит то, что важно прямо сейчас, например имя человека, которого вы только что встретили. Долговременную память дополняют книги, компьютеры, заметки и так далее.

Какой механизм памяти выбрать для данных, зависит от того, как часто они нужны. Информацию, важную для всех задач, нужно встроить во внутреннее знание модели через обучение или finetuning. Редко нужную информацию лучше хранить в долгосрочной памяти. Краткосрочная память зарезервирована для срочной, контекстной информации.

![Иерархия памяти агента: внутреннее знание в весах, краткосрочная память (контекст) и долгосрочная память с retriever](/assets/ai-engineering/ch06-memory-hierarchy.png)

Как читать схему. В центре модель. К ней идут три источника: контекст (краткосрочная память), внешнее хранилище через retriever (долгосрочная память) и знания в весах (internal knowledge). Пунктирные стрелки показывают, куда стоит класть информацию: редкую уносим в долгосрочную память, нужную почти во всех задачах закладываем в модель обучением.

Память необходима человеку, чтобы функционировать. С развитием AI-приложений разработчики быстро поняли, что память важна и для AI-моделей. Появилось много инструментов управления памятью, а многие провайдеры моделей встроили внешнюю память. Расширять AI-модель системой памяти полезно по многим причинам. Вот некоторые:

- **Управление переполнением информации в рамках сессии.** Во время выполнения задачи агент получает много новой информации, и её может быть больше максимальной длины контекста. Лишнюю информацию можно отправить в систему памяти с долгосрочным хранением.
- **Сохранение информации между сессиями.** AI-коуч почти бесполезен, если каждый раз, когда вам нужен совет, приходится пересказывать всю свою жизнь. AI-ассистент раздражал бы, если бы постоянно забывал ваши предпочтения. Имея доступ к истории общения, агент может подстраивать действия под вас. Например, вы просите рекомендации книг, и модель помнит, что вам понравилась «Задача трёх тел». Она предложит похожие.
- **Повышение согласованности модели.** Если вы дважды зададите мне субъективный вопрос, например оцените шутку от 1 до 5, я с большей вероятностью отвечу одинаково, если помню прошлый ответ. Так и модель: если она может сослаться на прошлые ответы, она согласует будущие.
- **Сохранение структуры данных.** Текст неструктурирован по природе, поэтому и данные в контексте текстовой модели неструктурированы. Структурированные данные можно вставить в контекст. Например, таблицу построчно. Но нет гарантии, что модель поймёт, что это таблица. Система памяти, которая умеет хранить структурированные данные, помогает сохранить структурную целостность. Например, агент, которому поручили искать контакты потенциальных клиентов, может хранить их в таблице Excel. Агент может использовать и очередь, чтобы хранить порядок действий.

Система памяти для AI-моделей обычно состоит из двух функций:

- **Управление памятью** (`memory management`): решать, какую информацию хранить в краткосрочной и долгосрочной памяти;
- **Поиск в памяти** (`memory retrieval`): доставать из долгосрочной памяти информацию, релевантную задаче.

Поиск в памяти похож на поиск в `RAG`, потому что долгосрочная память — внешний источник данных. Здесь автор сосредоточен на управлении памятью. Оно обычно состоит из двух операций: **добавить** и **удалить** информацию. Если хранилище не ограничено, удалять не обязательно. Для долгосрочной памяти это может работать: внешнее хранилище относительно дёшево и легко расширяется. Но краткосрочная память ограничена максимальной длиной контекста модели, и ей нужна стратегия, что добавлять и что удалять.

Долгосрочную память можно использовать для хранения переполнения краткосрочной. Как это работает, зависит от того, сколько места вы отводите под краткосрочную память. Контекст, который идёт в модель на конкретный запрос, состоит из краткосрочной памяти и информации, найденной в долгосрочной. Поэтому ёмкость краткосрочной памяти определяется тем, какую долю контекста вы резервируете под информацию из долгосрочной. Например, если зарезервировано 30% контекста, то под краткосрочную память модель может использовать не больше 70% лимита. Когда этот предел достигнут, переполнение можно перенести в долгосрочную память.

![Бюджет контекста: 70% под историю диалога (short-term), 30% под найденное в long-term; переполнение по FIFO уходит в long-term](/assets/ai-engineering/ch06-memory-budget.png)

Как читать схему. Это наша схема на примере из книги (30% под long-term). Верхняя полоса — весь контекст модели, она делится на две части: историю диалога и найденные факты. Когда история упирается в свой предел, самые старые сообщения (FIFO) уходят в долгосрочную память. По запросу нужные факты возвращаются через `memory retrieval`. Красная заметка напоминает риск FIFO.

Как и многие другие компоненты главы, управление памятью важно не только для AI-приложений. Управление памятью — краеугольный камень всех систем работы с данными, и придумано много стратегий эффективного использования памяти.

**FIFO.** Самая простая стратегия — `FIFO` (first in, first out, «первым пришёл — первым ушёл»). Что первым попало в краткосрочную память, то первым переносится во внешнее хранилище. Когда разговор становится длиннее, провайдеры API вроде OpenAI могут начать убирать его начало. Фреймворки вроде LangChain умеют хранить N последних сообщений или N последних токенов. В длинном разговоре эта стратегия предполагает, что ранние сообщения менее важны для текущего обсуждения. Но предположение может оказаться фатально неверным. В некоторых разговорах самые ранние сообщения содержат больше всего информации, особенно когда они задают цель разговора. `FIFO` просто реализовать, но модель может потерять важное.

> **Заметка автора.** В человеческих разговорах бывает наоборот: первые сообщения — любезности.

> **Заметка автора.** Стратегии на основе использования, например удаление самой редко используемой информации, сложнее: нужно знать, когда модель использует конкретную информацию.

**Избавление от избыточности.** Более изощрённые стратегии убирают избыточность. В человеческих языках есть избыточность: она повышает ясность и компенсирует возможные недопонимания. Если найти способ автоматически обнаруживать избыточность, объём памяти заметно сократится.

Один способ — использовать **summary** (краткое изложение) разговора. Его может сделать та же или другая модель. Вместе с отслеживанием именованных сущностей summary очень помогает. Bae et al. (2022) пошли дальше. Получив summary, они хотели построить новую память, объединив старую память с ключевой информацией, которой в summary не хватало. Для этого они обучили классификатор, который для каждого предложения в памяти и каждого предложения в summary решает, добавить в новую память только одно из них, оба или ни одного.

Liu et al. (2023) использовали подход через reflection. После каждого действия агента просят сделать две вещи:

1. Подумать об информации, которую он только что получил.
2. Решить, добавить ли новую информацию в память, слить ли её с существующей или заменить другой информацией, особенно если другая информация устарела и противоречит новой.

**Противоречия.** Если информация противоречит, одни оставляют более новую. Другие просят AI-модель выбрать, какую информацию сохранить. Как разбирать противоречия, зависит от сценария. Противоречия могут сбивать агента с толку, но могут и помогать ему учиться, глядя с разных сторон.

Ниже программа с памятью: бюджет контекста, три стратегии (FIFO без хранилища, FIFO с переносом в long-term, summary), `memory retrieval` и противоречия. Токены в ней считаются словами, а `summarize()` — простое правило. В реальной системе это вызов модели.

<details>
<summary>Код: ch06_memory.py</summary>

```python
"""Глава 6: memory системы: short-term (контекст) и long-term (внешнее хранилище), стратегии управления.
Показывает: бюджет контекста (часть отдана под long-term), переполнение и стратегию FIFO,
риск FIFO (теряется цель разговора), memory retrieval из long-term, сжатие в summary и обработку
противоречий (новый факт заменяет старый). Токены здесь = слова; summarize() — простое правило
(в реальной системе это вызов модели).
Запуск: python3 -I scripts/ai-engineering-code/ch06_memory.py   (только стандартная библиотека)"""
import re

CONTEXT_LIMIT = 90   # «токенов» в контексте
RESERVED = 0.30      # доля контекста под информацию из long-term
SHORT_CAP = int(CONTEXT_LIMIT * (1 - RESERVED))
print(f"== 0. Бюджет: контекст {CONTEXT_LIMIT} токенов, под long-term отдано {RESERVED:.0%}, на short-term остаётся {SHORT_CAP}")

dialog = [
    "I am planning a two-week trip to Vietnam with a budget of 5000 dollars and I am vegetarian.",
    "Which city should I visit first?",
    "Hanoi is a good start because the old quarter is easy to walk.",
    "How many days do I need there?",
    "Three days are enough for the main sights.",
    "What about transport between cities?",
    "Night trains are cheap and flights are fast.",
    "Is it safe to take taxis?",
    "Use a ride app and check the price before the ride.",
    "What should I pack?",
    "Light clothes and a rain jacket for the wet season.",
]


def tokens(text):
    return len(text.split())


class Memory:
    def __init__(self, strategy):
        self.strategy, self.short, self.long = strategy, [], []

    def used(self):
        return sum(tokens(m) for m in self.short)

    def add(self, message):
        self.short.append(message)
        while self.used() > SHORT_CAP and len(self.short) > 1:
            oldest = self.short.pop(0)  # FIFO: что вошло первым, уходит первым
            if self.strategy == "fifo_drop":
                continue                # просто забываем
            if self.strategy == "fifo_to_longterm":
                self.long.append(oldest)  # переносим в long-term
            elif self.strategy == "summary":
                self.long.append(summarize(oldest))  # в long-term кладём сжатую версию

    def retrieve(self, query, k=1):
        """memory retrieval: ищем в long-term по пересечению слов (как простейший term-based поиск)."""
        q = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored = sorted(self.long, key=lambda m: -len(q & set(re.findall(r"[a-z0-9]+", m.lower()))))
        return [m for m in scored[:k] if q & set(re.findall(r"[a-z0-9]+", m.lower()))]


def summarize(text):
    """MOCK: оставляем числа и слова с большой буквы (сущности). Модель сделала бы связный пересказ."""
    keep = [w for w in re.findall(r"[A-Za-z0-9]+", text) if w[0].isdigit() or (w[0].isupper() and w != "I") or w in ("budget", "vegetarian", "trip")]
    return "summary: " + " ".join(keep)


print("\n== 1. Три стратегии на одном диалоге; потом спрашиваем: «What is my budget?»")
for strategy in ("fifo_drop", "fifo_to_longterm", "summary"):
    mem = Memory(strategy)
    for msg in dialog:
        mem.add(msg)
    in_short = any("5000" in m for m in mem.short)
    found = mem.retrieve("What is my budget for the trip?", k=1)
    print(f"[{strategy}] short-term занято {mem.used()} из {SHORT_CAP}, сообщений: {len(mem.short)}; в short-term есть бюджет: {in_short}")
    if strategy == "fifo_drop":
        print("  long-term нет. Бюджет потерян: модель переспросит или выдумает.")
    else:
        print(f"  из long-term найдено: {found}")
print("Самое первое сообщение содержало цель разговора, и FIFO убрал его первым.")

print("\n== 2. Что остаётся в short-term после FIFO")
mem = Memory("fifo_to_longterm")
for msg in dialog:
    mem.add(msg)
for m in mem.short:
    print("  short:", m[:60])
print(f"в long-term перенесено сообщений: {len(mem.long)}")

print("\n== 3. Противоречия: новый факт заменяет старый (merge / replace / add)")
facts = {}


def remember(key, value, turn):
    if key not in facts:
        facts[key] = (value, turn)
        return f"добавили {key}={value}"
    old_value, old_turn = facts[key]
    if old_value == value:
        return f"{key}={value} уже есть, повтор"
    facts[key] = (value, turn)  # правило: побеждает более новое. Можно спросить модель или пользователя.
    return f"заменили {key}: {old_value} (ход {old_turn}) -> {value} (ход {turn})"


for turn, (k, v) in enumerate([("budget", "5000"), ("diet", "vegetarian"), ("budget", "5000"), ("budget", "7000")], 1):
    print(f"ход {turn}: {remember(k, v, turn)}")
print("итоговая память:", {k: v for k, (v, _) in facts.items()})
print("Правило «новое побеждает» — одно из возможных. Иногда противоречие нужно показать пользователю.")
```

</details>

Запуск: `python3 scripts/ai-engineering-code/ch06_memory.py`. Реальный вывод:

```text
== 0. Бюджет: контекст 90 токенов, под long-term отдано 30%, на short-term остаётся 62

== 1. Три стратегии на одном диалоге; потом спрашиваем: «What is my budget?»
[fifo_drop] short-term занято 59 из 62, сообщений: 8; в short-term есть бюджет: False
  long-term нет. Бюджет потерян: модель переспросит или выдумает.
[fifo_to_longterm] short-term занято 59 из 62, сообщений: 8; в short-term есть бюджет: False
  из long-term найдено: ['I am planning a two-week trip to Vietnam with a budget of 5000 dollars and I am vegetarian.']
[summary] short-term занято 59 из 62, сообщений: 8; в short-term есть бюджет: False
  из long-term найдено: ['summary: trip Vietnam budget 5000 vegetarian']
Самое первое сообщение содержало цель разговора, и FIFO убрал его первым.

== 2. Что остаётся в short-term после FIFO
  short: How many days do I need there?
  short: Three days are enough for the main sights.
  short: What about transport between cities?
  short: Night trains are cheap and flights are fast.
  short: Is it safe to take taxis?
  short: Use a ride app and check the price before the ride.
  short: What should I pack?
  short: Light clothes and a rain jacket for the wet season.
в long-term перенесено сообщений: 3

== 3. Противоречия: новый факт заменяет старый (merge / replace / add)
ход 1: добавили budget=5000
ход 2: добавили diet=vegetarian
ход 3: budget=5000 уже есть, повтор
ход 4: заменили budget: 5000 (ход 1) -> 7000 (ход 4)
итоговая память: {'budget': '7000', 'diet': 'vegetarian'}
Правило «новое побеждает» — одно из возможных. Иногда противоречие нужно показать пользователю.
```

Что видно в выводе:

- Блок 0: контекст 90 токенов, под long-term отдано 30%, на short-term остаётся 62.
- Блок 1: все три стратегии одинаково переполняют short-term и теряют первое сообщение, в котором была цель разговора (бюджет 5000 и вегетарианство). Без long-term бюджет потерян. С переносом в long-term и поиском бюджет находится. Со summary в long-term остаётся сжатый след: «trip Vietnam budget 5000 vegetarian».
- Блок 2: в short-term остались последние сообщения, в long-term перенесено три первых.
- Блок 3: противоречие «бюджет 5000» против «бюджет 7000». Правило «побеждает более новое» заменяет значение. Иногда лучше спросить пользователя.

## Практика в DuckDB: поиск и логи агента

Для data engineer это знакомые вещи. Inverted index — таблица `(term, chunk_id, tf)`. BM25 — запрос с join и агрегацией. RRF — `UNION ALL` и `GROUP BY`. Метрики retrieval — агрегация по двум таблицам: что нашли и что релевантно. Лог вызовов агента — обычная таблица событий, по ней считают метрики сбоев. Построим всё это в SQL.

Запустите `duckdb` в терминале или откройте [shell.duckdb.org](https://shell.duckdb.org). Блоки идут по порядку, в одной сессии.

### Шаг 1. Документы и chunks

В таблице `docs` четыре маленьких документа про data engineering. Абзацы внутри документа разделены `||`. Мы режем текст на chunks (один абзац — один chunk) прямо в SQL.

```sql
CREATE TABLE docs AS
SELECT * FROM (VALUES
  (1, 'dbt incremental', 'An incremental model in dbt only processes new rows||Use the is_incremental macro and a unique key to merge changed rows||Run a full refresh when the schema of the source changes'),
  (2, 'Airflow retries', 'Airflow retries a failed task three times by default||Set retry_delay to wait between attempts||Send an alert to Slack when a task fails after all retries'),
  (3, 'Snowflake costs', 'Snowflake bills compute by the second while a warehouse runs||Auto suspend stops the warehouse after a minute of silence||Resize the warehouse only when queries are slow'),
  (4, 'Password reset', 'To reset the password open the login page||Click forgot password and check your email for the reset link||If the link expired request a new one')
) t(doc_id, title, body);

-- chunking в SQL: режем body по разделителю '||'. Один абзац = один chunk.
CREATE TABLE chunks AS
SELECT row_number() OVER (ORDER BY doc_id, pos) AS chunk_id, doc_id, pos, text
FROM (
  SELECT doc_id, unnest(string_split(body, '||')) AS text,
         unnest(generate_series(1, len(string_split(body, '||')))) AS pos
  FROM docs
);

SELECT chunk_id, doc_id, pos, text FROM chunks ORDER BY chunk_id LIMIT 4;
```

```text
┌──────────┬────────┬───────┬─────────────────────────────────────────────────────────────────────┐
│ chunk_id │ doc_id │  pos  │                                text                                 │
│  int64   │ int32  │ int64 │                               varchar                               │
├──────────┼────────┼───────┼─────────────────────────────────────────────────────────────────────┤
│        1 │      1 │     1 │ An incremental model in dbt only processes new rows                 │
│        2 │      1 │     2 │ Use the is_incremental macro and a unique key to merge changed rows │
│        3 │      1 │     3 │ Run a full refresh when the schema of the source changes            │
│        4 │      2 │     1 │ Airflow retries a failed task three times by default                │
└──────────┴────────┴───────┴─────────────────────────────────────────────────────────────────────┘
```

Что видно:

- Из 4 документов получилось 12 chunks (по 3 абзаца). Здесь показаны первые четыре.
- Колонка `pos` хранит порядок абзаца в документе. Он пригодится, если захочется склеивать соседние chunks.

### Шаг 2. Inverted index

Превращаем текст в токены (нижний регистр, без стоп-слов), считаем `tf` для каждой пары (термин, chunk), `df` для каждого термина и длину каждого chunk.

```sql
CREATE TABLE stopwords AS
SELECT * FROM (VALUES ('a'), ('an'), ('the'), ('of'), ('to'), ('in'), ('and'), ('is'), ('for'), ('when'),
                      ('only'), ('by'), ('or'), ('after'), ('all'), ('how'), ('while')) t(word);

-- токены: нижний регистр, только слова, без стоп-слов
CREATE TABLE tokens AS
SELECT chunk_id, term
FROM (SELECT chunk_id, unnest(regexp_split_to_array(lower(text), '[^a-z0-9_]+')) AS term FROM chunks)
WHERE term <> '' AND term NOT IN (SELECT word FROM stopwords);

-- inverted index: термин -> в каких chunks и сколько раз (tf)
CREATE TABLE chunk_terms AS
SELECT term, chunk_id, count(*) AS tf FROM tokens GROUP BY term, chunk_id;

CREATE TABLE term_df AS SELECT term, count(*) AS df FROM chunk_terms GROUP BY term;
CREATE TABLE chunk_len AS SELECT chunk_id, count(*) AS len FROM tokens GROUP BY chunk_id;

SELECT term, chunk_id, tf FROM chunk_terms WHERE term IN ('retries', 'reset', 'warehouse') ORDER BY term, chunk_id;
```

```text
┌───────────┬──────────┬───────┐
│   term    │ chunk_id │  tf   │
│  varchar  │  int64   │ int64 │
├───────────┼──────────┼───────┤
│ reset     │       10 │     1 │
│ reset     │       11 │     1 │
│ retries   │        4 │     1 │
│ retries   │        6 │     1 │
│ warehouse │        7 │     1 │
│ warehouse │        8 │     1 │
│ warehouse │        9 │     1 │
└───────────┴──────────┴───────┘
```

Что видно: слово `warehouse` есть в трёх chunks, `retries` в двух. Именно такую структуру Elasticsearch хранит в inverted index.

### Шаг 3. Проверяем

Каждый chunk должен получить хотя бы один токен. Первый запрос должен вернуть 0 строк.

```sql
-- проверка: у каждого chunk есть хотя бы один токен. Запрос должен вернуть 0 строк.
SELECT c.chunk_id FROM chunks c LEFT JOIN chunk_len l USING (chunk_id) WHERE l.len IS NULL;

SELECT count(*) AS chunks, (SELECT count(*) FROM term_df) AS distinct_terms,
       (SELECT round(avg(len), 1) FROM chunk_len) AS avg_len
FROM chunks;
```

```text
┌──────────┐
│ chunk_id │
│  int64   │
├──────────┤
│  0 rows  │
└──────────┘
┌────────┬────────────────┬─────────┐
│ chunks │ distinct_terms │ avg_len │
│ int64  │     int64      │ double  │
├────────┼────────────────┼─────────┤
│     12 │             65 │     6.2 │
└────────┴────────────────┴─────────┘
```

### Шаг 4. BM25 на SQL

Оформим BM25 как табличный макрос `bm25_search(q)`: он принимает текст запроса и возвращает chunks с баллами. Формула та же, что в нашем Python-коде: `k1 = 1,5`, `b = 0,75`.

```sql
CREATE MACRO bm25_search(q) AS TABLE
  WITH query_terms AS (SELECT DISTINCT unnest(regexp_split_to_array(lower(q), '[^a-z0-9_]+')) AS term),
       stats AS (SELECT count(*) AS n, avg(len) AS avg_len FROM chunk_len)
  SELECT ct.chunk_id,
         round(sum(ln(1 + (s.n - d.df + 0.5) / (d.df + 0.5))                          -- IDF
                   * ct.tf * 2.5 / (ct.tf + 1.5 * (0.25 + 0.75 * l.len / s.avg_len))), 3) AS bm25  -- TF с поправкой на длину
  FROM query_terms qt
  JOIN chunk_terms ct USING (term)
  JOIN term_df d USING (term)
  JOIN chunk_len l USING (chunk_id)
  CROSS JOIN stats s
  GROUP BY ct.chunk_id;
```

Пробуем три запроса.

```sql
SELECT b.chunk_id, b.bm25, c.text FROM bm25_search('how to retry a failed task') b JOIN chunks c USING (chunk_id) ORDER BY b.bm25 DESC, b.chunk_id;

SELECT b.chunk_id, b.bm25, c.text FROM bm25_search('reset password email') b JOIN chunks c USING (chunk_id) ORDER BY b.bm25 DESC, b.chunk_id;

-- синонимы и другие формы слова: «order», «fast» не встречаются в документах
SELECT count(*) AS hits FROM bm25_search('how fast is my order');
```

```text
┌──────────┬────────┬────────────────────────────────────────────────────────────┐
│ chunk_id │  bm25  │                            text                            │
│  int64   │ double │                          varchar                           │
├──────────┼────────┼────────────────────────────────────────────────────────────┤
│        4 │   3.59 │ Airflow retries a failed task three times by default       │
│        6 │  1.669 │ Send an alert to Slack when a task fails after all retries │
└──────────┴────────┴────────────────────────────────────────────────────────────┘
┌──────────┬────────┬───────────────────────────────────────────────────────────────┐
│ chunk_id │  bm25  │                             text                              │
│  int64   │ double │                            varchar                            │
├──────────┼────────┼───────────────────────────────────────────────────────────────┤
│       11 │  4.813 │ Click forgot password and check your email for the reset link │
│       10 │  3.604 │ To reset the password open the login page                     │
└──────────┴────────┴───────────────────────────────────────────────────────────────┘
┌───────┐
│ hits  │
│ int64 │
├───────┤
│     0 │
└───────┘
```

Что видно:

- По запросу «how to retry a failed task» найдены два chunks про Airflow. Chunk 5 (`Set retry_delay…`) не найден: в запросе `retry`, а в chunk `retry_delay`. Term-based поиск не знает, что это близкие слова.
- По запросу «reset password email» первым идёт chunk 11, где совпали три слова. Chunk 10 ниже.
- «how fast is my order» не находит ничего: общих слов нет. Это слабое место, которое лечит embedding-based поиск.

### Шаг 5. Hybrid: слияние рангов RRF

Пусть embedding-based retriever по тому же запросу вернул chunks 4, 5 и 6. Мы подставляем его ответ вручную: настоящая vector database здесь не нужна. Сольём два рейтинга формулой `1 / (60 + rank)`.

```sql
-- рейтинг BM25 по запросу
CREATE TABLE bm25_rank AS
SELECT 'bm25' AS src, chunk_id, row_number() OVER (ORDER BY bm25 DESC, chunk_id) AS rnk
FROM bm25_search('how to retry a failed task');

-- рейтинг vector database: подставлен руками (как будто ответил embedding-based retriever)
CREATE TABLE emb_rank AS
SELECT 'emb' AS src, * FROM (VALUES (4, 1), (5, 2), (6, 3)) t(chunk_id, rnk);

-- RRF: score = сумма 1 / (60 + rank) по всем рейтингам
SELECT chunk_id, round(sum(1.0 / (60 + rnk)), 5) AS rrf_score,
       string_agg(src || '=' || rnk, ', ' ORDER BY src) AS ranks
FROM (SELECT * FROM bm25_rank UNION ALL SELECT * FROM emb_rank)
GROUP BY chunk_id ORDER BY rrf_score DESC, chunk_id;
```

```text
┌──────────┬───────────┬───────────────┐
│ chunk_id │ rrf_score │     ranks     │
│  int64   │  double   │    varchar    │
├──────────┼───────────┼───────────────┤
│        4 │   0.03279 │ bm25=1, emb=1 │
│        6 │     0.032 │ bm25=2, emb=3 │
│        5 │   0.01613 │ emb=2         │
└──────────┴───────────┴───────────────┘
```

Что видно: chunk 4 первый в обоих рейтингах и получил максимум. Chunk 5 нашёл только embedding-based поиск (BM25 пропустил его из-за `retry_delay`), но в итоговом рейтинге он есть. Chunk 6 стоит выше chunk 5, потому что его назвали оба retriever.

### Шаг 6. Метрики retrieval

В таблице `relevance` — что считается релевантным (разметка людьми или AI judge). В `retrieved` — что вернул retriever при `k = 3`. Считаем `context precision` и `context recall`.

```sql
-- evaluation set: что мы считаем релевантным (разметка людьми или AI judge)
CREATE TABLE relevance AS
SELECT * FROM (VALUES ('q1', 4), ('q1', 5), ('q1', 6), ('q2', 10), ('q2', 11)) t(query_id, chunk_id);

-- что вернул retriever (k = 3) и на каком ранге
CREATE TABLE retrieved AS
SELECT * FROM (VALUES ('q1', 4, 1), ('q1', 6, 2), ('q1', 1, 3),
                      ('q2', 2, 1), ('q2', 10, 2), ('q2', 3, 3)) t(query_id, chunk_id, rnk);

SELECT r.query_id,
       count(*) AS found,
       sum((rel.chunk_id IS NOT NULL)::INT) AS relevant_found,
       round(sum((rel.chunk_id IS NOT NULL)::INT) / count(*), 2) AS context_precision,
       round(sum((rel.chunk_id IS NOT NULL)::INT)
             / (SELECT count(*) FROM relevance x WHERE x.query_id = r.query_id), 2) AS context_recall
FROM retrieved r LEFT JOIN relevance rel USING (query_id, chunk_id)
GROUP BY r.query_id ORDER BY r.query_id;
```

```text
┌──────────┬───────┬────────────────┬───────────────────┬────────────────┐
│ query_id │ found │ relevant_found │ context_precision │ context_recall │
│ varchar  │ int64 │     int128     │      double       │     double     │
├──────────┼───────┼────────────────┼───────────────────┼────────────────┤
│ q1       │     3 │              2 │              0.67 │           0.67 │
│ q2       │     3 │              1 │              0.33 │            0.5 │
└──────────┴───────┴────────────────┴───────────────────┴────────────────┘
```

Что видно:

- Для `q1` из трёх найденных документов релевантны два: precision 0,67. Всего релевантных три, найдено два: recall 0,67.
- Для `q2` релевантен один из трёх найденных: precision 0,33. Релевантных всего два, найден один: recall 0,5.
- Recall потребовал знать все релевантные chunks для каждого запроса, поэтому его считать дороже.

### Шаг 7. Запрос из примера Kitty Vogue

Вернёмся к text-to-SQL из раздела про таблицы. Создадим маленькую таблицу `sales` и выполним запрос, который модель написала бы по вопросу про Fruity Fedora. В DuckDB вместо `CURDATE()` из MySQL мы пишем дату явно, «сегодня» из примера книги: 13 сентября 2030.

```sql
CREATE TABLE sales AS
SELECT * FROM (VALUES
  (1, DATE '2030-09-04', 'Fruity Fedora', 18.00, 1),
  (2, DATE '2030-09-08', 'Fruity Fedora', 18.00, 2),
  (3, DATE '2030-09-10', 'Purr & Shake', 25.00, 2),
  (4, DATE '2030-09-12', 'Fruity Fedora', 18.00, 3),
  (5, DATE '2030-09-13', 'Meow Mix Seasoning', 10.99, 1),
  (6, DATE '2030-09-13', 'Fruity Fedora', 18.00, 1)
) t(order_id, sold_on, product_name, price, units);

-- запрос, который text-to-SQL модель написала бы по вопросу «Сколько Fruity Fedora продали за последние 7 дней?»
-- «Сегодня» зафиксировано датой из примера книги (13 сентября 2030), чтобы результат не менялся.
SELECT sum(units) AS total_units_sold
FROM sales
WHERE product_name = 'Fruity Fedora'
  AND sold_on >= DATE '2030-09-13' - INTERVAL 7 DAY;
```

```text
┌──────────────────┐
│ total_units_sold │
│      int128      │
├──────────────────┤
│                6 │
└──────────────────┘
```

Что видно: за последние 7 дней продано 6 штук (заказы 2, 4 и 6: 2 + 3 + 1). Заказ 1 старше семи дней и в сумму не входит. Этот результат text-to-SQL и отдал бы generative model, чтобы она написала ответ.

### Шаг 8. Лог вызовов агента

Теперь другая сторона главы: оценка агента. Мы генерируем лог вызовов: 80 запусков по 2–6 шагов. Данные случайные, но с фиксированным seed, и в них нарочно «трудный» инструмент `fetch_top_products`. Для `write`-инструмента `update_price` есть колонка `approved` (человек подтвердил) и `executed` (действие выполнено).

```sql
SELECT setseed(0.6);

CREATE TABLE tool_inventory AS
SELECT * FROM (VALUES
  ('get_today_date', 'read'), ('fetch_top_products', 'read'), ('fetch_product_info', 'read'),
  ('run_sql', 'read'), ('update_price', 'write')
) t(tool_name, access);

-- лог вызовов tools: 80 запусков агента по 2-6 шагов. Данные случайные, но с «трудным» tool fetch_top_products.
CREATE TABLE agent_calls AS
WITH steps AS (
  SELECT run_id, step, random() AS r_tool, random() AS r_out, random() AS r_appr
  FROM generate_series(1, 80) a(run_id), generate_series(1, 6) b(step)
  WHERE step <= 2 + run_id % 5
), picked AS (
  SELECT *, list_extract(['get_today_date', 'fetch_top_products', 'fetch_product_info', 'run_sql', 'update_price'],
                         1 + floor(r_tool * 5)::INT) AS tool,
         CASE WHEN list_extract(['get_today_date', 'fetch_top_products', 'fetch_product_info', 'run_sql', 'update_price'],
                                1 + floor(r_tool * 5)::INT) = 'fetch_top_products' THEN 2.5 ELSE 1.0 END AS hardness
  FROM steps
), outcomes AS (
  SELECT *,
         CASE WHEN r_out < 0.03 * hardness THEN 'invalid_tool'
              WHEN r_out < 0.08 * hardness THEN 'invalid_params'
              WHEN r_out < 0.16 * hardness THEN 'wrong_value'
              ELSE 'ok' END AS outcome
  FROM picked
)
SELECT run_id, step,
       CASE WHEN outcome = 'invalid_tool' THEN 'bing_search' ELSE tool END AS requested_tool,
       outcome,
       (tool = 'update_price' AND r_appr < 0.7) AS approved,                    -- человек подтвердил write-действие
       outcome = 'ok' AND (tool <> 'update_price' OR r_appr < 0.7) AS executed,  -- write без подтверждения не выполняется
       300 + floor(random() * 1200)::INT AS tokens
FROM outcomes;
```

Считаем метрики. Это те же вопросы, что автор предлагает задать planning dataset.

```sql
-- 1. Как часто и как именно ломаются вызовы
SELECT outcome, count(*) AS calls, round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM agent_calls GROUP BY outcome ORDER BY calls DESC;

-- 2. На каких tools ошибок больше всего (invalid_tool считаем отдельно: такого tool нет в inventory)
SELECT requested_tool, count(*) AS calls, round(100.0 * avg((outcome <> 'ok')::INT), 1) AS error_pct
FROM agent_calls WHERE requested_tool IN (SELECT tool_name FROM tool_inventory)
GROUP BY requested_tool ORDER BY error_pct DESC;

-- 3. Эффективность: шагов и токенов на задачу
SELECT round(avg(steps), 1) AS avg_steps, round(avg(tokens)) AS avg_tokens, max(steps) AS max_steps
FROM (SELECT run_id, count(*) AS steps, sum(tokens) AS tokens FROM agent_calls GROUP BY run_id);
```

```text
┌────────────────┬───────┬────────┐
│    outcome     │ calls │  pct   │
│    varchar     │ int64 │ double │
├────────────────┼───────┼────────┤
│ ok             │   259 │   80.9 │
│ wrong_value    │    34 │   10.6 │
│ invalid_params │    19 │    5.9 │
│ invalid_tool   │     8 │    2.5 │
└────────────────┴───────┴────────┘
┌────────────────────┬───────┬───────────┐
│   requested_tool   │ calls │ error_pct │
│      varchar       │ int64 │  double   │
├────────────────────┼───────┼───────────┤
│ fetch_top_products │    61 │      31.1 │
│ update_price       │    64 │      15.6 │
│ run_sql            │    78 │      15.4 │
│ get_today_date     │    62 │      14.5 │
│ fetch_product_info │    47 │       6.4 │
└────────────────────┴───────┴───────────┘
┌───────────┬────────────┬───────────┐
│ avg_steps │ avg_tokens │ max_steps │
│  double   │   double   │   int64   │
├───────────┼────────────┼───────────┤
│       4.0 │     3708.0 │         6 │
└───────────┴────────────┴───────────┘
```

Что видно:

- Около 81% вызовов успешны. Чаще всего ломаются значения параметров (10,6%), потом параметры (5,9%), потом имя инструмента (2,5%).
- У `fetch_top_products` доля ошибок 31,1%, у остальных 6–16%. Это кандидат на упрощение: лучше описание, примеры, разбиение на два инструмента.
- В среднем 4 шага и около 3700 токенов на запуск. Это показатели эффективности. Их сравнивают с базой.

### Шаг 9. Проверка политики write-действий

Это аудит безопасности по логу. Write-действие не должно выполняться без подтверждения. Запрос должен вернуть 0 строк.

```sql
-- проверка политики: write-действие не должно выполняться без подтверждения. Должно вернуть 0 строк.
SELECT c.run_id, c.step, c.requested_tool
FROM agent_calls c JOIN tool_inventory i ON i.tool_name = c.requested_tool
WHERE i.access = 'write' AND c.executed AND NOT c.approved;

-- сколько write-вызовов подождало подтверждения и сколько выполнено
SELECT count(*) AS write_calls, count(*) FILTER (WHERE executed) AS executed, count(*) FILTER (WHERE NOT approved) AS not_approved
FROM agent_calls WHERE requested_tool = 'update_price';
```

```text
┌────────┬───────┬────────────────┐
│ run_id │ step  │ requested_tool │
│ int64  │ int64 │    varchar     │
├────────┴───────┴────────────────┤
│             0 rows              │
└─────────────────────────────────┘
┌─────────────┬──────────┬──────────────┐
│ write_calls │ executed │ not_approved │
│    int64    │  int64   │    int64     │
├─────────────┼──────────┼──────────────┤
│          64 │       32 │           25 │
└─────────────┴──────────┴──────────────┘
```

Что видно: нарушений нет (в наших данных так задумано). Из 64 вызовов `update_price` 32 выполнены, а 25 не получили подтверждения и не выполнялись. В реальных логах такую проверку запускают по расписанию, и любая строка в результате — тревога.

### Задания

1. Посчитайте `MRR` для таблиц `retrieved` и `relevance`.
2. Для запроса «reset the warehouse link» найдите по одному лучшему chunk в каждом документе. Верните название документа, текст chunk и балл.
3. Найдите три запуска агента с наибольшим числом шагов и покажите, сколько токенов они потратили.
4. Проверьте согласованность лога: вызовы с исходом `invalid_tool` должны иметь имя инструмента, которого нет в `tool_inventory`. Запрос про нарушения должен вернуть 0 строк.

<details><summary>Решение 1</summary>

```sql
SELECT round(avg(1.0 / first_rank), 2) AS mrr
FROM (SELECT r.query_id, min(r.rnk) AS first_rank
      FROM retrieved r JOIN relevance rel USING (query_id, chunk_id)
      GROUP BY r.query_id);
```

```text
┌────────┐
│  mrr   │
│ double │
├────────┤
│   0.75 │
└────────┘
```

Для `q1` первый верный chunk стоит на ранге 1 (вклад 1), для `q2` на ранге 2 (вклад 0,5). Среднее: 0,75.

</details>

<details><summary>Решение 2</summary>

```sql
SELECT d.title, c.text, b.bm25
FROM bm25_search('reset the warehouse link') b
JOIN chunks c USING (chunk_id)
JOIN docs d USING (doc_id)
QUALIFY row_number() OVER (PARTITION BY d.doc_id ORDER BY b.bm25 DESC) = 1
ORDER BY b.bm25 DESC;
```

```text
┌─────────────────┬───────────────────────────────────────────────────────────────┬────────┐
│      title      │                             text                              │  bm25  │
│     varchar     │                            varchar                            │ double │
├─────────────────┼───────────────────────────────────────────────────────────────┼────────┤
│ Password reset  │ Click forgot password and check your email for the reset link │  2.908 │
│ Snowflake costs │ Resize the warehouse only when queries are slow               │  1.434 │
└─────────────────┴───────────────────────────────────────────────────────────────┴────────┘
```

`QUALIFY` с `row_number()` оставляет по одной лучшей строке на документ. Документ про dbt и Airflow в выдаче нет: у них нет общих слов с запросом.

</details>

<details><summary>Решение 3</summary>

```sql
SELECT run_id, count(*) AS steps, sum(tokens) AS tokens
FROM agent_calls GROUP BY run_id ORDER BY steps DESC, tokens DESC, run_id LIMIT 3;
```

```text
┌────────┬───────┬────────┐
│ run_id │ steps │ tokens │
│ int64  │ int64 │ int128 │
├────────┼───────┼────────┤
│      9 │     6 │   7902 │
│     19 │     6 │   6596 │
│     69 │     6 │   6547 │
└────────┴───────┴────────┘
```

Запуски с 6 шагами самые дорогие. Такие выбросы смотрят вручную: часто в них видны циклы или лишние вызовы.

</details>

<details><summary>Решение 4</summary>

```sql
SELECT c.requested_tool, count(*) AS bad_calls
FROM agent_calls c
WHERE c.outcome = 'invalid_tool' AND c.requested_tool IN (SELECT tool_name FROM tool_inventory)
GROUP BY c.requested_tool;
```

```text
┌────────────────┬───────────┐
│ requested_tool │ bad_calls │
│    varchar     │   int64   │
├────────────────┴───────────┤
│           0 rows           │
└────────────────────────────┘
```

Пустой результат значит, что все ошибочные имена инструментов действительно отсутствуют в inventory. Если появятся строки, значит, логгер записывает исход неверно.

</details>

## Итоги главы

- `RAG` работает в два шага: сначала находит релевантную информацию во внешней памяти, потом использует её для более точного ответа. Он родился как обход ограничения контекста, но помогает и экономнее использовать информацию, повышать качество и снижать цену.
- Многим задачам нужно больше фоновых знаний, чем помещается в контекст: кодовым ассистентам нужны целые кодовые базы, исследовательским ассистентам нужно разобрать несколько книг. Длинный контекст не отменяет `RAG`: данных всегда больше, а длинный контекст дорог, медленнее и модель использует его не идеально.
- Успех `RAG` зависит от качества retriever. Term-based поиск (`BM25`, Elasticsearch) проще, быстрее, дешевле и даёт сильную базу для сравнения. Embedding-based поиск требует больше вычислений, но может обойти term-based, особенно после дообучения. В production чаще всего их объединяют: последовательно (reranking) или параллельно (`RRF`).
- Embedding-based поиск стоит на vector search. Он же лежит в основе поиска и рекомендаций в интернете. Приближённые алгоритмы (`LSH`, `HNSW`, `IVF`, product quantization, `Annoy`) обменивают точность на скорость, время построения и размер индекса.
- Retrieval улучшают четырьмя тактиками: `chunking` (размер, overlap, структура), `reranking`, переписывание запроса и `contextual retrieval`. Качество измеряют по компонентам (context precision и recall, ранговые метрики, качество embeddings) и сквозным образом по итоговым ответам.
- `RAG` можно считать частным случаем агента, где retriever — один из инструментов. Он работает не только с текстом, но и с картинками (мультимодальные embeddings) и с таблицами (text-to-SQL).
- Агента определяют его среда и инструменты, к которым он имеет доступ. В AI-агенте AI — планировщик: он разбирает задачу, рассматривает варианты и выбирает самый перспективный. Инструменты бывают трёх видов: расширение знаний, расширение возможностей и действия записи. Больше инструментов — больше возможностей, но выбирать и использовать их труднее.
- Планирование стоит отделять от выполнения и проверять план до запуска. Помогают function calling, иерархическое планирование, разные виды control flow, reflection (`ReAct`, `Reflexion`) и намеренный выбор набора инструментов через ablation. Способность моделей планировать остаётся открытым вопросом. Накопление ошибок делает агентам необходимыми сильные модели.
- Сбои агента бывают трёх групп: сбои планирования (неверный инструмент, неверные параметры или значения, цель не достигнута, ошибка reflection), сбои инструментов и неэффективность. Каждую группу нужно измерять отдельно.
- Чем больше агент автоматизирован, тем катастрофичнее могут быть его ошибки. Использование инструментов открывает агента для рисков безопасности (глава 5), поэтому в реальном мире нужны строгие меры защиты и подтверждение человеком.
- Память состоит из внутреннего знания (веса), краткосрочной памяти (контекст) и долгосрочной (внешнее хранилище). Система памяти решает две задачи: управление (что хранить и удалять: FIFO, summary, reflection) и поиск. Она помогает справляться с переполнением контекста и держать информацию между сессиями.
- `RAG` и агенты — это prompt-подходы: они влияют на качество модели только через вход и не меняют саму модель. Изменение самой модели может открыть ещё больше возможностей. Об этом следующая [глава 7](/book-summaries/ai/ai-engineering/07-finetuning/).

## Что изменилось к 2026 году

Книга написана в 2024 году. Вот что важно знать сейчас. Это наше дополнение, его нет в книге.

- **MCP (Model Context Protocol).** Открытый протокол от Anthropic (ноябрь 2024). Стал стандартом для подключения tools и данных к моделям. Его поддерживают OpenAI, Google, Microsoft. Есть MCP-серверы для баз данных, BI и облаков.
- **Agentic search вместо классического RAG.** Coding agents часто ищут без vector store: grep, чтение файлов, SQL. Агент сам решает, что найти. Vector RAG остаётся для больших коллекций текста.
- **Агенты в продакшене.** Есть SDK для агентов у OpenAI, Anthropic, Google. Агенты работают в браузере и на компьютере (computer use).
- **Память агентов стала функцией продукта.** Долгая память есть в ChatGPT, Claude, coding agents. Идеи из главы (короткая и долгая память) это и описывают.
- **Контекст стал длиннее.** Совет про 200 000 токенов в этой главе относится к 2024 году. Сейчас у ряда моделей контекст миллион токенов и больше. Аргументы автора остаются в силе: длинный контекст стоит денег, добавляет задержку, и модель использует его не идеально. Поэтому «положить всё в prompt» остаётся вариантом для небольшой базы знаний, а для больших баз нужен поиск.

## Ключевые термины

| Термин | Значение |
|---|---|
| `RAG` | Достать данные из внешней памяти и дать их модели как контекст для ответа |
| `retriever` / `generator` | Часть, которая ищет данные / часть, которая пишет ответ |
| индексация и запрос (`indexing`, `querying`) | Подготовка данных для быстрого поиска заранее и поиск по запросу |
| `chunk`, `chunking` | Кусок документа и разбиение документов на куски |
| `overlap` | Перекрытие соседних chunks, чтобы смысл на границе не терялся |
| `term-based retrieval` | Поиск по словам (лексический): `TF-IDF`, `BM25`, Elasticsearch |
| `TF` | Term frequency: сколько раз термин встречается в документе |
| `IDF` | Inverse document frequency: чем в большем числе документов термин, тем он менее информативен |
| `BM25` | Вариант TF-IDF с поправкой на длину документа. Сильная база для сравнения |
| `inverted index` | Словарь «термин → документы, где он есть» |
| `embedding-based retrieval` | Поиск по смыслу: embeddings и vector search |
| `vector database` | Хранилище vectors с быстрым поиском ближайших |
| `k-NN` / `ANN` | Точный поиск k ближайших соседей перебором / приближённый, быстрее, но не гарантирует точный ответ |
| `LSH`, `HNSW`, `IVF`, product quantization, `Annoy` | Алгоритмы ANN: корзины, многослойный граф, кластеры, сжатие vectors, случайные деревья |
| `hybrid search` | Term-based и embedding-based поиск вместе |
| `reranking` | Пересортировка кандидатов более точным методом или по времени |
| `RRF` | Reciprocal rank fusion: балл документа = сумма `1 / (k + rank)` по всем рейтингам, обычно `k = 60` |
| `query rewriting` | Переписывание запроса, чтобы он был понятен без диалога |
| `contextual retrieval` | Добавление к chunk контекста (метаданные, вопросы, описание места в документе) |
| `context precision` / `context recall` | Доля релевантных среди найденных / доля найденных среди всех релевантных |
| `MRR`, `MAP`, `NDCG` | Ранговые метрики: учитывают порядок документов в выдаче |
| `MTEB`, `BEIR`, ANN-Benchmarks | Benchmarks для embeddings, для retrieval, для ANN-алгоритмов |
| text-to-SQL | Модель превращает вопрос и схему таблиц в SQL-запрос |
| агент (`agent`) | Система, которая воспринимает среду и действует в ней через инструменты |
| среда и действия (`environment`, `actions`) | То, где агент работает, и то, что он может делать |
| инструмент (`tool`), tool inventory | Функция или API, доступные агенту, и их набор |
| read-only и write actions | Инструменты, которые читают данные, и инструменты, которые меняют данные или мир |
| `function calling` | Модель выбирает инструмент и аргументы, а вызывает функцию ваш код |
| `planner`, `evaluator`, `executor` | Составляет план, проверяет его и результат, выполняет шаги |
| `control flow` | Порядок выполнения шагов: sequential, parallel, `if`, `for` |
| `hierarchical planning` | Сначала план верхнего уровня, потом детальные планы для его частей |
| `intent classifier` | Определяет, чего хочет пользователь; может пометить запрос как `IRRELEVANT` |
| `reflection` | Оценка плана или результата и исправление ошибок |
| `ReAct`, `Reflexion` | Паттерны: Thought–Act–Observation; evaluator плюс self-reflection и новая траектория |
| ablation study | Убрать один инструмент и посмотреть, упадёт ли качество |
| failure modes агента | Сбои планирования, сбои инструментов, неэффективность |
| `internal knowledge`, `short-term memory`, `long-term memory` | Знания в весах, контекст, внешнее хранилище |
| `memory management` / `memory retrieval` | Что хранить и удалять / как достать нужное из long-term |
| `FIFO` | Первым вошёл, первым вышел: самое старое уходит из short-term первым |

## Что это значит на практике

- **Retrieval это data pipeline.** Индексация: загрузка, очистка, chunking, embeddings, запись в index. Нужны расписание, версии, алерты и lineage, как в любом пайплайне.
- **Инкрементальные обновления.** Пересчёт embeddings стоит денег. Обновляйте только изменённые chunks, как `incremental` модель в `dbt`. При смене embedding model или tokenizer нужна полная переиндексация.
- **Свой evaluation set.** Запросы, документы и метки релевантности хранят как таблицы в warehouse. Версионируйте их. Считайте precision и recall по расписанию.
- **Не начинайте с vector database.** Сначала BM25 или полнотекстовый поиск как база. Потом hybrid. Векторы в PostgreSQL или warehouse могут хватить.
- **Text-to-SQL опирается на ваш слой данных.** Чистые имена колонок, описания в `dbt` docs, понятные grain и метрики делают модель точнее. Давайте ей отдельный read-only доступ к витринам, а не к сырым таблицам.
- **Write actions под контролем.** Права только на нужные таблицы, подтверждение человека, лог каждого вызова.
- **Стоимость агента.** Считайте шаги, токены и время на задачу. Складывайте их в таблицу логов, как метрики пайплайна.
- **Chunk — это строка таблицы со своим grain.** Храните `doc_id`, позицию, дату и метаданные рядом с текстом. Тогда chunking можно пересчитать, а выдачу объяснить и отфильтровать. Размер chunk и overlap подбирайте экспериментом на своём evaluation set.
- **Храните версию embedding model рядом с vectors.** Vectors от разных моделей несравнимы. Смена модели означает полный пересчёт, поэтому планируйте её как миграцию.
- **Точные идентификаторы ищите term-based поиском.** Имена таблиц, коды ошибок, ID, SKU embeddings «размывают». Hybrid search закрывает эту дыру.
- **Логируйте каждый вызов tool в таблицу.** Имя, аргументы, результат, длительность, токены, кто подтвердил. По такой таблице считаются доля валидных вызовов, цена задачи и аудит write-действий (мы сделали это в DuckDB).
- **Проверяйте аргументы вызова до выполнения.** Схема ловит неверный tool и лишние параметры, а неверное значение ловят отдельные проверки: сверка с данными запроса, `dry run`, ограничения диапазона.
- **Planning dataset — это регрессионный тест агента.** Запускайте его после смены prompt, модели или набора tools, как тесты `dbt` после смены модели данных.
- **Ставьте предел шагов, токенов и времени на задачу.** Ошибка планировщика без предела сжигает деньги на API.
- **Решайте, что можно забыть.** Долгосрочная память хранит личные данные пользователей. Нужны правила хранения и возможность удалить записи.
- **Отсекайте чужие запросы.** `intent classifier` с классом `IRRELEVANT` дешевле, чем агент, который тратит вычисления на то, что он не умеет.

## Вопросы для самопроверки

1. Какие два аргумента приводит автор в пользу того, что длинный контекст не отменяет `RAG`? Что на это влияет, если вы платите за каждый токен?
2. Почему term-based поиск не находит запрос «I lost access to my profile», а embedding-based может не найти код `EADDRNOTAVAIL (99)`? Как с этим помогает hybrid search?
3. Как размер chunk влияет на качество, стоимость и скорость поиска? Зачем нужен overlap?
4. Документ занял первое место у одного retriever и третье у другого. Посчитайте его балл `RRF` при `k = 60`. Почему при `k = 60` разница между рангами сглажена?
5. Агент делает 20 шагов, на каждом точность 95%. Какова вероятность, что вся цепочка прошла без ошибок? Что вы сделаете, чтобы снизить риск?
6. Почему планирование нужно отделять от выполнения и что проверяет validator плана? Какие виды сбоев планирования связаны с инструментами и как измерить каждый?
7. Чем различаются `internal knowledge`, short-term и long-term memory? Куда вы положите редкий факт, а куда информацию, нужную почти в каждой задаче? Чем опасна стратегия `FIFO`?

Предыдущая: [Глава 5. Prompt engineering](/book-summaries/ai/ai-engineering/05-prompt-engineering/). Следующая: [Глава 7. Finetuning](/book-summaries/ai/ai-engineering/07-finetuning/).
