"""Laboratory work 6, variant 15: SPF/MX sender audit and spam frequency.

The module compares observed sender addresses with a deterministic allow-list
derived from MX/SPF policy, then ranks rejected senders using
``collections.Counter``.
"""

from __future__ import annotations

from collections import Counter


# Sender addresses allowed by the configured MX/SPF policy.
AUTHORIZED_MX_SPF_IPS: frozenset[str] = frozenset(
    {"192.0.2.10", "192.0.2.11", "198.51.100.44", "198.51.100.45"}
)


def audit_sender_addresses(
    observed_ips: set[str], authorized_ips: frozenset[str]
) -> dict[str, set[str] | float]:
    """Compare actual senders ``A`` with MX/SPF policy ``B`` using sets."""

    compliant = observed_ips.intersection(authorized_ips)
    unauthorized = observed_ips.difference(authorized_ips)
    missing_expected = authorized_ips.difference(observed_ips)
    union = observed_ips.union(authorized_ips)
    jaccard_similarity = len(compliant) / len(union) if union else 1.0

    return {
        "compliant": compliant,
        "unauthorized": unauthorized,
        "missing_expected": missing_expected,
        "jaccard_similarity": jaccard_similarity,
    }


def count_spam_attacks(blocked_sender_events: list[str]) -> Counter[str]:
    """Return a frequency map of rejected sender IPs via ``Counter``."""

    return Counter(blocked_sender_events)


def print_audit_report(
    received_sender_events: list[str], audit: dict[str, set[str] | float]
) -> None:
    """Print the set audit and Counter ranking in a deterministic form."""

    observed_ips = set(received_sender_events)
    blocked_events = [ip for ip in received_sender_events if ip not in AUTHORIZED_MX_SPF_IPS]
    frequency = count_spam_attacks(blocked_events)
    jaccard_similarity = audit["jaccard_similarity"]

    if not isinstance(jaccard_similarity, float):
        raise TypeError("Індекс Жаккара має бути дійсним числом.")

    separator = "=" * 104
    row_separator = "-" * 104
    print(separator)
    print(f"{'ЛБ6, ВАРІАНТ 15 — АУДИТ MX/SPF ТА ЧАСТОТНИЙ АНАЛІЗ SPAM':^104}")
    print(separator)
    print(f"  Нормативний список MX/SPF (B): {sorted(AUTHORIZED_MX_SPF_IPS)}")
    print(f"  Унікальні фактичні відправники (A): {sorted(observed_ips)}")
    print(row_separator)
    print("РЕЗУЛЬТАТИ ТЕОРЕТИКО-МНОЖИННОГО АУДИТУ")
    print(f"  Дозволені адреси (A ∩ B):             {sorted(audit['compliant'])}")
    print(f"  Недозволені адреси (A \\ B):           {sorted(audit['unauthorized'])}")
    print(f"  Очікувані, але не побачені (B \\ A):   {sorted(audit['missing_expected'])}")
    print(
        "  Індекс Жаккара |A ∩ B| / |A ∪ B|: "
        f"{jaccard_similarity:.4f} ({jaccard_similarity * 100:.2f}%)"
    )
    print(row_separator)
    print("COUNTER: TOP ДЖЕРЕЛ ВІДХИЛЕНИХ SPAM-ПОВІДОМЛЕНЬ")
    print(f"| {'Ранг':^6} | {'IP відправника':^25} | {'Відхилено повідомлень':^28} | {'Частка':^18} |")
    print(row_separator)

    total_blocked = len(blocked_events)
    for rank, (sender_ip, count) in enumerate(frequency.most_common(3), start=1):
        share = (count / total_blocked) * 100 if total_blocked else 0.0
        share_text = f"{share:.2f}%"
        print(f"| {rank:^6d} | {sender_ip:^25} | {count:^28d} | {share_text:^18} |")

    print(separator)
    print(f"  Усього подій доставки: {len(received_sender_events)}")
    print(f"  Відхилено як spam:     {total_blocked}")
    print(separator)


def main() -> None:
    """Run the sender-policy comparison and rank all rejected senders."""

    received_sender_events = [
        "192.0.2.10",
        "192.0.2.10",
        "192.0.2.11",
        "198.51.100.44",
        "203.0.113.77",
        "203.0.113.77",
        "203.0.113.77",
        "203.0.113.77",
        "203.0.113.77",
        "198.51.100.250",
        "198.51.100.250",
        "198.51.100.250",
        "203.0.113.88",
        "203.0.113.88",
    ]
    audit = audit_sender_addresses(set(received_sender_events), AUTHORIZED_MX_SPF_IPS)
    print_audit_report(received_sender_events, audit)


if __name__ == "__main__":
    main()
