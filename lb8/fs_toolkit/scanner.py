"""Бізнес-логіка аудиту символьних посилань для ЛБ8, варіант 15.

Для обходу дерева та отримання метаданих використовується тільки ``pathlib.Path``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SymlinkRecord:
    """Структуровані відомості про один символьний зв'язок."""

    link_path: Path
    relative_path: Path
    raw_target: str
    resolved_target: Path
    is_broken: bool
    link_size_bytes: int
    modified_at: str
    permissions: str


@dataclass(frozen=True)
class SymlinkScanResult:
    """Результат сканування разом із підсумками і безпечними попередженнями."""

    records: tuple[SymlinkRecord, ...]
    total_symlinks: int
    total_broken: int
    warnings: tuple[str, ...]


def _resolve_link_target(link_path: Path, raw_target: Path) -> Path:
    """Повертає абсолютний нормалізований шлях цілі без вимоги її існування."""
    candidate = raw_target if raw_target.is_absolute() else link_path.parent / raw_target
    return candidate.resolve(strict=False)


def scan_symbolic_links(base_path: Path, broken_only: bool = False) -> SymlinkScanResult:
    """Рекурсивно знаходить символьні посилання в ``base_path``.

    Якщо ``broken_only`` істинне, до ``records`` потрапляють лише посилання,
    для яких ``Path.exists()`` повертає ``False``. У підсумках при цьому все
    одно зберігається загальна кількість знайдених і битих посилань.
    """
    if not base_path.exists():
        raise ValueError(f"Шлях '{base_path}' не існує.")
    if not base_path.is_dir():
        raise ValueError(f"Шлях '{base_path}' не є каталогом.")

    records: list[SymlinkRecord] = []
    warnings: list[str] = []
    total_symlinks = 0
    total_broken = 0

    try:
        tree_items = sorted(base_path.rglob("*"), key=lambda item: str(item))
    except OSError as error:
        raise OSError(f"Не вдалося обійти каталог '{base_path}': {error}") from error

    for item in tree_items:
        try:
            # На відміну від is_file(), is_symlink() не губить биті посилання.
            if not item.is_symlink():
                continue

            total_symlinks += 1
            raw_target_path = item.readlink()
            is_broken = not item.exists()
            if is_broken:
                total_broken += 1

            stat_result = item.lstat()
            record = SymlinkRecord(
                link_path=item,
                relative_path=item.relative_to(base_path),
                raw_target=str(raw_target_path),
                resolved_target=_resolve_link_target(item, raw_target_path),
                is_broken=is_broken,
                link_size_bytes=stat_result.st_size,
                modified_at=time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(stat_result.st_mtime)
                ),
                permissions=oct(stat_result.st_mode & 0o777),
            )
            if not broken_only or record.is_broken:
                records.append(record)
        except (OSError, ValueError) as error:
            warnings.append(f"Не вдалося перевірити '{item}': {error}")

    return SymlinkScanResult(
        records=tuple(records),
        total_symlinks=total_symlinks,
        total_broken=total_broken,
        warnings=tuple(warnings),
    )
