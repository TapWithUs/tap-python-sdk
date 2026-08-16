# Send haptic (vibration) sequences

```python
await sdk.send_vibration_sequence([1000, 300, 200])
# same as await sdk.set_haptic_pattern([...])
```

Periods are in milliseconds, clamped to **0–2550** in **10 ms** steps. Values are stored as `period // 10` on the wire (framed write on `c3ff000f`).

The list alternates **on** and **off** durations. The example above vibrates for 1 s, pauses 300 ms, then vibrates 200 ms.

## Limits

- At most **18** period values (up to 9 on/off pairs). Longer lists are truncated.
- Requires an active BLE connection (`await sdk.start()` or `await sdk.run()` first).

## Example pattern

```python
# short buzz, pause, short buzz, pause, long buzz
await sdk.send_vibration_sequence([100, 200, 100, 200, 500])
```

Runnable samples: [`examples/connect.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/connect.py), [`examples/v2.py`](https://github.com/TapWithUs/tap-python-sdk/blob/v2/examples/v2.py).
