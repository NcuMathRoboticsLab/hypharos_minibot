#!/usr/bin/python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='hypharos_minibot',
            executable='mpu6050_node.py',
            name='imu_auto',
            output='screen',
            parameters=[{
                'port': '/dev/mpu6050',
                'imu_frame': 'imu_link',
                'baudrate': 57600,
            }],
        ),
    ])
