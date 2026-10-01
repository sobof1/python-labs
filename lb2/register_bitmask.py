"""Лабораторна робота № 2: 16-бітний регістр варіанта 15."""

SLEEP_MODE_SHIFT = 15
SLEEP_MODE_MASK = 0x1
WAKEUP_SOURCE_SHIFT = 9
WAKEUP_SOURCE_MASK = 0x3F
BATTERY_LEVEL_SHIFT = 3
BATTERY_LEVEL_MASK = 0x3F
SYSTEM_STATE_SHIFT = 0
SYSTEM_STATE_MASK = 0x7
REGISTER_MASK = 0xFFFF


def pack_power_register(sleep_mode: bool, wakeup_source: int, battery_level: int, system_state: int) -> int:
    """Упаковує параметри керування живленням у 16-бітне машинне слово."""
    if not 0 <= wakeup_source <= WAKEUP_SOURCE_MASK:
        raise ValueError("WAKEUP_SOURCE має належати діапазону 0..63.")
    if not 0 <= battery_level <= BATTERY_LEVEL_MASK:
        raise ValueError("BATTERY_LVL має належати діапазону 0..63.")
    if not 0 <= system_state <= SYSTEM_STATE_MASK:
        raise ValueError("SYS_ST має належати діапазону 0..7.")

    return (
        (int(sleep_mode) << SLEEP_MODE_SHIFT)
        | (wakeup_source << WAKEUP_SOURCE_SHIFT)
        | (battery_level << BATTERY_LEVEL_SHIFT)
        | (system_state << SYSTEM_STATE_SHIFT)
    )


def unpack_power_register(register_value: int) -> dict[str, int | bool]:
    """Виділяє поля регістра зсувами праворуч і масками побітового І."""
    register_value &= REGISTER_MASK
    return {
        "sleep_mode": bool((register_value >> SLEEP_MODE_SHIFT) & SLEEP_MODE_MASK),
        "wakeup_source": (register_value >> WAKEUP_SOURCE_SHIFT) & WAKEUP_SOURCE_MASK,
        "battery_level": (register_value >> BATTERY_LEVEL_SHIFT) & BATTERY_LEVEL_MASK,
        "system_state": (register_value >> SYSTEM_STATE_SHIFT) & SYSTEM_STATE_MASK,
    }


def set_sleep_mode(register_value: int) -> int:
    """Встановлює біт SLEEP_MODE операцією побітового АБО."""
    return (register_value | (1 << SLEEP_MODE_SHIFT)) & REGISTER_MASK


def clear_sleep_mode(register_value: int) -> int:
    """Скидає біт SLEEP_MODE операціями побітового І та НЕ."""
    return register_value & ~(1 << SLEEP_MODE_SHIFT) & REGISTER_MASK


def toggle_sleep_mode(register_value: int) -> int:
    """Інвертує біт SLEEP_MODE операцією виключного АБО."""
    return (register_value ^ (1 << SLEEP_MODE_SHIFT)) & REGISTER_MASK


def main() -> None:
    """Демонструє упакування, розпакування та модифікацію регістра."""
    sleep_mode = False
    wakeup_source = 17
    battery_level = 45
    system_state = 5
    register_value = pack_power_register(sleep_mode, wakeup_source, battery_level, system_state)
    unpacked = unpack_power_register(register_value)

    print("=" * 80)
    print(f"{'РЕЄСТР КЕРУВАННЯ ЕНЕРГОСПОЖИВАННЯМ ВАРІАНТУ 15':^80}")
    print("=" * 80)
    print(f"Початкові поля: SLEEP={sleep_mode}, WAKEUP={wakeup_source}, BATTERY={battery_level}, SYS_ST={system_state}")
    print(f"DEC: {register_value:d}")
    print(f"HEX: 0x{register_value:04X}")
    print(f"BIN: 0b{register_value:016b}")
    print(f"OCT: 0o{register_value:06o}")
    print("-" * 80)
    print("Розпаковані поля:")
    print(f"SLEEP_MODE    = {unpacked['sleep_mode']}")
    print(f"WAKEUP_SOURCE = {unpacked['wakeup_source']}")
    print(f"BATTERY_LVL   = {unpacked['battery_level']}")
    print(f"SYS_ST        = {unpacked['system_state']}")
    print("-" * 80)
    after_set = set_sleep_mode(register_value)
    after_clear = clear_sleep_mode(after_set)
    after_toggle = toggle_sleep_mode(after_clear)
    print(f"SET SLEEP_MODE:    0x{after_set:04X} | {after_set:016b}")
    print(f"CLEAR SLEEP_MODE:  0x{after_clear:04X} | {after_clear:016b}")
    print(f"TOGGLE SLEEP_MODE: 0x{after_toggle:04X} | {after_toggle:016b}")
    print("=" * 80)


if __name__ == "__main__":
    main()
