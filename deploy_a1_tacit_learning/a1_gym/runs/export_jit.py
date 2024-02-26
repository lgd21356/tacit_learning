import torch
from ml_logger import logger
from a1_gym_learn.ppo_cse.actor_critic import ActorCritic
import copy
import os


# path = "/home/li/walk-these-ways-a1/walk-these-ways/runs/gait-conditioned-agility/2024-01-08/train/105343.499672/checkpoints/"
path = "/home/li/walk-these-ways-a1/walk-these-ways/runs/gait-conditioned-agility/2024-02-06/train/125717.566281/checkpoints/"
checkpoints = "ac_weights_080000"

save_path = path

ac_weights= logger.load_torch(path+checkpoints+".pt", map_location='cuda:0')

num_privileged_obs = 0
num_observations = 70
num_obs_history = 2100
num_actions = 12

actor_critic = ActorCritic(num_observations,
                           num_privileged_obs,
                           num_obs_history,
                           num_actions,
                           ).to("cuda:0")

actor_critic.load_state_dict(ac_weights)

adaptation_module_path = path+'adaptation_module_'+checkpoints.split('_')[-1]+'.jit'
adaptation_module = copy.deepcopy(actor_critic.adaptation_module).to('cpu')
traced_script_adaptation_module = torch.jit.script(adaptation_module)
traced_script_adaptation_module.save(adaptation_module_path)

body_path =path+'body_'+checkpoints.split('_')[-1]+'.jit'
body_model = copy.deepcopy(actor_critic.actor_body).to('cpu')
traced_script_body_module = torch.jit.script(body_model)
traced_script_body_module.save(body_path)


