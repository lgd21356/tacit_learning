# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2023 Tohoku University, Li Guanda

import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from multiprocessing import Process, Value
import time
import os

class SaveLogger:
    def __init__(self, dt, num_envs, max_steps):
        self.state_log = defaultdict(list)
        self.rew_log = defaultdict(list)
        self.dt = dt
        self.num_episodes = 0
        self.num_envs = num_envs
        self.max_steps = max_steps
        self.create_buffer(num_envs, max_steps)
        self.save_process = None


    def create_buffer(self, num_envs, max_steps):
        self.base_vel_buffer = np.zeros((num_envs, max_steps,3))
        self.base_pos_buffer = np.zeros((num_envs, max_steps,3))
        self.base_vel_yaw_buffer = np.zeros((num_envs, max_steps))
        self.joint_torque_buffer = np.zeros((num_envs, max_steps,12))
        self.joint_pos_buffer = np.zeros((num_envs, max_steps,12))
        self.joint_vel_buffer = np.zeros((num_envs, max_steps,12))
        self.contact_forces_buffer = np.zeros((num_envs, max_steps,4))
        self.command_buffer = np.zeros((num_envs, max_steps,15))
        self.foot_pos_buffer = np.zeros((num_envs, max_steps,4,3))

    def _save_buffer(self, name):
        # save buffers as a npz file
        # time_stamp = time.strftime("%Y%m%d-%H%M%S")
        file_name="./save_data/"+name+"_data.npz"
        # create directory if it does not exist
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        np.savez(file_name, base_vel=self.base_vel_buffer,
                            base_pos=self.base_pos_buffer,
                            base_vel_yaw=self.base_vel_yaw_buffer,
                            joint_torque=self.joint_torque_buffer,
                            joint_pos=self.joint_pos_buffer,
                            joint_vel=self.joint_vel_buffer,
                            contact_forces=self.contact_forces_buffer,
                            command=self.command_buffer,
                            num_envs=self.num_envs,
                            max_steps=self.max_steps,
                            dt=self.dt)
        print("Saved data to: ", file_name)

    def save_buffer(self, name):
        self.save_process = Process(target=self._save_buffer, args=(name,))
        self.save_process.start()

    # def __del__(self):
    #     if self.save_process is not None:
    #         self.save_process.kill()


    # def _plot(self):
    #     base_vel_target = np.linalg.norm(self.command_buffer[:, :, 0:2], axis=2).mean(axis=1)
    #     base_vel = np.linalg.norm(self.base_vel_buffer[:, :, 0:2], axis=2)
    #     base_vel_mean = base_vel.mean(axis=1)
    #     base_vel_std = base_vel.std(axis=1)
    #
    #
    #     power= np.abs(self.joint_vel_buffer*self.joint_torque_buffer).sum(axis=2)
    #     weight=12*9.81
    #     CoT_mean= power.mean(axis=1)/(weight*base_vel.mean(axis=1))
    #     CoT_std= power.std(axis=1)/(weight*base_vel.std(axis=1))
    #
    #     nb_rows = 2
    #     nb_cols = 2
    #     # bar plot comparison of mean and std of base velocity and CoT
    #     fig, axs = plt.subplots(nb_rows, nb_cols)
    #
    #     base_vel_bar = axs[0, 0]
    #     base_vel_bar.bar(np.arange(self.num_envs), base_vel_mean, yerr=base_vel_std, align='center', alpha=0.5, ecolor='black', capsize=10)
    #
    #     plt.tight_layout()
    #     plt.show()
