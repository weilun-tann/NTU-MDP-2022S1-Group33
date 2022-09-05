import socket
import time
from typing import List, Tuple

from setup_logger import logger


class Communication:
    """
    A TCP socket (Algo) client to communiacate the TCP socket (RPi) server listening at (self.ipv4, self.port)
    """

    def __init__(self):
        self.ipv4: str = socket.gethostbyname(
            socket.gethostname()
        )  # TODO - switch to "192.168.33.1" when before deployed to RPi  # server's ipv4 address
        self.port: int = 5000  # server's port
        self.client_socket: socket.socket = (
            socket.socket()
        )  # the socket object used for 2-way TCP communication with the RPi
        self.msg: str = "nothing"  # message received from the Rpi
        self.msg_format: str = "utf-8"  # message format for sending (encoding to a UTF-8 byte sequence) and receiving (decoding a UTF-8 byte sequence) data from the Rpi
        self.read_limit_bytes: int = 2048  # number of bytes to read from the socket in a single blocking socket.recv command

    def connect(self) -> None:
        """
        Initiates a TCP socket connection to the server at (self.ipv4, self.port)
        """
        logger.debug(f"Connecting to the server at {self.ipv4}:{self.port}...")
        self.client_socket.connect((self.ipv4, self.port))
        logger.debug(f"Successfully connected to the server at {self.ipv4}:{self.port}")

    def disconnect(self):
        if not (self.client_socket and not self.client_socket._closed):
            logger.warning(
                "There is no active connection with a server currently. Unable to disconnect."
            )
            return

        logger.debug(f"Disconnecting from the server at {self.ipv4}:{self.port}...")
        self.client_socket.shutdown(socket.SHUT_RDWR)
        self.client_socket.close()
        logger.debug(
            f"Successfully disconnected from the server at {self.ipv4}:{self.port}"
        )

    def convert_movement_to_newline_ending_string(self, movements: List[str]) -> str:
        """Converts a list of "w", "a", "s", "d" movements into a comma-separated string

        Args:
            movements (List[str]): A list of movements needed to be taken by the right - "w" (forward), "a" (turn left on the spot), "s" (backward), "d" (turn right on the spot)

        Returns:
            str: The movements as a comma-separated string
        """
        return ",".join(movements) + "\n"

    def send_message(self, message: str) -> None:
        """Sends string data to the RPi

        Args:
            message (str): the unencoded raw string to send to the RPi
        """
        server_ipv4, server_port = self.client_socket.getpeername()
        logger.debug(
            f"Client is sending '{message}' to server at {server_ipv4}: '{server_port}'"
        )
        self.client_socket.send(message.encode(self.msg_format))

    def get_obstacles(self) -> List[Tuple[int, int, str]]:
        # TODO - convert all (x, y, direction) into namedtuple or dataclass

        """Returns the list of obstacles sent via Android

        Sample input `data` from RPi
        "1,3,North,19,10,South,12,13,East,11,0,West" - each obstacle is represented by a comma-separated string of x,y,direction

        Sample output from
        Returns:
            List[Tuple[int, int, str]]: A list of obstacles in the format (x, y, direction)
        """
        logger.debug("Client is waiting for the server to send the obstacles list")

        while True:
            logger.debug("[BLOCKING] Client listening for data from server...")
            data = self.client_socket.recv(self.read_limit_bytes).strip()

            if len(data) > 0:
                data = data.decode(self.msg_format)
                logger.debug(f"Client received data from server: '{data}'")
                obstacles = data.split(",")
                new_obstacles = []
                for i in range(0, len(obstacles), 3):
                    temp = [
                        int(obstacles[i]),
                        int(obstacles[i + 1]),
                    ]

                    if obstacles[i + 2].lower().strip() == "north":
                        temp.append(10)
                    elif obstacles[i + 2].lower().strip() == "south":
                        temp.append(12)
                    elif obstacles[i + 2].lower().strip() == "east":
                        temp.append(11)
                    elif obstacles[i + 2].lower().strip() == "west":
                        temp.append(13)
                    logger.debug(f"Obstacle {i}: {temp}")
                    new_obstacles.append(
                        tuple(temp)
                    )  # TODO - convert each obstcle to a namedtuple in constants

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

        self.msg = self.client_socket.recv(self.read_limit_bytes).strip()

        if len(self.msg) > 0 and self.msg != "nothing":
            self.msg = self.msg.decode("utf-8")
            logger.debug(f"Client received data from server: '{self.msg}'")
        else:
            logger.debug(
                f"Client received no data from server: '{self.msg}'. Sleeping for 1 second..."
            )
            time.sleep(1)

    def communicate(self, data, listen=True, write=True):
        if write and data:
            data = self.convert_movement_to_newline_ending_string(data)
            logger.debug(f"Client sending data to the server: '{data}'")
            self.send_message(data)
        if listen:
            self.listen_to_rpi()
