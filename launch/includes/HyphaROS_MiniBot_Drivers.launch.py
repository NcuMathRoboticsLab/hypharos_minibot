#!/usr/bin/python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def launch_setup(context, *args, **kwargs):
    wheel_separation = LaunchConfiguration('wheel_separation').perform(context)
    wheel_radius = LaunchConfiguration('wheel_radius').perform(context)
    use_imu = LaunchConfiguration('use_imu').perform(context)

    tf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('hypharos_minibot'), 'launch', 'includes', 'minibot_tf.launch.py')
        )
    )

    ydlidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ydlidar_ros2_driver'), 'launch', 'ydlidar_launch.py')
        )
    )

    base_control_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('hypharos_minibot'), 'launch', 'includes', 'minibot_base.launch.py')
        ),
        launch_arguments={
            'wheel_separation': wheel_separation,
            'wheel_radius': wheel_radius,
        }.items()
    )

    imu_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('hypharos_minibot'), 'launch', 'includes', 'minibot_imu.launch.py')
        ),
        condition=IfCondition(use_imu),
    )

    return [
        tf_launch,
        ydlidar_launch,
        base_control_launch,
        imu_launch
    ]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('wheel_separation', default_value='0.158', description='Separation between wheels (m)'),
        DeclareLaunchArgument('wheel_radius', default_value='0.032', description='Wheel radius (m)'),
        DeclareLaunchArgument('use_imu', default_value='false', description='Use IMU or not'),
        OpaqueFunction(function=launch_setup)
    ])