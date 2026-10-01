"""Лабораторна робота № 3, варіант 15.

Обчислення ряду Бесселя J0(x) рекурентним способом.
"""

from __future__ import annotations

import math
import time


def compute_bessel_j0_series(
    x: float, epsilon: float = 1e-7, max_iterations: int = 10_000
) -> tuple[float, int, float]:
    """Обчислює J0(x) = Σ (-1)^k (x/2)^(2k)/(k!)².

    Наступний член одержується рекурентно:
    a_k = a_(k-1) * (-x² / (4k²)).
    Повертає суму, кількість доданих ненульових членів і останній доданок.
    """
    if epsilon <= 0.0:
        raise ValueError("Точність epsilon має бути додатною.")
    if max_iterations <= 0:
        raise ValueError("max_iterations має бути додатним.")

    # У точці x = 0 всі члени після a0 дорівнюють нулю.
    if x == 0.0:
        return 1.0, 0, 0.0

    k = 0
    term = 1.0
    series_sum = term

    while abs(term) >= epsilon and k < max_iterations:
        k += 1
        term *= -(x * x) / (4.0 * k * k)
        series_sum += term

    if k >= max_iterations and abs(term) >= epsilon:
        raise RuntimeError("Не досягнуто заданої точності за max_iterations ітерацій.")

    return series_sum, k, term


def compute_bessel_j0_direct(
    x: float, epsilon: float = 1e-15, max_iterations: int = 10_000
) -> float:
    """Незалежне контрольне обчислення J0(x) через степінь і factorial.

    У модулі math відсутня функція Bessel J0, тому це контрольний еталон
    для перевірки рекурентного алгоритму. У робочому алгоритмі ця функція
    не використовується.
    """
    total = 0.0
    for k in range(max_iterations):
        term = ((-1.0) ** k) * (x / 2.0) ** (2 * k) / (math.factorial(k) ** 2)
        total += term
        if abs(term) < epsilon:
            return total
    raise RuntimeError("Контрольний ряд не збігся за max_iterations ітерацій.")


def print_series_table(points: list[float], epsilon: float = 1e-7) -> None:
    """Виводить порівняння рекурентної суми з незалежним контролем."""
    line = "=" * 100
    print(line)
    print(f"{'РЯД БЕССЕЛЯ J0(x), ВАРІАНТ 15; ε = 1e-7':^100}")
    print(line)
    print(
        f"| {'x':^8} | {'S(x), рекурентно':^22} | {'Контрольне значення':^22} | "
        f"{'k':^5} | {'|a_k|':^13} | {'Абсолютна похибка':^20} |"
    )
    print("-" * 100)

    for x_value in points:
        series_sum, iterations, last_term = compute_bessel_j0_series(x_value, epsilon)
        reference = compute_bessel_j0_direct(x_value)
        error = abs(series_sum - reference)
        print(
            f"| {x_value:^8.2f} | {series_sum:^22.12f} | {reference:^22.12f} | "
            f"{iterations:^5} | {abs(last_term):^13.4e} | {error:^20.4e} |"
        )
    print(line)
    print("Примітка: math не містить J0; контроль отримано незалежним прямим рядом.")


def main() -> None:
    """Запускає тестування рекурентного алгоритму в контрольних точках."""
    started_at = time.perf_counter()
    print_series_table([0.0, 0.5, 1.0, 2.0, 5.0])
    elapsed_ms = (time.perf_counter() - started_at) * 1_000.0
    print(f"Час виконання: {elapsed_ms:.3f} мс")


if __name__ == "__main__":
    main()
