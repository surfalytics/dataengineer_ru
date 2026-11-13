"""Глава 3. Консоль duckdb: EXPORT DATABASE и IMPORT DATABASE. Настоящий запуск CLI в пустой папке."""
import os
import subprocess
import tempfile


def cli(cwd, *args, sql=None):
    r = subprocess.run(["duckdb", *args], input=sql, capture_output=True, text=True, cwd=cwd, timeout=60)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
    return r.stdout.rstrip("\n")


with tempfile.TemporaryDirectory() as d:
    cli(d, sql="""
        CREATE TABLE products (product_id INTEGER PRIMARY KEY, title VARCHAR, price DECIMAL(10, 2));
        INSERT INTO products VALUES (1, 'Мышь', 20.00), (2, 'Лампа', 40.00);
        EXPORT DATABASE 'shop_db';
    """)
    print("Файлы в папке shop_db:", sorted(os.listdir(os.path.join(d, "shop_db"))))
    print()
    print("schema.sql:")
    print(open(os.path.join(d, "shop_db", "schema.sql"), encoding="utf-8").read().strip())
    print()
    print("load.sql:")
    print(open(os.path.join(d, "shop_db", "load.sql"), encoding="utf-8").read().strip())
    print()
    print("IMPORT DATABASE в новой базе:")
    print(cli(d, "new.duckdb", "-csv", sql="IMPORT DATABASE 'shop_db'; SELECT * FROM products ORDER BY product_id;"))
