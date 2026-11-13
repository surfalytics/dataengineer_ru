"""Глава 1: токены и цена запроса.
Часть 1. Мини-BPE: учим словарь токенов на крошечном корпусе. Видим, почему токены лучше слов и символов
         (меньше словаря, чем у слов; короче последовательность, чем у символов; новые слова не ломают модель).
Часть 2. Калькулятор запроса к API модели: токены, деньги, время. Цены ниже придуманы для примера, это НЕ прайс-лист.
         В реальной системе вы подставите цены своего провайдера и настоящий токенизатор.
Запуск: python3 -I scripts/ai-engineering-code/ch01_tokens_cost.py   (только стандартная библиотека)"""
from collections import Counter

# ---------- Часть 1. Мини-BPE ----------
STEMS = "cook load join sort scan wait chat chatgpt".split()
SUFFIXES = ["", "s", "ing", "ed", "er", "ers", "able", "ly"]
HELD_OUT = {"chatgpting", "loaders", "sortable", "waitly"}  # этих слов нет в обучающем корпусе: проверим, как токенизатор справится
CORPUS = [stem + suf for stem in STEMS for suf in SUFFIXES if stem + suf not in HELD_OUT]


def learn_bpe(words, n_merges):
    seqs = [tuple(w) for w in words]
    merges = []
    for _ in range(n_merges):
        pairs = Counter()
        for s in seqs:
            for a, b in zip(s, s[1:]):
                pairs[(a, b)] += 1
        if not pairs:
            break
        best = max(pairs, key=lambda p: (pairs[p], p))  # при равенстве берём по алфавиту: результат стабилен
        merges.append(best)
        new = []
        for s in seqs:
            out, i = [], 0
            while i < len(s):
                if i + 1 < len(s) and (s[i], s[i + 1]) == best:
                    out.append(s[i] + s[i + 1]); i += 2
                else:
                    out.append(s[i]); i += 1
            new.append(tuple(out))
        seqs = new
    return merges


def tokenize(word, merges):
    s = list(word)
    for a, b in merges:
        out, i = [], 0
        while i < len(s):
            if i + 1 < len(s) and s[i] == a and s[i + 1] == b:
                out.append(a + b); i += 2
            else:
                out.append(s[i]); i += 1
        s = out
    return s


N_MERGES = 30
merges = learn_bpe(CORPUS, n_merges=N_MERGES)
chars = sorted({c for w in CORPUS for c in w})
subword_vocab = set(chars) | {a + b for a, b in merges}
word_vocab = set(CORPUS)

print("== 1. Три способа выбрать токены")
print(f"слова:   словарь {len(word_vocab)} токенов (все слова корпуса)")
print(f"символы: словарь {len(chars)} токенов")
print(f"BPE:     словарь {len(subword_vocab)} токенов (символы + {N_MERGES} слияний)")

print("\n== 2. Как режутся слова")
for w in ["cooking", "joiners", "loaders", "chatgpting", "sortable"]:
    in_vocab = "есть" if w in word_vocab else "НЕТ"
    print(f"{w:<13} слово в словаре: {in_vocab:<4} | BPE: {tokenize(w, merges)} | символов: {len(w)}")

print("\n== 3. Длина последовательности для одного текста")
text = "cooking joiners loaders chatgpting".split()
n_word = len(text)  # слово = 1 токен; если слова нет в словаре, это <UNK> (тоже 1 токен, но смысл потерян)
unk = sum(1 for w in text if w not in word_vocab)
n_bpe = sum(len(tokenize(w, merges)) for w in text)
n_chr = sum(len(w) for w in text)
print(f"слова:   {n_word} токенов, из них <UNK> (смысл потерян): {unk}")
print(f"BPE:     {n_bpe} токенов, ничего не потеряно")
print(f"символы: {n_chr} токенов, ничего не потеряно, но последовательность в {n_chr / n_bpe:.1f} раза длиннее")

# ---------- Часть 2. Калькулятор запроса ----------
print("\n== 4. Правило из книги: 100 токенов ~ 75 слов")
TOKENS_PER_WORD = 4 / 3


def words_to_tokens(words):
    return round(words * TOKENS_PER_WORD)


for words in [75, 450, 110]:
    print(f"{words:>4} слов ~ {words_to_tokens(words):>4} токенов")

print("\n== 5. Цена и время одного запроса (цены придуманы)")
# цена в долларах за 1 миллион токенов: (вход, выход)
MODELS = {"большая модель": (5.00, 15.00), "малая модель": (0.25, 1.00)}
TTFT_MS, TPOT_MS = 400, 10  # время до первого токена и время на каждый следующий токен
REQ_PER_DAY = 20_000
in_tokens, out_tokens = words_to_tokens(450), words_to_tokens(110)
print(f"запрос: {in_tokens} токенов на входе, {out_tokens} на выходе, {REQ_PER_DAY} запросов в день")
latency = (TTFT_MS + TPOT_MS * out_tokens) / 1000
print(f"время ответа: {TTFT_MS} мс + {out_tokens} токенов x {TPOT_MS} мс = {latency:.2f} с")
for name, (p_in, p_out) in MODELS.items():
    one = (in_tokens * p_in + out_tokens * p_out) / 1_000_000
    month = one * REQ_PER_DAY * 30
    print(f"{name:<15}: ${one:.5f} за запрос, ${month:,.0f} в месяц".replace(",", " "))

print("\n== 6. Что будет, если провайдер снизит цены (в книге: цены упали на два порядка за год)")
p_in, p_out = MODELS["большая модель"]
one = (in_tokens * p_in + out_tokens * p_out) / 1_000_000
for factor in [1, 2, 10, 100]:
    print(f"цена / {factor:<3}: ${one / factor * REQ_PER_DAY * 30:>10,.0f} в месяц".replace(",", " "))
