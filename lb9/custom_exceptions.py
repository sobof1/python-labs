"""Лабораторна робота № 9, варіант 15: винятки контролера DDR5."""

from __future__ import annotations


class MemoryTimingError(Exception):
    """Базовий доменний виняток для некоректної конфігурації DDR5."""

    def __init__(self, message: str, error_code: int = 9000) -> None:
        super().__init__(message)
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[DDR5-{self.error_code}] {super().__str__()}"


class CASLatencyConflictError(MemoryTimingError):
    """Сигналізує про tCL поза допустимим числовим діапазоном."""

    def __init__(self, cas_latency: int, minimum: int = 28, maximum: int = 40) -> None:
        self.cas_latency = cas_latency
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(
            f"tCL = {cas_latency} не належить діапазону [{minimum}; {maximum}].",
            error_code=9001,
        )


class VDDOverVoltageError(MemoryTimingError):
    """Сигналізує про перевищення верхньої межі напруги VDD."""

    def __init__(self, voltage: float, maximum: float = 1.15) -> None:
        self.voltage = voltage
        self.maximum = maximum
        super().__init__(
            f"VDD = {voltage:.3f} В перевищує верхню межу {maximum:.3f} В.",
            error_code=9002,
        )


class VDDUnderVoltageError(MemoryTimingError):
    """Сигналізує про занижену напругу VDD."""

    def __init__(self, voltage: float, minimum: float = 1.05) -> None:
        self.voltage = voltage
        self.minimum = minimum
        super().__init__(
            f"VDD = {voltage:.3f} В нижча за межу {minimum:.3f} В.",
            error_code=9003,
        )


class DataRateOutOfRangeError(MemoryTimingError):
    """Сигналізує про частоту DDR5 поза діапазоном 4800…6400 MT/s."""

    def __init__(self, data_rate_mt_s: int, minimum: int = 4800, maximum: int = 6400) -> None:
        self.data_rate_mt_s = data_rate_mt_s
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(
            f"Частота {data_rate_mt_s} MT/s не належить діапазону [{minimum}; {maximum}] MT/s.",
            error_code=9004,
        )
