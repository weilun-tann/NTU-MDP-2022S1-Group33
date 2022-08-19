import socket
from map import *


class Communication:
    def __init__(self):
        self.port = 5005
        self.s = socket.socket()
        self.ip_address = "192.168.17.28"
        self.c = None
        self.addr = None
        self.msg = "nothing"
        self.map = Map()

    def connect(self):
        try:
            print("trying")
            self.s.bind((self.ip_address, self.port))
            self.s.listen(10)
            self.c, self.addr = self.s.accept()
            print("conncected")
            print(self.msg)
        except Exception as e:
            print("Error", e)

    def convert_movement_to_string(self, movements):
        movement_string = ""
        if movements:
            movement_string = ",".join(movements)
        return movement_string

    def send_data(self, data):
        try:
            self.c.send(data.encode("utf-8"))
        except Exception as e:
            print("error", e)
            raise e

    def get_obstacles(self):
        try:
            count = 0
            while count != 1:
                data = self.c.recv(2048).strip()
                if len(data) > 0:
                    count += 1
                    data = data.decode("utf-8")
                    print(data)
                    obstacles_list = data.split(",")
                    obstacles_list.pop(0)
                    new_obstacles_list = []
                    for i in range(0, len(obstacles_list), 4):
                        temp = []
                        temp.append(int(obstacles_list[i + 1]))
                        temp.append(int(obstacles_list[i + 2]))
                        if obstacles_list[i + 3] == "North":
                            temp.append(10)
                        elif obstacles_list[i + 3] == "South":
                            temp.append(12)
                        elif obstacles_list[i + 3] == "East":
                            temp.append(11)
                        elif obstacles_list[i + 3] == "West":
                            temp.append(13)
                        temp.append(int(obstacles_list[i]))
                        new_obstacles_list.append(temp)

                    print(new_obstacles_list)
                    return new_obstacles_list
        except Exception as e:
            print("error", e)

    def listen_to_rpi(self):
        try:
            self.msg = self.c.recv(2048).strip()
            if len(self.msg) > 0 and self.msg != "nothing":
                self.msg = self.msg.decode("utf-8")
                print(self.msg)
            else:
                print("nothing")
        except Exception as e:
            print("error", e)
            raise e

    def communicate(self, data, listen=True, write=True):
        if write:
            final_data = self.convert_movement_to_string(data)
            print("sending data")
            self.send_data(final_data)
        if listen:
            self.listen_to_rpi()

    def disconnect(self):
        try:
            print(self.c.close())
        except Exception as e:
            print("error", e)
            return False
