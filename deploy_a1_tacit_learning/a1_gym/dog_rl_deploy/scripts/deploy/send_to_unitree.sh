#!/bin/bash
rsync -av --progress -e ssh --exclude=*.pt --exclude=*.npz --exclude=*.mp4 --exclude=.git $PWD/../../../dog_rl_deploy $PWD/../../../runs $PWD/../../setup.py quadruped@192.168.0.103:/home/quadruped/a1_gym
