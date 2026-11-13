#!/usr/bin/env python3
"""Chapter 8 (Accessing Remote Data) diagrams. Usage: ch08_diagrams.py [name ...]  (no args = all)
Числа на второй схеме взяты из нашего запуска ch08_range_demo.py (см. figures-ch08.md)."""
from excb import N, E, Z, T, run_all

D = {}
GRAY = "#495057"

# ---------- main: DuckDB + httpfs -> remote sources ----------
D["ch08-remote-sources"] = dict(items=[
    N("q", "Ваш SQL\nSELECT ... FROM 'ссылка'", 0, 150, "pu", 320, 110),
    N("h", "расширение httpfs\nHTTP, HTTPS, S3 API", 480, 150, "p", 320, 110),
    N("s1", "Файл по URL\n(сервер, GitHub raw)", 1000, 0, "n", 330, 100),
    N("s2", "Объектное хранилище\ns3://...", 1000, 150, "n", 330, 100),
    N("s3", "Hugging Face\nhf://datasets/...", 1000, 300, "y", 330, 100),
    T("Файл не нужно скачивать вручную: DuckDB берёт из него столько, сколько нужно запросу.", 0, 470, 20, GRAY),
], edges=[E("q", "h"), E("h", "s1"), E("h", "s2"), E("h", "s3")])

# ---------- CSV vs Parquet over the network ----------
D["ch08-remote-bytes"] = dict(items=[
    Z("CSV по сети: строки подряд", 0, 0, 700, 400),
    Z("Parquet по сети: метаданные + нужные столбцы", 780, 0, 800, 400),
    N("c1", "SELECT count(*)\nчитает файл целиком", 40, 70, "r", 620, 80),
    N("c2", "Наш замер: 58,7 МБ файл,\nскачано 90,7 МБ (больше файла)", 40, 190, "r", 620, 100),
    T("Строки лежат подряд: нужные куски не выбрать.", 40, 320, 19, "#e03131"),
    N("p1", "DESCRIBE, count(*)\n0,03 МБ из 23,8", 810, 70, "g", 340, 100),
    N("p2", "avg(age)\n0,07 МБ", 1190, 70, "g", 340, 100),
    N("p3", "SELECT agency, age\n0,09 МБ", 810, 200, "g", 340, 100),
    N("p4", "SELECT *\n23,7 МБ (весь файл)", 1190, 200, "y", 340, 100),
    T("Нужны метаданные и range requests: берём только нужные куски.", 810, 330, 19, "#2f9e44"),
], edges=[])

# ---------- hf:// path ----------
D["ch08-hf-path"] = dict(items=[
    N("a", "hf://datasets/", 0, 80, "n", 270, 80),
    N("b", "пользователь\n(scikit-learn)", 310, 80, "p", 270, 80),
    N("c", "датасет\n(tips)", 620, 80, "g", 230, 80),
    N("d", "папка, если есть\n(data/)", 890, 80, "y", 270, 80),
    N("e", "файл\n(tips.csv)", 1200, 80, "q", 230, 80),
    T("Пользователь и датасет видны на странице датасета. Файлы и папки: вкладка Files.", 0, 230, 20, GRAY),
    T("Много файлов сразу: в конце маска, например data/*.parquet", 0, 280, 20, GRAY),
], edges=[E("a", "b"), E("b", "c"), E("c", "d"), E("d", "e")])

# ---------- private dataset: two auth providers ----------
D["ch08-auth"] = dict(items=[
    Z("CONFIG: токен в команде", 0, 0, 720, 330),
    Z("CREDENTIAL_CHAIN: токен из файла", 800, 0, 790, 330),
    N("c1", "CREATE SECRET ...\nTOKEN '...'", 40, 70, "r", 300, 100),
    N("c2", "токен виден\nв коде и в истории", 390, 70, "r", 290, 100),
    T("Проще, но небезопасно.", 40, 210, 20, "#e03131"),
    N("k1", "huggingface-cli login\nтокен в ~/.cache/\nhuggingface/token", 830, 70, "g", 340, 120),
    N("k2", "CREATE SECRET ...\nPROVIDER\nCREDENTIAL_CHAIN", 1220, 70, "g", 330, 120),
    T("Токена нет в коде. DuckDB ищет его сам.", 830, 220, 20, "#2f9e44"),
], edges=[E("c1", "c2"), E("k1", "k2")])

if __name__ == "__main__":
    run_all(D)
