#!/usr/bin/python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    wheel_separation = LaunchConfiguration('wheel_separation').perform(context)
    wheel_radius = LaunchConfiguration('wheel_radius').perform(context)
    odom_topic = LaunchConfiguration('odom_topic').perform(context)
    pub_tf_str = LaunchConfiguration('pub_tf').perform(context)
    pub_tf_bool = pub_tf_str.lower() == 'true'

    base_control_node = Node(
        package='hypharos_minibot',
        executable='base_control.py',
        name='base_control',
        output='screen',
        parameters=[{
            'port': '/dev/stm32base',
            'baudrate': 115200,
            'base_id': 'base_footprint',
            'odom_id': 'odom',
            'odom_topic': odom_topic,
            'pub_tf': pub_tf_bool,
            'wheel_separation': wheel_separation,
            'wheel_radius': wheel_radius,
        }],
    )

    return [
        base_control_node
    ]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('wheel_separation', default_value='0.158', description='Separation between wheels (m)'),
        DeclareLaunchArgument('wheel_radius', default_value='0.032', description='Wheel radius (m)'),
        DeclareLaunchArgument('odom_topic', default_value='/odom', description='Odom topic name'),
        DeclareLaunchArgument('pub_tf', default_value='true', description='Publish TF or not'),
        OpaqueFunction(function=launch_setup)
    ])