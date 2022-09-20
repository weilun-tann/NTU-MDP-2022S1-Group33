import concurrent.futures
import socket
import time

import pytest
from comms import Communication
from constants import Direction, Obstacle
from setup_logger import logger


def start_client(
    client: Communication, server_ipv4: str, server_port: int
) -> Communication:
    logger.debug(f"Client connecting to server at {server_ipv4}:{server_port}...")
    client.connect()
    time.sleep(2)  # let the client successfully connect first
    logger.debug(f"Client successfully connected")
    return client


def start_server(
    server: socket.socket, server_ipv4: str, server_port: int
) -> socket.socket:
    logger.debug(
        f"[BLOCKING] Server listening at {server_ipv4}:{server_port} for a client to connect..."
    )
    server.listen(0)
    client_conn, _ = server.accept()
    client_ipv4, client_port = client_conn.getpeername()
    logger.debug(f"Connection with client at {client_ipv4}:{client_port} established")
    return client_conn


def stop_server(server: socket.socket):
    server_ipv4, server_port = server.getsockname()
    logger.debug(f"Server at {server_ipv4}:{server_port} is shutting down")
    server.shutdown(socket.SHUT_RDWR)
    server.close()


def test_connect(server: socket.socket, client: Communication):
    """
    1. Start the mock Rpi server listening at at its assigned host and port
    2. Start the actual Algo client and connect it to the mock Rpi server
    3. Assert that the connection established and maintained by both client and server are correct

    Args:
        server (socket.socket): The mock Rpi server
        client (Communication): The actual Algo client
    """
    try:
        server_ipv4, server_port = server.getsockname()

        # start mock TCP socket server listening on port 5000 - this will block
        with concurrent.futures.ThreadPoolExecutor() as executor:
            server_socket_future = executor.submit(
                start_server, server, server_ipv4, server_port
            )
            time.sleep(2)  # let the server start listening first
            client_future = executor.submit(
                start_client, client, server_ipv4, server_port
            )
            time.sleep(2)  # let the client successfully connect first
            server_socket, client = (
                server_socket_future.result(),
                client_future.result(),
            )

            # client and server should be using the same TCP connection (i.e. IP and port of opposite end should match)
            assert client.socket.getsockname() == server_socket.getpeername()
            assert client.socket.getpeername() == server_socket.getsockname()

            # save the actual server socket (after calling .listen() on original socket)
            pytest.server_conn = server_socket

    except Exception as e:
        pytest.fail(e)
        client.disconnect()
        server.shutdown(socket.SHUT_RDWR)
        server.close()


@pytest.mark.dependency(depends=["test_connect"])
def test_get_obstacles(client: Communication, obstacles: str):
    try:
        server = pytest.server_conn
        logger.debug(f"Server sending client message: '{obstacles}'...")

        # let the server receive the message first, since send is non-blocking
        # the actual sending of the buffered data over the TCP connection may NOT be finished by the time the send() method returns due to TCP flow control
        server.send(obstacles.encode(client.msg_format))
        time.sleep(1)
        actual_obstacles = client.get_obstacles()
        expected_index, expected_x, expected_y, expected_direction = obstacles.split(
            ","
        )
        expected_obstacles = [
            Obstacle(
                int(expected_index),
                int(expected_x),
                19
                - int(
                    expected_y
                ),  # convert from arena representation to algo representation
                10
                if expected_direction == Direction.NORTH.value
                else 11
                if expected_direction == Direction.EAST.value
                else 12
                if expected_direction == Direction.SOUTH.value
                else 13
                if expected_direction == Direction.WEST.value
                else None,
            )
        ]
        assert len(actual_obstacles) == len(expected_obstacles)
        assert all(
            [
                actual == expected
                for actual, expected in zip(actual_obstacles, expected_obstacles)
            ]
        )
    except Exception as e:
        pytest.fail(e)
        client.disconnect()
        server.shutdown(socket.SHUT_RDWR)
        server.close()
