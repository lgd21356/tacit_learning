import time

import lcm
import numpy as np
import pickle
from lcm_types.logger_lcmt import logger_lcmt
from lcm_types.optitrack_lcmt import optitrack_lcmt

import datetime


class DataLogger:
    def __init__(self, length=1):
        self.length = length
        self.reset_data_arrays()
        self.filename = "./logged_data/"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+"_data_"
        self.save_times = 0
        self.init_time = 0





    def reset_data_arrays(self):
        self.data_arrays = {
            'time_np': np.zeros(self.length),
            'torques_np': np.zeros((self.length, 12)),
            'dof_vel_np': np.zeros((self.length, 12)),
            'dof_pos_np': np.zeros((self.length, 12)),
            'contact_state_np': np.zeros((self.length, 4)),
            'real_pos_np': np.zeros((self.length, 3)),
            'real_rot_np': np.zeros((self.length, 3)),
            'output_torques_np': np.zeros((self.length, 12)),
            'tacit_torques_np': np.zeros((self.length, 12)),
        }
        self.message_count = 0

    def message_handler(self, channel, data):
        if channel == "lcm_logging":
            robot_msg = logger_lcmt.decode(data)
            if self.init_time != robot_msg.time:
                self.init_time = robot_msg.time
                self.data_arrays['time_np'][self.message_count] = robot_msg.time
                self.data_arrays['torques_np'][self.message_count, :] = robot_msg.joint_torques
                self.data_arrays['dof_vel_np'][self.message_count, :] = robot_msg.joint_velocities
                self.data_arrays['dof_pos_np'][self.message_count, :] = robot_msg.joint_positions
                self.data_arrays['contact_state_np'][self.message_count, :] = robot_msg.contact_forces
                self.data_arrays['output_torques_np'][self.message_count, :] = robot_msg.output_torques
                self.data_arrays['tacit_torques_np'][self.message_count, :] = robot_msg.tacit_torques
                self.message_count += 1

        elif channel == "optitrack_channel":
            opti_msg = optitrack_lcmt.decode(data)
            self.data_arrays['real_pos_np'][self.message_count,:] = opti_msg.pos
            self.data_arrays['real_rot_np'][self.message_count,:] = opti_msg.rot

        if self.message_count >= self.length:

            np.savez(self.filename+str(self.save_times),
                        time_np=self.data_arrays['time_np'],
                        torques_np=self.data_arrays['torques_np'],
                        dof_vel_np=self.data_arrays['dof_vel_np'],
                        dof_pos_np=self.data_arrays['dof_pos_np'],
                        contact_state_np=self.data_arrays['contact_state_np'],
                        output_torques_np=self.data_arrays['output_torques_np'],
                        tacit_torques_np=self.data_arrays['tacit_torques_np'],
                        real_pos_np=self.data_arrays['real_pos_np'],
                        real_rot_np=self.data_arrays['real_rot_np'])
            print("Saved data to: ", self.filename+str(self.save_times))
            self.reset_data_arrays()
            self.save_times+=1
        # with open(self.filename, 'ab') as f:
        #     pickle.dump(self.data_arrays, f)
        # self.message_count += 1
        # if self.message_count >= self.length:
        #     with open(self.filename, 'ab') as f:
        #         pickle.dump(self.data_arrays, f)
        #     # self.reset_data_arrays(self.length)
        #     self.message_count = 0

def main():
    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=255")
    logger = DataLogger(500)

    robot_subscription = lc.subscribe("lcm_logging", logger.message_handler)
    optitrack_subscription = lc.subscribe("optitrack_channel", logger.message_handler)


    try:
        while True:
            lc.handle()
            # time.sleep(0.01)
    except KeyboardInterrupt:
        print("Interrupted by user. Exiting program.")
    finally:
        # if logger.message_count > 0:
        #     with open(logger.filename, 'ab') as f:
        #         pickle.dump(logger.data_arrays, f)
        lc.unsubscribe(robot_subscription)
        lc.unsubscribe(optitrack_subscription)

if __name__ == "__main__":
    main()