import socket
import time
from typing import List, Tuple

from setup_logger import logger


class Communication:
    def __init__(self):
        self.ipv4: str = socket.gethostbyname(
            socket.gethostname()
        )  # server's ipv4 address
        self.port: int = (
            5005  # port the server is listening on for new websocket connections
        )
        self.socket: socket.socket = (
            socket.socket()
        )  # the socket object used for 2-way TCP communication with the RPi
        self.connection: socket.socket = (
            None  # represents a socket connection to a client
        )
        self.backlog: int = 0  # number of unaccepted connections that the server will allow before refusing new connections
        self.msg: str = "nothing"  # message received from the Rpi
        self.message_format: str = "utf-8"  # message format for sending (encoding to a UTF-8 byte sequence) and receiving (decoding a UTF-8 byte sequence) data from the Rpi
        self.read_limit_bytes: int = 2048  # number of bytes to read from the socket in a single blocking socket.recv command

    def connect(self):
        if self.connection and not self.connection._closed:
            client_ip, client_port = self.connection.getpeername()
            logger.warn(
                f"There is already an active connection to a client at {client_ip}:{client_port}"
            )
            return

        logger.debug(f"Server is trying to create a socket at {self.ipv4}:{self.port}")
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # reuse the socket if it's already in use
        self.socket.bind((self.ipv4, self.port))
        logger.debug(
            f"[BLOCKING] Server is now listening at {self.ipv4}:{self.port} and waiting for a client to connect..."
        )
        self.socket.listen(self.backlog)
        (
            self.connection,
            _,
        ) = (
            self.socket.accept()
        )  # blocking call, wait for new websocket connection to server
        client_ipv4, client_port = self.connection.getpeername()
        logger.debug(
            f"Server has picked up a connected client at {client_ipv4}:{client_port}"
        )
        logger.debug(
            f"Send your obstacles list (formatted as 'x1,y1,Direction1,x2,y2,Direction2,...') to the server first before pressing 'Create Map'"
        )

    def convert_movement_to_newline_ending_string(self, movements: List[str]) -> str:
        """Converts a list of "w", "a", "s", "d" movements into a comma-separated string

        Args:
            movements (List[str]): A list of movements needed to be taken by the right - "w" (forward), "a" (turn left on the spot), "s" (backward), "d" (turn right on the spot)

        Returns:
            str: The movements as a comma-separated string
        """
        return ",".join(movements) + "\n"

    def send_data(self, data: str) -> None:
        """Sends string data to the RPi

        Args:
            data (str): Data as a string
        """
        client_ipv4, client_port = self.connection.getpeername()
        logger.debug(f"Server is sending data to client {client_ipv4}: '{client_port}'")
        self.connection.send(data.encode(self.message_format))

    def get_obstacles(self) -> List[Tuple[int, int, str]]:
        # TODO - convert all (x, y, direction) into namedtuple or dataclass

        """Returns the list of obstacles sent via Android

        Sample input `data` from RPi
        "1,3,North,19,10,South,12,13,East,11,0,West" - each obstacle is represented by a comma-separated string of x,y,direction

        Sample output from
        Returns:
            List[Tuple[int, int, str]]: A list of obstacles in the format (x, y, direction)
        """
        logger.debug("Server is waiting for the client to send the obstacles list")

        while True:
            logger.debug("[BLOCKING] Server listening for data from client...")
            data = self.connection.recv(self.read_limit_bytes).strip()

            if len(data) > 0:
                data = data.decode(self.message_format)
                logger.debug(f"Server received data from client: '{data}'")
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
        Reads at most `self.read_limit_bytes` bytes from the socket and saves the data into `self.msg`
        """
        logger.debug("[BLOCKING] Server listening for data from client...")

        self.msg = self.connection.recv(self.read_limit_bytes).strip()

        if len(self.msg) > 0 and self.msg != "nothing":
            self.msg = self.msg.decode("utf-8")
            logger.debug(f"Server received data from client: '{self.msg}'")
        else:
            logger.debug(
                f"Server received empty data from client: '{self.msg}'. Sleeping for 1 second..."
            )
            time.sleep(1)

    def communicate(self, data, listen=True, write=True):
        if write and data:
            data = self.convert_movement_to_newline_ending_string(data)
            logger.debug(f"Server sending data to the client: '{data}'")
            self.send_data(data)
        if listen:
            self.listen_to_rpi()

    def disconnect(self):
        if not self.connection or self.connection._closed:
            logger.warning("There is no active connection with a client")
            return

        client_ipv4, client_port = self.connection.getpeername()
        logger.debug(
            f"Server closing the active connection to the client at {client_ipv4}:{client_port}"
        )
        self.connection.close()
        logger.debug(f"Server closing its socket at {self.ipv4}:{self.port}")
        self.socket.close()
