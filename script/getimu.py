#!/usr/bin/python3
# Copyright 2018 HyphaROS Workshop.
# Developer: HaoChih, LIN (hypha.ros@gmail.com)
# Developer: Kuo-Shih Tseng (kuoshih@math.ncu.edu.tw)
# Developer: An-You Xue (112201017@cc.ncu.edu.tw)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modifications Copyright 2025 NCU MathmaticRoboticsLab.
# This file has been modified by An-You Xue in 2025.
# Changes include:
# - Migrated to ROS 2 Jazzy
# - Updated to use rclpy instead of rospy
# - Code style adjustments and performance optimizations
# The original file was developed by HaoChih, LIN (hypha.ros@gmail.com)

import math
import sys
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from mpu6050 import mpu6050
from sensor_msgs.msg import Imu


MAX_N = 500
f = open('imu_data', 'w')


class IMUNode(Node):
    def __init__(self):
        super().__init__('mpu6050_node')

        # ROS Parameters
        # Declare parameters:
        self.declare_parameter('ori_cov', '0.0025')       # Orientation covariance
        self.declare_parameter('vel_cov', '0.02')         # Angular velocity covariance
        self.declare_parameter('acc_cov', '0.04')         # Linear acceleration covariance
        self.declare_parameter('imu_i2c', 0x68)           # I2C device No
        self.declare_parameter('imu_link', 'imu_link')    # imu_link name
        self.declare_parameter('pub_freq', 50)            # hz of imu pub
        # Get Parameters:
        self.ori_cov = float(self.get_parameter('ori_cov').value)
        self.vel_cov = float(self.get_parameter('vel_cov').value)
        self.acc_cov = float(self.get_parameter('acc_cov').value)
        self.imu_i2c = self.get_parameter('imu_i2c').value
        self.imu_link = self.get_parameter('imu_link').value
        self.pub_freq = self.get_parameter('pub_freq').value

        # I2C Communication:
        try:
            self.sensor = mpu6050(0x68)
            self.get_logger().info('Flusing first 50 data readings ...')
            for x in range(0, 50):
                gyro_data = self.sensor.get_gyro_data()
                time.sleep(0.01)
        except Exception:
            self.get_logerr().info(
                'Can not receive data from the I2C device: '
                + self.imu_i2c
                + '. Did you specify the correct No. ?'
            )
            sys.exit(0)

        self.get_logger().info('Communication success !')
        self.seq = 0

        # ROS handler
        qos_profile = qos_profile_sensor_data
        qos_profile.depth = 1
        self.pub = self.create_publisher(Imu, 'imu/data_raw', qos_profile)
        self.timer = self.create_timer(1.0 / self.pub_freq, self.timerCB)

    def timerCB(self):
        # I2C Serial read & publish
        try:
            gyro_data = self.sensor.get_gyro_data()
            accel_data = self.sensor.get_accel_data()

            imuMsg = Imu()
            imuMsg.header.stamp = self.get_clock().now().to_msg()
            imuMsg.header.frame_id = self.imu_link
            imuMsg.orientation_covariance[0] = self.ori_cov
            imuMsg.orientation_covariance[4] = self.ori_cov
            imuMsg.orientation_covariance[8] = self.ori_cov
            imuMsg.angular_velocity_covariance[0] = self.vel_cov
            imuMsg.angular_velocity_covariance[4] = self.vel_cov
            imuMsg.angular_velocity_covariance[8] = self.vel_cov
            imuMsg.linear_acceleration_covariance[0] = self.acc_cov
            imuMsg.linear_acceleration_covariance[4] = self.acc_cov
            imuMsg.linear_acceleration_covariance[8] = self.acc_cov
            imuMsg.angular_velocity.x = float(gyro_data['x'])
            imuMsg.angular_velocity.y = float(gyro_data['y'])
            imuMsg.angular_velocity.z = float(gyro_data['z'])
            imuMsg.linear_acceleration.x = float(accel_data['x'])
            imuMsg.linear_acceleration.y = float(accel_data['y'])
            imuMsg.linear_acceleration.z = float(accel_data['z'])
            self.pub.publish(imuMsg)
            self.seq += 1

            if self.seq == 1:
                print('Collecting IMU data')
            if self.seq <= MAX_N:
                f.write(str(self.seq) + '\n')
                f.write(str(gyro_data['x']) + '\n')
                f.write(str(gyro_data['y']) + '\n')
                f.write(str(gyro_data['z']) + '\n')
                f.write(str(accel_data['x']) + '\n')
                f.write(str(accel_data['y']) + '\n')
                f.write(str(accel_data['z']) + '\n')
            if self.seq == MAX_N:
                print('Collected all IMU data')
                f.close()

        except Exception:
            self.get_logger().info('Error in sensor value !')


def main(args=None):
    try:
        # ROS Init
        rclpy.init(args=args)
        # Constract IMUNode Obj
        imu = IMUNode()
        imu.get_logger().info('Start Reading ...')
        rclpy.spin(imu)

    except KeyboardInterrupt:
        print('Shutting down')

    finally:
        f.close()
        imu.destroy_node()


if __name__ == '__main__':
    main()
