# Windows BLE connect implementation notes

Background/rationale for the Windows-specific connect logic in
[`tapsdk/_transport.py`](../tapsdk/_transport.py). These are "why", not "what"
notes - pulled out of inline comments to keep the source file focused on the
code itself. Each section is referenced from the corresponding spot in
`_transport.py` via a short pointer comment.

## Watchdog timing (`WINDOWS_CONNECT_ATTEMPT_WATCHDOG_SEC`)

The outer watchdog bounds the *entire* `connect_retrieved()` call (primary
bleak connect + WinRT fallback). It must be long enough for both the primary
attempt to fail/raise AND the fallback (manual `BluetoothLEDevice` +
`GattSession` + uncached service enumeration) to complete - that fallback is
often the only path that actually succeeds on Windows. The primary attempt
itself uses a much shorter internal timeout (see the "Primary connect timeout
vs. watchdog" section below) so it reliably raises and hands off to the
fallback well within this budget instead of being hard-cancelled mid-flight
(`asyncio.wait_for`'s cancellation raises `CancelledError`, which bypasses the
`except Exception` fallback handler entirely, silently skipping the
fallback).

## Closing BLE device handles in `get_connected_taps()`

`BluetoothLEDevice` holds a native handle until closed; if left open, repeated
polling (`windows_reconnect_poller` calls this every 3s) can accumulate leaked
handles to the same address and contend with a later real connect attempt via
`TapClient`, causing that connect to stall or fail with `"Device with address
... was not found."`

## Unbonded-connection warning (`_windows_warn_if_unbonded`)

An unbonded/unpaired GATT connection to this Tap's firmware exposes a reduced
(v1-looking) characteristic set - v2-only characteristics (e.g.
`c3ff0005`/`0006`/`000a`, NUS `6e400003`) are missing from discovery entirely,
not just inaccessible. This commonly happens when `connect_tap()` falls back
to a live BLE scan connect (no AEP-known bond) instead of attaching to an
already-paired device. Confirmed fix is manual pairing via Windows Settings,
not anything fixable from this code path, so this only logs a clear
diagnostic instead of a silent "protocol detected as v1" surprise.

## Forcing uncached services in `TapClient.__init__`

Windows caches the GATT service table per-address. A Tap that was previously
paired while running v1 firmware (or before a firmware update) can otherwise
report stale (v1-only) services, causing `detect_protocol()` to misidentify a
v2 device as v1.

## Primary connect timeout vs. watchdog

Keep the primary connect's internal timeout (8s) shorter than
`WINDOWS_CONNECT_ATTEMPT_WATCHDOG_SEC` so the primary attempt reliably
fails/raises on its own (letting the WinRT fallback run) instead of being
hard-cancelled by the outer watchdog, which would skip the fallback entirely.

## `already_connected` - skipping the doomed primary connect

`already_connected=True` means the caller already confirmed via AEP
(`get_tap_device()`) that this device is connected/bonded but not
advertising. bleak's primary `connect()` locates the device by scanning for
its advertisement first, which can never succeed here (it isn't advertising)
- it would only burn the full `timeout` before failing. Skip straight to the
WinRT fallback (manual `BluetoothLEDevice` + `GattSession` attach), which is
the path that actually works for this case, so the connect returns almost
instantly instead of after a wasted multi-second wait.

## Services-changed retry loop in the WinRT fallback

Requesting GATT services is what actually causes Windows to finish
establishing the encrypted link - the session isn't necessarily `ACTIVE` yet
when discovery starts. If Windows revises the service/characteristic table
mid-discovery (typically once pairing/encryption completes just after our
first snapshot), it fires a `GattServicesChanged` event - and bleak's own real
`connect()` (see `bleak/backends/winrt/client.py`) handles this with a
retry-on-services-changed loop instead of trusting a single `get_services()`
call. Without this, our manual fallback previously kept a stale/incomplete
characteristic list from the first (too-early) snapshot, which is what
produced the `"Characteristic ... was not found!"` / v1-misdetection symptom
even on an otherwise "successful" fallback connect.

This was investigated at length (see repo memory /
`docs`/session history for `tap-python-sdk`) - the missing-characteristics
symptom turned out to reproduce identically across several different fix
attempts and was ultimately tied to a leaked `GattSession` (see below), not
to this retry loop by itself. The retry loop is still correct/necessary
(it mirrors bleak's own tested behavior) but is not sufficient on its own.

## Leaked `GattSession` cleanup (`atexit`)

`maintain_connection=True` tells Windows to keep this GATT session alive
independent of our process. If the script is killed (e.g. Ctrl+C) without
ever calling `client.disconnect()`, that session is never closed and can leak
past process exit - the next run's fresh session negotiation then collides
with the orphaned one, which was observed to produce an incomplete
characteristic view on alternating runs. We register a defensive `atexit`
cleanup (closing the same `_session`/`_requester` attributes bleak's own
`disconnect()` closes) so an abrupt exit still releases the session. This is
a no-op if `disconnect()` already ran normally (attributes will already be
`None` by then).

Callers should still prefer an explicit, well-behaved shutdown over relying
on this safety net - e.g. `examples/connect.py` uses `sdk` as an async
context manager (`async with await connect() as sdk:`, which calls
`sdk.client.disconnect()` on exit via `__aexit__`) and catches
`KeyboardInterrupt` around `asyncio.run(main())`.

## Service cache mode on retry

A services-changed event means Windows just updated its own cache; re-read
the *service* list from that cache rather than forcing another live
`UNCACHED` query (matches bleak's own retry behavior). Characteristic/
descriptor discovery stays `UNCACHED` throughout, regardless of retries.

## Polling for `session_status == ACTIVE`

Give the session a short window to reach `ACTIVE` (mirrors bleak's own
post-discovery `await event.wait()`), but don't hard-fail if it doesn't -
`session_status` can lag behind the actual link state.

## `already_connected` derivation in `connect_tap()`

`already_connected=True` whenever the address came from `get_tap_device()`
(AEP already reports it connected, so it won't be advertising and the primary
bleak connect would just waste the full timeout before failing). An explicit
user-supplied address may not be connected yet, so it still gets a normal
primary connect attempt.

## Open issue: intermittent missing-characteristics / v1-misdetection

Despite the fixes documented above, this symptom (specific v2-only
characteristics missing from GATT discovery, protocol misdetected as v1) has
been observed to recur intermittently, including alternating pass/fail across
consecutive runs. Root cause is not fully confirmed. Leading theories, in the
order they were investigated and ruled out or left open:

1. Session not yet `ACTIVE` when discovery starts - addressed by the
   services-changed retry loop above; did not fully resolve the symptom on
   its own.
2. Leaked `GattSession` from a prior run killed without a clean disconnect -
   addressed by the `atexit` cleanup and the `examples/connect.py` shutdown
   fix above; not yet confirmed to fully resolve the symptom across many
   consecutive Ctrl+C-killed runs.
3. Insufficient negotiated encryption/authentication level for the current
   Windows bond (Windows silently omits characteristics requiring a security
   level the current link doesn't satisfy, rather than raising a
   per-characteristic error) - this remains the leading unresolved
   hypothesis if (1) and (2) don't fully fix it. The confirmed workaround for
   this case is to fully unpair the Tap in Windows Settings, manually
   re-pair via Settings > Bluetooth & devices > Add device (not via tapsdk),
   power-cycle the Tap, then rerun.

If this recurs, the next diagnostic step is enabling bleak's own debug logging
