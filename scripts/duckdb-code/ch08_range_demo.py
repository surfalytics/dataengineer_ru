"""Глава 8: сколько байт уходит по HTTP при запросе к CSV и к Parquet.
Свой маленький HTTP-сервер на localhost считает отданные байты. Он понимает Range-запросы.
Нужна сеть только для INSTALL httpfs (расширение скачивается один раз)."""
import os
import re
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import duckdb

tmp = tempfile.mkdtemp()
con = duckdb.connect()
con.sql("""
    CREATE TABLE sales AS
    SELECT i AS id,
           ['A','B','C','D'][1 + i % 4] AS agency,
           20 + i % 50 AS age,
           round(10 + (hash(i) % 10000) / 100, 2) AS net_sales,
           'destination ' || (i % 200) AS destination,
           'note ' || hash(i) AS note
    FROM range(1000000) t(i)
""")
con.sql(f"COPY sales TO '{tmp}/sales.csv' (HEADER)")
con.sql(f"COPY sales TO '{tmp}/sales.parquet' (FORMAT PARQUET)")

sent = {"bytes": 0}


class Handler(BaseHTTPRequestHandler):
    def _serve(self, body_needed):
        path = os.path.join(tmp, self.path.lstrip("/"))
        size = os.path.getsize(path)
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m.group(1) == "":
                start = max(0, size - int(m.group(2)))
            else:
                start = int(m.group(1))
                if m.group(2):
                    end = min(int(m.group(2)), size - 1)
        length = end - start + 1
        self.send_response(206 if rng else 200)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        if rng:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        if body_needed:
            with open(path, "rb") as f:
                f.seek(start)
                self.wfile.write(f.read(length))
            sent["bytes"] += length

    def do_HEAD(self):
        self._serve(False)

    def do_GET(self):
        self._serve(True)

    def log_message(self, *a):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_address[1]}"

duckdb.connect().sql("INSTALL httpfs;")

csv_mb = os.path.getsize(f"{tmp}/sales.csv") / 1e6
pq_mb = os.path.getsize(f"{tmp}/sales.parquet") / 1e6
print(f"Размер файлов: CSV {csv_mb:.1f} МБ, Parquet {pq_mb:.1f} МБ (1 000 000 строк, 6 столбцов)")
print()

tests = [
    ("CSV     SELECT count(*)", f"SELECT count(*) FROM '{base}/sales.csv'"),
    ("Parquet SELECT *", f"SELECT * FROM '{base}/sales.parquet'"),
    ("Parquet DESCRIBE", f"DESCRIBE SELECT * FROM '{base}/sales.parquet'"),
    ("Parquet SELECT count(*)", f"SELECT count(*) FROM '{base}/sales.parquet'"),
    ("Parquet SELECT avg(age)", f"SELECT avg(age) FROM '{base}/sales.parquet'"),
    ("Parquet SELECT agency, age", f"SELECT agency, age FROM '{base}/sales.parquet'"),
]
print(f"{'Запрос':32}{'скачано, МБ':>14}{'доля файла':>12}")
for name, q in tests:
    # новое соединение для каждого запроса: кеш файлов не прячет скачивание
    remote = duckdb.connect()
    remote.sql("LOAD httpfs")
    sent["bytes"] = 0
    remote.sql(q).fetchall()
    total = csv_mb if name.startswith("CSV") else pq_mb
    mb = sent["bytes"] / 1e6
    print(f"{name:32}{mb:>14.2f}{mb / total:>11.0%}")
server.shutdown()
