"""
Telemetry gathering logic.
"""

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> tuple[bool, "Telemetry | None"]:
        """
        Falliable create (instantiation) method to create a Telemetry object.
        """
        try:
            telemetry = cls(cls.__private_key, connection, local_logger)  # use the constructor
            return True, telemetry
        except AssertionError:
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"

        # Do any intializiation here
        self._connection = connection
        self._logger = local_logger

    def run(
        self,
    ) -> "tuple[bool, TelemetryData | None]":
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """
        start = time.perf_counter()
        msg_attitude = None
        msg_position = None

        while time.perf_counter() - start < 1:

            remaining = 1 - (time.perf_counter())

            msg = self._connection.recv_match(
                type=["ATTITUDE", "LOCAL_POSITION_NED"],
                blocking=True,
                timeout=remaining,
            )

            if msg is not None and msg.get_type() == "LOCAL_POSITION_NED":
                msg_position = msg
            elif msg is not None and msg.get_type() == "ATTITUDE":
                msg_attitude = msg

            if (
                msg_position is not None and msg_attitude is not None
            ):  # if both messages have been recieved
                break

        if msg_attitude is None or msg_position is None:
            self._logger.error("Did not recieve both position and attitude", True)
            return False, None

        timestamp = max(msg_position.time_boot_ms, msg_attitude.time_boot_ms)

        # create telemetry data object with msg_attitude and msg_position
        telemetry = TelemetryData(
            timestamp,
            msg_position.x,
            msg_position.y,
            msg_position.z,
            msg_position.vx,
            msg_position.vy,
            msg_position.vz,
            msg_attitude.roll,
            msg_attitude.pitch,
            msg_attitude.yaw,
            msg_attitude.rollspeed,
            msg_attitude.pitchspeed,
            msg_attitude.yawspeed,
        )

        return True, telemetry

        # Read MAVLink message LOCAL_POSITION_NED (32)
        # Read MAVLink message ATTITUDE (30)
        # Return the most recent of both, and use the most recent message's timestamp


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
