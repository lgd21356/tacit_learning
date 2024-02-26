#!/bin/bash
# 定义退出信号处理函数
cleanup() {
    echo "Exiting..."
    # 在这里执行需要在退出时执行的代码
    bash ./stop_all.sh
    sudo pkill -f optitrack_publisher.py
    sudo pkill -f lcm_subscriber.py

}

# 捕捉退出信号
trap cleanup EXIT
# 主要程序逻辑
echo "Starting..."

cd robot
bash ./stop_all.sh
bash ./start_optitrack.sh
bash ./start_save_logger.sh
bash ./start_unitree_sdk.sh
bash ./start_tacit_controller.sh

echo "End."
