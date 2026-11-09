"""Скачивает открытые источники данных для учебной базы SQL.

Файлы кладём в .cache/raw. Уже скачанные файлы не качаем повторно.
Запуск: python3 fetch.py
"""
import json
import pathlib
import time
import urllib.parse
import urllib.request

RAW = pathlib.Path(__file__).parent / ".cache" / "raw"
UA = "dataengineer-ru-sql-tutorial/1.0 (https://dataengineer.ru)"

SOURCES = {
    # Crunchbase export, декабрь 2015. Лицензия CC BY-NC 4.0.
    "companies.csv": "https://raw.githubusercontent.com/notpeter/crunchbase-data/master/companies.csv",
    "acquisitions.csv": "https://raw.githubusercontent.com/notpeter/crunchbase-data/master/acquisitions.csv",
    "investments.csv": "https://raw.githubusercontent.com/notpeter/crunchbase-data/master/investments.csv",
    # Capital Bikeshare (Вашингтон), поездки за 2012 год.
    "bikeshare2012.zip": "https://s3.amazonaws.com/capitalbikeshare-data/2012-capitalbikeshare-tripdata.zip",
    # US Census: новое жильё по регионам, по месяцам. Public domain.
    "starts.xlsx": "https://www.census.gov/construction/nrc/xls/starts_cust.xlsx",
    # SF Open Data: инциденты полиции за январь 2014. Public domain (PDDL).
    "sfcrime.json": "https://data.sfgov.org/resource/tmnf-yvry.json?"
    + urllib.parse.urlencode(
        {"$where": "date between '2014-01-01T00:00:00' and '2014-01-31T23:59:59'", "$limit": 50000}
    ),
    # Дневные цены акций Apple 2000-2014.
    "aapl.json": "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?period1=946684800&period2=1420070400"
    "&interval=1d&events=split",
}


def get(url: str, dest: pathlib.Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    print("fetch", dest.name)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        dest.write_bytes(r.read())
    time.sleep(0.3)


def billboard() -> None:
    """Итоговые чарты Billboard за 1956-2013 из Википедии (вики-разметка)."""
    out = RAW / "billboard"
    out.mkdir(exist_ok=True)
    for year in range(1956, 2014):
        title = f"Billboard Year-End Hot 100 singles of {year}"
        url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "parse", "page": title, "prop": "wikitext", "format": "json", "redirects": 1}
        )
        get(url, out / f"{year}.json")


def earthquakes() -> None:
    """Число землетрясений в мире по годам и магнитуде, каталог USGS. Public domain."""
    dest = RAW / "earthquakes.json"
    if dest.exists():
        return
    bins = [(8, 10), (7, 8), (6, 7), (5, 6), (4, 5), (3, 4)]
    res = {}
    for year in range(2000, 2013):
        for lo, hi in bins:
            url = "https://earthquake.usgs.gov/fdsnws/event/1/count?" + urllib.parse.urlencode(
                {"starttime": f"{year}-01-01", "endtime": f"{year + 1}-01-01", "minmagnitude": lo, "maxmagnitude": hi - 0.01}
            )
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                res[f"{year}:{lo}"] = int(r.read().decode().strip())
            time.sleep(0.2)
    dest.write_text(json.dumps(res))


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        get(url, RAW / name)
    billboard()
    earthquakes()
    print("done")
