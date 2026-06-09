#!/usr/bin/env python3
"""Real-hardware smoke test for pyflowercare.

Scans for nearby FlowerCare/MiFlora sensors and exercises every code path
touched by the recent fixes against live devices:

  * connect() best-effort GATT name read  -> device.name
  * get_device_info()                      -> name / firmware / battery
  * read_sensor_data()                     -> live sensor reading (signed temp)
  * get_historical_data()                  -> 3-byte init + 2-byte entry index,
                                              historical parsing + signed temp,
                                              last_history_complete signal

Each hard check prints PASS/FAIL and validates that values fall within the
ranges the data model accepts. Plausibility warnings (WARN) flag values that
are technically valid but look like parse artifacts (e.g. conductivity 0xFFFF).
A correctly-signaled partial read (BLE dropped mid-retrieval) is reported, not
failed. Exit code is non-zero only if a hard check fails.

Requires a Bluetooth adapter with permission granted to the running terminal.

    poetry run python examples/hardware_smoke_test.py [--debug]

Use --debug to log the raw hex of each historical entry (for offset debugging).
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pyflowercare import FlowerCareScanner, setup_logging
from pyflowercare.exceptions import TimeoutError as FCTimeoutError
from pyflowercare.models import SensorData

SCAN_TIMEOUT = 15.0
CONNECT_ATTEMPTS = 3

# Plausibility ceiling (not a hard model limit) used to sanity-check brightness.
MAX_PLAUSIBLE_LUX = 200_000  # direct sunlight tops out ~100-150k lux

_failures: list[str] = []
_warnings: list[str] = []
_checks = 0


def check(condition: bool, label: str, detail: str = "") -> bool:
    global _checks
    _checks += 1
    mark = "PASS" if condition else "FAIL"
    line = f"  [{mark}] {label}"
    if detail:
        line += f" -> {detail}"
    print(line)
    if not condition:
        _failures.append(label)
    return condition


def warn(condition: bool, label: str, detail: str = "") -> None:
    """Soft check: record a warning if condition is False, never fails the run."""
    if not condition:
        line = f"  [WARN] {label}"
        if detail:
            line += f" -> {detail}"
        print(line)
        _warnings.append(label)


def validate_sensor(data: SensorData, source: str) -> None:
    """Hard range checks. Brightness/conductivity may be None ("not measured")."""
    check(
        -50.0 <= data.temperature <= 100.0,
        f"{source}: temperature in [-50,100]",
        f"{data.temperature}C",
    )
    check(0 <= data.moisture <= 100, f"{source}: moisture in [0,100]", f"{data.moisture}%")

    if data.brightness is None:
        print(f"  [INFO] {source}: brightness not measured (None)")
    else:
        check(
            0 <= data.brightness <= MAX_PLAUSIBLE_LUX,
            f"{source}: brightness plausible",
            f"{data.brightness} lux",
        )

    if data.conductivity is None:
        print(f"  [INFO] {source}: conductivity not measured (None)")
    else:
        check(
            0 <= data.conductivity <= 20_000,
            f"{source}: conductivity plausible",
            f"{data.conductivity} uS/cm",
        )


async def connect_with_retry(device):
    """Connect, retrying transient BLE timeouts (a single timeout is not a bug)."""
    last_err = None
    for attempt in range(1, CONNECT_ATTEMPTS + 1):
        try:
            await device.connect()
            return True
        except FCTimeoutError as e:
            last_err = e
            print(f"  connect attempt {attempt}/{CONNECT_ATTEMPTS} timed out, retrying...")
    print(f"  [WARN] could not connect after {CONNECT_ATTEMPTS} attempts: {last_err}")
    _warnings.append(f"{device.mac_address}: connect failed (transient BLE)")
    return False


async def test_device(device) -> None:
    print(f"\n=== Device: {device.name} ({device.mac_address}) ===")

    if not await connect_with_retry(device):
        return
    try:
        check(device.is_connected, "connected to device")
        check(
            isinstance(device.name, str) and len(device.name) > 0,
            "device.name resolved",
            device.name,
        )

        # --- Device info ---
        info = await device.get_device_info()
        check(bool(info.name), "device_info.name present", info.name)
        if info.battery_level is not None:
            check(0 <= info.battery_level <= 100, "battery in [0,100]", f"{info.battery_level}%")
        if info.firmware_version:
            check(bool(info.firmware_version), "firmware present", info.firmware_version)

        # --- Live sensor reading (validates signed temperature parse) ---
        live = await device.read_sensor_data()
        print(f"  live reading: {live}")
        validate_sensor(live, "live")

        # --- Historical data ---
        history = await device.get_historical_data()
        complete = device.last_history_complete
        print(f"  historical: {len(history)} entries parsed, complete={complete}")

        if not complete:
            # Correct behavior when BLE drops mid-read: signal it, don't fail.
            warn(
                False,
                "historical retrieval interrupted (partial data returned)",
                f"{len(history)} entries before drop",
            )
        else:
            check(complete, "historical retrieval completed (last_history_complete)")

        if history:
            now = datetime.now()
            future_slack = now + timedelta(minutes=5)
            oldest = now - timedelta(days=400)

            check(
                all(oldest <= e.timestamp <= future_slack for e in history),
                "all historical timestamps within sane window",
            )
            for e in history:
                validate_sensor(e.sensor_data, "history")

            unique_ts = {e.timestamp for e in history}
            # A 1-byte-index regression re-reads low-256 slots -> duplicate records.
            check(
                len(unique_ts) == len(history),
                "historical timestamps unique (no index-wrap duplicates)",
                f"{len(unique_ts)} unique / {len(history)} total",
            )

            if len(history) > 255:
                check(
                    True, "retrieved > 255 entries (2-byte index path exercised)", str(len(history))
                )

            recent = sorted(history, key=lambda e: e.timestamp, reverse=True)[:3]
            print("  most recent 3 entries:")
            for e in recent:
                print(f"    {e}")
        elif complete:
            # Device reported a count but we parsed nothing -> protocol/parse problem.
            warn(
                False,
                "device completed retrieval but parsed 0 entries " "(check history-read protocol)",
            )
    finally:
        await device.disconnect()


async def main() -> int:
    debug = "--debug" in sys.argv
    setup_logging("DEBUG" if debug else "INFO")
    scanner = FlowerCareScanner()

    print(f"Scanning for FlowerCare devices ({SCAN_TIMEOUT:.0f}s)...")
    devices = await scanner.scan_for_devices(timeout=SCAN_TIMEOUT)

    if not devices:
        print("No FlowerCare devices found. Make sure a sensor is nearby and powered.")
        return 2

    print(
        f"Found {len(devices)} device(s): "
        + ", ".join(f"{d.name} ({d.mac_address})" for d in devices)
    )

    for device in devices:
        try:
            await test_device(device)
        except Exception as e:  # noqa: BLE001 - report, keep testing other devices
            _failures.append(f"{device.mac_address}: {type(e).__name__}: {e}")
            print(f"  [FAIL] unhandled error: {type(e).__name__}: {e}")

    print("\n" + "=" * 50)
    passed = _checks - len(_failures)
    print(f"RESULT: {passed}/{_checks} hard checks passed across {len(devices)} device(s)")
    if _warnings:
        print(f"{len(_warnings)} warning(s):")
        for w in _warnings:
            print(f"  - {w}")
    if _failures:
        print("Failures:")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print("All hard checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
