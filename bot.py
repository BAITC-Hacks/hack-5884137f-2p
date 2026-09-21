#!/usr/bin/env python3
"""
Простой FAQ-бот для терминала.
Читает faq.txt (пары вопрос/ответ, разделённые пустой строкой),
сравнивает вопрос пользователя с вопросами из базы по пересечению
ключевых слов и печатает лучший ответ. Если совпадение слабое — "не знаю".
"""

import re
import sys

FAQ_PATH = "faq.txt"
MIN_OVERLAP = 1          # минимум общих ключевых слов, чтобы считать совпадением
MIN_SCORE = 0.2          # минимальная доля пересечения (Jaccard), чтобы считать совпадением

# Слова, которые не несут смысла и не учитываются при сравнении
STOPWORDS = {
    "а", "и", "или", "но", "в", "во", "на", "с", "со", "к", "ко", "по",
    "за", "от", "до", "из", "у", "о", "об", "для", "как", "что", "это",
    "то", "ли", "же", "бы", "не", "ни", "мне", "мой", "моя", "мои",
    "вы", "ты", "я", "мы", "он", "она", "они", "есть", "будет", "был",
    "когда", "где", "какой", "какая", "какие", "можно", "нужно",
}


def tokenize(text: str) -> set:
    words = re.findall(r"[а-яёa-z0-9]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def load_faq(path: str):
    """Загружает пары (вопрос, ответ) из текстового файла.
    Формат: строка-вопрос, строка-ответ, пустая строка-разделитель."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    blocks = [b.strip() for b in raw.split("\n\n") if b.strip()]
    faq = []
    for block in blocks:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if len(lines) >= 2:
            question, answer = lines[0], " ".join(lines[1:])
            faq.append((question, answer, tokenize(question)))
    return faq


def find_answer(user_question: str, faq):
    user_tokens = tokenize(user_question)
    if not user_tokens:
        return None

    best = None
    best_score = 0.0

    for question, answer, tokens in faq:
        if not tokens:
            continue
        overlap = user_tokens & tokens
        if len(overlap) < MIN_OVERLAP:
            continue
        # Jaccard-подобная метрика: пересечение / объединение
        score = len(overlap) / len(user_tokens | tokens)
        if score > best_score:
            best_score = score
            best = answer

    if best is not None and best_score >= MIN_SCORE:
        return best
    return None


def main():
    try:
        faq = load_faq(FAQ_PATH)
    except FileNotFoundError:
        print(f"Не найден файл {FAQ_PATH}. Положите его рядом со скриптом.")
        sys.exit(1)

    if not faq:
        print("В faq.txt не найдено ни одной пары вопрос-ответ.")
        sys.exit(1)

    print("FAQ-бот репетиции. Задавайте вопросы (время, команда, трек, сдача, призы).")
    print("Для выхода — команда exit или Ctrl+C.\n")

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nПока!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "выход"}:
            print("Пока!")
            break

        answer = find_answer(user_input, faq)
        if answer:
            print(answer)
        else:
            print("Не знаю.")


if __name__ == "__main__":
    main()
