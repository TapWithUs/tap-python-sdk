# Send haptic (vibration) sequences

```python
await tap.send_vibration_sequence([1000, 300, 200])
```

Periods are in milliseconds, clamped to **10–2550** in **10 ms** steps. Values are stored as `period // 10` on the wire.

The list alternates **on** and **off** durations. The example above vibrates for 1 s, pauses 300 ms, then vibrates 200 ms.

## Limits

- At most **18** period values (up to 9 on/off pairs). Longer lists are truncated.
- Requires an active BLE connection (`await tap.run()` first).

## Example pattern

```python
# short buzz, pause, short buzz, pause, long buzz
await tap.send_vibration_sequence([100, 200, 100, 200, 500])
```
