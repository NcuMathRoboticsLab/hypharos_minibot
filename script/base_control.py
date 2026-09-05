#!/usr/bin/python3
# Copyright 2018 HyphaROS Workshop.
# Developer: HaoChih, LIN (hypha.ros@gmail.com)
# Developer: An-You Xue (112201017@cc.ncu.edu.tw)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
import serial
import tf2_ros
import tf_transformations
from geometry_msgs.msg import TransformStamped, TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy


class BaseControl(Node):
    def __init__(self):
        super().__init__('base_control')

        # Declare parameters with defaults
        self.declare_parameter('base_id', 'base_footprint')  # base link
        self.declare_parameter('odom_id', 'odom')  # odom link
        self.declare_parameter('port', '/dev/stm32base')  # device port
        self.declare_parameter('baudrate', 115200)  # baudrate
        self.declare_parameter('odom_freq', '50.0')  # hz of odom pub
        self.declare_parameter('wheel_separation', '0.158')  # unit: meter
        self.declare_parameter('wheel_radius', '0.032')  # unit: meter
        self.declare_parameter('vx_cov', '1.0')  # covariance for Vx measurement
        self.declare_parameter('vyaw_cov', '1.0')  # covariance for Vyaw measurement
        self.declare_parameter('odom_topic', '/odom')  # topic name
        self.declare_parameter('pub_tf', 'True')  # whether publishes TF or not
        self.declare_parameter('debug_mode', 'False')  # true for detail info

        # Get parameters
        self.baseId = self.get_parameter('base_id').value
        self.odomId = self.get_parameter('odom_id').value
        self.device_port = self.get_parameter('port').value
        self.baudrate = self.get_parameter('baudrate').value
        self.odom_freq = float(self.get_parameter('odom_freq').value)
        self.wheelSep = float(self.get_parameter('wheel_separation').value)
        self.wheelRad = float(self.get_parameter('wheel_radius').value)
        self.VxCov = float(self.get_parameter('vx_cov').value)
        self.VyawCov = float(self.get_parameter('vyaw_cov').value)
        self.odom_topic = self.get_parameter('odom_topic').value
        self.pub_tf = bool(self.get_parameter('pub_tf').value)
        self.debug_mode = bool(self.get_parameter('debug_mode').value)

        # Serial Communication
        try:
            self.serial = serial.Serial(self.device_port, self.baudrate, timeout=10)
            self.get_logger().info('Flusing first 50 data readings ...')
            for x in range(0, 50):
                data = self.serial.read()
                time.sleep(0.01)

        except serial.serialutil.SerialException:
            self.get_logger().info(
                'Can not receive data from the port: '
                + self.device_port
                + '. Did you specify the correct port ?'
            )
            self.serial.close
            sys.exit(0)

        self.get_logger().info('Communication success !')

        # ROS handler
        self.qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
        )

        self.sub = self.create_subscription(
            TwistStamped,
            '/cmd_vel',
            self.cmdCB,
            self.qos,
        )
        self.pub = self.create_publisher(
            Odometry,
            self.odom_topic,
            self.qos,
        )
        self.timer_odom = self.create_timer(
            1.0 / self.odom_freq,
            self.timerOdomCB,
        )
        self.timer_cmd = self.create_timer(
            0.1,
            self.timerCmdCB,
        )  # 10Hz
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        # variables
        self.trans_x = 0.0  # cmd
        self.rotat_z = 0.0
        self.WL_send = 0.0
        self.WR_send = 0.0
        self.current_time = self.get_clock().now()
        self.previous_time = self.get_clock().now()
        self.pose_x = 0.0  # SI
        self.pose_y = 0.0
        self.pose_yaw = 0.0

        # reading loop
        # while True:
        #     reading = self.serial.read(6)
        #     if reading[0] == 255 and reading[1] == 254:
        #         self.data = reading
        #     else:
        #         self.serial.read(1)

    def cmdCB(self, data: TwistStamped):
        self.trans_x = data.twist.linear.x
        self.rotat_z = data.twist.angular.z

    def timerOdomCB(self):
        # Serial read & publish
        try:
            data = self.data

            # Normal mode
            if len(data) == 6:
                WL = float(
                    (data[2] * 256 + data[3] - 500) * 100.0 / 1560.0 * 2 * math.pi
                )  # unit: rad/sec
                WR = float(
                    (data[4] * 256 + data[5] - 500) * 100.0 / 1560.0 * 2 * math.pi
                )
            else:
                print(
                    'Error Value! header1: '
                    + str(data[0])
                    + ', header2: '
                    + str(data[1])
                )

            # Twist
            VL = WL * self.wheelRad  # V = omega * radius, unit: m/s
            VR = WR * self.wheelRad
            Vyaw = (VR - VL) / self.wheelSep
            Vx = (VR + VL) / 2.0

            # Pose
            self.current_time = self.get_clock().now()
            dt = (self.current_time - self.previous_time).to_sec()
            self.previous_time = self.current_time
            self.pose_x = self.pose_x + Vx * math.cos(self.pose_yaw) * dt
            self.pose_y = self.pose_y + Vx * math.sin(self.pose_yaw) * dt
            self.pose_yaw = self.pose_yaw + Vyaw * dt
            pose_quat = tf_transformations.quaternion_from_euler(0, 0, self.pose_yaw)

            # Publish Odometry
            msg = Odometry()
            msg.header.stamp = self.current_time
            msg.header.frame_id = self.odomId
            msg.child_frame_id = self.baseId
            msg.pose.pose.position.x = self.pose_x
            msg.pose.pose.position.y = self.pose_y
            msg.pose.pose.position.z = 0.0
            msg.pose.pose.orientation.x = pose_quat[0]
            msg.pose.pose.orientation.y = pose_quat[1]
            msg.pose.pose.orientation.z = pose_quat[2]
            msg.pose.pose.orientation.w = pose_quat[3]
            msg.twist.twist.linear.x = Vx
            msg.twist.twist.angular.z = Vyaw
            for i in range(36):
                msg.twist.covariance[i] = 0
            msg.twist.covariance[0] = self.VxCov
            msg.twist.covariance[35] = self.VyawCov
            msg.pose.covariance = msg.twist.covariance
            self.pub.publish(msg)

            # TF Broadcaster
            if self.pub_tf:
                t = TransformStamped()
                t.header.stamp = self.current_time
                t.header.frame_id = self.odomId
                t.child_frame_id = self.baseId
                t.transform.translation.x = self.pose_x
                t.transform.translation.y = self.pose_y
                t.transform.translation.z = 0.0
                t.transform.rotation.x = pose_quat[0]
                t.transform.rotation.y = pose_quat[1]
                t.transform.rotation.z = pose_quat[2]
                t.transform.rotation.w = pose_quat[3]

                self.tf_broadcaster.sendTransform(t)

            # Debug mode
            if self.debug_mode:
                if len(data) == 6:
                    header_1 = data[0]
                    header_2 = data[1]
                    tx_1 = data[2]
                    tx_2 = data[3]
                    tx_3 = data[4]
                    tx_4 = data[5]
                    self.get_logger().info(
                        f'[Debug] header_1:{header_1}, header_2:{header_2}, tx_1:{tx_1}, tx_2:{tx_2}, tx_3:{tx_3}, tx_4:{tx_4}'
                    )

        except Exception:
            # self.get_logger().info("Error in sensor value !")
            pass

    def timerCmdCB(self):
        # send cmd to motor
        WR = (self.trans_x + self.wheelSep / 2.0 * self.rotat_z) / self.wheelRad  # unit: rad/sec
        WL = (self.trans_x - self.wheelSep / 2.0 * self.rotat_z) / self.wheelRad
        self.WR_send = int(WR / 100.0 * 1560.0 / 2 / math.pi)
        self.WL_send = int(WL / 100.0 * 1560.0 / 2 / math.pi)
        R_forward = 1  # 0: reverse, >0: forward
        L_forward = 1  # 0: reverse, >0: forward
        if self.WR_send < 0:
            R_forward = 0
            self.WR_send = -self.WR_send
        if self.WL_send < 0:
            L_forward = 0
            self.WL_send = -self.WL_send
        if self.WR_send > 255:
            self.WR_send = 255
        if self.WL_send > 255:
            self.WL_send = 255

        output = [255, 254, self.WL_send, L_forward, self.WR_send, R_forward]
        # print output
        self.serial.write(output)


def main(args=None):
    try:
        rclpy.init(args=args)
        node = BaseControl()
        node.get_logger().info('HyphaROS MiniBot Base Control ...')
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.serial.close()

    finally:
        print('Shutting down')
        if node and node is not None:
            node.serial.close()
            node.destroy_node()


if __name__ == '__main__':
    main()
