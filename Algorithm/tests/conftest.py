import socket

import pytest
from comms import Communication
from setup_logger import logger

from tests.conftest import *


def pytest_configure():
    pytest.server_conn = None


@pytest.fixture(scope="session")
def server() -> socket.socket:
    """
    Returns:
        socket.socket: A TCP socket server mocking the RPi socket server on the same local network
    """
    ipv4, port = socket.gethostbyname(socket.gethostname()), 5000
    logger.debug(f"Creating a TCP socket server at {ipv4}:{port}")
    server = socket.socket()
    server.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # reuse the socket if it's already in use
    server.bind((ipv4, port))
    return server


@pytest.fixture(scope="session")
def client() -> Communication:
    """
    Returns:
        Communication: the Algo TCP socket client
    """
    return Communication()


@pytest.fixture()
def obstacles() -> str:
    """
    Returns:
        str: The list of obstacles formatted as 'index1,x1,y1,Direction1,index2,x2,y2,Direction2,...',
        where 0 <= x, y <= 19 and Direction in {"N", "S", "E", "W"}.
        The (x, y) should be in arena representation (treating bottom-left as (0, 0))
    """
    return "0,3,4,S"
    return "0,1,18,S,1,6,12,N,2,10,7,E,3,15,16,W,4,19,9,W,5,13,2,E"  # sample arena
