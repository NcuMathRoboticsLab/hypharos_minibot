#!/usr/bin/python3

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # base_footprint → base_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_footprint2base_link',
            output='screen',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0.05',        # x, y, z (m)
                '--roll', '0', '--pitch', '0', '--yaw', '0',  # roll, pitch, yaw (rad)
                '--frame-id', 'base_footprint',               # parent frame
                '--child-frame-id', 'base_link'               # child frame
            ],
        ),

        # base_link → laser_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link2laser_link',
            output='screen',
            arguments=[
                '--x', '-0.03', '--y', '0', '--z', '0.11',
                '--roll', '0', '--pitch', '0', '--yaw', '0',
                '--frame-id', 'base_link',
                '--child-frame-id', 'laser_link'
            ],
        ),

        # base_link → imu_link
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link2imu',
            output='screen',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0',
                '--roll', '0', '--pitch', '0', '--yaw', '3.1415926',
                '--frame-id', 'base_link',
                '--child-frame-id', 'imu_link'
            ],
        ),
    ])
