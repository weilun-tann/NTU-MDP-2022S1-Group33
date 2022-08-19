import time
import math
from map import *
from constants import *
from path_find_algo import *
import sys
import numpy as np
from fastest_path_algo import FastestPath


class Robot:
    def __init__(self, simulator):
        self.simulator = simulator
        self.map = Map()
        self.y = config.map_size["height"] - 2
        self.x = 1
        self.consecutive_forward = 1
        self.bearing = Bearing.NORTH
        self.update_map = True
        self.robot_rpi_temp_movement = []
        self.rpi_goal = ["obstacles"]
        # tuple of location coordinates and bearing
        self.prev_loc = [((1, 18), Bearing.NORTH)]

    def validate(self, x, y):
        if (
            0 < self.x + x < config.map_size["width"] - 1
            and 0 < self.y + y < config.map_size["height"] - 1
        ):
            return True

    def set_location(self, x, y):
        self.x = x
        self.y = y

    # recalculate center of robot
    def move(self):
        if self.bearing == Bearing.NORTH and self.check_front():
            self.y -= 1
        elif self.bearing == Bearing.EAST and self.check_front():
            self.x += 1
        elif self.bearing == Bearing.SOUTH and self.check_front():
            self.y += 1
        elif self.bearing == Bearing.WEST and self.check_front():
            self.x -= 1

    def reverse(self):
        if self.bearing == Bearing.NORTH:
            self.y += 1
        elif self.bearing == Bearing.EAST:
            self.x -= 1
        elif self.bearing == Bearing.SOUTH:
            self.y -= 1
        elif self.bearing == Bearing.WEST:
            self.x += 1

    def left(self):
        # rotate anticlockwise by 90 deg
        self.bearing = Bearing.prev_bearing(self.bearing)

    def right(self):
        # rotate clockwise by 90 deg
        self.bearing = Bearing.next_bearing(self.bearing)

    def get_right_bearing(self):
        return Bearing.next_bearing(self.bearing)

    def get_left_bearing(self):
        return Bearing.prev_bearing(self.bearing)

    def get_back_bearing(self):
        return Bearing.next_bearing(Bearing.next_bearing(self.bearing))

    def reset(self):
        self.y = config.map_size["height"] - 2
        self.x = 1
        self.bearing = Bearing.NORTH
        self.prev_loc = [((1, 18), Bearing.NORTH)]

    def check_front(self):
        if (
            self.bearing == Bearing.NORTH
            and self.validate(0, -1)
            and self.north_is_free()
        ):
            return True
        elif (
            self.bearing == Bearing.EAST and self.validate(1, 0) and self.east_is_free()
        ):
            return True
        elif (
            self.bearing == Bearing.SOUTH
            and self.validate(0, 1)
            and self.south_is_free()
        ):
            return True
        elif (
            self.bearing == Bearing.WEST
            and self.validate(-1, 0)
            and self.west_is_free()
        ):
            return True
        else:
            return False

    # check obstacles
    def north_is_free(self):
        for i in range(3):
            if map_sim[self.y - 2][self.x - i + 1] in [10, 11, 12, 13]:
                return False
        return True

    def south_is_free(self):
        for i in range(3):
            if map_sim[self.y + 2][self.x - i + 1] in [10, 11, 12, 13]:
                return False
        return True

    def east_is_free(self):
        for i in range(3):
            if map_sim[self.y - i + 1][self.x + 2] in [10, 11, 12, 13]:
                return False
        return True

    def west_is_free(self):
        for i in range(3):
            if map_sim[self.y - i + 1][self.x - 2] in [10, 11, 12, 13]:
                return False
        return True

    def get_target_movement(self, from_dir, to_dir):
        if from_dir == to_dir:
            return

        if from_dir == Bearing.NORTH:
            self.get_target_movement_north(to_dir)
        elif from_dir == Bearing.EAST:
            self.get_target_movement_east(to_dir)
        elif from_dir == Bearing.SOUTH:
            self.get_target_movement_south(to_dir)
        else:
            self.get_target_movement_west(to_dir)

    def get_target_movement_north(self, to_dir):
        if to_dir == Bearing.EAST:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.EAST

        elif to_dir == Bearing.WEST:
            self.simulator.robot_movement.append(MOVEMENT.LEFT)
            self.robot_rpi_temp_movement.append(MOVEMENT.LEFT)
            self.bearing = Bearing.WEST

        elif to_dir == Bearing.SOUTH:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.SOUTH

    def get_target_movement_east(self, to_dir):
        if to_dir == Bearing.NORTH:
            self.simulator.robot_movement.append(MOVEMENT.LEFT)
            self.robot_rpi_temp_movement.append(MOVEMENT.LEFT)
            self.bearing = Bearing.NORTH

        elif to_dir == Bearing.SOUTH:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.SOUTH

        elif to_dir == Bearing.WEST:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.WEST

    def get_target_movement_south(self, to_dir):
        if to_dir == Bearing.EAST:
            self.simulator.robot_movement.append(MOVEMENT.LEFT)
            self.robot_rpi_temp_movement.append(MOVEMENT.LEFT)
            self.bearing = Bearing.EAST

        elif to_dir == Bearing.WEST:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.WEST

        elif to_dir == Bearing.NORTH:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.NORTH

    def get_target_movement_west(self, to_dir):
        if to_dir == Bearing.NORTH:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.NORTH
        elif to_dir == Bearing.SOUTH:
            self.simulator.robot_movement.append(MOVEMENT.LEFT)
            self.robot_rpi_temp_movement.append(MOVEMENT.LEFT)
            self.bearing = Bearing.SOUTH
        elif to_dir == Bearing.EAST:
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.simulator.robot_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.robot_rpi_temp_movement.append(MOVEMENT.RIGHT)
            self.bearing = Bearing.EAST

    def fastestPath(self, maze):
        self.simulator.temp_pairs = []
        print("Fastest path")
        start = [1, 18, 10]
        new_goal_nodes = []
        g = self.simulator.goal_pairs
        g.insert(0, start)
        encoded_pairs = {}
        count = 0
        k = []
        for i in range(len(self.simulator.gp)):
            if self.simulator.gp[i][2] == 10:
                k.append(
                    [
                        self.simulator.gp[i][0],
                        self.simulator.gp[i][1] - 4,
                        12,
                        self.simulator.gp[i][3],
                    ]
                )
            elif self.simulator.gp[i][2] == 11:
                k.append(
                    [
                        self.simulator.gp[i][0] + 4,
                        self.simulator.gp[i][1],
                        13,
                        self.simulator.gp[i][3],
                    ]
                )
            elif self.simulator.gp[i][2] == 12:
                k.append(
                    [
                        self.simulator.gp[i][0],
                        self.simulator.gp[i][1] + 4,
                        10,
                        self.simulator.gp[i][3],
                    ]
                )
            else:
                k.append(
                    [
                        self.simulator.gp[i][0] - 4,
                        self.simulator.gp[i][1],
                        11,
                        self.simulator.gp[i][3],
                    ]
                )

        for i in g:
            encoded_pairs[count] = i
            count += 1
        print("encoded pairs", encoded_pairs)
        dist = []
        index = 0
        for i in g:
            temp = []
            for j in g:
                if i == j:
                    temp.append(sys.maxsize)
                else:
                    sqr = pow(i[0] - j[0], 2) + pow(i[1] - j[1], 2)
                    root = math.sqrt(sqr)
                    temp.append(root)
            dist.append(temp)
        n = len(g)
        fastest_path = FastestPath()
        path = fastest_path.plan_path(dist, n)
        print(path)
        for i in path:
            if i != 0:
                new_goal_nodes.append(encoded_pairs[i])
                t = encoded_pairs[i]
                for j in range(len(k)):
                    if k[j][0] == t[0] and k[j][1] == t[1]:
                        self.rpi_goal.append(str(int(k[j][3])))
                        break
        print(self.rpi_goal)
        for x in new_goal_nodes:
            if x[2] == 10:
                tempGoal = [x[0], x[1] - 3]
            elif x[2] == 11:
                tempGoal = [x[0] + 3, x[1]]
            elif x[2] == 12:
                tempGoal = [x[0], x[1] + 3]
            else:
                tempGoal = [x[0] - 3, x[1]]
            self.simulator.temp_pairs.append(tempGoal)

        self.hamiltonian_path_search(maze, new_goal_nodes)

    def hamiltonian_path_search(self, maze, target_obstacles):
        start = [18, 1, 10]
        end = [
            target_obstacles[0][1],
            target_obstacles[0][0],
            target_obstacles[0][2],
        ]  # ending position
        cost = 10  # cost per movement
        for i in range(len(target_obstacles)):
            self.simulator.robot_temp_movement = []
            self.robot_rpi_temp_movement = []
            path = search(maze, cost, start, end)

            # Path movement
            for row in range(len(path)):
                for item in range(len(path[row])):
                    if path[row][item] not in [-1, 0]:
                        self.simulator.robot_temp_movement.insert(
                            path[row][item], [row, item]
                        )
            tempStart = start
            for j in range(len(self.simulator.robot_temp_movement)):
                move = [
                    [tempStart[0] - 1, tempStart[1]],
                    [tempStart[0], tempStart[1] + 1],
                    [tempStart[0] + 1, tempStart[1]],
                    [tempStart[0], tempStart[1] - 1],
                ]
                direction = [Bearing.NORTH, Bearing.EAST, Bearing.SOUTH, Bearing.WEST]
                for k in range(len(move)):
                    if move[k] in self.simulator.robot_temp_movement:
                        if self.bearing == direction[k]:
                            self.simulator.robot_movement.append("w")
                            self.robot_rpi_temp_movement.append("w")
                            tempStart = move[k]
                            self.simulator.robot_temp_movement.remove(tempStart)
                            break
                        elif self.bearing == direction[(k + 2) % 4]:
                            self.simulator.robot_movement.append("s")
                            self.robot_rpi_temp_movement.append("s")
                            tempStart = move[k]
                            self.simulator.robot_temp_movement.remove(tempStart)
                            break
                        elif self.bearing == direction[(k + 1) % 4]:
                            self.simulator.robot_movement.append("a")
                            self.simulator.robot_movement.append("w")
                            self.robot_rpi_temp_movement.append("a")
                            self.robot_rpi_temp_movement.append("w")
                            self.bearing = Bearing.prev_bearing(self.bearing)
                            tempStart = move[k]
                            self.simulator.robot_temp_movement.remove(tempStart)
                            break
                        elif self.bearing == direction[(k + 3) % 4]:
                            self.simulator.robot_movement.append("d")
                            self.simulator.robot_movement.append("w")
                            self.robot_rpi_temp_movement.append("d")
                            self.robot_rpi_temp_movement.append("w")
                            self.bearing = Bearing.next_bearing(self.bearing)
                            tempStart = move[k]
                            self.simulator.robot_temp_movement.remove(tempStart)
                            break
            self.get_target_movement(
                self.bearing, Bearing.conversion_robot(target_obstacles[i][2])
            )
            self.simulator.robot_movement.append("x")
            self.robot_rpi_temp_movement.append("x")
            print("ROBOT TEMP: ", self.robot_rpi_temp_movement)
            self.simulator.movement_to_rpi.append(self.robot_rpi_temp_movement)
            start = end
            if i + 1 < len(target_obstacles):
                end = [
                    target_obstacles[i + 1][1],
                    target_obstacles[i + 1][0],
                    target_obstacles[i + 1][2],
                ]

        self.bearing = Bearing.NORTH  # Reset bearing to North
        self.displayMovement()

    def displayMovement(self):
        if not self.simulator.robot_movement:
            return
        movement = self.simulator.robot_movement.pop(0)
        if movement == "w":
            self.move()
        elif movement == "a":
            self.left()
        elif movement == "d":
            self.right()
        elif movement == "s":
            self.reverse()
        elif movement == "x":
            goal = self.simulator.temp_pairs.pop(0)
            map_sim[goal[1]][goal[0]] = 1
            time.sleep(1)
        self.simulator.update_map(radius=3)
        # Refresh every 0.5 sec
        self.simulator.job = self.simulator.root.after(100, self.displayMovement)
