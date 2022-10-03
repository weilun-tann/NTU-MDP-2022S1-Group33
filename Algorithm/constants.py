from dataclasses import dataclass
from enum import Enum, IntEnum


class Bearing(IntEnum):
    NORTH = 0
    EAST = 2
    SOUTH = 4
    WEST = 6

    NORTH_EAST = 1
    SOUTH_EAST = 3
    SOUTH_WEST = 5
    NORTH_WEST = 7

    @staticmethod
    def next_bearing(current_bearing):
        return Bearing((current_bearing.value + 2) % 8)

    @staticmethod
    def prev_bearing(current_bearing):
        return Bearing((current_bearing.value + 6) % 8)

    @staticmethod
    def conversion_sim(current_bearing):
        if current_bearing == 0:
            return 10
        elif current_bearing == 2:
            return 11
        elif current_bearing == 4:
            return 12
        else:
            return 13

    @staticmethod
    def conversion_robot(current_bearing):
        if current_bearing == 10:
            return 0
        elif current_bearing == 11:
            return 2
        elif current_bearing == 12:
            return 4
        else:
            return 6

    @staticmethod
    def next_bearing_diag(current_bearing):
        return Bearing((current_bearing.value + 1) % 8)

    @staticmethod
    def prev_bearing_diag(current_bearing):
        return Bearing((current_bearing.value + 7) % 8)

    @staticmethod
    def next_bearing_diag(current_bearing):
        return Bearing((current_bearing.value + 1) % 8)

    @staticmethod
    def prev_bearing_diag(current_bearing):
        return Bearing((current_bearing.value + 7) % 8)

    @staticmethod
    def is_diag_bearing(current_bearing):
        return current_bearing.value % 2 == 1

    @staticmethod
    def int_to_bearing(bearing: int):
        """Converts an integer to a Bearing enum object

        Args:
            bearing (int): The bearing matching one of the 8 enum directions specified in this class

        Returns:
            _type_: The bearing object, if the bearing is valid (0-7)
        """
        return Bearing(bearing)


class Movement(Enum):
    FORWARD = "w010"
    LEFT = "j010"
    RIGHT = "k010"
    REVERSE = "s010"
    STOP = "x"


class Message(Enum):
    ACK = "$"


class Cost(IntEnum):
    INFINITE_COST = 9999
    MOVE_COST = 10
    MOVE_COST_DIAG = 15
    TURN_COST = 20
    TURN_COST_DIAG = 10
    WAYPONT_PENALTY = 1000


class Direction(Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"


class Distance(IntEnum):
    # number of cells away to do image capture (measured from centres)
    IMAGE_CAPTURE = 4

    # number of cells separation from edge of robot to edge of obstacle
    MIN_SEPARATION = 3


@dataclass
class Obstacle:
    """
    Class to represent an obstacle
    """

    id: int
    x: int
    y: int
    direction: Direction


@dataclass
class State:
    """
    Class to represent the state (its coordinates and the direction it's facing) of a robot
    """

    x: int
    y: int
    direction: Direction
