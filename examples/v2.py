from tapsdk import DeviceFeatures, TapSDK2
from tapsdk.enumerations import (  # noqa: F401
    ImuAcclSensitivity,
    ImuGyroSensitivity,
    ModelTypes,
    UnifiedAirGestures,
    VisionSensorOpModes,
)
import asyncio
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("tapsdk").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

tap_instance = []
tap_identifiers = []


def on_connect(serial_number):
    serial_str = serial_number.decode("utf-8") if isinstance(serial_number, (bytes, bytearray)) else str(serial_number)
    logger.info("Connected taps:" + serial_str)


def on_disconnect(serial_number):
    serial_str = serial_number.decode("utf-8") if isinstance(serial_number, (bytes, bytearray)) else str(serial_number)
    logger.info("Tap has disconnected" + serial_str)


motion_first_packet_time = 0
motion_total_packets = 0
imu_motion_pps = 0.0


def imu_motion_data(identifier, motion_data):
    global motion_first_packet_time, motion_total_packets, imu_motion_pps

    if motion_first_packet_time == 0:
        motion_first_packet_time = time.time()

    motion_total_packets += 1
    elapsed = time.time() - motion_first_packet_time
    imu_motion_pps = (motion_total_packets / elapsed) if elapsed > 0 else 0.0

    dx, dy, isMouse, euler_angles = motion_data
    print_str = ""
    if isMouse:
        print_str += "Mouse motion: " + "dx: " + str(dx) + " dy: " + str(dy)
    print_str += " Euler angles: " + str(euler_angles)
    logger.info(print_str + f"({imu_motion_pps:.2f} packets/sec)")


def on_standby_state_event(identifier, is_standby):
    logger.info(f"Standby state changed: {'STANDBY' if is_standby else 'ACTIVE'}")


def on_tap_event(identifier, tapcode):
    logger.info("Tap:" + str(tapcode))


air_first_packet_time = 0
air_total_packets = 0
air_gesture_pps = 0.0


def on_air_gesture_event(identifier, gesture_data):
    global air_first_packet_time, air_total_packets, air_gesture_pps

    if air_first_packet_time == 0:
        air_first_packet_time = time.time()

    air_total_packets += 1
    elapsed = time.time() - air_first_packet_time
    air_gesture_pps = (air_total_packets / elapsed) if elapsed > 0 else 0.0

    serial_str = identifier.decode("utf-8") if isinstance(identifier, (bytes, bytearray)) else str(identifier)
    logger.info(
        f"[{serial_str}] Unified Air Gesture: {UnifiedAirGestures(int(gesture_data[0])).name} ")
    if air_total_packets > 14:
        air_total_packets = 0
        air_first_packet_time = 0
        logger.info(f"({air_gesture_pps:.2f} packets/sec)")


first_raw_imu_packet_time = 0
total_raw_imu_packets = 0
raw_imu_pps = 0.0


def on_raw_imu_sensor_data(identifier, raw_sensor_data):
    global total_raw_imu_packets
    global first_raw_imu_packet_time
    global raw_imu_pps
    if raw_sensor_data and first_raw_imu_packet_time == 0:
        first_raw_imu_packet_time = time.time()
    total_raw_imu_packets += len(raw_sensor_data)
    elapsed = time.time() - first_raw_imu_packet_time
    raw_imu_pps = (total_raw_imu_packets / elapsed) if elapsed > 0 else 0.0
    if elapsed > 0 and total_raw_imu_packets > 400:
        logger.info(
            "Received %d imu packets in %.2f seconds (%.2f packets/sec)",
            total_raw_imu_packets,
            elapsed,
            raw_imu_pps,
        )
    for idx, m in enumerate(raw_sensor_data):
        if (total_raw_imu_packets - len(raw_sensor_data) + idx) % 100 == 0:
            logger.info("%s, %s, %s", m['type'], time.time(), m['payload'])

    if total_raw_imu_packets > 400:
        total_raw_imu_packets = 0
        first_raw_imu_packet_time = 0


async def _setup_vision():
    # await asyncio.sleep(1)
    await tap_instance.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
    await tap_instance.set_vision_sensor_model(ModelTypes.AIR_GESTURE)


async def main():
    global tap_instance
    tap_instance = TapSDK2()
    tap_instance.register_connection_events(on_connect)
    tap_instance.register_disconnection_events(on_disconnect)
    tap_instance.register_tap_events(on_tap_event)
    tap_instance.register_raw_imu_data_events(on_raw_imu_sensor_data)
    tap_instance.register_air_gesture_events(on_air_gesture_event)
    tap_instance.register_imu_motion_data_events(imu_motion_data)
    tap_instance.register_standby_state_events(on_standby_state_event)
    await tap_instance.run()
    for feature in DeviceFeatures:
        await tap_instance.set_feature(feature, False)

    logger.info("Setting model detection to True - Gesture mode - 5 seconds")
    await tap_instance.set_feature(DeviceFeatures.MODEL_DETECTION, True)
    await tap_instance.set_vision_sensor_model(ModelTypes.AIR_GESTURE)
    await tap_instance.set_vision_sensor_op_mode(VisionSensorOpModes.STREAM)
    await asyncio.sleep(5)

    logger.info("Setting model detection to False - Tapping mode - 5 seconds")
    await tap_instance.set_vision_sensor_model(ModelTypes.TAPPING)
    await tap_instance.set_vision_sensor_op_mode(VisionSensorOpModes.TRIGGER)
    await asyncio.sleep(5)
    await tap_instance.set_feature(DeviceFeatures.MODEL_DETECTION, False)

    logger.info("Setting standby gesture detection - 5 seconds")
    await tap_instance.set_feature(DeviceFeatures.STANDBY_GESTURE_DETECTION, True)
    await asyncio.sleep(5)
    await tap_instance.set_feature(DeviceFeatures.STANDBY_GESTURE_DETECTION, False)
    await tap_instance.set_standby_state(False)

    logger.info("Setting IMU motion data - 5 seconds")
    await tap_instance.set_feature(DeviceFeatures.IMU_MOTION_DATA, True)
    await asyncio.sleep(5)
    await tap_instance.set_feature(DeviceFeatures.IMU_MOTION_DATA, False)

    logger.info("Setting RAW IMU data - 5 seconds")
    await tap_instance.set_feature(DeviceFeatures.RAW_IMU_DATA, True)
    await tap_instance.set_imu_sensitivity(
        xl_sensitivity=ImuAcclSensitivity.G2,
        gyro_sensitivity=ImuGyroSensitivity.DPS125,
        scaled=True,
    )
    await asyncio.sleep(5)
    await tap_instance.set_feature(DeviceFeatures.RAW_IMU_DATA, False)

    sequence = [500, 200, 500, 500, 500, 200]
    await tap_instance.send_vibration_sequence(sequence)

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
