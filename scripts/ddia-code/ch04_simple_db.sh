#!/bin/bash
# DDIA2, глава 4: самая простая база «ключ — значение» на двух функциях bash.
# Запуск: bash scripts/ddia-code/ch04_simple_db.sh  (работает во временной папке)
set -e
cd "$(mktemp -d)"

db_set () {
  echo "$1,$2" >> database
}
db_get () {
  grep "^$1," database | sed -e "s/^$1,//" | tail -n 1
}

db_set 1 '{"city":"Казань","sights":["Кремль"]}'
db_set 2 '{"city":"Сочи","sights":["Роза Хутор"]}'
db_get 2
db_set 2 '{"city":"Сочи","sights":["Дендрарий"]}'
db_get 2
cat database
