#!/usr/bin/env python3
"""Глава 16 (Airflow): новые диаграммы. Старые (ch16-security-layers, ch16-secrets-lookup) делает specs/ch16.py.
Usage: python3 scripts/airflow-diagrams/ch16_diagrams.py [name ...]"""
from excb import N, E, Z, T, run_all

D = {}

# ---------- Fig 16.14: рукопожатие HTTPS ----------
D["ch16-https-handshake"] = dict(items=[
    N("s1", "1. Браузер просит страницу по https://", 0, 150, "n", 920, 60),
    N("s2", "2. Web server отдаёт certificate с public key", 0, 250, "y", 920, 60),
    N("s3", "3. Браузер проверяет certificate по списку доверенных центров", 0, 350, "y", 920, 60),
    N("s4", "4. Браузер шлёт случайный session key, зашифрованный public key", 0, 450, "pu", 920, 60),
    N("s5", "5. Web server расшифровывает его своим private key", 0, 550, "pu", 920, 60),
    N("s6", "6. Дальше весь трафик шифруется session key (symmetric)", 0, 650, "g", 920, 60),
], edges=[E("s1", "s2"), E("s2", "s3"), E("s3", "s4"), E("s4", "s5"), E("s5", "s6")])

# ---------- Fig 16.9: дерево каталога DIT ----------
D["ch16-ldap-dit"] = dict(items=[
    N("com", "dc=com", 360, 0, "n", 200, 60),
    N("air", "dc=apacheairflow", 340, 120, "n", 240, 60),
    N("people", "ou=people", 120, 240, "p", 200, 60),
    N("servers", "ou=servers", 600, 240, "p", 200, 60),
    N("bob", "cn=bob\nsn=Smith, mail=...", 0, 380, "g", 240, 80),
    N("alice", "cn=alice", 280, 380, "g", 160, 80),
    T("DN Боба: cn=bob,ou=people,dc=apacheairflow,dc=com", 60, 520, 20, "#1971c2"),
], edges=[E("com", "air"), E("air", "people"), E("air", "servers"), E("people", "bob"), E("people", "alice")])

if __name__ == "__main__":
    run_all(D)
