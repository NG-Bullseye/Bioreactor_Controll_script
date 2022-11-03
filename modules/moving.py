import time
from xarm.wrapper import XArmAPI
import numpy as np
import json
from os.path import isfile, join, exists
from os import path

arm = XArmAPI("10.6.51.180")
arm.motion_enable(enable=True)
x, y, z, roll, pitch, yaw = arm.get_position()[1]
arm = XArmAPI("10.6.51.180")
data = []


# For reading or writing robot positions
def _align_head(speed=20):
    tmp = arm.get_servo_angle()[1]
    arm.set_servo_angle(angle=[tmp[0], tmp[1], tmp[2], -(tmp[1] + tmp[2]), tmp[4]],
                             speed=speed, is_radian=False, wait=True)
def loading(index=0):
    _align_head()
    file = "../position.json"
    if path.isfile(file) is True:
        with open(file) as f:
            data_j = json.load(f)
            x_pos = data_j[index]['x']
            y_pos = data_j[index]["y"]
            z_pos = data_j[index]["z"]
            r_pos = data_j[index]["roll"]
            yaw_pos = data_j[index]["yaw"]
            pitch_pos = data_j[index]["pitch"]
            print("Move to: ")
            print(x_pos, y_pos, z_pos, r_pos, yaw_pos, pitch_pos)

            arm.set_position(x=x_pos, y=y_pos, z=z_pos, roll=r_pos, yaw=yaw_pos, pitch=pitch_pos, speed=10)


def save():
    print("Saving position")
    data_j=[]
    file = "../position.json"
    if path.isfile(file) is True:
        with open(file, "r") as f:
            data_j = json.load(f)
    data_j.append({"x": x, "y": y, "z": z, "roll": roll, "pitch": pitch, "yaw": yaw})
    with open(file, "w") as json_file:
        json.dump(data_j, json_file, indent=4, separators=(',', ': '))


 # time.sleep(10)
loading(1)

# alpha = np.pi * 5 / 180
#
# u = x + 10
# v = y + 10
# # delta = x - u
# # u += 2 * delta
# # v = -x * np.sin(alpha) + y * np.cos(alpha)
# arm.set_position(u, v, z, speed=10)
