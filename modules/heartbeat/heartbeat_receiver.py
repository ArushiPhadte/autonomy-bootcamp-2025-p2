"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

# import time
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[True, HeartbeatReceiver] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:
            sender = cls(cls.__private_key, connection, local_logger)  # use the constructor
            return True, sender
        except AssertionError:
            return False, None

    def __init__(
        self, key: object, connection: mavutil.mavfile, local_logger: logger.Logger
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        # Do any intializiation here
        self._connection = connection
        self._logger = local_logger
        self._count = 0

    def run(
        self,
    ) -> None:
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        state = "Connected"

        msg = self._connection.recv_match(type="HEARTBEAT", blocking=True, timeout=1)

        if msg is not None and msg.get_type() == "HEARTBEAT":
            self._logger.debug("Recieved heartbeat", True)
            # set the current state
            state = "Connected"
            self._count = 0

        else:
            self._logger.error("Did not recieve message", True)
            self._count = self._count + 1
            if self._count >= 5:
                state = "Disconnected"

        # tell drone the state if it is connected or disconnected
        return state


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
