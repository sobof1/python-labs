"""Лабораторна робота № 2: математична модель варіанта 15."""

import math


def compute_power_model(x: float, y: float) -> float:
    """Обчислює f(x, y) для варіанта 15 та перевіряє область визначення."""
    if y < -1.0:
        raise ValueError("Для sqrt(y + 1) параметр y має бути не меншим за -1.")

    numerator = x**2 * math.sqrt(y + 1.0) + math.exp(-x)
    denominator = math.log2(x**2 + y**2 + 2.0)
    return numerator / denominator


def main() -> None:
    """Демонструє розрахунок моделі та перевірку точності IEEE 754."""
    x_value = 2.5
    y_value = 3.0
    calculated = compute_power_model(x_value, y_value)

    numerator = x_value**2 * math.sqrt(y_value + 1.0) + math.exp(-x_value)
    denominator = math.log2(x_value**2 + y_value**2 + 2.0)
    reference = numerator / denominator
    is_accurate = math.isclose(calculated, reference, rel_tol=1e-12)

    print("=" * 80)
    print(f"{'МАТЕМАТИЧНЕ МОДЕЛЮВАННЯ ВАРІАНТУ 15':^80}")
    print("=" * 80)
    print("f(x, y) = (x² · √(y + 1) + exp(-x)) / log₂(x² + y² + 2)")
    print(f"Вхідні дані: x = {x_value:.3f}, y = {y_value:.3f}")
    print(f"Чисельник: {numerator:.10f}")
    print(f"Знаменник: {denominator:.10f}")
    print(f"Обчислене f(x, y): {calculated:.10f}")
    print(f"Еталонне значення:  {reference:.10f}")
    print(f"Перевірка math.isclose: {is_accurate} (rel_tol=1e-12)")
    print("=" * 80)


if __name__ == "__main__":
    main()
