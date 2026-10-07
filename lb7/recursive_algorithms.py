"""Лабораторна робота № 7, варіант 15.

Безпечне дослідження рекурсивної функції Аккермана для ``m <= 3`` з
контролем глибини стеку та порівнянням з ітеративною реалізацією.
"""

from __future__ import annotations

import sys
import time
from typing import NamedTuple


class AckermannSafetyError(ValueError):
    """Повідомляє про запит, небезпечний для демонстрації рекурсії."""


class IterativeStats(NamedTuple):
    """Результат ітеративної симуляції разом з метриками явного стеку."""

    value: int
    steps: int
    max_pending_frames: int


class RecursionDepthTracker:
    """Рахує власні рекурсивні кадри та перериває небезпечне обчислення."""

    def __init__(self, max_allowed_depth: int) -> None:
        if max_allowed_depth < 1:
            raise ValueError("max_allowed_depth має бути не меншим за 1.")
        self.max_allowed_depth = max_allowed_depth
        self.current_depth = 0
        self.max_observed_depth = 0

    def enter(self) -> None:
        """Фіксує вхід у кадр, не дозволяючи перевищити власний ліміт."""
        self.current_depth += 1
        self.max_observed_depth = max(self.max_observed_depth, self.current_depth)
        if self.current_depth > self.max_allowed_depth:
            self.current_depth -= 1
            raise RecursionError(
                "Перевищено програмний ліміт рекурсії: "
                f"{self.max_observed_depth} > {self.max_allowed_depth}"
            )

    def leave(self) -> None:
        """Фіксує повернення з кадру рекурсивної функції."""
        self.current_depth -= 1


def _is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def ackermann_closed_form_for_small_m(m: int, n: int) -> int:
    """Обчислює значення A(m, n) за формулами, коректними лише для m <= 3."""
    if m == 0:
        return n + 1
    if m == 1:
        return n + 2
    if m == 2:
        return 2 * n + 3
    if m == 3:
        return 2 ** (n + 3) - 3
    raise AckermannSafetyError("Замкнена форма в модулі підтримує лише m <= 3.")


def validate_ackermann_request(m: object, n: object, max_depth: int) -> tuple[int, int, int]:
    """Валідує межі варіанта та оцінює безпечність до рекурсивного виклику."""
    if not _is_plain_int(m) or not _is_plain_int(n):
        raise AckermannSafetyError("m і n мають бути цілими числами, а не bool або float.")
    if m < 0 or n < 0:
        raise AckermannSafetyError("Для цієї роботи допускаються лише невід'ємні m і n.")
    if m > 3:
        raise AckermannSafetyError("Варіант 15 обмежує дослідження умовою m <= 3.")
    if not _is_plain_int(max_depth) or max_depth < 1:
        raise AckermannSafetyError("max_depth має бути додатним цілим числом.")

    expected_value = ackermann_closed_form_for_small_m(m, n)
    # Для m=3 глибина традиційної рекурсивної реалізації росте разом зі
    # значенням A(3, n). Оцінка нижче консервативно зупиняє запит до того,
    # як CPython досягне власного ліміту рекурсії.
    estimated_required_depth = expected_value + 2
    if estimated_required_depth > max_depth:
        raise AckermannSafetyError(
            f"A({m}, {n}) = {expected_value}; прогнозована глибина не менше "
            f"{estimated_required_depth}, що перевищує безпечний ліміт {max_depth}."
        )
    return m, n, expected_value


def ackermann_recursive(m: int, n: int, tracker: RecursionDepthTracker) -> int:
    """Рекурсивне означення функції Аккермана з аудитом глибини викликів."""
    tracker.enter()
    try:
        if m == 0:
            return n + 1
        if n == 0:
            return ackermann_recursive(m - 1, 1, tracker)
        return ackermann_recursive(
            m - 1,
            ackermann_recursive(m, n - 1, tracker),
            tracker,
        )
    finally:
        tracker.leave()


