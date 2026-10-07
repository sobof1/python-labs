"""Лабораторна робота № 7, варіант 15.

Менеджер пулу пам'яті: варіативна функція ``*args``, валідація блоків
пам'яті та багатокритеріальне lambda-сортування.
"""

from __future__ import annotations

import time
from typing import Any


def _is_plain_int(value: object) -> bool:
    """Повертає True лише для int, але не для логічного значення."""
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_options(options: dict[str, Any]) -> dict[str, int | None]:
    """Перевіряє опції пулу, отримані через ``**options``."""
    allowed_options = {"alignment", "pool_start", "pool_size"}
    unknown_options = sorted(set(options) - allowed_options)
    if unknown_options:
        raise ValueError(
            "Невідомі параметри пулу: " + ", ".join(unknown_options)
        )

    alignment = options.get("alignment", 16)
    pool_start = options.get("pool_start", 0)
    pool_size = options.get("pool_size")

    if not _is_plain_int(alignment) or alignment <= 0:
        raise ValueError("alignment має бути додатним цілим числом.")
    if alignment & (alignment - 1):
        raise ValueError("alignment має бути степенем двійки (наприклад, 8, 16 або 64).")
    if not _is_plain_int(pool_start) or pool_start < 0:
        raise ValueError("pool_start має бути невід'ємною цілою адресою.")
    if pool_size is not None and (not _is_plain_int(pool_size) or pool_size <= 0):
        raise ValueError("pool_size має бути додатним цілим числом або None.")

    return {
        "alignment": alignment,
        "pool_start": pool_start,
        "pool_size": pool_size,
    }


def _validate_raw_block(
    raw_block: object,
    source_index: int,
    settings: dict[str, int | None],
) -> tuple[dict[str, Any] | None, str | None]:
    """Перетворює один опис блока на запис або повертає причину відхилення."""
    if not isinstance(raw_block, tuple) or len(raw_block) != 3:
        return None, "очікується кортеж (address, size_bytes, owner)"

    address, size_bytes, owner = raw_block
    alignment = settings["alignment"]
    pool_start = settings["pool_start"]
    pool_size = settings["pool_size"]

    if not _is_plain_int(address) or address < 0:
        return None, "адреса має бути невід'ємним цілим числом"
    if not _is_plain_int(size_bytes) or size_bytes <= 0:
        return None, "розмір має бути додатним цілим числом у байтах"
    if not isinstance(owner, str) or not owner.strip():
        return None, "власник блока має бути непорожнім рядком"
    if address % alignment != 0:
        return None, f"адреса не вирівняна на {alignment} байт"
    if address < pool_start:
        return None, "адреса розташована до початку пулу"

    end_address = address + size_bytes
    if pool_size is not None and end_address > pool_start + pool_size:
        return None, "блок виходить за межі пулу пам'яті"

    return {
        "source_index": source_index,
        "address": address,
        "size_bytes": size_bytes,
        "end_address": end_address,
        "owner": owner.strip(),
    }, None


def manage_memory_pool(*raw_blocks: object, **options: Any) -> dict[str, Any]:
    """Валідує довільну кількість блоків пам'яті та повертає структурований звіт.

    Кожен позиційний аргумент ``raw_blocks`` має форму
    ``(address, size_bytes, owner)``. Опції ``alignment``, ``pool_start`` і
    ``pool_size`` приймаються через ``**options``; вони мають значення за
    замовчуванням 16, 0 та None відповідно.

    Блоки, що перетинаються, не додаються до пулу. Для однозначної перевірки
    адреси обробляються у зростаючому порядку, незалежно від порядку передачі
    через ``*args``.
    """
    settings = _validate_options(options)
    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for source_index, raw_block in enumerate(raw_blocks, start=1):
        block, reason = _validate_raw_block(raw_block, source_index, settings)
        if block is None:
            rejected.append(
                {
                    "source_index": source_index,
                    "raw_block": raw_block,
                    "reason": reason,
                }
            )
        else:
            candidates.append(block)

    accepted: list[dict[str, Any]] = []
    last_end_address: int | None = None
    last_owner: str | None = None
    for block in sorted(candidates, key=lambda item: (item["address"], item["source_index"])):
        if last_end_address is not None and block["address"] < last_end_address:
            rejected.append(
                {
                    "source_index": block["source_index"],
                    "raw_block": (
                        block["address"],
                        block["size_bytes"],
                        block["owner"],
                    ),
                    "reason": (
                        "перетинається з блоком "
                        f"{last_owner!r}, що завершується за адресою {last_end_address:#06x}"
                    ),
                }
            )
            continue

        accepted.append(block)
        last_end_address = block["end_address"]
        last_owner = block["owner"]

    accepted_by_input = sorted(accepted, key=lambda item: item["source_index"])
    blocks_by_size = sorted(
        accepted,
        key=lambda item: (-item["size_bytes"], item["address"]),
    )

    return {
        "settings": settings,
        "accepted_blocks": accepted_by_input,
        "blocks_by_size": blocks_by_size,
        "rejected_blocks": sorted(rejected, key=lambda item: item["source_index"]),
        "summary": {
            "received": len(raw_blocks),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "allocated_bytes": sum(block["size_bytes"] for block in accepted),
        },
    }


