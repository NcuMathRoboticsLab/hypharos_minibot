![alt text](https://github.com/Hypha-ROS/hypharos_minibot/blob/master/document/logo/HyphaROS_logo_2.png)  
![alt text](https://github.com/Hypha-ROS/hypharos_minibot/blob/master/document/HyphaROS_MiniBot_photo.jpg)  

## Abstract
This code is for final projects of MA5039 Perception and Estimation in Robotics.
It is a sample code based on HyphaROS Minibot.
This code activate a node "main" and the other sensor nodes. 
Main node subscribes three topics -- imu_data, odom, and scan. 
You can access data from three Callback functions in src/main.cpp.
There is a maker for landmarks or targets.
You can see it in rviz.

## About us

Developer:   
* Kuo-Shih Tseng   
Contact: kuoshih@math.ncu.edu.tw   
Date: 2018/10/22  
License: Apache 2.0  


## Compile the code
$ cd colcon_ws/src  
$ git clone -b jazzy https://github.com/NcuMathRoboticsLab/hypharos_minibot.git   
$ cd ..  
$ colcon build --symlink-install

Or Download this this code to pi\colcon_ws\src.   
Unzip hypharos_minibot.zip to replace the original code.
  
$ cd colcon_ws  
$ colcon build --symlink-install  

## Run the code   
$ ros2 launch hypharos_minibot project_sample.launch.py

## rviz
$ rviz  
Press "Add" button in rviz, then select "Marker"  
Set fixed frame as "target"  
![alt text](https://github.com/kuoshih/hypharos_minibot/blob/master/document/target.png)  
## Edit code  
You can edit src/main.cpp for your project.

## About Minibot
More information about Minibot can be found https://github.com/Hypha-ROS/hypharos_minibot.   
