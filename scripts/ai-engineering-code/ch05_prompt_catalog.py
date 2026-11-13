"""Глава 5: prompt catalog. Prompt хранится отдельно от кода, у каждой версии есть метаданные.
Что показывает:
 1. класс PromptVersion: текст-шаблон, модель, приложение, автор, дата, параметры sampling, схемы входа и выхода;
 2. каталог: явные версии, поиск по метаданным, закрепление версии за приложением, список устаревших потребителей;
 3. разницу между «одна актуальная версия в Git» и каталогом с закреплёнными версиями;
 4. разбор простого .prompt-файла: метаданные в начале, текст-шаблон ниже.
Запуск: python3 -I scripts/ai-engineering-code/ch05_prompt_catalog.py   (только стандартная библиотека)"""
import difflib
import json
import string
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class PromptVersion:
    name: str
    version: int
    text: str                   # шаблон с переменными ${имя}
    model_name: str
    application: str            # для какого приложения написан
    creator: str
    date_created: str           # ISO-дата строкой
    temperature: float = 0.0    # лучшие параметры sampling для этого prompt
    top_p: float = 1.0
    input_schema: dict = field(default_factory=dict)    # имя поля -> тип
    output_schema: dict = field(default_factory=dict)

    def render(self, **values):
        """Подставляет значения. Лишнее или пропущенное поле это ошибка, а не тихий сбой."""
        missing = sorted(set(self.input_schema) - set(values))
        extra = sorted(set(values) - set(self.input_schema))
        if missing or extra:
            raise KeyError(f"{self.name} v{self.version}: не хватает {missing}, лишнее {extra}")
        return string.Template(self.text).substitute(values)


class Catalog:
    def __init__(self):
        self.versions = {}   # имя -> список версий
        self.pins = {}       # (приложение, имя prompt) -> номер версии

    def publish(self, name, text, **meta):
        number = len(self.versions.get(name, [])) + 1
        pv = PromptVersion(name=name, version=number, text=text, **meta)
        self.versions.setdefault(name, []).append(pv)
        return pv

    def get(self, name, version=None):
        items = self.versions[name]
        return items[-1] if version is None else items[version - 1]

    def pin(self, app, name, version):
        self.get(name, version)           # проверяем, что версия существует
        self.pins[(app, name)] = version

    def use(self, app, name):
        """Приложение получает ту версию, на которую оно закреплено."""
        return self.get(name, self.pins[(app, name)])

    def consumers(self, name):
        return sorted((app, v) for (app, n), v in self.pins.items() if n == name)

    def outdated(self, name):
        last = self.get(name).version
        return [(app, v) for app, v in self.consumers(name) if v < last]

    def search(self, **filters):
        """Поиск по метаданным: search(model_name='model-small')."""
        found = []
        for items in self.versions.values():
            for pv in items:
                if all(getattr(pv, k) == v for k, v in filters.items()):
                    found.append(pv)
        return found

    def diff(self, name, a, b):
        ta, tb = self.get(name, a).text.splitlines(), self.get(name, b).text.splitlines()
        return "\n".join(difflib.unified_diff(ta, tb, f"v{a}", f"v{b}", lineterm="", n=0))


def parse_prompt_file(text):
    """Мини-разбор .prompt-файла: блок метаданных между '---' и текст-шаблон. Вложенность по отступам."""
    _, head, body = text.split("---\n", 2)
    root = {}
    stack = [(-1, root)]  # (отступ, словарь, куда писать)
    for line in head.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        val = val.strip()
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if val == "":
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = int(val) if val.lstrip("-").isdigit() else val
    return root, body.strip()


# --- Демонстрация -----------------------------------------------------------------------------
cat = Catalog()
V1 = "Ты помощник аналитика. Таблицы: ${tables}\nВопрос: ${question}\nОтвет (один SQL-запрос):"
V2 = ("Ты помощник аналитика. Таблицы: ${tables}\nВопрос: ${question}\n"
      "Разрешены только запросы SELECT.\nОтвет (один SQL-запрос):")
common = dict(model_name="model-small", application="analytics-bot", creator="anna",
              input_schema={"tables": "string", "question": "string"}, output_schema={"sql": "string"})
cat.publish("sql-helper", V1, date_created="2025-01-15", **common)
cat.publish("cust-summary", "Кратко опиши клиента: ${profile}", model_name="model-large", application="crm-bot",
            creator="boris", date_created="2025-02-01", input_schema={"profile": "string"})

print("== 1. Две версии одного prompt и разница между ними")
cat.pin("analytics-bot", "sql-helper", 1)
cat.pin("report-bot", "sql-helper", 1)
cat.publish("sql-helper", V2, date_created="2025-03-10", **common)
print(cat.diff("sql-helper", 1, 2))

print("\n== 2. Что видят приложения")
print("Если prompt лежит в Git рядом с кодом, все берут актуальную версию:")
for app in ("analytics-bot", "report-bot"):
    print(f"  {app}: v{cat.get('sql-helper').version} (без выбора)")
print("В каталоге у каждого приложения своя закреплённая версия:")
for app in ("analytics-bot", "report-bot"):
    print(f"  {app}: v{cat.use(app, 'sql-helper').version}")
print("Устаревшие потребители:", cat.outdated("sql-helper"))

print("\nreport-bot проверил v2 на своём eval-наборе и обновился.")
cat.pin("report-bot", "sql-helper", 2)
for app, v in cat.outdated("sql-helper"):
    print(f"Уведомление владельцу {app}: вышла v{cat.get('sql-helper').version}, вы на v{v}")

print("\n== 3. Поиск по метаданным")
for pv in cat.search(model_name="model-small"):
    print(f"model-small: {pv.name} v{pv.version}, приложение {pv.application}, автор {pv.creator}")
print("потребители sql-helper:", cat.consumers("sql-helper"))

print("\n== 4. Подстановка и ошибки")
pv = cat.use("report-bot", "sql-helper")
print(pv.render(tables="sales.orders(id, amount)", question="Сколько заказов?"))
try:
    pv.render(tables="sales.orders")
except KeyError as e:
    print("ошибка:", e.args[0])

print("\n== 5. Запись каталога как JSON")
print(json.dumps(asdict(cat.get("cust-summary")), ensure_ascii=False, indent=2))

print("\n== 6. Разбор .prompt-файла")
PROMPT_FILE = """---
model: model-small
temperature: 0
input:
  schema:
    theme: string
output:
  format: json
  schema:
    name: string
    price: integer
---
Придумай блюдо, которое может быть в ресторане в стиле ${theme}. Верни JSON.
"""
meta, body = parse_prompt_file(PROMPT_FILE)
print(json.dumps(meta, ensure_ascii=False))
print(string.Template(body).substitute(theme="космос"))
