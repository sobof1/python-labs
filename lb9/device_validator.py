"""Лабораторна робота № 9, варіант 15.

Валідація конфігурації контролера пам'яті DDR5, власні винятки,
ланцюжки ``raise ... from ...`` та тестовий стенд відновлення.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from custom_exceptions import (
    CASLatencyConflictError,
    DataRateOutOfRangeError,
    MemoryTimingError,
    VDDOverVoltageError,
    VDDUnderVoltageError,
)


MIN_TCL = 28
MAX_TCL = 40
NOMINAL_VDD = 1.10
MIN_VDD = 1.05
MAX_VDD = 1.15
MIN_DATA_RATE = 4800
MAX_DATA_RATE = 6400
SAFE_CONFIGURATION = {"tcl": 36, "vdd": NOMINAL_VDD, "data_rate_mt_s": 5600}


def _read_number(config: Mapping[str, Any], key: str, target_type: type[float] | type[int]) -> float | int:
    """Читає числовий параметр, зберігаючи першопричину помилки перетворення."""
    if key not in config:
        raise MemoryTimingError(f"Відсутній обов'язковий параметр '{key}'.", error_code=9005)

    try:
        value = target_type(config[key])
    except (TypeError, ValueError) as cause:
        raise MemoryTimingError(
            f"Параметр '{key}' повинен бути числом; отримано {config[key]!r}.", error_code=9006
        ) from cause

    if not math.isfinite(float(value)):
        raise MemoryTimingError(f"Параметр '{key}' повинен бути скінченним числом.", error_code=9007)
    return value


def validate_ddr5_configuration(config: Mapping[str, Any]) -> dict[str, float | int]:
    """Валідує tCL, VDD і частоту передачі даних контролера DDR5."""
    cas_latency = int(_read_number(config, "tcl", int))
    vdd = float(_read_number(config, "vdd", float))
    data_rate = int(_read_number(config, "data_rate_mt_s", int))

    if not MIN_TCL <= cas_latency <= MAX_TCL:
        raise CASLatencyConflictError(cas_latency, MIN_TCL, MAX_TCL)
    if vdd > MAX_VDD:
        raise VDDOverVoltageError(vdd, MAX_VDD)
    if vdd < MIN_VDD:
        raise VDDUnderVoltageError(vdd, MIN_VDD)
    if not MIN_DATA_RATE <= data_rate <= MAX_DATA_RATE:
        raise DataRateOutOfRangeError(data_rate, MIN_DATA_RATE, MAX_DATA_RATE)

    return {"tcl": cas_latency, "vdd": vdd, "data_rate_mt_s": data_rate}


def recover_configuration(error: MemoryTimingError) -> dict[str, float | int]:
    """Повертає безпечний профіль після локалізації помилки конфігурації."""
    recovered = dict(SAFE_CONFIGURATION)
    if isinstance(error, CASLatencyConflictError):
        recovered["tcl"] = min(max(error.cas_latency, MIN_TCL), MAX_TCL)
        action = "tCL обмежено безпечним діапазоном"
    elif isinstance(error, VDDOverVoltageError):
        recovered["vdd"] = MAX_VDD
        action = "VDD знижено до верхньої безпечної межі"
    elif isinstance(error, VDDUnderVoltageError):
        recovered["vdd"] = MIN_VDD
        action = "VDD підвищено до нижньої безпечної межі"
    elif isinstance(error, DataRateOutOfRangeError):
        recovered["data_rate_mt_s"] = min(
            max(error.data_rate_mt_s, MIN_DATA_RATE), MAX_DATA_RATE
        )
        action = "частоту обмежено безпечним діапазоном"
    else:
        action = "використано повністю безпечний профіль за замовчуванням"

    print(f"  Відновлення: {action}.")
    return recovered


def run_fault_tolerance_testbench() -> None:
    """Демонструє ``try-except-else-finally`` для всіх сценаріїв варіанта 15."""
    scenarios: list[tuple[str, dict[str, Any]]] = [
        ("Валідна конфігурація", {"tcl": 36, "vdd": 1.10, "data_rate_mt_s": 5600}),
        ("Конфлікт CAS latency", {"tcl": 24, "vdd": 1.10, "data_rate_mt_s": 5600}),
        ("Перенапруга VDD", {"tcl": 36, "vdd": 1.18, "data_rate_mt_s": 5600}),
        ("Недостатня VDD", {"tcl": 36, "vdd": 1.00, "data_rate_mt_s": 5600}),
        ("Неприпустима частота", {"tcl": 36, "vdd": 1.10, "data_rate_mt_s": 7200}),
        ("Некоректний тип VDD", {"tcl": 36, "vdd": "high", "data_rate_mt_s": 5600}),
    ]

    successes = 0
    detected_faults = 0
    recovered_faults = 0
    separator = "=" * 94

    print(separator)
    print(f"{'ЛБ9, ВАРІАНТ 15 — ВІДМОВОСТІЙКІСТЬ КОНТРОЛЕРА DDR5':^94}")
    print(separator)

    for number, (title, config) in enumerate(scenarios, start=1):
        print(f"\nСценарій {number}: {title}")
        print(f"  Вхідна конфігурація: {config}")
        try:
            validated = validate_ddr5_configuration(config)
        except CASLatencyConflictError as error:
            detected_faults += 1
            print(f"  Перехоплено {type(error).__name__}: {error}")
            recovered = recover_configuration(error)
        except VDDOverVoltageError as error:
            detected_faults += 1
            print(f"  Перехоплено {type(error).__name__}: {error}")
            recovered = recover_configuration(error)
        except VDDUnderVoltageError as error:
            detected_faults += 1
            print(f"  Перехоплено {type(error).__name__}: {error}")
            recovered = recover_configuration(error)
        except DataRateOutOfRangeError as error:
            detected_faults += 1
            print(f"  Перехоплено {type(error).__name__}: {error}")
            recovered = recover_configuration(error)
        except MemoryTimingError as error:
            detected_faults += 1
            print(f"  Перехоплено базовий {type(error).__name__}: {error}")
            if error.__cause__ is not None:
                print(f"  Ланцюжок причини: {type(error.__cause__).__name__}: {error.__cause__}")
            recovered = recover_configuration(error)
        else:
            successes += 1
            print(f"  Успіх: валідна конфігурація {validated}.")
            continue
        finally:
            print("  FINALLY: журнал конфігурації закрито, стан контролера зафіксовано.")

        try:
            validate_ddr5_configuration(recovered)
        except MemoryTimingError as recovery_error:
            print(f"  Відновлення не вдалося: {recovery_error}")
        else:
            recovered_faults += 1
            print(f"  Відновлення успішне: {recovered}.")

    p_recovery = recovered_faults / detected_faults if detected_faults else 1.0
    print("\n" + separator)
    print("ПІДСУМКОВІ МЕТРИКИ")
    print(f"  Валідних сценаріїв: {successes}")
    print(f"  Виявлених збоїв: {detected_faults}")
    print(f"  Успішно відновлених збоїв: {recovered_faults}")
    print(f"  P_recovery = {recovered_faults}/{detected_faults} = {p_recovery:.2f}")
    print(separator)


if __name__ == "__main__":
    run_fault_tolerance_testbench()
