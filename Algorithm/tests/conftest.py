import socket

import pytest
from comms import Communication

from tests.conftest import *


@pytest.fixture(scope="session")
def server() -> Communication:
    return Communication()


@pytest.fixture(scope="session")
def client() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


@pytest.fixture()
def obstacles() -> str:
    return "7,18,West"