def _print_block_table(title: str, blocks: list[dict[str, Any]]) -> None:
    """Друкує таблицю прийнятих блоків у стабільному компактному форматі."""
    print(title)
    print("-" * 79)
    print(f"| {'№':^3} | {'Власник':<18} | {'Початок':^10} | {'Кінець':^10} | {'Розмір, B':>11} |")
    print("-" * 79)
    for number, block in enumerate(blocks, start=1):
        print(
            f"| {number:^3d} | {block['owner']:<18} | {block['address']:#010x} | "
            f"{block['end_address']:#010x} | {block['size_bytes']:>11d} |"
        )
    if not blocks:
        print("|                         Немає прийнятих блоків                         |")
    print("-" * 79)


def _print_rejected_blocks(rejected_blocks: list[dict[str, Any]]) -> None:
    """Друкує результати валідації, не приховуючи негативні сценарії."""
    print("ВІДХИЛЕНІ БЛОКИ (контроль валідації)")
    print("-" * 100)
    if not rejected_blocks:
        print("Відхилених блоків немає.")
    for record in rejected_blocks:
        print(f"#{record['source_index']}: {record['raw_block']!r}")
        print(f"    Причина: {record['reason']}")
    print("-" * 100)


def main() -> None:
    """Запускає відтворювану демонстрацію варіанта 15."""
    print("=" * 100)
    print(f"{'ЛБ7, ВАРІАНТ 15 — МЕНЕДЖЕР ПУЛУ ПАМ\'ЯТІ':^100}")
    print("=" * 100)

    # Дані містять коректні та навмисно некоректні записи. Це демонструє
    # валідацію варіативної функції у реальному запуску, а не окремий тест.
    memory_blocks = (
        (0x1000, 256, "bootloader"),
        (0x1100, 512, "framebuffer"),
        (0x1300, 512, "dma-buffer"),
        (0x1500, 128, "network"),
        (0x1280, 128, "overlap-check"),
        (0x1588, 64, "unaligned"),
        (0x1600, 0, "empty"),
        ("0x1700", 64, "wrong-address-type"),
        (0x1600, 64, "io-window"),
        (0x1FF0, 64, "outside-pool"),
    )
    pool_options = {
        "alignment": 16,
        "pool_start": 0x1000,
        "pool_size": 0x1000,
    }

    started_at = time.perf_counter()
    result = manage_memory_pool(*memory_blocks, **pool_options)
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    settings = result["settings"]
    summary = result["summary"]
    print("Виклик: manage_memory_pool(*memory_blocks, **pool_options)")
    print(
        "Параметри через **options: "
        f"alignment={settings['alignment']}, pool_start={settings['pool_start']:#06x}, "
        f"pool_size={settings['pool_size']} B"
    )
    print(
        f"Через *args передано: {summary['received']} блоків; "
        f"прийнято: {summary['accepted']}; відхилено: {summary['rejected']}."
    )
    print()

    _print_block_table("ПРИЙНЯТІ БЛОКИ У ПОРЯДКУ ПЕРЕДАЧІ", result["accepted_blocks"])
    print()
    _print_rejected_blocks(result["rejected_blocks"])
    print()
    _print_block_table(
        "LAMBDA-СОРТУВАННЯ: key=(-size_bytes, address)",
        result["blocks_by_size"],
    )

    sorted_correctly = result["blocks_by_size"] == sorted(
        result["accepted_blocks"],
        key=lambda item: (-item["size_bytes"], item["address"]),
    )
    print(f"Виділено пам'яті: {summary['allocated_bytes']} B")
    print(f"Контроль багатокритеріального lambda-сортування: {str(sorted_correctly).upper()}")
    print(f"Час виконання функціонального конвеєра: {elapsed_ms:.3f} мс")
    print("=" * 100)


if __name__ == "__main__":
    main()
