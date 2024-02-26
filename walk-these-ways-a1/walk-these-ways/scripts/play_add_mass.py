import time
from isaacgym import gymutil

import isaacgym
assert isaacgym
import torch
import numpy as np
import sys

import glob
import pickle as pkl

from a1_gym.envs import *
from a1_gym.envs.base.legged_robot_config import Cfg
from a1_gym.envs.a1.a1_config import config_a1
from a1_gym.envs.a1.velocity_tracking import VelocityTrackingEasyEnv


from matplotlib import pyplot as plt

from a1_gym.utils import SaveLogger

def load_policy(logdir):
    body = torch.jit.load(logdir + '/checkpoints/body_latest.jit')
    import os
    adaptation_module = torch.jit.load(logdir + '/checkpoints/adaptation_module_latest.jit')

    def policy(obs, info={}):
        i = 0
        latent = adaptation_module.forward(obs["obs_history"].to('cpu'))
        action = body.forward(torch.cat((obs["obs_history"].to('cpu'), latent), dim=-1))
        info['latent'] = latent
        return action

    return policy


def load_env(label, headless=False, args=None):

    dirs = glob.glob(f"../runs/{label}/*")
    logdir = sorted(dirs)[0]

    with open(logdir + "/parameters.pkl", 'rb') as file:
        pkl_cfg = pkl.load(file)
        print(pkl_cfg.keys())
        cfg = pkl_cfg["Cfg"]
        print(cfg.keys())

        for key, value in cfg.items():
            if hasattr(Cfg, key):
                for key2, value2 in cfg[key].items():
                    setattr(getattr(Cfg, key), key2, value2)

    # turn off DR for evaluation script
    Cfg.domain_rand.push_robots = False
    Cfg.domain_rand.randomize_friction = False
    Cfg.domain_rand.randomize_gravity = False
    Cfg.domain_rand.randomize_restitution = False
    Cfg.domain_rand.randomize_motor_offset = False
    Cfg.domain_rand.randomize_motor_strength = False
    Cfg.domain_rand.randomize_friction_indep = False
    Cfg.domain_rand.randomize_ground_friction = False
    Cfg.domain_rand.randomize_base_mass = True
    Cfg.domain_rand.added_mass_range = [args.add_mass, args.add_mass]
    Cfg.domain_rand.randomize_Kd_factor = False
    Cfg.domain_rand.randomize_Kp_factor = False
    Cfg.domain_rand.randomize_joint_friction = False
    Cfg.domain_rand.randomize_com_displacement = False

    Cfg.env.num_recording_envs = 1
    Cfg.env.num_envs = 6
    Cfg.terrain.num_rows = 1
    Cfg.terrain.num_cols = 1
    Cfg.terrain.border_size = 0
    Cfg.terrain.center_robots = True
    Cfg.terrain.center_span = 1
    Cfg.terrain.teleport_robots = True
    Cfg.terrain.yaw_init_range = 0
    Cfg.terrain.x_init_range = 0
    Cfg.terrain.y_init_range = 0
    Cfg.terrain.terrain_length = 50
    Cfg.terrain.terrain_width = 50

    Cfg.noise.add_noise = False

    Cfg.domain_rand.lag_timesteps = 6
    Cfg.domain_rand.randomize_lag_timesteps = True
    Cfg.control.control_type = "actuator_net"
    Cfg.control.tacit_gain = args.tacit_weight

    from a1_gym.envs.wrappers.history_wrapper import HistoryWrapper

    env = VelocityTrackingEasyEnv(sim_device='cuda:0', headless=False, cfg=Cfg)
    env = HistoryWrapper(env)

    # load policy
    from ml_logger import logger
    from a1_gym_learn.ppo_cse.actor_critic import ActorCritic

    policy = load_policy(logdir)

    return env, policy


