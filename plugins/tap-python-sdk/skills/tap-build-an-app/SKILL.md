---
name: tap-build-an-app
description: Build a complete app or interactive experience controlled by a Tap - games, browser pages, presentations, media control, keyboard shortcuts, or creative tools. Use when the user asks to "build", "make", or "create" something with their Tap, especially if they are not a developer.
---

# Build an app with a Tap

The user may not be a developer. Keep the project small, explain how to run it in plain words, and test with the real device.

## Workflow

1. **Ask** (only what is missing): device (Tap Strap / Tap Strap 2 / TapXR / TapBand), OS, and what the app should do.
2. **Connect first.** Run the `tap-getting-started` quickstart and confirm taps arrive before building anything else.
3. **Pick the input** (load the matching skill):
   - finger taps and combos: `tap-tapping`
   - swipes, pinches, fist: `tap-vision-models` (v2)
   - pointer, tilt, rotation: `tap-imu-motion`
   - twist-to-adjust value: `tap-knob` (v2)
   - directions + select + drag/rotate: `tap-dpad` (v2)
   - data recording: `tap-raw-sensors`
4. **Pick the output** (pattern below).
5. **Build one interaction, test it with the user, then add the next.**
6. **Give feedback**: haptics (`send_vibration_sequence`) and on-screen state, so the user knows the gesture was seen.
7. **Deliver**: one folder, a `requirements.txt`, and one run command (`python app.py`).

## Core pattern: callbacks to a queue

SDK callbacks run on the Bluetooth path. Do not draw UI or do slow work in them. Put events on an `asyncio.Queue` and handle them in your own loop:

```python
import asyncio
from tapsdk import InputModeController, TapSDK2, connect

def first(v):
    return v[0] if isinstance(v, (list, tuple)) else v

async def main():
    events = asyncio.Queue()
    sdk = await connect()
    sdk.register_tap_events(lambda i, t: events.put_nowait(("tap", first(t))))
    sdk.register_air_gesture_events(lambda i, g: events.put_nowait(("air", first(g))))
    await sdk.start()
    if not isinstance(sdk, TapSDK2):
        await sdk.set_input_mode(InputModeController())
    # v2: enable a vision model here (tap-vision-models)

    while True:
        kind, code = await events.get()
        handle(kind, code)

asyncio.run(main())
```

## Output patterns

| Output | How | Extra install |
|--------|-----|---------------|
| Terminal | `print`, or `rich` for a live view | none / `rich` |
| Browser page (best for visual apps) | Python sends events over a WebSocket; an HTML page reacts | `websockets` |
| Keyboard / media keys (control other apps) | `pynput` key presses | `pynput` |
| Game window | `pygame` loop reads a thread-safe `queue.Queue` | `pygame` |
| Sound / music | `simpleaudio`, or a browser page with Web Audio | varies |

### Browser bridge (WebSocket)

```python
# pip install websockets
import json, websockets

clients = set()

async def ws_handler(ws):
    clients.add(ws)
    try:
        await ws.wait_closed()
    finally:
        clients.discard(ws)

async def broadcast(event):
    msg = json.dumps(event)
    for ws in list(clients):
        await ws.send(msg)

# in main(): await websockets.serve(ws_handler, "localhost", 8765)
# in the loop: await broadcast({"kind": kind, "code": code})
```

```html
<script>
  const ws = new WebSocket("ws://localhost:8765");
  ws.onmessage = (e) => { const ev = JSON.parse(e.data); /* update the page */ };
</script>
```

Serve the HTML with `python -m http.server` or open the file directly.

### pygame (blocking loop)

pygame needs the main thread. Run the Tap SDK in a background thread with its own event loop and pass events through `queue.Queue`:

```python
import queue, threading
q = queue.Queue()
threading.Thread(target=lambda: asyncio.run(tap_main(q)), daemon=True).start()
# in the pygame loop: while not q.empty(): handle(*q.get_nowait())
```

## Rules

- Do not add dependencies to the SDK. Add them to the app's `requirements.txt`.
- Use a virtual environment (`python3 -m venv .venv`).
- Add a keyboard fallback (arrow keys, space) so the user can test the app without the Tap.
- Show connection status on screen ("Connecting...", "Connected", "Disconnected").
- macOS: Bluetooth permission for the terminal; Accessibility permission when sending keys.
- If the device does not connect, use the troubleshooting table in `tap-getting-started`.
