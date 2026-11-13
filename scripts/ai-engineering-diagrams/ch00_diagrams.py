#!/usr/bin/env python3
"""Карта книги (обзор). Usage: ch00_diagrams.py [name ...]  (no args = all)"""
from excb import N, E, Z, T, run_all

D = {}

D["ch00-book-map"] = dict(items=[
    Z("Основы", -20, -60, 320, 360), Z("Оценка", 360, -60, 320, 360),
    Z("Адаптация модели", 740, -60, 320, 700), Z("Продакшен", 1120, -60, 320, 360),
    N("c1", "1. Введение в\nAI engineering", 0, 20, "p", 280), N("c2", "2. Foundation\nmodels", 0, 160, "p", 280),
    N("c3", "3. Методы\nоценки", 380, 20, "y", 280), N("c4", "4. Оценка\nAI-систем", 380, 160, "y", 280),
    N("c5", "5. Prompt\nengineering", 760, 20, "g", 280), N("c6", "6. RAG\nи агенты", 760, 160, "g", 280),
    N("c7", "7. Finetuning", 760, 300, "g", 280), N("c8", "8. Dataset\nengineering", 760, 440, "g", 280),
    N("c9", "9. Оптимизация\ninference", 1140, 20, "pu", 280), N("c10", "10. Архитектура\nи feedback", 1140, 160, "pu", 280),
], edges=[E("c1", "c3"), E("c3", "c5"), E("c5", "c9")])

if __name__ == "__main__":
    run_all(D)
