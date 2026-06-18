"""
Heartbeat sending logic.
"""

from pymavlink import mavutil
import time
from modules.common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger, 
    ) -> "tuple[True, HeartbeatSender] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """
        try: 
            sender = cls(cls.__private_key, connection, local_logger) #use the constructor
            return True, sender

        except Exception: 
            return False, None

    def __init__( #constructor 
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger
    ):
        assert key is HeartbeatSender.__private_key, "Use create() method"

        # Do any intializiation here
        self._connection = connection
        self._logger = local_logger


    def run(
        self
    ):
        """
        Attempt to send a heartbeat message.
        """
        try:  #send heartbeat message to main process and how to recieve message mavlink
            self._logger.debug("Heartbeat sent", True)
            self._connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
            

        except Exception as e: 
            #log error 
            self._logger.error("Cannot locate drone", True)
            pass

        time.sleep(1)

# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
