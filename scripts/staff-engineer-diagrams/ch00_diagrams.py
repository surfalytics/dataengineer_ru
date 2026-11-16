#!/usr/bin/env python3
"""Overview page diagram (book map). Usage: ch00_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, T, Z, run_all

D = {}

D["ch00-book-map"] = dict(items=[
    Z("Часть 1. Staff engineering: главы 1–5", -30, -150, 1130, 390),
    N("c1", "1. Что такое Staff-инженер\nчетыре архетипа,\nработа, должность", 0, 0, "p", 280, 130),
    N("c23", "2–3. Работа на уровне Staff\nважное, стратегия, качество,\nвлияние и люди", 380, 0, "g", 300, 130),
    N("c4", "4. Уровень Staff\nв своей компании", 790, -90, "y", 280, 110),
    N("c5", "5. Смена компании", 790, 90, "y", 280, 110),
    Z("Часть 2. Истории 14 Staff-инженеров: главы 6–8", -30, 290, 1130, 200),
    N("s6", "6. Stripe, Mailchimp,\nFastly, Slack, Etsy", 0, 350, "pu", 320, 110),
    N("s7", "7. Dropbox, Uber, Stripe,\nSlack, Squarespace", 380, 350, "pu", 320, 110),
    N("s8", "8. Split, Auth0,\nStripe, Samsara", 760, 350, "pu", 310, 110),
    T("Приложение для руководителей в конспект не вошло.", 0, 520),
], edges=[E("c1", "c23"), E("c23", "c4"), E("c23", "c5")])

if __name__ == "__main__":
    run_all(D)
