from optitrack import Optitrack
import time
from lcm_types import optitrack_lcmt
import lcm
import math


def square_trajectory(t, a=0.8, v=0.5):
    # The total perimeter of the square
    perimeter = 8 * a
    # Time to complete one full loop around the square
    total_time = perimeter / v

    # Normalize t to always fall within the range [0, total_time) for continuous motion
    t = t % total_time

    # Adjust t to be in the range [0, 4) to reuse the previous logic
    # This scales the [0, total_time) range to [0, 4) to match the segments of the square's path
    t_scaled = 4 * t / total_time

    if t_scaled < 1:
        # Move right along the top edge
        x = -a + 2 * a * t_scaled  # t ranges from 0 to 1
        y = a
    elif t_scaled < 2:
        # Move down along the right edge
        x = a
        y = a - 2 * a * (t_scaled - 1)  # t-1 ranges from 0 to 1
    elif t_scaled < 3:
        # Move left along the bottom edge
        x = a - 2 * a * (t_scaled - 2)  # t-2 ranges from 0 to 1
        y = -a
    else:
        # Move up along the left edge
        x = -a
        y = -a + 2 * a * (t_scaled - 3)  # t-3 ranges from 0 to 1

    return x, y

def calculate_command(real_pos, real_rot):
    t= time.time()

    # calculate command
    pos_x = real_pos[0]
    # print("pos_x", pos_x)
    pos_y = real_pos[1]
    # print("pos_y", pos_y)
    heading = real_rot[2]/180.0*math.pi
    # print("heading", heading)

    # target_circle_traj_x = math.cos(t) # vel=1[m/s], r = 1[m]
    # target_circle_traj_y = math.sin(t)

    target_square_traj_x, target_square_traj_y = square_trajectory(t,a=0.5, v=0.5)

    target_heading = math.atan2(target_square_traj_x - pos_y, target_square_traj_y - pos_x)

    yaw_diff = target_heading - heading
    yaw_diff = (yaw_diff + math.pi) % (2 * math.pi) - math.pi
    max_angular_velocity = 5
    vel_yaw = ((yaw_diff > 0) - (yaw_diff < 0)) * min(max_angular_velocity, 4 * math.fabs(yaw_diff))

    return vel_yaw

if __name__ == "__main__":
    # if setup loopback in motive 3.0.1
    client_address = "192.168.0.103"
    optitrack_server_address = "192.168.0.43"

    lc= lcm.LCM("udpm://239.255.76.67:7667?ttl=255")
    msg = optitrack_lcmt()

    robot_id = 1  # target streaming rigidbody ids (lookup in motive app)
    frequency = 60  # streaming frequency
    robo_pos = Optitrack(client_address, optitrack_server_address, frequency)
    is_running = robo_pos.streaming_client.run()

    while is_running:
        if robot_id in robo_pos.positions:
            # msg.target_yaw = calculate_command(robo_pos.positions[robot_id], robo_pos.rotations[robot_id])
            msg.pos = robo_pos.positions[robot_id]
            msg.rot = robo_pos.rotations[robot_id]
            lc.publish("optitrack_channel", msg.encode())
        time.sleep(1 / frequency)
    else:
        is_running = robo_pos.streaming_client.run()

