"""Рисует ERD-схемы (модель данных) для страниц уровней курса и вставляет их в страницы.

Столбцы и типы берём из файла базы, поэтому схема не расходится с базой.
Запуск: python3 erd.py <файл .duckdb>
Схема вставляется между маркерами <!-- erd:start --> и <!-- erd:end -->.
Если маркеров нет, блок ставится перед первым заголовком «## » страницы.
Стили (.erd ...) лежат в src/styles/custom.css.
"""
import html
import pathlib
import re
import subprocess
import sys

SQL_DIR = pathlib.Path(__file__).resolve().parents[2] / "src/content/docs/practice/sql"

ROW_H, HEAD_H, CH, PAD = 18, 28, 7.3, 12   # высота строки, шапки, ширина символа, отступ
GAP_X, GAP_Y, MARGIN = 64, 40, 14

# Какие столбцы показывать у широких таблиц. Остальные заменяет строка «… ещё N ст.».
# У таблиц, которых здесь нет, показаны все столбцы.
SHOW = {
    "crunchbase_companies": ["permalink", "name", "category_code", "funding_total_usd", "status",
                             "country_code", "state_code", "founded_at", "founded_year"],
    "crunchbase_acquisitions": ["company_permalink", "company_name", "acquirer_name", "acquired_at",
                                "acquired_year", "price_amount", "price_currency_code"],
    "crunchbase_investments": ["company_permalink", "company_name", "investor_permalink", "investor_name",
                               "investor_country_code", "funding_round_type", "funded_at", "funded_year",
                               "raised_amount_usd"],
    "sf_crime_incidents_2014_01": ["incidnt_num", "category", "descript", "day_of_week", "date", "time",
                                   "resolution", "lon", "lat"],
    "dc_bikeshare_q1_2012": ["duration_seconds", "start_time", "start_station", "start_terminal", "end_time",
                             "end_station", "end_terminal", "rider_type"],
    "worldwide_earthquakes": ["magnitude", "year_2000", "year_2001", "year_2012"],
    # представления
    "crunchbase_companies_clean_date": ["permalink", "founded_at", "founded_at_clean"],
    "crunchbase_acquisitions_clean_date": ["company_permalink", "acquired_at", "acquired_at_cleaned"],
    "sf_crime_incidents_cleandate": ["incidnt_num", "date", "time", "cleaned_date"],
    "crunchbase_investments_part1": [],
    "crunchbase_investments_part2": [],
}
# Представления: основная таблица и пояснение (если своих столбцов нет).
VIEWS = {
    "crunchbase_investments_part1": ("crunchbase_investments",
                                     ["Компании A–L", "Те же столбцы, что у", "crunchbase_investments"]),
    "crunchbase_investments_part2": ("crunchbase_investments",
                                     ["Компании M–Z", "Те же столбцы, что у", "crunchbase_investments"]),
    "crunchbase_companies_clean_date": ("crunchbase_companies", None),
    "crunchbase_acquisitions_clean_date": ("crunchbase_acquisitions", None),
    "sf_crime_incidents_cleandate": ("sf_crime_incidents_2014_01", None),
}
BENN = {"dimension_rollup_periods", "college_football_teams", "college_football_players", "sample_event_table"}

# Связи: (таблица A, столбец A, таблица B, столбец B, кратность A, кратность B)
R = {
    "cb": [("crunchbase_companies", "permalink", "crunchbase_acquisitions", "company_permalink", "1", "N"),
           ("crunchbase_companies", "permalink", "crunchbase_investments", "company_permalink", "1", "N")],
    "fb": [("college_football_teams", "school_name", "college_football_players", "school_name", "1", "N")],
    "ym": [("yammer_users", "user_id", "yammer_events", "user_id", "1", "N"),
           ("yammer_users", "user_id", "yammer_emails", "user_id", "1", "N"),
           ("yammer_users", "user_id", "yammer_experiments", "user_id", "1", "N")],
    "cbv": [("crunchbase_companies_clean_date", "permalink", "crunchbase_acquisitions_clean_date",
             "company_permalink", "1", "N")],
}

