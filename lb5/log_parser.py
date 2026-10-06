"""Laboratory work 5, variant 15: CAN-bus log parsing and RPM decoding.

The input format is deliberately textual so that a compiled regular expression
with named capture groups can turn each log line into a structured CAN frame.
The first two data bytes encode engine speed as an unsigned big-endian value in
quarters of one RPM: ``RPM = ((byte0 << 8) | byte1) * 0.25``.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from text_sanitizer import sanitize_log_line


CAN_FRAME_PATTERN = re.compile(
    r"^Timestamp_MS:\s*(?P<timestamp_ms>\d+)\s*\|\s*"
    r"CAN_ID:\s*(?P<can_id>[0-9A-Fa-f]{3})\s*\|\s*"
    r"DLC:\s*(?P<dlc>\d+)\s*\|\s*"
    r"Data_Bytes:\s*(?P<data_bytes>[0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})*)\s*\|\s*"
    r"Bus_State:\s*(?P<bus_state>[A-Za-z_]+)$"
)

ALLOWED_BUS_STATES = frozenset({"ACTIVE", "PASSIVE", "OFF"})
RPM_SCALE = 0.25
INPUT_FILE = Path(__file__).resolve().with_name("input_logs.txt")


@dataclass(frozen=True)
class CanFrame:
    """One semantically valid CAN engine-speed frame."""

    source_line: int
    timestamp_ms: int
    can_id: str
    dlc: int
    data_bytes: tuple[int, ...]
    bus_state: str
    rpm: float


@dataclass
class ParseStatistics:
    """Counters that make parsing and normalisation results auditable."""

    data_lines: int = 0
    normalized_lines: int = 0
    rejected_lines: int = 0


def decode_engine_rpm(data_bytes: tuple[int, ...]) -> float:
    """Decode RPM from the first two bytes of a CAN engine-speed payload."""

    if len(data_bytes) < 2:
        raise ValueError("Для декодування RPM потрібні щонайменше два байти даних.")

    raw_speed = (data_bytes[0] << 8) | data_bytes[1]
    return raw_speed * RPM_SCALE


def build_frame(groups: dict[str, str], line_number: int) -> CanFrame:
    """Validate regex groups and convert them into a :class:`CanFrame`.

    The variant requires a standard 11-bit CAN identifier, a DLC from 1 to 8,
    exactly ``DLC`` hexadecimal bytes and a recognised bus state.  RPM adds the
    extra physical requirement of at least two payload bytes.
    """

    timestamp_ms = int(groups["timestamp_ms"])
    can_id_value = int(groups["can_id"], 16)
    dlc = int(groups["dlc"])
    data_bytes = tuple(int(byte, 16) for byte in groups["data_bytes"].split())
    bus_state = groups["bus_state"].upper()

    if can_id_value > 0x7FF:
        raise ValueError("CAN_ID має належати стандартному 11-бітному діапазону 000..7FF.")
    if not 1 <= dlc <= 8:
        raise ValueError("DLC має бути в діапазоні 1..8.")
    if len(data_bytes) != dlc:
        raise ValueError(
            f"DLC={dlc}, але в полі Data_Bytes передано {len(data_bytes)} байт(и)."
        )
    if bus_state not in ALLOWED_BUS_STATES:
        allowed = ", ".join(sorted(ALLOWED_BUS_STATES))
        raise ValueError(f"Bus_State має бути одним з: {allowed}.")

    return CanFrame(
        source_line=line_number,
        timestamp_ms=timestamp_ms,
        can_id=f"{can_id_value:03X}",
        dlc=dlc,
        data_bytes=data_bytes,
        bus_state=bus_state,
        rpm=decode_engine_rpm(data_bytes),
    )


def parse_can_log(file_path: Path) -> tuple[list[CanFrame], ParseStatistics]:
    """Read, normalise, parse and validate each non-comment CAN log line."""

    if not file_path.is_file():
        raise FileNotFoundError(f"Вхідний файл журналу не знайдено: {file_path}")

    frames: list[CanFrame] = []
    statistics = ParseStatistics()

    with file_path.open(encoding="utf-8") as input_file:
        for line_number, raw_line in enumerate(input_file, start=1):
            raw_without_newline = raw_line.rstrip("\r\n")
            normalized = sanitize_log_line(raw_line)

            if not normalized or normalized.startswith("#"):
                continue

            statistics.data_lines += 1
            if normalized != raw_without_newline:
                statistics.normalized_lines += 1

            match = CAN_FRAME_PATTERN.fullmatch(normalized)
            if match is None:
                statistics.rejected_lines += 1
                print(f"ПОМИЛКА РОЗБОРУ, рядок {line_number}: {normalized}")
                continue

            try:
                frames.append(build_frame(match.groupdict(), line_number))
            except ValueError as error:
                statistics.rejected_lines += 1
                print(f"ПОМИЛКА ВАЛІДАЦІЇ, рядок {line_number}: {error}")

    return frames, statistics


def format_bytes(data_bytes: tuple[int, ...]) -> str:
    """Return an uppercase hexadecimal array suitable for the report table."""

    return " ".join(f"{byte:02X}" for byte in data_bytes)


def print_report(frames: list[CanFrame], statistics: ParseStatistics) -> None:
    """Print a deterministic diagnostic table and aggregate RPM statistics."""

    separator = "=" * 119
    row_separator = "-" * 119
    print("\n" + separator)
    print(f"{'ЛБ5, ВАРІАНТ 15 — АНАЛІЗ АВТОМОБІЛЬНОЇ ШИНИ CAN-BUS':^119}")
    print(separator)
    print("Формула декодування датчика обертів: RPM = ((Data[0] << 8) | Data[1]) × 0.25")
    print(
        f"| {'Рядок':^6} | {'Час, мс':^10} | {'CAN ID':^8} | {'DLC':^5} | "
        f"{'Data_Bytes':^23} | {'Стан шини':^11} | {'RPM':^12} |"
    )
    print(row_separator)

    for frame in frames:
        print(
            f"| {frame.source_line:^6d} | {frame.timestamp_ms:^10d} | {frame.can_id:^8} | "
            f"{frame.dlc:^5d} | {format_bytes(frame.data_bytes):<23} | "
            f"{frame.bus_state:^11} | {frame.rpm:>10.2f} |"
        )

    print(separator)
    print("ПІДСУМКОВА СТАТИСТИКА")
    print(row_separator)
    print(f"  Рядків даних у файлі:                 {statistics.data_lines}")
    print(f"  Нормалізовано рядків:                 {statistics.normalized_lines}")
    print(f"  Коректно розібрано CAN-кадрів:        {len(frames)}")
    print(f"  Відхилено рядків (format/validation): {statistics.rejected_lines}")

    if frames:
        rpm_values = [frame.rpm for frame in frames]
        states = Counter(frame.bus_state for frame in frames)
        print(f"  Мінімальні оберти двигуна:            {min(rpm_values):.2f} RPM")
        print(f"  Максимальні оберти двигуна:           {max(rpm_values):.2f} RPM")
        print(f"  Середні оберти двигуна:               {sum(rpm_values) / len(rpm_values):.2f} RPM")
        print(
            "  Кадри за станом шини:                 "
            + ", ".join(f"{state}={states[state]}" for state in sorted(states))
        )
    else:
        print("  RPM-статистика недоступна: немає коректних кадрів.")
    print(separator)


def main() -> None:
    """Run the complete CAN-bus parsing pipeline for the supplied input file."""

    frames, statistics = parse_can_log(INPUT_FILE)
    print_report(frames, statistics)


if __name__ == "__main__":
    main()
