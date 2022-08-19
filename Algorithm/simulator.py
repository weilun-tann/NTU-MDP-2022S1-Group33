from time import sleep
from tkinter import *
import tkinter.ttk as ttk
from tkinter import scrolledtext
from map import *
import config
from constants import *
from robot import Robot
from comms import Communication
import time


class Simulator:
    def __init__(self):
        self.simulated_robot = True
        self.root = Tk()
        self.root.title("MDP Simulation")
        self.root.resizable(False, False)
        self.job = None
        self.map = Map()
        self.robot = Robot(self)
        self.robot_n = []
        self.robot_e = []
        self.robot_s = []
        self.robot_w = []
        self.robot_temp_movement = []
        self.robot_movement = []
        self.movement_to_rpi = []
        self.goal_pairs = []
        self.temp_pairs = []
        self.gp = []
        self.communicate = Communication()
        for i in range(3):
            self.robot_n.append([])
            self.robot_e.append([])
            self.robot_s.append([])
            self.robot_w.append([])
            for j in range(3):
                self.robot_n[i].append(config.robot_grid["north"][i][j])
                self.robot_e[i].append(config.robot_grid["east"][i][j])
                self.robot_s[i].append(config.robot_grid["south"][i][j])
                self.robot_w[i].append(config.robot_grid["west"][i][j])
        t = Toplevel(self.root)
        t.title("Control Panel")
        t.geometry("+610+0")
        t.resizable(False, False)

        self.canvas = Canvas(
            self.root,
            width=40 * config.map_size["width"],
            height=40 * config.map_size["height"],
        )
        self.canvas.pack()

        self.control_panel = ttk.Frame(t, padding=(10, 10))
        self.control_panel.grid(row=0, column=1, sticky="snew")
        control_pane_window = ttk.Panedwindow(self.control_panel, orient=VERTICAL)
        control_pane_window.grid(column=0, row=0, sticky=(N, S, E, W))
        parameter_pane = ttk.Frame(control_pane_window)
        action_pane = ttk.Frame(control_pane_window)
        parameter_pane.grid(column=0, row=0, sticky=(N, S, E, W))
        action_pane.grid(column=0, row=1, pady=(10, 0), sticky=(N, S, E, W))

        self.text_area = scrolledtext.ScrolledText(
            control_pane_window, wrap=WORD, width=35, height=10
        )
        self.text_area.grid(row=2, column=0, pady=(20, 10))

        hamiltonian_path_button = ttk.Button(
            action_pane,
            text="Hamiltonian Path Computation",
            command=self.hamiltonian_path,
            width=30,
        )
        hamiltonian_path_button.grid(column=0, row=0, sticky="ew")
        fastest_path_button = ttk.Button(
            action_pane, text="Fastest Path", command=self.findFP
        )
        fastest_path_button.grid(column=0, row=1, sticky="ew")
        reset_button = ttk.Button(action_pane, text="Reset", command=self.reset)
        reset_button.grid(column=0, row=2, sticky="ew")
        create_map_button = ttk.Button(
            action_pane, text="Create Map", command=self.android_map_formation
        )
        create_map_button.grid(column=0, row=3, sticky="ew")
        connect_button = ttk.Button(
            action_pane,
            text="Connect to RPI",
            command=self.communicate.connect,
            width=30,
        )
        connect_button.grid(column=0, row=4, sticky="ew")
        disconnect_button = ttk.Button(
            action_pane,
            text="Disconnect to RPI",
            command=self.communicate.disconnect,
            width=30,
        )
        disconnect_button.grid(column=0, row=5, sticky="ew")
        self.control_panel.columnconfigure(0, weight=1)
        self.control_panel.rowconfigure(0, weight=1)
        self.update_map(full=True)
        self.event_loop()
        self.root.mainloop()

    def event_loop(self):
        while not general_queue.empty():
            msg = general_queue.get()
            print(msg[:3])

            if msg[:3] == START_EXPLORATION:
                logging.debug("Starting exploration")
                self.hamiltonian_path()
            elif msg[:3] == START_FASTEST_PATH:
                logging.debug("Starting fp")
                self.findFP()
            elif msg[:3] == RESET:
                self.reset()
        self.root.after(200, self.event_loop)

    def android_map_formation(self):
        data = self.communicate.get_obstacles()
        self.gp = data
        print("gp", self.gp)
        self.map.create_map(data)
        self.reset()
        self.robot.fastestPath(map_sim)
        self.movement_to_rpi.insert(0, self.robot.rpi_goal)
        print(self.movement_to_rpi)
        for i in self.movement_to_rpi:
            self.communicate.communicate(i)
            sendNext = False
            while sendNext == False:
                if self.communicate.msg == "Movement Done":
                    print("obstacle done")
                    sendNext = True
                    self.communicate.msg = ""

    def findFP(self):
        self.robot.fastestPath(map_sim)

    def hamiltonian_path(self):
        self.robot.hamiltonian_path_search(map_sim, self.goal_pairs)

    def put_robot(self, x, y, bearing):
        if bearing == Bearing.NORTH:
            front_coor = (x * 40 + 15, y * 40 - 10, x * 40 + 25, y * 40)
        elif bearing == Bearing.NORTH_EAST:
            front_coor = (x * 40 + 35, y * 40 - 5, x * 40 + 45, y * 40 + 5)
        elif bearing == Bearing.EAST:
            front_coor = (x * 40 + 40, y * 40 + 10, x * 40 + 50, y * 40 + 20)
        elif bearing == Bearing.SOUTH_EAST:
            front_coor = (x * 40 + 35, y * 40 + 35, x * 40 + 45, y * 40 + 45)
        elif bearing == Bearing.SOUTH:
            front_coor = (x * 40 + 15, y * 40 + 40, x * 40 + 25, y * 40 + 50)
        elif bearing == Bearing.SOUTH_WEST:
            front_coor = (x * 40 - 5, y * 40 + 35, x * 40 + 5, y * 40 + 45)
        elif bearing == Bearing.WEST:
            front_coor = (x * 40 - 10, y * 40 + 10, x * 40, y * 40 + 20)
        else:
            front_coor = (x * 40 - 5, y * 40 - 5, x * 40 + 5, y * 40 + 5)

        try:
            self.canvas.delete(self.robot_body)
            self.canvas.delete(self.robot_header)
        except:
            pass

        self.robot_body = self.canvas.create_oval(
            x * 40 - 20,
            y * 40 - 20,
            x * 40 + 60,
            y * 40 + 60,
            fill="dodger blue",
            outline="",
        )
        self.robot_header = self.canvas.create_oval(
            front_coor[0],
            front_coor[1],
            front_coor[2],
            front_coor[3],
            fill="white",
            outline="",
        )

    def update_cell(self, x, y):
        def wall_radius(wall, wall_c):
            for i in range(3):
                for j in range(3):
                    if not (
                        x - 1 + j < 0
                        or x + j > config.map_size["width"]
                        or y - 1 + i < 0
                        or y - 1 + i >= config.map_size["height"]
                    ):
                        self.canvas.itemconfig(
                            config.map_cells_1[y - 1 + i][x - 1 + j], fill=wall_c
                        )
                        if not map_sim[y - 1 + i][x - 1 + j] in [
                            10,
                            11,
                            12,
                            13,
                        ]:  # Skip the obstacle itself to prevent changes
                            # Update surrounding wall near the obstacle (3x3)
                            map_sim[y - 1 + i][x - 1 + j] = wall

        if map_sim[y][x] in [10, 11, 12, 13]:
            if [x, y] not in self.temp_pairs:
                self.temp_pairs.append([x, y])
        elif map_sim[y][x] == 2:
            self.temp_pairs.remove([x, y])

        direction = ""
        # Start box
        if (17 <= y <= 19) and (0 <= x <= 2):
            color = "gold"
        elif map_sim[y][x] in [0, 2]:
            color = "gray64"
            self.canvas.itemconfig(config.map_cells_2[y][x], text="")
        elif map_sim[y][x] == 10:
            direction = "N"
            color = "magenta"
        elif map_sim[y][x] == 11:
            direction = "E"
            color = "peach puff"
        elif map_sim[y][x] == 12:
            direction = "S"
            color = "dark slate gray"
        elif map_sim[y][x] == 13:
            direction = "W"
            color = "chocolate1"
        else:
            color = "light pink"

        if not config.map_cells_1[y][x]:
            config.map_cells_1[y][x] = self.canvas.create_rectangle(
                x * 40, y * 40, x * 40 + 40, y * 40 + 40, fill=color
            )
            config.map_cells_2[y][x] = self.canvas.create_text(
                x * 40 + 20, y * 40 + 20, text=direction, fill="black", font="bold"
            )
            self.canvas.bind("<ButtonPress-1>", self.on_click)
        else:
            if direction in ["N", "S", "E", "W"]:
                wall_radius(1, "light pink")
                self.canvas.itemconfig(
                    config.map_cells_2[y][x], text=direction, fill="black", font="bold"
                )
            elif map_sim[y][x] == 2:
                wall_radius(0, "gray64")
            self.text_area.delete("0.0", END)
            self.text_area.insert("end", "Goals:\n" + str(self.temp_pairs), "\n")
            self.canvas.itemconfig(config.map_cells_1[y][x], fill=color)

    def update_goal_pairs(self):
        for i in self.temp_pairs:
            if map_sim[i[1]][i[0]] == 10:
                self.goal_pairs.append([i[0], i[1] - 4, 12])
            elif map_sim[i[1]][i[0]] == 11:
                self.goal_pairs.append([i[0] + 4, i[1], 13])
            elif map_sim[i[1]][i[0]] == 12:
                self.goal_pairs.append([i[0], i[1] + 4, 10])
            else:
                self.goal_pairs.append([i[0] - 4, i[1], 11])

    def on_click(self, event):
        x = event.x // 40
        y = event.y // 40

        if map_sim[y][x] == 0:
            map_sim[y][x] = 10  # North
        elif map_sim[y][x] == 10:
            map_sim[y][x] = 11  # East
        elif map_sim[y][x] == 11:
            map_sim[y][x] = 12  # South
        elif map_sim[y][x] == 12:
            map_sim[y][x] = 13  # West
        else:
            map_sim[y][x] = 2  # Reset to 0 later

        self.update_cell(x, y)
        self.goal_pairs = []
        self.update_goal_pairs()

    def update_map(self, radius=2, full=False):
        if full:
            y_range = range(config.map_size["height"])
            x_range = range(config.map_size["width"])
        else:
            y_range = range(
                max(0, self.robot.y - radius),
                min(self.robot.y + radius, config.map_size["height"] - 1) + 1,
            )
            x_range = range(
                max(0, self.robot.x - radius),
                min(self.robot.x + radius, config.map_size["width"] - 1) + 1,
            )

        for y in y_range:
            for x in x_range:
                try:
                    self.update_cell(x, y)
                except IndexError:
                    pass

        self.update_goal_pairs()
        self.text_area.delete("0.0", END)
        self.text_area.insert("end", "Goals:\n" + str(self.temp_pairs), "\n")
        self.put_robot(self.robot.x, self.robot.y, self.robot.bearing)

    def reset(self):
        if self.job:
            self.root.after_cancel(self.job)
        self.robot_movement = []
        self.goal_pairs = []
        self.temp_pairs = []
        self.movement_to_rpi = []
        self.robot.reset()
        self.map.reset()
        self.update_map(full=True)
