"""Форматування консольного звіту аудиту символьних посилань."""

from __future__ import annotations

from pathlib import Path

from .scanner import SymlinkScanResult


def _shorten(value: str, width: int) -> str:
    """Скорочує рядок для таблиці, не приховуючи його закінчення."""
    return value if len(value) <= width else f"…{value[-(width - 1):]}"


def print_symlink_audit_report(
    scan_result: SymlinkScanResult,
    search_root: Path,
    broken_only: bool,
) -> None:
    """Друкує таблицю та підсумки аудиту символьних посилань."""
    line = "=" * 118
    separator = "-" * 118
    filter_label = "лише биті посилання" if broken_only else "усі символьні посилання"

    print()
    print(line)
    print(f"{'ЛБ8, ВАРІАНТ 15 — АУДИТ СИМВОЛЬНИХ ПОСИЛАНЬ':^118}")
    print(line)
    print(f"Каталог сканування: {search_root}")
    print(f"Режим фільтрації: {filter_label}")
    print(separator)
    print(
        f"| {'№':^3} | {'Відносний шлях посилання':<32} | {'Ціль, записана у посиланні':<36} | "
        f"{'Стан':^10} | {'Права':^7} | {'B':>6} |"
    )
    print(separator)

    if scan_result.records:
        for number, record in enumerate(scan_result.records, start=1):
            status = "BROKEN" if record.is_broken else "OK"
            print(
                f"| {number:^3d} | {_shorten(str(record.relative_path), 32):<32} | "
                f"{_shorten(record.raw_target, 36):<36} | {status:^10} | "
                f"{record.permissions:^7} | {record.link_size_bytes:>6d} |"
            )
    else:
        print("|" + " Немає символьних посилань, що відповідають активному фільтру. ".center(116) + "|")
    print(separator)

    if scan_result.records:
        print("Розв'язані цільові шляхи:")
        for record in scan_result.records:
            status = "BROKEN" if record.is_broken else "OK"
            print(f"  [{status}] {record.relative_path} -> {record.resolved_target}")
            print(f"           метадані посилання: modified={record.modified_at}, mode={record.permissions}")

    print(separator)
    print(f"Усього символьних посилань знайдено: {scan_result.total_symlinks}")
    print(f"Із них битих:                        {scan_result.total_broken}")
    print(f"Відображено за поточним фільтром:     {len(scan_result.records)}")
    if scan_result.warnings:
        print(f"Системні попередження:                {len(scan_result.warnings)}")
        for warning in scan_result.warnings:
            print(f"  Попередження: {warning}")
    print(line)
