"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        args,  # Put your own arguments here
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a Command object.
        """

        try: 
            command = cls(cls.__private_key, connection, target, local_logger) #use the constructor
            return True, command
        except Exception: 
            return False, None
        
    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        # Do any intializiation here
        self._connection = connection
        self._logger = local_logger
        self._target = target
        self.x_velocity = 0 #drone starts at rest 
        self.y_velocity = 0 
        self.z_velocity = 0 
        self.num_data = 0

    def run(
        self,
        telemetry_data: telemetry.TelemetryData
        # Put your own arguments here
    ):
        """
        Make a decision based on received telemetry data.
        """
        # Log average velocity for this trip so far
        self.num_data = self.num_data + 1
        self.x_velocity = (self.x_velocity + telemetry_data.x_velocity)
        self.y_velocity = (self.y_velocity + telemetry_data.y_velocity)
        self.z_velocity = (self.z_velocity + telemetry_data.z_velocity)

        avg_x = self.x_velocity / self.num_data
        avg_y = self.y_velocity / self.num_data
        avg_z = self.z_velocity / self.num_data

        self._logger.info("Average X velocity: " + str(avg_x), None)
        self._logger.info("Average Y velocity: " + str(avg_y), None)
        self._logger.info("Average Z velocity: " + str(avg_z), None)

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"

        change_height = 0

        if (abs(telemetry_data.z - self._target.z) >= 0.5):

            change_height = self._target.z - telemetry_data.z

            self._connection.mav.command_long_send(
                1, 
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                0, 
                1.0, 
                0, 
                0, 
                0, 
                0, 
                0, 
                self._target.z,
            )
            self._logger.info("CHANGE ALTITUDE: " + str(change_height), True)

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"

        #compare yaw actual to yaw desired 
        desired_yaw = math.degrees(math.atan2(
            self._target.y - telemetry_data.y, 
            self._target.x - telemetry_data.x
        ))

        yaw_change = desired_yaw - math.degrees(telemetry_data.yaw)
        yaw_change = ((yaw_change + 180) % 360) - 180

        if abs(yaw_change) > 5: 
            #update yaw
            self._connection.mav.command_long_send(
                1, 
                0,
                mavutil.mavlink.MAV_CMD_CONDITION_YAW, 
                0, 

                abs(yaw_change), 
                5,
                0, 
                1, 

                0, 
                0,
                0 
            )
            self._logger.info("CHANGE YAW: " + str(yaw_change), True)

        # Positive angle is counter-clockwise as in a right handed system



# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