# Страницы: колонки таблиц (сверху вниз) и связи.
PAGES = {
    "basic": dict(
        cols=[["us_housing_units", "crunchbase_companies"], ["billboard_top_100_year_end"]], rel=[],
        label="Модель данных уровня «Основы»: три таблицы без связей"),
    "intermediate": dict(
        cols=[["crunchbase_acquisitions", "college_football_teams", "aapl_historical_stock_price"],
              ["crunchbase_companies", "crunchbase_investments", "crunchbase_investments_part1",
               "crunchbase_investments_part2", "college_football_players"]],
        rel=R["cb"] + R["fb"], label="Модель данных среднего уровня"),
    "analytics": dict(
        cols=[["yammer_events", "yammer_emails", "dimension_rollup_periods"],
              ["yammer_users", "yammer_experiments"]],
        rel=R["ym"], label="Модель данных кейсов: данные Yammer"),
    "advanced": dict(
        cols=[["crunchbase_acquisitions", "crunchbase_acquisitions_clean_date", "crunchbase_investments",
               "crunchbase_investments_part1", "crunchbase_investments_part2", "worldwide_earthquakes"],
              ["crunchbase_companies", "crunchbase_companies_clean_date", "sf_crime_incidents_2014_01",
               "sf_crime_incidents_cleandate", "dc_bikeshare_q1_2012", "sample_event_table",
               "college_football_teams", "college_football_players"]],
        rel=R["cb"][:1] + R["cbv"] + R["fb"], label="Модель данных продвинутого уровня"),
}

TAIL = (" Показаны главные столбцы широких таблиц. Полный список столбцов: "
        "[Учебные данные](/practice/sql/datasets/).")
LEGEND = {
    "basic": "Таблицы этого уровня не связаны друг с другом." + TAIL,
    "intermediate": ("**Как читать схему.** Линия — связь для `JOIN`. Подписи `1` и `N` показывают, сколько строк "
                     "с каждой стороны: у одной компании может быть много покупок и инвестиций. "
                     "Выделенный столбец — ключ соединения. Пунктир — представление (view): часть данных другой "
                     "таблицы. Таблицы без линий не связаны с остальными." + TAIL),
    "analytics": ("**Как читать схему.** Линия — связь для `JOIN` по `user_id`: один пользователь, много событий, "
                  "писем и участий в тестах. Выделенный столбец — ключ соединения. `dimension_rollup_periods` — "
                  "справочник периодов, он соединяется по времени, а не по ключу."),
    "advanced": ("**Как читать схему.** Линия — связь для `JOIN`, подписи `1` и `N` — число строк с каждой стороны. "
                 "Выделенный столбец — ключ соединения. Пунктир — представление (view): оно показывает часть "
                 "данных основной таблицы. Таблицы без линий не связаны с остальными." + TAIL),
}


def columns(db):
    q = ("select table_name, column_name, lower(data_type) from information_schema.columns "
         "where table_schema in ('tutorial','benn') order by table_name, ordinal_position")
    out = subprocess.run(["duckdb", "-readonly", "-csv", "-noheader", db, "-c", q],
                         capture_output=True, text=True, check=True).stdout
    cols = {}
    for line in out.strip().split("\n"):
        t, c, ty = line.split(",")
        cols.setdefault(t, []).append((c, ty))
    return cols


def short(ty):
    return {"varchar": "text", "integer": "int"}.get(ty, ty)


