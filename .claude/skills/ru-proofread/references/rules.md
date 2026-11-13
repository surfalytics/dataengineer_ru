# Rules for Russian technical text

Every example below comes from a real page of this site (DDIA chapter 6 test). Add new ones.

## 0. What we never touch

- Technical terms in English: `hot spot`, `rebalancing`, `scatter/gather`, `key range`, `pre-splitting`. Product names: MongoDB, Kafka.
- Code, inline code, commands, paths, URLs, image paths, front matter keys.
- Facts, numbers, the order of ideas.
- Inside backticks a term is not declined. In plain text an English term is used like a Russian noun: `в routing tier`, `два hot spot`.
- One form per term on a page. If the glossary says `consumer`, do not also write `потребитель`. If the glossary says `партиция`, do not also write `partition` (SQL keywords in code are fine). The script reports this as `term-drift`.
- Do not change the form the glossary gives, in either direction. If the glossary has no entry, keep the form the page uses most and report the term to the owner.

Gender of an English term in a sentence follows the Russian noun you would use for it. Use one gender for one term in all chapters. Write it in the glossary if it is not clear.

| Term | Behaves like | Example |
|---|---|---|
| `range scan` | «скан» (m) | эффективный range scan |
| `hot spot` | «точка» (f) or keep as a name | возник hot spot |
| `rebalancing` | «процесс» (m) | rebalancing нагружает сеть |

## 1. Punctuation

| Rule | Wrong | Right |
|---|---|---|
| Dash before «это» in a definition | Партиция в книге это то же, что shard | Партиция в книге — это то же, что shard |
| Dash for a dropped verb | часть определяет партицию, часть порядок | одна часть определяет партицию, другая — порядок |
| Colon, not comma, before an explanation | Не путайте с network partition, это сбой сети | Не путайте с network partition: это сбой сети |
| Comma before «и» between two clauses with different subjects | Узлы было дорого добавлять и нагрузка распределялась плохо | …добавлять, и нагрузка распределялась плохо |
| No comma inside a participle phrase | Индекс, разбитый отдельно, по term | Индекс, разбитый отдельно по term |
| Short dash in ranges | 00-99, 1-3 | 00–99, 1–3 |
| One dash per paragraph is plenty | three `—` in one paragraph | split the sentences, use a colon or a period |

Do not put a dash before «это» when «это» is not a link between two nouns:
`Как это работает`, `Если ключ растёт, это hot spot`, `Тогда это на практике не нужно`.

## 2. Meaning and sentence structure

Check every sentence: who does what to whom? Is there a subject, a verb, and an object?

| Problem | Wrong | Right |
|---|---|---|
| Verb without object | Термин плохо работает, он путает | Термин сбивает с толку и плохо работает |
| Wrong subject | Тогда чтение должно читать все 100 ключей | Тогда нужно прочитать все 100 ключей |
| Same root twice | запрос по датчикам требует отдельных запросов | выборка по датчикам требует отдельных запросов |
| Unclear brackets | range scan (цена) | range scan (например, по цене) |
| Noun for a thing that cannot do it | Индекс ищет значения | Индекс нужен для поиска по значению |
| Dropped predicate | для аналитики сложнее | для аналитики устроены сложнее |
| «Это/этого» with no clear link | от этого отказались | от этой схемы отказались |
| «Должен/обязан» for a thing | Хеш-функция не обязана быть криптографической | Хеш-функции не нужно быть криптографической / Хеш-функция может быть простой |
| Wrong agreement | Когда выбрать каждый? (about a neuter noun) | Когда выбирать каждый подход? |
| Wrong preposition after a verb | запускает на обновление; запустит на любую комбинацию | запускает при каждом обновлении; запустит при любой комбинации |
| Book or code does a human action | Книга проверяет, есть ли…; Consumer пишет шаблон и падает | В примере книги задача проверяет…; В consumer написан шаблон, и он падает |
| Verb missing after «советует» | Автор советует настоящий URI | Автор советует использовать настоящий URI |
| Impersonal verb without a subject | Но подходы смешивают | Но подходы можно смешивать |
| Same thing, two words (term drift) | потребитель / consumer в одном абзаце | consumer (as in the glossary) everywhere |

## 3. Calques from English

Source of truth: `scripts/ru-proofread/calques.tsv`. The script finds them. Samples:

| English | Wrong (calque) | Right |
|---|---|---|
| it makes sense | имеет смысл | логично, разумно |
| human in the loop | человек в цикле | участие человека |
| fairly (distributed) | справедливо распределена | равномерно распределена |
| overhead | лишние расходы | накладные расходы |
| to heal | не лечат проблему | не решают проблему |
| X has Y (for a system) | MongoDB имеет config server | В MongoDB есть config server |
| X follows Y | число партиций следует за объёмом | число партиций меняется вместе с объёмом |
| at the end of the day | в конце дня | в итоге |
| to address | адресовать проблему | решить проблему |
| actually | актуально | на самом деле |

