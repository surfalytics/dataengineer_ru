#!/usr/bin/env python3
"""Глава 3: запросы к LLM не помнят друг друга (stateless).
Бесплатная модель-заглушка вместо Anthropic API: она видит только те сообщения,
которые ей передали. Запуск: python3 -I scripts/claude-code-code/ch03_stateless.py"""
import re


def fake_model(messages):
    """Отвечает на «What is my name?», только если имя есть в переданных сообщениях."""
    last = messages[-1]["content"]
    if last.startswith("My name is"):
        return "Nice to meet you!"
    if last == "What is my name?":
        for m in messages:
            found = re.match(r"My name is (.+)\.", m["content"])
            if m["role"] == "user" and found:
                return f"Your name is {found.group(1)}."
        return "I don't know your name."
    return "OK."


def words(messages):
    return sum(len(m["content"].split()) for m in messages)


prompts = ["My name is Inigo Montoya.", "What is my name?"]

print("Без истории (как голый API):")
for p in prompts:
    msgs = [{"role": "user", "content": p}]
    print(f"  {p!r} -> {fake_model(msgs)!r}")

print("С историей (как Claude Code):")
history = []
for p in prompts:
    history.append({"role": "user", "content": p})
    answer = fake_model(history)
    print(f"  {p!r} -> {answer!r}  (отправлено слов: {words(history)})")
    history.append({"role": "assistant", "content": answer})
