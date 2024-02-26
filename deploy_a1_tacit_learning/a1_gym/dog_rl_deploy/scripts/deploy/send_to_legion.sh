#!/bin/bash
rsync -av --progress -e ssh $PWD/../../../dog_rl_deploy/scripts/lcm_logger li@192.168.0.112:/home/li/unitree_deploy/dog_rl_deploy/scripts/lcm_logger