Stop words (канцелярит). Say it with a verb: `является` → `это`; `осуществлять` → `делать`; `в рамках` → `в`, `при`; `данный` → `этот`; `в случае, если` → `если`.

## 4. Flow: how to make it pleasant to read

The site style is short sentences. That is good. But short sentences with no links read like a list of facts. The reader has to guess how one fact follows from another. Fix this without adding facts.

Targets (check with `check.py --stats`). They are a guide, not a goal:

| Number | Target | Dry page (example) |
|---|---|---|
| Median words per sentence | 8 or more | 5–6 |
| Sentences of 5 words or less | 30% or less | 40–57% |
| Link words per 100 sentences | 10 or more | 3–5 |

### The tools

1. **Link the sentences.** Put a word that shows the relation: «поэтому», «но», «а», «при этом», «к тому же», «например», «то есть», «в итоге». One link per 2–3 sentences is enough.
2. **Join two halves of one thought.** Use a colon, «и», «а», «но», «который», «когда».
3. **Unfold fragments.** In prose every sentence has a verb. Fragments are fine only in tables.
4. **Vary the rhythm.** No more than 3 short sentences in a row. Do not start three sentences with the same word. Mix short and medium sentences (10–20 words). A short sentence after two medium ones gives stress.
5. **Known first, new last.** The new or main word goes to the end of the sentence: `При росте данных нужен rebalancing` (new: rebalancing), `Rebalancing нужен при росте данных` (new: when).
6. **Use a verb, not a noun chain.** `для проведения анализа производительности` → `чтобы проанализировать скорость`.
7. **Cut long sentences.** More than 30 words: split in two. After joining, stay under 25 words.
8. **Use the same word for the same thing.** Not `партиция`, `раздел`, `кусок` in one section.
9. **Active voice.** `Приложение добавляет число к ключу`, not `Число добавляется приложением к ключу`. Passive is fine when the actor does not matter (`данные переносятся`).
10. **Read it aloud.** If you stumble, rewrite.

### Examples (real paragraphs)

Before (DDIA ch 6): five sentences, one link word.

> Автоматика удобна, но непредсказуема. Rebalancing нагружает сеть и узлы. Вместе с автоматическим детектором отказов возможен каскад: медленный узел сочтён мёртвым, нагрузка уходит на другие, они тоже замедляются. Поэтому часто нужен человек в цикле. Couchbase, Riak и Voldemort предлагают план, но ждут подтверждения.

After: same facts, the links are visible.

> Автоматика удобна, но непредсказуема. К тому же rebalancing нагружает сеть и узлы. В паре с автоматическим детектором отказов это может вызвать каскад: система считает медленный узел мёртвым и переносит его нагрузку на другие узлы, а те от этого тоже замедляются. Поэтому в процессе часто оставляют человека: Couchbase, Riak и Voldemort сами предлагают план, но ждут подтверждения.

What changed: «к тому же» (link, no new cause), «система считает» (a subject for the passive fragment), «а те от этого» (link inside the chain), the last two sentences joined with a colon (the second is an example of the first).

Before (fragments): `Новичок. Читайте по порядку. Главы 1, 2, 5 дают основу. Главу 9 оставьте на второй проход.`

After: `Новичку лучше читать по порядку: главы 1, 2 и 5 дают основу, а главу 9 можно оставить на второй проход.`

### Do not

- Do not add facts, numbers, examples, or opinions to make the text "livelier".
- **Do not add a cause the text does not state.** «Поэтому» and «потому что» are claims. In the example above the text does not say that automation is unpredictable *because* rebalancing is heavy. So the link is «к тому же», not «потому что».
- Do not add filler: «стоит отметить», «важно понимать», «как известно», «давайте разберёмся».
- Do not add jokes, emoji, or idioms.
- Do not turn tables into paragraphs or paragraphs into lists.
- Do not pad sentences to hit the numbers.

## 5. Typography (what the script checks)

- Quotes: «ёлочки», nested „лапки“. Never `"..."` in prose. In code and YAML keep straight quotes.
- Dash: `—` with spaces. Short dash `–` between numbers.
- Numbers in text: `0,85`, `10 000`, `20 %` or `20%` (pick the project's form and keep it). Inside code: `0.85`.
- No arrows in prose: write «после этого», «даёт».
- Do not add non-breaking spaces by hand. Do not run `typograf` on the Markdown source: it breaks list bullets and `**bold:**`.

## 6. Things that look wrong but are fine

- English term in a Russian sentence, not translated.
- `ключ равен timestamp`: both forms are fine.
- `Эффективные range scan`: fine if the sentence speaks about several scans.
- A table cell without a final period.
- A definition with a colon instead of a dash: `Skew: неравномерная нагрузка`.
- A sentence that starts with a Latin term.

When in doubt, leave the text and list it under "doubtful" in the report.
