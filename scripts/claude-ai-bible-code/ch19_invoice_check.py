"""Глава 19: проверка полей, которые vision извлёк из счетов.
Ответы модели заданы JSON-строками, поэтому ключ API не нужен.
Сумма строк сверяется с итогом, сумма — с заказом (PO). Всё спорное идёт человеку."""
import json
from decimal import Decimal

APPROVED_PO = {"PO-501": Decimal("1250.00"), "PO-502": Decimal("480.00"), "PO-503": Decimal("99.90")}

EXTRACTED = [  # так мог бы ответить Claude на скан счёта
    '{"vendor": "Северный склад", "po": "PO-501", "total": "1250.00", "lines": ["1000.00", "250.00"]}',
    '{"vendor": "Альфа-Принт", "po": "PO-502", "total": "480.00", "lines": ["300.00", "130.00"]}',
    '{"vendor": "ТехноСнаб", "po": "PO-503", "total": "199.90", "lines": ["199.90"]}',
    '{"vendor": null, "po": "PO-504", "total": "75.00", "lines": ["75.00"]}',
]


def check_purchase_order(po, total):
    """Наш «инструмент»: есть ли одобренный заказ и совпадает ли сумма."""
    if po not in APPROVED_PO:
        return f"заказа {po} нет"
    if APPROVED_PO[po] != total:
        return f"по заказу {APPROVED_PO[po]}, в счёте {total}"
    return None


for i, raw in enumerate(EXTRACTED, 1):
    inv = json.loads(raw)
    total = Decimal(inv["total"])
    lines_sum = sum(Decimal(x) for x in inv["lines"])
    problems = [f"поле {k} пустое" for k in ("vendor", "po", "total") if inv[k] is None]
    if lines_sum != total:  # дешёвая проверка арифметики ловит опечатку чтения
        problems.append(f"строки дают {lines_sum}, итог {total}")
    po_issue = check_purchase_order(inv["po"], total)
    if po_issue:
        problems.append(po_issue)
    verdict = "провести" if not problems else "на проверку: " + "; ".join(problems)
    print(f"счёт {i}: {verdict}")
