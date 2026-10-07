"""CLI-точка входу аудитора символьних посилань (ЛБ8, варіант 15)."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Sequence

from fs_toolkit import print_symlink_audit_report, scan_symbolic_links


class CLIArgumentError(ValueError):
    """Помилка ручного розбору параметрів ``sys.argv``."""


def print_usage_help() -> None:
    """Виводить довідку без використання argparse чи сторонніх бібліотек."""
    print(
        """
ВИКОРИСТАННЯ:
    python cli_main.py --path <каталог> [--broken-only]

ПАРАМЕТРИ:
    --path <каталог>  Обов'язковий шлях до каталогу, який треба перевірити.
    --broken-only     Показувати лише биті символьні посилання.
    --help, -h        Показати цю довідку та завершитися з кодом 0.

ПРИКЛАДИ:
    python cli_main.py --path ./test_sandbox
    python cli_main.py --path ./test_sandbox --broken-only
""".strip()
    )


def parse_cli_arguments(arguments: Sequence[str]) -> dict[str, object]:
    """Вручну розбирає параметри після ``sys.argv[0]`` і повертає конфігурацію."""
    if not arguments or "--help" in arguments or "-h" in arguments:
        return {"show_help": True, "path": None, "broken_only": False}

    config: dict[str, object] = {
        "show_help": False,
        "path": None,
        "broken_only": False,
    }
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--path":
            if index + 1 >= len(arguments):
                raise CLIArgumentError("Після '--path' необхідно вказати каталог.")
            if config["path"] is not None:
                raise CLIArgumentError("Параметр '--path' не можна вказувати двічі.")
            config["path"] = Path(arguments[index + 1]).expanduser().resolve(strict=False)
            index += 2
        elif argument == "--broken-only":
            if config["broken_only"] is True:
                raise CLIArgumentError("Прапорець '--broken-only' не можна вказувати двічі.")
            config["broken_only"] = True
            index += 1
        else:
            raise CLIArgumentError(f"Невідомий параметр: {argument!r}.")

    if config["path"] is None:
        raise CLIArgumentError("Обов'язковий параметр '--path' не вказано.")
    return config


def main(arguments: Sequence[str] | None = None) -> int:
    """Запускає аудит та повертає код, який передається в ``sys.exit``."""
    raw_arguments = list(sys.argv[1:] if arguments is None else arguments)
    try:
        config = parse_cli_arguments(raw_arguments)
    except CLIArgumentError as error:
        print(f"Помилка синтаксису CLI: {error}", file=sys.stderr)
        print_usage_help()
        return 2

    if config["show_help"]:
        print_usage_help()
        return 0

    target_path = config["path"]
    broken_only = config["broken_only"]
    assert isinstance(target_path, Path)
    assert isinstance(broken_only, bool)

    started_at = time.perf_counter()
    try:
        result = scan_symbolic_links(target_path, broken_only=broken_only)
    except ValueError as error:
        print(f"Помилка параметра --path: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Системна помилка під час сканування: {error}", file=sys.stderr)
        return 3

    print_symlink_audit_report(result, target_path, broken_only)
    elapsed_ms = (time.perf_counter() - started_at) * 1000
    print(f"Аудит успішно завершено за {elapsed_ms:.3f} мс. Код завершення: 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