def ackermann_iterative(m: int, n: int, max_pending_frames: int = 100_000) -> IterativeStats:
    """Симулює рекурсію явним стеком, не використовуючи викликів самої себе."""
    pending_m_values = [m]
    steps = 0
    max_observed = 1

    while pending_m_values:
        if len(pending_m_values) > max_pending_frames:
            raise AckermannSafetyError(
                "Ітеративний явний стек перевищив безпечний ліміт "
                f"{max_pending_frames} кадрів."
            )

        current_m = pending_m_values.pop()
        steps += 1

        if current_m == 0:
            n += 1
        elif n == 0:
            n = 1
            pending_m_values.append(current_m - 1)
        else:
            # A(m, n) = A(m - 1, A(m, n - 1)). У стек спочатку кладемо
            # зовнішній виклик, а верхівкою — внутрішній, який виконається першим.
            pending_m_values.append(current_m - 1)
            pending_m_values.append(current_m)
            n -= 1

        max_observed = max(max_observed, len(pending_m_values))

    return IterativeStats(n, steps, max_observed)


def _choose_safe_depth_limit() -> int:
    """Залишає запас до ліміту CPython і не змінює глобальне налаштування sys."""
    return min(600, max(64, sys.getrecursionlimit() - 128))


def main() -> None:
    """Порівнює дві реалізації на безпечному для m=3 наборі параметрів."""
    print("=" * 100)
    print(f"{'ЛБ7, ВАРІАНТ 15 — ФУНКЦІЯ АККЕРМАНА ТА КОНТРОЛЬ СТЕКУ':^100}")
    print("=" * 100)

    m, n = 3, 5
    system_limit = sys.getrecursionlimit()
    safe_depth_limit = _choose_safe_depth_limit()
    validated_m, validated_n, expected_value = validate_ackermann_request(
        m, n, safe_depth_limit
    )

    print("Означення: A(0, n)=n+1; A(m, 0)=A(m-1, 1); A(m, n)=A(m-1, A(m, n-1)).")
    print(f"Системний ліміт CPython: {system_limit} кадрів")
    print(f"Програмний безпечний ліміт: {safe_depth_limit} кадрів")
    print(f"Обраний безпечний запит: A({validated_m}, {validated_n})")
    print(f"Контрольне значення за формулою для m <= 3: {expected_value}")
    print("-" * 100)

    tracker = RecursionDepthTracker(max_allowed_depth=safe_depth_limit)
    started_at = time.perf_counter()
    recursive_value = ackermann_recursive(validated_m, validated_n, tracker)
    recursive_elapsed_ms = (time.perf_counter() - started_at) * 1000

    started_at = time.perf_counter()
    iterative_stats = ackermann_iterative(validated_m, validated_n)
    iterative_elapsed_ms = (time.perf_counter() - started_at) * 1000

    print("РЕКУРСИВНА РЕАЛІЗАЦІЯ")
    print(f"Значення A({m}, {n}): {recursive_value}")
    print(f"Максимальна зафіксована глибина: {tracker.max_observed_depth} кадрів")
    print(f"Поточна глибина після завершення: {tracker.current_depth} кадрів")
    print(f"Час: {recursive_elapsed_ms:.3f} мс")
    print()
    print("ІТЕРАТИВНИЙ АНАЛОГ (явний стек)")
    print(f"Значення A({m}, {n}): {iterative_stats.value}")
    print(f"Кількість кроків: {iterative_stats.steps}")
    print(f"Максимальний розмір явного стеку: {iterative_stats.max_pending_frames} кадрів")
    print(f"Час: {iterative_elapsed_ms:.3f} мс")
    print()
    matches = recursive_value == iterative_stats.value == expected_value
    print(f"Порівняння рекурсивного, ітеративного та контрольного результатів: {str(matches).upper()}")
    print("-" * 100)

    print("ПЕРЕВІРКА ЗАХИСТУ ВІД НЕБЕЗПЕЧНИХ ЗАПИТІВ")
    for unsafe_m, unsafe_n in ((3, 7), (4, 0)):
        try:
            validate_ackermann_request(unsafe_m, unsafe_n, safe_depth_limit)
        except AckermannSafetyError as error:
            print(f"A({unsafe_m}, {unsafe_n}) відхилено: {error}")
    print("=" * 100)


if __name__ == "__main__":
    main()
