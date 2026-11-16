#!/usr/bin/env python3
"""DDIA 2nd ed., chapter 3 (data models and query languages) diagrams. Usage: ch03_diagrams.py [name ...]  (no args = all)
Reused without sources (1st-edition images): ch03-model-choice.png, ch03-graph-models.png."""
from excb import N, E, Z, T, run_all

D = {}

# Redrawn for the 2nd edition (same file name as the 1st-edition image): short history of data models
D["ch03-history"] = dict(items=[
    T("Конкуренты реляционной модели", 0, -60, 24, "#495057"),
    N("h1", "1970-е:\nnetwork и\nhierarchical модели", 0, 0, "q", 250, 120),
    N("h2", "Середина 1980-х:\nреляционная модель\nи SQL побеждают", 330, 0, "p", 250, 120),
    N("h3", "Конец 1980-х и 1990-е:\nобъектные базы", 660, 0, "r", 250, 120),
    N("h4", "2000-е:\nXML-базы\n(ниша)", 990, 0, "r", 250, 120),
    N("h5", "2010-е:\nNoSQL и NewSQL", 1320, 0, "db", 250, 120),
    N("sql", "Сегодня: SQL вбирает идеи конкурентов — поддержку XML, JSON и графов.\nОт NoSQL осталась популярность документной модели (JSON).", 0, 260, "g", 1570, 110),
], edges=[E("h1", "h2"), E("h2", "h3"), E("h3", "h4"), E("h4", "h5"),
          E("h3", "sql", dashed=True), E("h4", "sql", dashed=True), E("h5", "sql", dashed=True)])

# Fig 3-6: the running graph example (Lucy and Alain)
D["ch03-graph-example"] = dict(items=[
    N("nam", "North America\ntype: continent", 0, 0, "db", 230, 80),
    N("eur", "Europe\ntype: continent", 850, 0, "db", 230, 80),
    N("usa", "United States\ntype: country", 0, 190, "p", 230, 80),
    N("uk", "United Kingdom\ntype: country", 600, 190, "p", 230, 80),
    N("fr", "France\ntype: country", 1100, 190, "p", 230, 80),
    N("ida", "Idaho\ntype: state", 0, 380, "p", 230, 80),
    N("eng", "England\ntype: country", 600, 380, "p", 230, 80),
    N("stl", "Saint-Lô\ntype: city", 1100, 380, "p", 230, 80),
    N("lon", "London\ntype: city", 600, 570, "p", 230, 80),
    N("lucy", "Lucy\n:Person", 250, 760, "y", 230, 80),
    N("alain", "Alain\n:Person", 950, 760, "y", 230, 80),
], edges=[E("ida", "usa", "WITHIN"), E("usa", "nam", "WITHIN"),
          E("lon", "eng", "WITHIN"), E("eng", "uk", "WITHIN"), E("uk", "eur", "WITHIN"),
          E("stl", "fr", "WITHIN"), E("fr", "eur", "WITHIN"),
          E("lucy", "ida", "BORN_IN"), E("lucy", "lon", "LIVES_IN"),
          E("alain", "stl", "BORN_IN"), E("alain", "lon", "LIVES_IN"),
          E("lucy", "alain", "MARRIED_TO")])

# Fig 3-8: event sourcing and CQRS in a conference system
D["ch03-event-sourcing"] = dict(items=[
    N("cmd", "Команды:\nзабронировать места,\nотменить бронь,\nсменить зал", 0, 125, "n", 250, 140),
    N("chk", "Команда\nдопустима?", 330, 115, "y", 240, 160, "diamond"),
    N("rej", "Отказ:\nсобытие не пишется", 330, 370, "r", 240, 90),
    N("log", "Event log (только дописываем)\n\nSeatsBooked\nBookingCancelled\nCapacityChanged", 730, 95, "q", 320, 200),
    N("v1", "View: статус\nкаждой брони", 1200, 0, "g", 280, 100),
    N("v2", "View: графики\nдля организатора", 1200, 145, "g", 280, 100),
    N("v3", "View: файлы\nдля печати бейджей", 1200, 290, "g", 280, 100),
    T("CQRS: пишем в одной форме (события), читаем из других (materialized views).\nЛюбой view можно удалить и пересчитать, если проиграть события по порядку.", 640, 420, 20, "#495057"),
], edges=[E("cmd", "chk"), E("chk", "log", "да"), E("chk", "rej", "нет"),
          E("log", "v1"), E("log", "v2"), E("log", "v3")])

if __name__ == "__main__":
    run_all(D)
