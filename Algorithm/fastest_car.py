import numpy as np
from robot import robot
from constants import *
from fastest_path_algo import FastestPath
from map import *
from path_find_algo import *
from setup_logger import logger

class FastestCar:
    def __init__(self, dist, vis, cur, cnt, n, cost, ans):
        self.bearing : Bearing = Bearing.NORTH