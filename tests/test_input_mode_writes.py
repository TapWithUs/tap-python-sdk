import asyncio
from unittest.mock import AsyncMock, MagicMock, call, patch

from tapsdk.enumerations import InputType
from tapsdk.inputmodes import InputModeController, input_type_command
from tapsdk.tap import TapSDK


def test_auto_refresh_waits_before_first_write():
    calls = []

    async def refresh():
        calls.append("refresh")

    refresh_helper = __import__("tapsdk.tap", fromlist=["InputModeAutoRefresh"]).InputModeAutoRefresh(
        refresh, timeout=0.05
    )

    async def scenario():
        await refresh_helper.start()
        await asyncio.sleep(0.02)
        assert calls == []
        await asyncio.sleep(0.04)
        assert calls == ["refresh"]
        await refresh_helper.stop()

    asyncio.run(scenario())


def test_auto_refresh_writes_periodically():
    calls = []

    async def refresh():
        calls.append("refresh")

    refresh_helper = __import__("tapsdk.tap", fromlist=["InputModeAutoRefresh"]).InputModeAutoRefresh(
        refresh, timeout=0.05
    )

    async def scenario():
        await refresh_helper.start()
        await asyncio.sleep(0.02)
        assert calls == []
        await asyncio.sleep(0.04)
        assert calls == ["refresh"]
        await asyncio.sleep(0.06)
        assert len(calls) >= 2
        await refresh_helper.stop()

    asyncio.run(scenario())


def test_set_input_mode_also_asserts_current_input_type():
    async def scenario():
        sdk = TapSDK.__new__(TapSDK)
        sdk.client = MagicMock()
        sdk.input_mode = InputModeController()
        sdk.input_type = InputType.AUTO
        sdk.input_mode_refresh = MagicMock()
        sdk.input_mode_refresh.is_running = True
        sdk._write_input_mode = AsyncMock()

        await TapSDK.set_input_mode(sdk, InputModeController())
        assert sdk._write_input_mode.await_args_list == [
            call(InputModeController().get_command()),
            call(input_type_command(InputType.AUTO)),
        ]

        sdk._write_input_mode.reset_mock()
        await TapSDK.set_input_type(sdk, InputType.KEYBOARD)
        sdk._write_input_mode.assert_awaited_once_with(
            input_type_command(InputType.KEYBOARD)
        )

        sdk._write_input_mode.reset_mock()
        await sdk._refresh_input_mode()
        assert sdk._write_input_mode.await_args_list == [
            call(InputModeController().get_command()),
            call(input_type_command(InputType.KEYBOARD)),
        ]

    asyncio.run(scenario())


def test_mode_writes_are_serialized_and_spaced():
    starts = []

    async def scenario():
        sdk = TapSDK.__new__(TapSDK)
        sdk.client = MagicMock()
        sdk._mode_write_lock = asyncio.Lock()

        async def write_gatt_char(uuid, value, response=False):
            assert response is True
            starts.append(asyncio.get_running_loop().time())

        sdk.client.write_gatt_char = AsyncMock(side_effect=write_gatt_char)
        with patch("tapsdk.tap.MODE_COMMAND_SETTLE_SECONDS", 0.01):
            await asyncio.gather(
                sdk._write_input_mode(InputModeController().get_command()),
                sdk._write_input_mode(input_type_command(InputType.KEYBOARD)),
            )

    asyncio.run(scenario())

    assert len(starts) == 2
    assert starts[1] - starts[0] >= 0.01
