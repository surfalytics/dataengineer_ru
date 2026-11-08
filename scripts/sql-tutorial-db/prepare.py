"""Готовит CSV из скачанных источников (.cache/raw -> .cache/csv).

Запуск: python3 prepare.py
Форматы столбцов повторяют учебные таблицы из SQL Tutorial (ThoughtSpot / Mode):
часть дат специально хранится строками — на них учимся чистить данные.
"""
import csv
import datetime as dt
import io
import json
import pathlib
import re
import zipfile

import openpyxl

ROOT = pathlib.Path(__file__).parent / ".cache"
RAW = ROOT / "raw"
OUT = ROOT / "csv"


def write(name: str, header: list[str], rows: list[list]) -> None:
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


# ---------- Billboard ----------

LINK = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
SPLIT = re.compile(r"\s+(?:featuring|feat\.|ft\.|with|and|vs\.?|x)\s+|\s*&\s*|\s*,\s*|\s*/\s*", re.I)


def strip_markup(s: str) -> str:
    s = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>", " / ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\{\{sort\|[^|}]*\|([^}]*)\}\}", r"\1", s, flags=re.I)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = LINK.sub(lambda m: m.group(2) or m.group(1), s)
    s = s.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", s).strip()


def artists(cell: str) -> list[str]:
    """Каждая вики-ссылка — один исполнитель. Текст без ссылок делим по разделителям."""
    cell = re.sub(r"<ref[^>]*/>|<ref.*?</ref>", "", cell, flags=re.S)
    cell = re.sub(r"\{\{[^{}]*\}\}", "", cell)
    links = []

    def keep(m):
        links.append((m.group(2) or m.group(1)).strip())
        return f"\x00{len(links) - 1}\x00"

    tokenized = LINK.sub(keep, cell)
    out = []
    for part in SPLIT.split(tokenized):
        for piece in re.split(r"(\x00\d+\x00)", part):
            piece = piece.strip(" ()\"'")
            if not piece:
                continue
            m = re.fullmatch(r"\x00(\d+)\x00", piece)
            name = links[int(m.group(1))] if m else strip_markup(piece)
            if name and name.lower() not in {"featuring", "and", "with"}:
                out.append(name)
    return out


def cell_attrs(c: str) -> tuple[int, str]:
    """Возвращает (rowspan, текст ячейки)."""
    m = re.match(r'\s*((?:[a-z-]+="[^"]*"\s*)+)\|(?!\|)(.*)$', c, flags=re.S)
    if m and "[[" not in m.group(1):
        span = re.search(r'rowspan="?(\d+)', m.group(1))
        return (int(span.group(1)) if span else 1), m.group(2)
    return 1, c


def billboard() -> None:
    rows = []
    for f in sorted((RAW / "billboard").glob("*.json")):
        year = int(f.stem)
        text = json.loads(f.read_text())["parse"]["wikitext"]["*"]
        table = text[text.find("{|") : text.find("|}", text.find("{|"))]
        carry: dict[int, tuple[int, str]] = {}  # колонка -> (сколько строк ещё, текст)
        for raw in table.split("\n|-")[1:]:
            lines = [l for l in raw.strip("\n").split("\n") if l.startswith(("|", "!")) and not l.startswith("|+")]
            cells = []
            for l in lines:
                # "!!" делит ячейки только в строках-заголовках ("Woo Hah!!" — это название песни).
                cells += re.split(r"\|\||!!" if l.startswith("!") else r"\|\|", l[1:])
            if not cells or "scope=\"col\"" in raw:
                continue
            parsed = [cell_attrs(c) for c in cells]
            full, src = [], 0
            for col in range(3):
                if col in carry and carry[col][0] > 0:
                    left, val = carry[col]
                    full.append(val)
                    carry[col] = (left - 1, val)
                elif src < len(parsed):
                    span, val = parsed[src]
                    src += 1
                    full.append(val)
                    if span > 1:
                        carry[col] = (span - 1, val)
                else:
                    full.append("")
            rank_txt = strip_markup(full[0])
            if not re.match(r"^\d+", rank_txt):
                continue
            rank = int(re.match(r"\d+", rank_txt).group())
            song = strip_markup(full[1]).strip('"').replace('" / "', " / ")
            group = strip_markup(full[2])
            for a in artists(full[2]) or [group]:
                rows.append([year, rank, group, a, song])
    rows = [r + [i + 1] for i, r in enumerate(rows)]
    write("billboard_top_100_year_end.csv", ["year", "year_rank", "group_name", "artist", "song_name", "id"], rows)


