#!/usr/bin/python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    pkg_share = get_package_share_directory('hypharos_minibot')

    driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'includes', 'HyphaROS_MiniBot_Drivers.launch.py')
        ),
        launch_arguments = {
            'wheel_separation': LaunchConfiguration('wheel_separation').perform(context),
            'wheel_radius': LaunchConfiguration('wheel_radius').perform(context),
            'use_imu': LaunchConfiguration('use_imu').perform(context),
        }.items()
    )

    minibot_node = Node(
        package='hypharos_minibot',
        executable='main',
        name='main',
        output='log',
    )

    tf_base2target = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base2target',
        output='log',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'base_footprint',
            '--child-frame-id', 'target'
        ],
    )

    return [
        driver_launch, 
        minibot_node, 
        tf_base2target
    ]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'wheel_separation',
            default_value='0.158',
            description='Separation between wheels (m)'
        ),
        DeclareLaunchArgument(
            'wheel_radius',
            default_value='0.032',
            description='Wheel radius (m)'
        ),
        DeclareLaunchArgument(
            'use_imu',
            default_value='false',
            description='Enable IMU driver'
        ),
        OpaqueFunction(function=launch_setup),
    ])
