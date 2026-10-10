set -e

ARDU_WS="$HOME/ardu_ws"

source /opt/ros/humble/setup.bash

source "$ARDU_WS/install/setup.bash"

export GZ_SIM_RESOURCE_PATH="$GZ_SIM_RESOURCE_PATH:$ARDU_WS/install/ardupilot_gazebo/share"
export SDF_PATH="$GZ_SIM_RESOURCE_PATH"

ros2 launch ardupilot_gz_bringup iris_maze.launch.py
