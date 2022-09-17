from constants import Direction

map_size = dict(height=20, width=20)

map_cells_1 = [[0 for _ in range(map_size["width"])] for _ in range(map_size["height"])]
map_cells_2 = [[0 for _ in range(map_size["width"])] for _ in range(map_size["height"])]
image_paths = dict(
    blue="images/blue.gif",
    gray="images/gray.gif",
    green="images/green.gif",
    light_blue="images/light_blue.gif",
    light_green="images/light_green.gif",
    pink="images/pink.gif",
    red="images/red.gif",
    yellow="images/yellow.gif",
)
robot_grid = {
    Direction.NORTH: [
        ["dodger blue", "white", "dodger blue"],
        ["dodger blue", "dodger blue", "dodger blue"],
        ["dodger blue", "dodger blue", "dodger blue"],
    ],
    Direction.EAST: [
        ["dodger blue", "dodger blue", "dodger blue"],
        ["dodger blue", "dodger blue", "white"],
        ["dodger blue", "dodger blue", "dodger blue"],
    ],
    Direction.SOUTH: [
        ["dodger blue", "dodger blue", "dodger blue"],
        ["dodger blue", "dodger blue", "dodger blue"],
        ["dodger blue", "white", "dodger blue"],
    ],
    Direction.WEST: [
        ["dodger blue", "dodger blue", "dodger blue"],
        ["white", "dodger blue", "dodger blue"],
        ["dodger blue", "dodger blue", "dodger blue"],
    ],
}

sensor_range = dict(
    front_middle=3, front_left=3, front_right=3, left_front=3, left_middle=3, right=5
)
