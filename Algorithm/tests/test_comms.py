import threading
import time
from socket import socket

import pytest
from comms import Communication
from setup_logger import logger


def initiate_connection(client: socket, server_ipv4: str, server_port: int):
    logger.debug(f"Client trying to connect to server at {server_ipv4}:{server_port}")
    client.connect((server_ipv4, server_port))
    time.sleep(2)  # let the client successfully connect first
    logger.debug(f"Client successfully connected")


def send_message(client: socket, message: str, encoding: str):
    logger.debug(f"Client trying to send server message: '{message}'")
    client.send(message.encode(encoding))


# this needs to be the first test to execute, as it will setup a 2-way TCP connection between client and server
@pytest.mark.order(1)
def test_connect(server: Communication, client: socket):
    """Test the setting up of a 2-way TCP socket connection between client and server

    Args:
        server (Communication): _description_
        client (socket): _description_
    """
    try:
        # start server listening on port 5005 - this will block
        server_thread = threading.Thread(target=server.connect)
        # connect the client to the server
        client_thread = threading.Thread(
            target=initiate_connection,
            args=(client, server.ipv4, server.port),
        )
        server_thread.start()
        # let the server create the socket and start listening first --> can use a condition variable on server.is_listening (bool) to make this more robust
        time.sleep(2)
        client_thread.start()

        # let the client successfully connect first
        time.sleep(2)

        # client and server should be using the same TCP connection (i.e. IP and port of opposite end should match)
        assert client.getsockname() == server.connection.getpeername()
        assert client.getpeername() == server.connection.getsockname()
    except Exception as e:
        pytest.fail(e)
        client.close()
        server.disconnect()


@pytest.mark.order(2)
def test_get_obstacles(server: Communication, client: socket, obstacles: str):

    # note that send() is a non-blocking operation - it fills up the local OS network buffer and returns immediately
    # the actual sending of the buffered data over the TCP connection may NOT be finished by the time the send() method returns due to TCP flow control
    send_message(client, obstacles, server.message_format)
    time.sleep(
        1
    )  # let the server receive the message first, since send is non-blocking
    actual_obstacles = server.get_obstacles()
    expected_x, expected_y, expected_direction = obstacles.split(",")
    assert actual_obstacles == [
        (
            int(expected_x),
            int(expected_y),
            10
            if expected_direction == "North"
            else 11
            if expected_direction == "East"
            else 12
            if expected_direction == "South"
            else 13,
        )
    ]