def play_a1(headless=True):
    from ml_logger import logger

    from pathlib import Path
    from a1_gym import MINI_GYM_ROOT_DIR
    import glob
    import os
    args = get_args()
    label = "gait-conditioned-agility/pretrain-v0/train"


    env, policy = load_env(label, headless=headless, args=args)

    num_eval_steps = 250
    gaits = {"pronking": [0, 0, 0],
             "trotting": [0.5, 0, 0],
             "bounding": [0, 0.5, 0],
             "pacing": [0, 0, 0.5]}

    x_vel_cmd = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    y_vel_cmd, yaw_vel_cmd = 0.0, 0.0
    body_height_cmd = 0.0
    step_frequency_cmd = 3.0
    gait = torch.tensor(gaits["trotting"])
    footswing_height_cmd = 0.08
    pitch_cmd = 0.0
    roll_cmd = 0.0
    stance_width_cmd = 0.25

    measured_x_vels = np.zeros(num_eval_steps)
    # target_x_vels = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0] with num_envs=6
    target_x_vels = np.ones((env.num_envs, num_eval_steps)) * np.arange(0.5, 3.5, 0.5).reshape(-1, 1)
    measured_y_vels = np.zeros(num_eval_steps)
    target_y_vels = np.ones(num_eval_steps) * y_vel_cmd
    measured_yaw_vels = np.zeros(num_eval_steps)
    target_yaw_vels = np.ones(num_eval_steps) * yaw_vel_cmd
    joint_positions = np.zeros((num_eval_steps, 12))

    base_pos_x = np.zeros(num_eval_steps)
    base_pos_y = np.zeros(num_eval_steps)

    save_logger = SaveLogger(env.dt, int(env.num_envs), num_eval_steps)

    obs = env.reset()
    for i in range(num_eval_steps):
        with torch.no_grad():
            actions = policy(obs)

        base_lin_vel_x = env.base_lin_vel[:, 0]
        base_lin_vel_y = env.base_lin_vel[:, 1]
        base_ang_vel_z = env.base_ang_vel[:, 2]

        for j in range(env.num_envs):
            env.commands[j, 0] = x_vel_cmd[j]+(base_lin_vel_x[j]-x_vel_cmd[j])*0.1
        env.commands[:, 1] = y_vel_cmd+(base_lin_vel_y-y_vel_cmd)*0.1
        env.commands[:, 2] = yaw_vel_cmd+(base_ang_vel_z-yaw_vel_cmd)*0.1
        env.commands[:, 3] = body_height_cmd
        env.commands[:, 4] = step_frequency_cmd
        env.commands[:, 5:8] = gait
        env.commands[:, 8] = 0.5
        env.commands[:, 9] = footswing_height_cmd
        env.commands[:, 10] = pitch_cmd
        env.commands[:, 11] = roll_cmd
        env.commands[:, 12] = stance_width_cmd
        obs, rew, done, info = env.step(actions)

        base_pos_x[i] = env.base_pos[0, 0]
        base_pos_y[i] = env.base_pos[0, 1]
        measured_x_vels[i] = env.base_lin_vel[0, 0]
        measured_y_vels[i] = env.base_lin_vel[0, 1]
        measured_yaw_vels[i] = env.base_ang_vel[0, 2]
        joint_positions[i] = env.dof_pos[0, :].cpu()

        save_logger.base_vel_buffer[:, i, :] = env.base_lin_vel.cpu().numpy()
        save_logger.base_pos_buffer[:, i, :] = env.root_states[:, :3].cpu().numpy()
        save_logger.base_vel_yaw_buffer[:, i] = env.base_ang_vel[:, 2].cpu().numpy()
        save_logger.joint_torque_buffer[:, i, :] = env.torques.detach().cpu().numpy()
        save_logger.joint_pos_buffer[:, i, :] = env.dof_pos.cpu().numpy()
        save_logger.joint_vel_buffer[:, i, :] = env.dof_vel.cpu().numpy()
        save_logger.command_buffer[:, i, :] = env.commands.cpu().numpy()

    save_logger.save_buffer("a1_wtw_tacitWeight"+str(args.tacit_weight)+"_addMass"+str(args.add_mass))

    # plot target and measured forward velocity
    # fig, axs = plt.subplots(4, 1, figsize=(12, 10))
    # axs[0].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), measured_x_vels, color='black', linestyle="-", label="Measured")
    # axs[0].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), target_x_vels[0], color='black', linestyle="--", label="Desired")
    # axs[0].legend()
    # axs[0].set_title("Forward Linear Velocity")
    # axs[0].set_xlabel("Time (s)")
    # axs[0].set_ylabel("Velocity (m/s)")
    #
    # axs[1].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), measured_y_vels, color='black', linestyle="-", label="Measured")
    # axs[1].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), target_y_vels, color='black', linestyle="--", label="Desired")
    # axs[1].legend()
    # axs[1].set_title("Lateral Linear Velocity")
    # axs[1].set_xlabel("Time (s)")
    # axs[1].set_ylabel("Velocity (m/s)")
    #
    # axs[2].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), measured_yaw_vels, color='black', linestyle="-", label="Measured")
    # axs[2].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), target_yaw_vels, color='black', linestyle="--", label="Desired")
    # axs[2].legend()
    # axs[2].set_title("Yaw Angular Velocity")
    # axs[2].set_xlabel("Time (s)")
    # axs[2].set_ylabel("Velocity (rad/s)")
    #
    # axs[3].plot(np.linspace(0, num_eval_steps * env.dt, num_eval_steps), joint_positions, linestyle="-", label="Measured")
    # axs[3].set_title("Joint Positions")
    # axs[3].set_xlabel("Time (s)")
    # axs[3].set_ylabel("Joint Position (rad)")
    #
    # plt.tight_layout()
    # plt.show()



def get_args():
    custom_parameters = [
        {"name": "--slope_angle", "type": float, "default": 0.0,
         "help": "Slope angle of the terrain. Overrides config file if provided."},
        {"name": "--add_mass", "type": float, "default": 0.0,
         "help": "Additional mass added to the robot. Overrides config file if provided."},
        {"name": "--tacit_weight", "type": float, "default": 0.0,
         "help": "Weight of tacit learning loss. Overrides config file if provided."},
    ]
    # parse arguments
    args = gymutil.parse_arguments(
        description="RL Policy",
        custom_parameters=custom_parameters)

    return args


if __name__ == '__main__':
    # to see the environment rendering, set headless=Fals
    #
    # e
    play_a1(headless=False)

