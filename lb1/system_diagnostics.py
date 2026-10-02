import sys
import platform


def analyze_numeric_types() -> None:
    """Вывод характеристик числовых типов Python."""

    float_info = sys.float_info
    int_info = sys.int_info

    print("=" * 80)
    print(f"{'ХАРАКТЕРИСТИКИ ЧИСЛОВЫХ ТИПОВ PYTHON':^80}")
    print("=" * 80)

    print("\nПАРАМЕТРЫ ТИПУ FLOAT")
    print("-" * 80)

    print(f"Максимальне значення float:       {float_info.max}")
    print(f"Мінімальне додатне float:         {float_info.min}")
    print(f"Машинний epsilon:                 {float_info.epsilon}")
    print(f"Десяткових цифр точності:         {float_info.dig}")
    print(f"Бітів у мантисі:                  {float_info.mant_dig}")
    print(f"Максимальний двійковий порядок:   {float_info.max_exp}")
    print(f"Мінімальний двійковий порядок:    {float_info.min_exp}")
    print(f"Максимальний десятковий порядок:  {float_info.max_10_exp}")
    print(f"Мінімальний десятковий порядок:   {float_info.min_10_exp}")

    print("\nПАРАМЕТРИ ТИПУ INT")
    print("-" * 80)

    print(f"Бітів на digit:                   {int_info.bits_per_digit}")
    print(f"Розмір digit у байтах:            {int_info.sizeof_digit}")

    print("\nІНФОРМАЦІЯ ПРО ІНТЕРПРЕТАТОР")
    print("-" * 80)

    print(f"Python:                            {platform.python_version()}")
    print(f"Реалізація:                        {platform.python_implementation()}")
    print(f"Архітектура:                       {platform.architecture()[0]}")

    print("=" * 80)


if __name__ == "__main__":
    analyze_numeric_types()