def build_svg(page, cols):
    spec = PAGES[page]
    keys = {}
    for a, ac, b, bc, *_ in spec["rel"]:
        keys.setdefault(a, set()).add(ac)
        keys.setdefault(b, set()).add(bc)

    # Содержимое и размер каждой таблицы.
    info = {}
    for col in spec["cols"]:
        for name in col:
            allc = [(c, short(ty)) for c, ty in cols[name]]
            show = SHOW.get(name)
            shown = allc if show is None else [x for x in allc if x[0] in show]
            lines = [("col", c, ty) for c, ty in shown]
            if name in VIEWS and VIEWS[name][1]:
                lines += [("note", n, "") for n in VIEWS[name][1]]
            elif len(shown) < len(allc):
                lines.append(("note", f"… ещё {len(allc) - len(shown)} ст.", ""))
            title = f"{'benn' if name in BENN else 'tutorial'}.{name}"
            w = max([len(title) * CH + 2 * PAD] +
                    [PAD * 2 + CH * (len(c) + (len(ty) + 3 if kind == "col" else 0)) for kind, c, ty in lines])
            info[name] = dict(lines=lines, title=title, w=max(w, 180), h=HEAD_H + ROW_H * len(lines) + 8)

    colw = [max(info[n]["w"] for n in col) for col in spec["cols"]]
    xs = [MARGIN + sum(colw[:i]) + GAP_X * i for i in range(len(colw))]
    pos, heights = {}, []
    for ci, col in enumerate(spec["cols"]):
        y = MARGIN
        for ri, name in enumerate(col):
            pos[name] = dict(x=xs[ci], y=y, w=colw[ci], h=info[name]["h"], c=ci, r=ri)
            y += info[name]["h"] + GAP_Y
        heights.append(y - GAP_Y + MARGIN)
    width, height = xs[-1] + colw[-1] + MARGIN + 18, max(heights)

    def col_y(name, col):
        p = pos[name]
        for i, (kind, c, _) in enumerate(info[name]["lines"]):
            if kind == "col" and c == col:
                return p["y"] + HEAD_H + ROW_H * i + ROW_H / 2
        return p["y"] + HEAD_H / 2

    out = [f'<svg class="erd-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
           f'width="{width:.0f}" height="{height:.0f}" role="img" aria-label="{html.escape(spec["label"])}">']

    def vlink(cls, top, bot):
        xc = top["x"] + top["w"] / 2
        out.append(f'<path class="{cls}" d="M{xc:.0f} {top["y"] + top["h"]:.0f} V{bot["y"]:.0f}"/>')
        return xc

    # Пунктир: представление -> основная таблица.
    for name, p in pos.items():
        base = VIEWS.get(name, (None,))[0]
        if not base or base not in pos:
            continue
        q = pos[base]
        if q["c"] == p["c"] and abs(q["r"] - p["r"]) == 1:
            vlink("erd-view-link", *((q, p) if q["r"] < p["r"] else (p, q)))
        elif q["c"] == p["c"]:   # не соседи: петля справа
            xr = p["x"] + p["w"] + 14
            ya, yb = p["y"] + HEAD_H / 2, q["y"] + HEAD_H / 2
            out.append(f'<path class="erd-view-link" d="M{p["x"] + p["w"]:.0f} {ya:.0f} H{xr:.0f} '
                       f'V{yb:.0f} H{q["x"] + q["w"]:.0f}"/>')

    # Связи.
    slots = {}
    for a, ac, b, bc, ca, cb in spec["rel"]:
        pa, pb = pos[a], pos[b]
        if pa["c"] == pb["c"]:   # в одной колонке (в схемах стоят рядом)
            top, bot = (pa, pb) if pa["r"] < pb["r"] else (pb, pa)
            xc = vlink("erd-link", top, bot)
            ct, cbt = (ca, cb) if top is pa else (cb, ca)
            out.append(f'<text class="erd-card" x="{xc + 12:.0f}" y="{top["y"] + top["h"] + 13:.0f}" '
                       f'text-anchor="middle">{ct}</text>')
            out.append(f'<text class="erd-card" x="{xc + 12:.0f}" y="{bot["y"] - 5:.0f}" '
                       f'text-anchor="middle">{cbt}</text>')
            continue
        ya, yb = col_y(a, ac), col_y(b, bc)
        if pa["x"] < pb["x"]:
            xa, xb, sa, sb = pa["x"] + pa["w"], pb["x"], 1, -1
        else:
            xa, xb, sa, sb = pa["x"], pb["x"] + pb["w"], -1, 1
        used = slots.setdefault((min(pa["c"], pb["c"]), max(pa["c"], pb["c"])), [])
        used.append(1)
        xm = (xa + xb) / 2 - (len(used) - 1) * 9 * sa   # сдвиг, чтобы вертикали не слипались
        out.append(f'<path class="erd-link" d="M{xa:.0f} {ya:.0f} H{xm:.0f} V{yb:.0f} H{xb:.0f}"/>')
        out.append(f'<text class="erd-card" x="{xa + 10 * sa:.0f}" y="{ya - 5:.0f}" text-anchor="middle">{ca}</text>')
        out.append(f'<text class="erd-card" x="{xb + 10 * sb:.0f}" y="{yb - 5:.0f}" text-anchor="middle">{cb}</text>')

    # Таблицы.
    for name, p in pos.items():
        i = info[name]
        cls = "erd-box erd-view" if name in VIEWS else "erd-box"
        x, y, w = p["x"], p["y"], p["w"]
        out.append(f'<g class="erd-table"><rect class="{cls}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" '
                   f'height="{p["h"]:.0f}" rx="6"/>')
        out.append(f'<path class="erd-head" d="M{x:.0f} {y + HEAD_H:.0f} V{y + 6:.0f} Q{x:.0f} {y:.0f} {x + 6:.0f} {y:.0f} '
                   f'H{x + w - 6:.0f} Q{x + w:.0f} {y:.0f} {x + w:.0f} {y + 6:.0f} V{y + HEAD_H:.0f} Z"/>')
        out.append(f'<text class="erd-title" x="{x + PAD:.0f}" y="{y + 18:.0f}">{html.escape(i["title"])}</text>')
        for li, (kind, c, ty) in enumerate(i["lines"]):
            ly = y + HEAD_H + ROW_H * li
            if kind == "col":
                is_key = c in keys.get(name, ())
                if is_key:
                    out.append(f'<rect class="erd-keyrow" x="{x + 1:.0f}" y="{ly:.0f}" width="{w - 2:.0f}" height="{ROW_H}"/>')
                out.append(f'<text class="erd-col{" erd-key" if is_key else ""}" x="{x + PAD:.0f}" '
                           f'y="{ly + 13:.0f}">{html.escape(c)}</text>')
                out.append(f'<text class="erd-type" x="{x + w - PAD:.0f}" y="{ly + 13:.0f}" '
                           f'text-anchor="end">{html.escape(ty)}</text>')
            else:
                out.append(f'<text class="erd-note" x="{x + PAD:.0f}" y="{ly + 13:.0f}">{html.escape(c)}</text>')
        out.append("</g>")
    out.append("</svg>")
    return "\n".join(out)


def block(page, svg):
    return ("<!-- erd:start -->\n"
            "## Модель данных\n\n"
            f'<div class="erd not-content" data-pagefind-ignore>\n{svg}\n</div>\n\n'
            f"{LEGEND[page]}\n"
            "<!-- erd:end -->\n")


def main():
    db = sys.argv[1]
    cols = columns(db)
    for page in PAGES:
        path = SQL_DIR / f"{page}.md"
        text = path.read_text()
        new = block(page, build_svg(page, cols))
        if "<!-- erd:start -->" in text:
            text = re.sub(r"<!-- erd:start -->.*?<!-- erd:end -->\n", lambda m: new, text, flags=re.S)
        else:
            head, sep, rest = text.partition("\n## ")
            text = head + "\n" + new + "\n## " + rest
        path.write_text(text)
        print(f"{page}: ok")


if __name__ == "__main__":
    main()
