"""Log raw Tap sensor packets to CSV (v1 or v2).

Run:  python log_csv.py --seconds 30 --out raw.csv
Columns: host_time, device_ts_ms, type ("imu" or "accl"), v0..vN
  imu  = [gyro_x, gyro_y, gyro_z, accl_x, accl_y, accl_z]   (mdps, mg when scaled)
  accl = 5 fingers x [x, y, z]                               (mg when scaled; v1 only)
"""
import argparse
import asyncio
import csv
import time

from tapsdk import DeviceFeatures, InputModeRaw, TapSDK2, connect
from tapsdk.enumerations import ImuAcclSensitivity, ImuGyroSensitivity


async def main(seconds, out):
    rows = []

    def on_raw(identifier, packets):
        now = time.time()
        for p in packets:
            rows.append([now, p["ts"], p["type"], *p["payload"]])

    sdk = await connect()
    sdk.register_raw_data_events(on_raw)
    await sdk.start()

    if isinstance(sdk, TapSDK2):
        await sdk.set_feature(DeviceFeatures.RAW_IMU_DATA, True)
        await sdk.set_imu_sensitivity(
            xl_sensitivity=ImuAcclSensitivity.G2,
            gyro_sensitivity=ImuGyroSensitivity.DPS125,
            scaled=True,
        )
    else:
        await sdk.set_input_mode(InputModeRaw(scaled=True))

    print(f"recording {seconds}s ...")
    await asyncio.sleep(seconds)

    if isinstance(sdk, TapSDK2):
        await sdk.set_feature(DeviceFeatures.RAW_IMU_DATA, False)

    with open(out, "w", newline="") as f:
        csv.writer(f).writerows(rows)
    print(f"wrote {len(rows)} packets to {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--out", default="raw.csv")
    args = parser.parse_args()
    asyncio.run(main(args.seconds, args.out))
