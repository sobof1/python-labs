"""Лабораторна робота № 4, варіант 15.

Матрична частина: генерація матриці 3×3, норма Фробеніуса, добуток
``A × A`` та пошук усіх сідлових точок.
"""

from __future__ import annotations

import math
import random
import time
from collections.abc import Sequence


# (N, M, K, X_MIN, X_MAX): такий самий незмінний кортеж, як у векторному модулі.
CONFIG: tuple[int, int, int, int, int] = (24, 3, 3, 0, 100)
MATRIX_SEED = 3


def matrix_shape(matrix: Sequence[Sequence[int]]) -> tuple[int, int]:
    """Валідує прямокутну матрицю та повертає її розмірність ``(rows, columns)``."""
    if not matrix or not matrix[0]:
        raise ValueError("Матриця повинна містити щонайменше один елемент.")

    rows = len(matrix)
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("Матриця повинна бути прямокутною.")
    return rows, columns


def generate_random_matrix(
    rows: int, columns: int, minimum: int, maximum: int, rng: random.Random
) -> list[list[int]]:
    """Генерує прямокутну матрицю випадкових цілих значень."""
    if rows <= 0 or columns <= 0:
        raise ValueError("Кількість рядків і стовпців має бути додатною.")
    if minimum > maximum:
        raise ValueError("Нижня межа діапазону не може перевищувати верхню.")

    return [[rng.randint(minimum, maximum) for _ in range(columns)] for _ in range(rows)]


def frobenius_norm(matrix: Sequence[Sequence[int]]) -> float:
    """Обчислює норму Фробеніуса ``sqrt(sum(A[i][j]²))``."""
    matrix_shape(matrix)
    squared_sum = sum(value * value for row in matrix for value in row)
    return math.sqrt(squared_sum)


def multiply_matrices(
    matrix_a: Sequence[Sequence[int]], matrix_b: Sequence[Sequence[int]]
) -> list[list[int]]:
    """Повертає класичний матричний добуток ``matrix_a × matrix_b``."""
    rows_a, columns_a = matrix_shape(matrix_a)
    rows_b, columns_b = matrix_shape(matrix_b)
    if columns_a != rows_b:
        raise ValueError(
            "Несумісні розмірності для множення: "
            f"A({rows_a}×{columns_a}) і B({rows_b}×{columns_b})."
        )

    return [
        [
            sum(matrix_a[row][index] * matrix_b[index][column] for index in range(columns_a))
            for column in range(columns_b)
        ]
        for row in range(rows_a)
    ]


def find_saddle_points(matrix: Sequence[Sequence[int]]) -> list[tuple[int, int, int]]:
    """Знаходить усі точки, що є мінімумом рядка і максимумом стовпця.

    Індекси у повернених кортежах нульові: ``(row_index, column_index, value)``.
    """
    rows, columns = matrix_shape(matrix)
    row_minima = [min(row) for row in matrix]
    column_maxima = [max(matrix[row][column] for row in range(rows)) for column in range(columns)]

    return [
        (row, column, matrix[row][column])
        for row in range(rows)
        for column in range(columns)
        if matrix[row][column] == row_minima[row]
        and matrix[row][column] == column_maxima[column]
    ]


def print_matrix(matrix: Sequence[Sequence[int]], title: str) -> None:
    """Виводить матрицю в компактному, придатному для скриншота форматі."""
    rows, columns = matrix_shape(matrix)
    print(f"\n{title} ({rows}×{columns}):")
    for row in matrix:
        print("  [ " + " ".join(f"{value:>5}" for value in row) + " ]")


def main() -> None:
    """Демонструє повне розв'язання матричної частини варіанта 15."""
    vector_length, rows, columns, minimum, maximum = CONFIG
    if rows != columns:
        raise ValueError("Для варіанта 15 добуток A × A потребує квадратної матриці.")

    matrix_a = generate_random_matrix(rows, columns, minimum, maximum, random.Random(MATRIX_SEED))
    squared_sum = sum(value * value for row in matrix_a for value in row)
    norm = frobenius_norm(matrix_a)
    matrix_product = multiply_matrices(matrix_a, matrix_a)
    saddle_points = find_saddle_points(matrix_a)
    row_minima = [min(row) for row in matrix_a]
    column_maxima = [max(matrix_a[row][column] for row in range(rows)) for column in range(columns)]

    print("=" * 88)
    print(f"{'ЛБ4, ВАРІАНТ 15 — МАТРИЦЯ, НОРМА ФРОБЕНІУСА ТА A × A':^88}")
    print("=" * 88)
    print(
        "CONFIG = "
        f"(N={vector_length}, M={rows}, K={columns}, X_MIN={minimum}, X_MAX={maximum})"
    )
    print(f"Фіксоване зерно генератора: {MATRIX_SEED}")
    print_matrix(matrix_a, "Початкова матриця A")
    print(f"\nΣ A[i][j]² = {squared_sum}")
    print(f"Норма Фробеніуса ||A||_F = √{squared_sum} = {norm:.6f}")
    print_matrix(matrix_product, "Матричний добуток A × A")
    print(
        "Перевірка C[0][0]: "
        f"{matrix_a[0][0]}×{matrix_a[0][0]} + {matrix_a[0][1]}×{matrix_a[1][0]} + "
        f"{matrix_a[0][2]}×{matrix_a[2][0]} = {matrix_product[0][0]}"
    )
    print("\nСідлові точки A (мінімум рядка та максимум стовпця):")
    print(f"  Мінімуми рядків: {row_minima}")
    print(f"  Максимуми стовпців: {column_maxima}")
    if saddle_points:
        for number, (row, column, value) in enumerate(saddle_points, start=1):
            print(
                f"  {number}. A[{row}][{column}] = {value} "
                f"(рядок {row + 1}, стовпець {column + 1})"
            )
    else:
        print("  Не виявлено.")

    print("=" * 88)


if __name__ == "__main__":
    started_at = time.perf_counter()
    main()
    elapsed_ms = (time.perf_counter() - started_at) * 1_000
    print(f"Час виконання матричного модуля: {elapsed_ms:.4f} мс")
