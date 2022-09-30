from typing import List

import numpy as np

from constants import Distance, Obstacle
from setup_logger import logger


class Node:
    """
    A node class for A* Pathfinding
    parent is parent of the current Node
    position is current position of the Node in the maze
    g is cost from start to current Node
    h is heuristic based estimated cost for current Node to end Node
    f is total cost of present node i.e. :  f = g + h
    """

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position


# This function return the path of the search


def return_path(current_node, maze):
    path = []
    no_rows, no_columns = np.shape(maze)
    # here we create the initialized result maze with -1 in every position
    result = [[-1 for i in range(no_columns)] for j in range(no_rows)]
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    # Return reversed path as we need to show from start to end path
    path = path[::-1]
    start_value = 0
    # we update the path of start to end found by A-star serch with every step incremented by 1
    for i in range(len(path)):
        result[path[i][0]][path[i][1]] = start_value
        start_value += 1
    return result


def is_adjacent_to_any_obstacle(
    x: int, y: int, min_separation: int, obstacles: List[Obstacle]
) -> bool:
    """Determines if the given (x, y) coordinate is vertically or horizontally adjacent (by `distance`) to any obstacle in `obstacles`

    Args:
        x (int): The x coordinate
        y (int): The y coordinate
        distance(int): Any (x - obstacle.x) and (y - obstacle.y) must be >= min_separation + 1
        obstacles (List[Obstacle]): A list of obstacles

    Returns:
        bool: True if the given (x, y) coordinate is vertically or horizontally adjacent to any obstacle in `obstacles`, False otherwise
    """
    return any(
        [
            (obstacle.x == x and abs(obstacle.y - y) < min_separation + 1)
            or (obstacle.y == y and abs(obstacle.x - x) < min_separation + 1)
            for obstacle in obstacles
        ]
    )


def search(maze, cost, start, end, obstacles: List[Obstacle]):
    """
    Returns a list of tuples as a path from the given start to the given end in the given maze
    """
    logger.debug(f"Searching for a path from (y, x, direction) = {start} to {end}")

    # Create start and end node with initized values for g, h and f
    start_node = Node(None, tuple(start))
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, tuple(end))
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both yet_to_visit and visited list
    # in this list we will put all node that are yet_to_visit for exploration.
    # From here we will find the lowest cost node to expand next
    yet_to_visit_list = []
    # in this list we will put all node those already explored so that we don't explore it again
    visited_list = []

    # Add the start node
    yet_to_visit_list.append(start_node)

    # Adding a stop condition. This is to avoid any infinite loop and stop
    # execution after some reasonable number of steps
    outer_iterations = 0
    max_iterations = (len(maze) // 2) ** 5

    # what squares do we search . serarch movement is left-right-top-bottom
    # (4 movements) from every positon

    move = [[-1, 0], [0, 1], [1, 0], [0, -1]]  # go up  # go right  # go down  # go left

    """
        1) We first get the current node by comparing all f cost and selecting the lowest cost node for further expansion
        2) Check max iteration reached or not . Set a message and stop execution
        3) Remove the selected node from yet_to_visit list and add this node to visited list
        4) Perofmr Goal test and return the path else perform below steps
        5) For selected node find out all children (use move to find children)
            a) get the current postion for the selected node (this becomes parent node for the children)
            b) check if a valid position exist (boundary will make few nodes invalid)
            c) if any node is a wall then ignore that
            d) add to valid children node list for the selected parent

            For all the children node
                a) if child in visited list then ignore it and try next node
                b) calculate child node g, h and f values
                c) if child in yet_to_visit list then ignore it
                d) else move the child to yet_to_visit list
    """
    # find maze has got how many rows and columns
    no_rows, no_columns = np.shape(maze)

    # Loop until you find the end

    while len(yet_to_visit_list) > 0:

        # Every time any node is referred from yet_to_visit list, counter of limit operation incremented
        outer_iterations += 1

        # Get the current node
        current_node = yet_to_visit_list[0]
        current_index = 0
        for index, item in enumerate(yet_to_visit_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # if we hit this point return the path such as it may be no solution or
        # computation cost is too high
        if outer_iterations > max_iterations:
            logger.error("giving up on pathfinding too many iterations")
            return return_path(current_node, maze)

        # Pop current node out off yet_to_visit list, add to visited list
        yet_to_visit_list.pop(current_index)
        visited_list.append(current_node)

        # test if goal is reached or not, if yes then return the path
        if (
            current_node.position[0] == end_node.position[0]
            and current_node.position[1] == end_node.position[1]
        ):
            return return_path(current_node, maze)

        # Generate children from all adjacent squares
        children = []
        i = 0

        for new_position in move:
            direction = [10, 11, 12, 13]

            # Get node position
            node_position = [
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1],
                direction[i],
            ]
            i += 1
            # Make sure within range (check if within maze boundary)
            # Make sure there is at least `Distance.MIN_SEPARATION.value`
            # horizontal and vertical buffer between robot and any obstacle
            if (
                node_position[0] > (no_rows - 1)
                or node_position[0] < 0
                or node_position[1] > (no_columns - 1)
                or node_position[1] < 0
                or is_adjacent_to_any_obstacle(
                    node_position[1],
                    node_position[0],
                    Distance.MIN_SEPARATION.value,
                    obstacles,
                )
            ):
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] in [1, 10, 11, 12, 13]:
                continue

            # Create new node
            new_node = Node(current_node, node_position)
            # Append
            children.append(new_node)

        # Loop through children
        for child in children:
            tempCost = cost

            # Child is on the visited list (search entire visited list)
            if (
                len(
                    [
                        visited_child
                        for visited_child in visited_list
                        if visited_child == child
                    ]
                )
                > 0
            ):
                continue

            # Increase the cost of turning by 2x
            # Robot facing North or South and making Left/Right turns
            if child.parent.position[2] in [10, 12]:
                if [
                    child.position[0] - child.parent.position[0],
                    child.position[1] - child.parent.position[1],
                ] == move[1]:
                    tempCost *= 2
                    child.position[2] = 11
                elif [
                    child.position[0] - child.parent.position[0],
                    child.position[1] - child.parent.position[1],
                ] == move[3]:
                    tempCost *= 2
                    child.position[2] = 13
            # Robot facing East or West and making Left/Right turns
            elif child.parent.position[2] in [11, 13]:
                if [
                    child.position[0] - child.parent.position[0],
                    child.position[1] - child.parent.position[1],
                ] == move[0]:
                    tempCost *= 2
                    child.position[2] = 10
                elif [
                    child.position[0] - child.parent.position[0],
                    child.position[1] - child.parent.position[1],
                ] == move[2]:
                    tempCost *= 2
                    child.position[2] = 12

            # Create the f, g, and h values
            child.g = current_node.g + tempCost
            # Heuristic costs calculated here, this is using eucledian distance
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                (child.position[1] - end_node.position[1]) ** 2
            )

            child.f = child.g + child.h

            # Child is already in the yet_to_visit list and g cost is already lower
            if len([i for i in yet_to_visit_list if child == i and child.g > i.g]) > 0:
                continue

            # Add the child to the yet_to_visit list
            yet_to_visit_list.append(child)
