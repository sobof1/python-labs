"""Laboratory work 6, variant 15: mail-relay inventory using dictionaries.

The nested registry implements the required mapping
``Relay_IP -> {Domain, SPF_Records_Set, DKIM_Status}``.  Its data is kept
deterministic so the console report is suitable for a repeatable lab run.
"""

from __future__ import annotations

from textwrap import wrap


def create_initial_relay_database() -> dict[str, dict[str, object]]:
    """Return the initial nested dictionary of mail relays and SPF policies."""

    return {
        "192.0.2.10": {
            "domain": "mx-east.example",
            "spf_records": {"v=spf1", "ip4:192.0.2.10", "ip4:192.0.2.11", "-all"},
            "dkim_status": "PASS",
        },
        "192.0.2.20": {
            "domain": "partner-relay.example",
            "spf_records": {"v=spf1", "ip4:192.0.2.20", "include:partner.example", "-all"},
            "dkim_status": "FAIL",
        },
        "198.51.100.44": {
            "domain": "outbound.example",
            "spf_records": {
                "v=spf1",
                "ip4:198.51.100.44",
                "ip4:198.51.100.45",
                "-all",
            },
            "dkim_status": "PASS",
        },
    }


def add_or_update_relay(
    relay_database: dict[str, dict[str, object]],
    relay_ip: str,
    relay_info: dict[str, object],
) -> str:
    """Create a relay or update its fields through :meth:`dict.update`."""

    if relay_ip in relay_database:
        relay_database[relay_ip].update(relay_info)
        return "UPDATE"

    relay_database[relay_ip] = relay_info
    return "CREATE"


def decommission_relay(
    relay_database: dict[str, dict[str, object]], relay_ip: str
) -> dict[str, object] | None:
    """Safely remove a temporary or retired relay with :meth:`dict.pop`."""

    return relay_database.pop(relay_ip, None)


def get_relay_domain(relay_database: dict[str, dict[str, object]], relay_ip: str) -> str:
    """Look up a domain safely with :meth:`dict.get` without risking ``KeyError``."""

    relay = relay_database.get(relay_ip)
    if relay is None:
        return "<реле не знайдено>"
    return str(relay.get("domain", "<домен не задано>"))


def add_spf_mechanism(
    relay_database: dict[str, dict[str, object]], relay_ip: str, mechanism: str
) -> None:
    """Add an SPF mechanism using ``setdefault`` for the nested set field."""

    relay = relay_database.get(relay_ip)
    if relay is None:
        raise KeyError(f"Неможливо доповнити SPF: реле {relay_ip} не існує.")

    spf_records = relay.setdefault("spf_records", set())
    if not isinstance(spf_records, set):
        raise TypeError("Поле spf_records має бути множиною.")
    spf_records.add(mechanism)


def build_spf_inverted_index(
    relay_database: dict[str, dict[str, object]],
) -> dict[str, list[str]]:
    """Build ``SPF mechanism -> relay domains`` with a Dict Comprehension."""

    all_mechanisms = {
        mechanism
        for relay in relay_database.values()
        for mechanism in relay.get("spf_records", set())
        if isinstance(mechanism, str)
    }

    return {
        mechanism: sorted(
            str(relay.get("domain", "<домен не задано>"))
            for relay in relay_database.values()
            if mechanism in relay.get("spf_records", set())
        )
        for mechanism in sorted(all_mechanisms)
    }


def format_spf_records(relay: dict[str, object]) -> str:
    """Format the stored SPF set in a stable order for a console report."""

    records = relay.get("spf_records", set())
    if not isinstance(records, set):
        return "<помилковий тип SPF>"
    return ", ".join(sorted(str(record) for record in records))


def print_inventory_report(
    relay_database: dict[str, dict[str, object]], inverted_index: dict[str, list[str]]
) -> None:
    """Print the nested-dictionary inventory and its SPF inverted index."""

    separator = "=" * 119
    row_separator = "-" * 119
    print(separator)
    print(f"{'ЛБ6, ВАРІАНТ 15 — РЕЄСТР ПОШТОВИХ РЕЛЕЇВ ТА SPF':^119}")
    print(separator)
    print(f"| {'Relay_IP':<15} | {'Domain':<25} | {'DKIM':^6} | {'SPF_Records_Set':<60} |")
    print(row_separator)

    for relay_ip, relay in sorted(relay_database.items()):
        spf_lines = wrap(
            format_spf_records(relay), width=60, break_long_words=False, break_on_hyphens=False
        ) or [""]
        print(f"| {relay_ip:<15} | {str(relay.get('domain', '')):<25} | " f"{str(relay.get('dkim_status', 'UNKNOWN')):^6} | {spf_lines[0]:<60} |")
        for spf_line in spf_lines[1:]:
            print(f"| {'':15} | {'':25} | {'':6} | {spf_line:<60} |")

    print(separator)
    print("ІНВЕРТОВАНИЙ ІНДЕКС (SPF-механізм → домени релеїв), Dict Comprehension")
    print(row_separator)
    for mechanism, domains in inverted_index.items():
        print(f"  {mechanism:<28} -> {', '.join(domains)}")
    print(separator)


def main() -> None:
    """Demonstrate CRUD, safe access and a Dict Comprehension on the registry."""

    relay_database = create_initial_relay_database()

    create_action = add_or_update_relay(
        relay_database,
        "192.0.2.11",
        {
            "domain": "mx-west.example",
            "spf_records": {"v=spf1", "ip4:192.0.2.10", "ip4:192.0.2.11", "-all"},
            "dkim_status": "PASS",
        },
    )
    update_action = add_or_update_relay(
        relay_database, "192.0.2.10", {"dkim_status": "PASS"}
    )
    add_or_update_relay(
        relay_database,
        "203.0.113.250",
        {
            "domain": "retired-test-relay.example",
            "spf_records": {"v=spf1", "ip4:203.0.113.250", "-all"},
            "dkim_status": "UNKNOWN",
        },
    )
    removed_relay = decommission_relay(relay_database, "203.0.113.250")
    add_spf_mechanism(relay_database, "198.51.100.44", "include:spf.backup.example")

    print("CRUD та безпечний доступ:")
    print(f"  {create_action}: додано реле 192.0.2.11.")
    print(f"  {update_action}: підтверджено статус DKIM реле 192.0.2.10.")
    print(
        "  DELETE: "
        + ("тимчасове реле 203.0.113.250 вилучено через pop()." if removed_relay else "не виконано.")
    )
    print(
        "  get(): домен для 192.0.2.10 = "
        f"{get_relay_domain(relay_database, '192.0.2.10')}; "
        f"для 203.0.113.1 = {get_relay_domain(relay_database, '203.0.113.1')}"
    )
    print("  setdefault(): до SPF 198.51.100.44 додано include:spf.backup.example.")
    print()

    inverted_index = build_spf_inverted_index(relay_database)
    print_inventory_report(relay_database, inverted_index)


if __name__ == "__main__":
    main()
