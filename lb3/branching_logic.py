"""Лабораторна робота № 3, варіант 15.

Кусочна функція та її чисельне табулювання.
"""

from __future__ import annotations

import math


def evaluate_piecewise_function(x: float) -> tuple[float, str]:
    """Повертає значення функції f(x) та назву вибраної гілки.

    f(x) = x²/(1 + exp(x)),          x < -1;
            sqrt(x² + 5),     -1 <= x <= 2;
            ln(2x - 3),             x > 2.
    """
    if x < -1.0:
        value = x**2 / (1.0 + math.exp(x))
        branch = "Гілка 1: x < -1"
    elif x <= 2.0:
        value = math.sqrt(x**2 + 5.0)
        branch = "Гілка 2: -1 ≤ x ≤ 2"
    else:
        # За умовою x > 2, тому 2x - 3 > 1 і логарифм визначений.
        value = math.log(2.0 * x - 3.0)
        branch = "Гілка 3: x > 2"
    return value, branch


def tabulate_function(start: float, end: float, step: float) -> list[tuple[float, float, str]]:
    """Табулює f(x) на [start, end] циклом for і range()."""
    if step <= 0.0:
        raise ValueError("Крок табулювання має бути додатним.")
    if start > end:
        raise ValueError("Початок інтервалу не може перевищувати кінець.")

    number_of_steps = math.floor((end - start) / step)
    rows: list[tuple[float, float, str]] = []

    for index in range(number_of_steps + 1):
        x_value = start + index * step
        # Округлення лише прибирає технічну похибку двійкового float у підписі вузла.
        x_value = round(x_value, 12)
        y_value, branch = evaluate_piecewise_function(x_value)
        rows.append((x_value, y_value, branch))

    return rows


def print_tabulation_table(data: list[tuple[float, float, str]]) -> None:
    """Друкує відформатовану таблицю табулювання."""
    line = "=" * 80
    print(line)
    print(f"{'ТАБУЛЮВАННЯ КУСОЧНОЇ ФУНКЦІЇ f(x), ВАРІАНТ 15':^80}")
    print(line)
    print(f"| {'№':^3} | {'x':^10} | {'f(x)':^18} | {'Вибрана гілка':^39} |")
    print("-" * 80)
    for number, (x_value, y_value, branch) in enumerate(data, start=1):
        print(f"| {number:^3} | {x_value:^10.2f} | {y_value:^18.10f} | {branch:<39} |")
    print(line)


def main() -> None:
    """Демонструє табулювання на інтервалі індивідуального варіанта."""
    table = tabulate_function(-3.0, 4.0, 0.25)
    print_tabulation_table(table)


if __name__ == "__main__":
    main()
