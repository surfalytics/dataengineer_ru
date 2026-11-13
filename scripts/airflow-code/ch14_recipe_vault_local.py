"""Recipe Vault без платных API: chunks, UUID по содержимому, compare, поиск по cosine similarity.
Embedding тут игрушечный: считает слова, а не смысл. Только стандартная библиотека."""
import hashlib
import math
import re
import uuid

DIMS = 256


def chunk_id(text: str) -> str:
    """Тот же текст даёт тот же id, любая правка даёт новый id."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, text.strip()))


def create_chunks(recipes: dict) -> list:
    rows = []
    for name, r in recipes.items():
        for kind, text in (("Ингредиенты", r["ingredients"]), ("Инструкция", r["instructions"])):
            chunk = f"{name}\n{kind}: {text}".strip()
            rows.append({"recipe_name": name, "chunk": chunk, "chunk_uuid": chunk_id(chunk)})
    return rows


def embed(text: str) -> list:
    """Игрушечный embedding: мешок слов в 256 корзинах, длина вектора 1."""
    vec = [0.0] * DIMS
    for word in re.findall(r"\w+", text.lower()):
        vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIMS] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine(a: list, b: list) -> float:
    return sum(x * y for x, y in zip(a, b))  # векторы уже нормированы


class MiniVectorDB:
    """Заменяет Weaviate: хранит объекты и их векторы в словаре."""

    def __init__(self):
        self.objects = {}  # chunk_uuid -> (строка, вектор)

    def compare(self, rows: list) -> list:
        """Метит строки create / update. Совпавшие рецепты выбрасывает."""
        marked = []
        for name in dict.fromkeys(r["recipe_name"] for r in rows):
            mine = [r for r in rows if r["recipe_name"] == name]
            in_db = {u for u, (o, _) in self.objects.items() if o["recipe_name"] == name}
            if not in_db:
                marked += [{**r, "regime": "create"} for r in mine]
            elif {r["chunk_uuid"] for r in mine} != in_db:
                marked += [{**r, "regime": "update"} for r in mine]
        return marked

    def delete_outdated(self, marked: list) -> int:
        names = {r["recipe_name"] for r in marked if r["regime"] == "update"}
        old = [u for u, (o, _) in self.objects.items() if o["recipe_name"] in names]
        for u in old:
            del self.objects[u]
        return len(old)

    def save(self, marked: list) -> int:
        for r in marked:
            self.objects[r["chunk_uuid"]] = (r, embed(r["chunk"]))
        return len(marked)

    def search(self, question: str, k: int = 2) -> list:
        q = embed(question)
        scored = [(cosine(q, v), o["chunk"]) for o, v in self.objects.values()]
        return sorted(scored, reverse=True)[:k]


def run_day(db: MiniVectorDB, label: str, recipes: dict) -> None:
    marked = db.compare(create_chunks(recipes))
    modes = sorted({(r["recipe_name"], r["regime"]) for r in marked})
    deleted = db.delete_outdated(marked)
    saved = db.save(marked)
    print(f"{label}: метки={modes or 'нет'}, удалено={deleted}, записано={saved}, всего в базе={len(db.objects)}")


if __name__ == "__main__":
    day1 = {
        "Лазанья": {"ingredients": "листы теста, фарш, томаты, сыр", "instructions": "Слоями выложить, запекать 40 минут"},
        "Блины": {"ingredients": "молоко, яйца, мука", "instructions": "Смешать и жарить на сковороде"},
    }
    day2 = {  # Блины без изменений, в лазанью добавили базилик, плюс новый рецепт
        "Лазанья": {"ingredients": "листы теста, фарш, томаты, сыр, базилик", "instructions": day1["Лазанья"]["instructions"]},
        "Блины": day1["Блины"],
        "Окрошка": {"ingredients": "квас, огурцы, яйца, зелень", "instructions": "Нарезать и залить квасом"},
    }
    a = "Блины\nИнгредиенты: молоко, 2 яйца, мука"
    b = "Блины\nИнгредиенты: молоко, 3 яйца, мука"
    print("UUID (2 яйца):", chunk_id(a))
    print("UUID (3 яйца):", chunk_id(b))
    print("Пробелы по краям не важны:", chunk_id(a) == chunk_id(a + "  \n"))
    db = MiniVectorDB()
    run_day(db, "День 1", day1)
    run_day(db, "День 2", day2)
    run_day(db, "День 2, повтор", day2)
    print("Поиск 'ингредиенты лазанья':")
    for score, chunk in db.search("ингредиенты лазанья"):
        print(f"  {score:.2f}  {chunk.splitlines()[0]} / {chunk.splitlines()[1].split(':')[0]}")
    print("Prompt:")
    context = "\n".join(c for _, c in db.search("ингредиенты лазанья", k=1))
    template = "Отвечай только по контексту.\nВопрос: {input}\nКонтекст: {context}"
    print(template.format(input="ингредиенты лазанья", context=context))
