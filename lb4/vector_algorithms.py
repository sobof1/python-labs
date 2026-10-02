"""Лабораторна робота № 4, варіант 15.

Одновимірний вектор: генерація, підрахунок частот, пошук екстремумів
та ручне сортування вибором. Модуль не використовує ``list.sort()``
або ``sorted()`` для отримання результату сортування.
"""

from __future__ import annotations

import random
import time
from collections.abc import Sequence


# (N, M, K, X_MIN, X_MAX): довжина вектора, розмір матриці та межі генерації.
CONFIG: tuple[int, int, int, int, int] = (24, 3, 3, 0, 100)
VECTOR_SEED = 20_261_015


def generate_random_vector(
    length: int, minimum: int, maximum: int, rng: random.Random
) -> list[int]:
    """Повертає випадковий вектор заданої довжини у замкненому діапазоні."""
    if length <= 0:
        raise ValueError("Довжина вектора має бути додатною.")
    if minimum > maximum:
        raise ValueError("Нижня межа діапазону не може перевищувати верхню.")

    return [rng.randint(minimum, maximum) for _ in range(length)]


def count_frequencies(vector: Sequence[int]) -> dict[int, int]:
    """Підраховує появи елементів, зберігаючи порядок їх першої появи."""
    frequencies: dict[int, int] = {}
    for value in vector:
        frequencies[value] = frequencies.get(value, 0) + 1
    return frequencies


def find_extrema_positions(vector: Sequence[int]) -> tuple[int, list[int], int, list[int]]:
    """Повертає мінімум, його індекси, максимум і його індекси."""
    if not vector:
        raise ValueError("Неможливо знайти екстремуми порожнього вектора.")

    minimum = min(vector)
    maximum = max(vector)
    minimum_positions = [index for index, value in enumerate(vector) if value == minimum]
    maximum_positions = [index for index, value in enumerate(vector) if value == maximum]
    return minimum, minimum_positions, maximum, maximum_positions


def selection_sort(vector: Sequence[int]) -> list[int]:
    """Сортує копію вектора за зростанням прямим алгоритмом Selection Sort."""
    result = list(vector)

    for current_index in range(len(result) - 1):
        minimum_index = current_index
        for candidate_index in range(current_index + 1, len(result)):
            if result[candidate_index] < result[minimum_index]:
                minimum_index = candidate_index

        if minimum_index != current_index:
            result[current_index], result[minimum_index] = (
                result[minimum_index],
                result[current_index],
            )

    return result


def is_non_decreasing(values: Sequence[int]) -> bool:
    """Перевіряє, що кожен наступний елемент не менший за попередній."""
    return all(values[index] <= values[index + 1] for index in range(len(values) - 1))


def print_frequency_table(frequencies: dict[int, int]) -> None:
    """Друкує компактну таблицю частот для зручного знімка екрана."""
    print("Частоти появи (значення: кількість; порядок першої появи):")
    entries = list(frequencies.items())
    for start in range(0, len(entries), 3):
        row = entries[start : start + 3]
        print("  " + " | ".join(f"{value:>3}: {count}" for value, count in row))


def main() -> None:
    """Демонструє повне розв'язання векторної частини варіанта 15."""
    vector_length, matrix_rows, matrix_columns, minimum, maximum = CONFIG
    rng = random.Random(VECTOR_SEED)
    vector = generate_random_vector(vector_length, minimum, maximum, rng)
    frequencies = count_frequencies(vector)
    repeated_values = [(value, count) for value, count in frequencies.items() if count > 1]
    minimum_value, minimum_positions, maximum_value, maximum_positions = find_extrema_positions(
        vector
    )
    sorted_vector = selection_sort(vector)

    print("=" * 88)
    print(f"{'ЛБ4, ВАРІАНТ 15 — ВЕКТОРИ ТА СОРТУВАННЯ ВИБОРОМ':^88}")
    print("=" * 88)
    print(
        "CONFIG = "
        f"(N={vector_length}, M={matrix_rows}, K={matrix_columns}, "
        f"X_MIN={minimum}, X_MAX={maximum})"
    )
    print(f"Фіксоване зерно генератора: {VECTOR_SEED}")
    print(f"Початковий випадковий вектор V ({len(vector)} елементи):\n  {vector}")
    print_frequency_table(frequencies)
    print(f"Сума всіх частот: {sum(frequencies.values())} (очікувано N = {vector_length})")
    print(f"Повторювані значення, List Comprehension: {repeated_values}")
    print(
        f"Мінімум: {minimum_value}; індекси (від 0): {minimum_positions}. "
        f"Максимум: {maximum_value}; індекси (від 0): {maximum_positions}."
    )
    print(f"Selection Sort (за зростанням):\n  {sorted_vector}")
    print(f"Перевірка неубування: {'PASS' if is_non_decreasing(sorted_vector) else 'FAIL'}")
    print(
        "Перевірка збереження частот: "
        f"{'PASS' if count_frequencies(vector) == count_frequencies(sorted_vector) else 'FAIL'}"
    )
    print("=" * 88)


if __name__ == "__main__":
    started_at = time.perf_counter()
    main()
    elapsed_ms = (time.perf_counter() - started_at) * 1_000
    print(f"Час виконання векторного модуля: {elapsed_ms:.4f} мс")
