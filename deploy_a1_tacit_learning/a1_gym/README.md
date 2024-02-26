# dog_rl_deploy
reference repositories：
https://github.com/Improbable-AI/walk-these-ways
https://github.com/fan-ziqi/dog_rl_deploy


```bash
ping 192.168.123.12
```


## deploy docker env

Go to the `scripts` folder of this project and execute the deployment script. 
The script will download the docker image and send it to the bot. (Password is 123)
```bash
cd dog_rl_deploy/scripts
bash deploy_env.sh
```

ssh into the robot

```
ssh unitree@192.168.123.12
```

install docker env

```bash
cd ~/a1_gym/dog_rl_deploy/docker
bash unzip_image.sh
```

The above steps need to be performed only once

## run controller

ssh into the robot

```bash
ssh unitree@192.168.123.12
```
Go to the `scripts` folder of this project and run the `run_rl.sh` script.
This script will stop the official unitree process and run the custom lcm program with docker
```bash
cd ~/a1_gym/dog_rl_deploy/scripts
bash run_rl.sh
```

