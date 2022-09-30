import socket
import time
from typing import List, Tuple

from constants import Direction, Obstacle
from setup_logger import logger


class Communication:
    """
    A TCP socket (Algo) client to communiacate the TCP socket (RPi) server listening at (self.ipv4, self.port)
    """

    def __init__(self):
        # self.ipv4 = "192.168.33.1" # TODO - comment on actual run
        self.ipv4: str = socket.gethostbyname(socket.gethostname())
        self.port: int = (
            5000  # port the server is listening on for new websocket connections
        )
        self.socket: socket.socket = (
            socket.socket()
        )  # the socket object used for 2-way TCP communication with the RPi
        self.msg: str = None  # message received from the Rpi
        self.msg_format: str = "utf-8"  # message format for sending (encoding to a UTF-8 byte sequence) and receiving (decoding a UTF-8 byte sequence) data from the Rpi
        self.read_limit_bytes: int = 2048  # number of bytes to read from the socket in a single blocking socket.recv command

    def connect(self) -> None:
        """
        Initiates a TCP socket connection to the server at (self.ipv4, self.port)
        """
        logger.debug(f"Connecting to the server at {self.ipv4}:{self.port}...")
        self.socket.connect((self.ipv4, self.port))
        logger.debug(f"Successfully connected to the server at {self.ipv4}:{self.port}")
        logger.debug(
            f"Algo - Press 'Create Map' now. Ask RPi server to send over command list"
        )

    def disconnect(self):
        if not (self.socket and not self.socket._closed):
            logger.warning(
                "There is no active connection with a server currently. Unable to disconnect."
            )
            return

        logger.debug(f"Disconnecting from the server at {self.ipv4}:{self.port}...")
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        logger.debug(f"Algo client socket has been closed")

    def send_message(self, message: str) -> None:
        """Sends string data to the RPi

        Args:
            message (str): the unencoded raw string to send to the RPi
        """
        server_ipv4, server_port = self.socket.getpeername()
        logger.debug(
            f"[ALGO SEND] Client is sending '{message}' to server at {server_ipv4}:{server_port}"
        )
        self.socket.send(str(message).encode(self.msg_format))

    def get_obstacles(self) -> List[Obstacle]:
        """Returns the list of obstacles sent via Android

        Sample input `data` from RPi
        "0,1,3,N,19,10,S,1,12,13,E,11,0,W" - each obstacle is represented by a comma-separated string of index,x,y,direction

        Returns:
            List[Tuple[int, int, int, str]]: A list of obstacles, where each obstacle is in the format (index, x, y, direction)
        """
        logger.debug("Client is waiting for the server to send the obstacles list")

        while True:
            logger.debug("[BLOCKING] Client listening for data from server...")
            data = self.socket.recv(self.read_limit_bytes).strip()

            if len(data) > 0:
                data = data.decode(self.msg_format)
                logger.debug(f"Client received obstacles from server: '{data}'")
                obstacles = data.split(",")
                new_obstacles = []
                for i in range(0, len(obstacles), 4):
                    index, x, y, direction = obstacles[i : i + 4]

                    # (19 - y) to convert from arena's representation which treats bottom-left as (0,0)
                    # to our representation which treats top-left as (0, 0)
                    index, x, y = (
                        int(index.strip()),
                        int(x.strip()),
                        19 - int(y.strip()),
                    )
                    direction = direction.strip()
                    direction = (
                        10
                        if direction == Direction.NORTH.value
                        else 12
                        if direction == Direction.SOUTH.value
                        else 11
                        if direction == Direction.EAST.value
                        else 13
                        if direction == Direction.WEST.value
                        else None
                    )

                    if not (0 <= x <= 19 and 0 <= y <= 19 and direction is not None):
                        logger.error(
                            f"Invalid obstacle '{obstacles[i: i + 4]}'. Coordinates are out of bounds [0, 19] or direction is invalid. Resend the obstacle list"
                        )
                        continue

                    new_obstacles.append(Obstacle(index, x, y, direction))

                logger.debug(
                    f"Client parsed obstacles from server: {new_obstacles}. Obstacle coordinates treat TOP-LEFT as (0, 0)"
                )
                return new_obstacles

            logger.warn(
                f"Server received empty data from client: '{data}'. Sleeping for 1 second..."
            )
            time.sleep(1)

    def listen_to_rpi(self):
        """
        Reads at most `self.read_limit_bytes` bytes from the server and saves the data into `self.msg`
        """
        logger.debug("[BLOCKING] Client listening for data from server...")

        while True:
            msg = self.socket.recv(self.read_limit_bytes).strip()

            if msg:
                self.msg = msg.decode(self.msg_format)
                logger.debug(
                    f"[ALGO RCV] Client received data from server: '{self.msg}'"
                )
                return

            logger.debug(
                f"[ALGO RCV] Client is waiting for data from server but received: '{self.msg}'. Sleeping for 1 second..."
            )
            time.sleep(1)

    def communicate(self, data: str, listen=True, write=True):
        if write and data:
            self.send_message(data)
        if listen:
            self.listen_to_rpi()