# ---------- US housing units ----------

def housing() -> None:
    wb = openpyxl.load_workbook(RAW / "starts.xlsx", read_only=True)
    ws = wb["Not Seasonally Adjusted"]
    rows = []
    for r in ws.iter_rows(values_only=True):
        d = r[0]
        if isinstance(d, dt.datetime) and 1968 <= d.year <= 2014:
            # Порядок регионов: south, west, midwest, northeast (как в учебнике).
            rows.append([d.year, d.month, d.strftime("%B"), r[9], r[11], r[7], r[5]])
    write("us_housing_units.csv", ["year", "month", "month_name", "south", "west", "midwest", "northeast"], rows)


# ---------- Apple stock ----------

def aapl() -> None:
    res = json.loads((RAW / "aapl.json").read_text())["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    # Yahoo отдаёт цены с поправкой на сплиты. Возвращаем реальные цены торгов.
    splits = [(dt.date(2000, 6, 21), 2), (dt.date(2005, 2, 28), 2), (dt.date(2014, 6, 9), 7), (dt.date(2020, 8, 31), 4)]
    rows = []
    for i, ts in enumerate(res["timestamp"]):
        day = (dt.datetime.utcfromtimestamp(ts) - dt.timedelta(hours=5)).date()
        if q["close"][i] is None:
            continue
        k = 1
        for sd, ratio in splits:
            if day < sd:
                k *= ratio
        p = [round(q[c][i] * k, 2) for c in ("open", "high", "low", "close")]
        rows.append([day.isoformat(), day.year, day.month, *p, int(q["volume"][i] / k)])
    rows = [r + [i + 1] for i, r in enumerate(rows)]
    write("aapl_historical_stock_price.csv", ["date", "year", "month", "open", "high", "low", "close", "volume", "id"], rows)


# ---------- SF crime ----------

def sfcrime() -> None:
    data = json.loads((RAW / "sfcrime.json").read_text())
    data.sort(key=lambda d: (d["date"], d["time"], d["incidntnum"]))
    rows = []
    for i, d in enumerate(data):
        day = dt.date.fromisoformat(d["date"][:10])
        lon, lat = float(d["x"]), float(d["y"])
        rows.append([
            int(d["incidntnum"]), d["category"], d["descript"], d["dayofweek"],
            # Дата строкой, как в исходной выгрузке: MM/DD/YYYY 08:00:00 AM +0000.
            day.strftime("%m/%d/%Y") + " 08:00:00 AM +0000",
            d["time"], d.get("pddistrict") or "", d["resolution"], d["address"],
            lon, lat, f"({lat}, {lon})", i + 1,
        ])
    write("sf_crime_incidents_2014_01.csv",
          ["incidnt_num", "category", "descript", "day_of_week", "date", "time", "pd_district",
           "resolution", "address", "lon", "lat", "location", "id"], rows)


# ---------- DC bikeshare ----------

def bikeshare() -> None:
    with zipfile.ZipFile(RAW / "bikeshare2012.zip") as z:
        text = z.read("2012Q1-capitalbikeshare-tripdata.csv").decode("utf-8")
    rows = []
    for i, r in enumerate(csv.DictReader(io.StringIO(text))):
        sec = int(r["Duration"])
        rows.append([
            f"{sec // 3600}h {sec % 3600 // 60}min. {sec % 60}sec.", sec,
            r["Start date"], r["Start station"], r["Start station number"],
            r["End date"], r["End station"], r["End station number"],
            r["Bike number"], "Registered" if r["Member type"] == "Member" else r["Member type"], i + 1,
        ])
    write("dc_bikeshare_q1_2012.csv",
          ["duration", "duration_seconds", "start_time", "start_station", "start_terminal", "end_time",
           "end_station", "end_terminal", "bike_number", "rider_type", "id"], rows)


# ---------- Earthquakes ----------

def earthquakes() -> None:
    d = json.loads((RAW / "earthquakes.json").read_text())
    rows = []
    for lo in (8, 7, 6, 5, 4, 3):
        label = "8.0 to 9.9" if lo == 8 else f"{lo}.0 to {lo}.9"
        rows.append([label] + [d[f"{y}:{lo}"] for y in range(2000, 2013)])
    write("worldwide_earthquakes.csv", ["magnitude"] + [f"year_{y}" for y in range(2000, 2013)], rows)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    billboard()
    housing()
    aapl()
    sfcrime()
    bikeshare()
    earthquakes()
