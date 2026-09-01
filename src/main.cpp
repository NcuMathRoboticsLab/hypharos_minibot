/*
 Copyright 2018 NCU MATH.
 Developer: Kuo-Shih Tseng (kuoshih@math.ncu.edu.tw)
 Developer: An-You Xue (112201017@cc.ncu.edu.tw)
 Description: This code activate a node "main." 
 This node subscribes three topics -- imu_data, odom, and scan. 
 You can access data from three Callback functions.
 $Revision: 1.0 $,  2018.07.24 
 $Revision: 1.1 $,  2018.12.20, add a marker for users 
 $Revision: 2.0 $,  2025.4.25, chage to ros2 
 

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 
 Modifications Copyright 2025 NCU MathmaticRoboticsLab.
 This file has been modified by An-You Xue in 2025.
 Changes include:
 - Migrated to ROS 2 Jazzy
 - Updated to use rclcpp.h instead of ros.h
 - Code style adjustments and performance optimizations
 The original file was developed by Kuo-Shih Tseng (kuoshih@math.ncu.edu.tw)
*/

// %Tag(FULLTEXT)%
#include <chrono>
#include <cmath>
#include <functional>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "rclcpp/logger.hpp"
#include "rclcpp/qos.hpp"
#include "std_msgs/msg/string.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "sensor_msgs/msg/laser_scan.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "visualization_msgs/msg/marker.hpp"

#define RAD2DEG(x) ((x)*180./M_PI)

using namespace std::chrono_literals;

visualization_msgs::msg::Marker marker;
uint32_t shape = visualization_msgs::msg::Marker::CYLINDER;
rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr marker_pub;
int counter = 0;

void callback1() {
    float x = std::cos(0.174f * counter);
    float y = std::sin(0.174f * counter);
    marker.pose.position.x = x;
    marker.pose.position.y = y;
    ++counter;

    marker_pub->publish(marker);
}

void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
    RCLCPP_INFO(rclcpp::get_logger("minibot_sample"), "Vel-> Linear: [%f], Angular: [%f]", msg->twist.twist.linear.x,msg->twist.twist.angular.z);
}

void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg) {
    /*
    ROS_INFO("V x: [%f], y: [%f], z: [%f]", msg->linear_acceleration.x,msg->linear_acceleration.y,msg->linear_acceleration.z);
    ROS_INFO("W x: [%f], y: [%f], z: [%f]", msg->angular_velocity.x,msg->angular_velocity.y,msg->angular_velocity.z);
    */
}

void scanCallback(const sensor_msgs::msg::LaserScan::SharedPtr scan) {
    int count = scan->scan_time / scan->time_increment;
    printf("[YDLIDAR INFO]: I heard a laser scan %s[%d]:\n", scan->header.frame_id.c_str(), count);
    /*
    printf("[YDLIDAR INFO]: angle_range : [%f, %f]\n", RAD2DEG(scan->angle_min), RAD2DEG(scan->angle_max));
 
    for(int i = 0; i < count; i++) 
    {
        float degree = RAD2DEG(scan->angle_min + scan->angle_increment * i);
	    if(degree > -5 && degree< 5)
        {printf("[YDLIDAR INFO]: angle-distance : [%f, %f, %i]\n", degree, scan->ranges[i], i);}
    }
    */
}

void init_marker() {
    // Initialize marker's setting.
    // Set the frame ID and timestamp.  See the TF tutorials for information on these.
    marker.header.frame_id = "/target";
    rclcpp::Clock clock(RCL_ROS_TIME);
    marker.header.stamp = clock.now();

    // Set the namespace and id for this marker.  This serves to create a unique ID
    // Any marker sent with the same namespace and id will overwrite the old one
    marker.ns = "basic_shapes";
    marker.id = 0;
    // Set the marker type.  Initially this is CUBE, and cycles between that and SPHERE, ARROW, and CYLINDER
    marker.type = shape;

    // Set the marker action.  Options are ADD, DELETE, and new in ROS Indigo: 3 (DELETEALL)
    // Tag(ACTION)
    marker.action = visualization_msgs::msg::Marker::ADD;

    // Set the marker action.  Options are ADD, DELETE, and new in ROS Indigo: 3 (DELETEALL)
    // Tag(ACTION)
    marker.pose.position.x = 0;
    marker.pose.position.y = 0;
    marker.pose.position.z = 0;
    marker.pose.orientation.x = 0.0;
    marker.pose.orientation.y = 0.0;
    marker.pose.orientation.z = 0.0;
    marker.pose.orientation.w = 1.0;

    // Set the scale of the marker -- 1x1x1 here means 1m on a side
    marker.scale.x = 0.1;
    marker.scale.y = 0.1;
    marker.scale.z = 0.2;

    // Set the color -- be sure to set alpha to something non-zero!
    marker.color.r = 0.0f;
    marker.color.g = 1.0f;
    marker.color.b = 0.0f;
    marker.color.a = 1.0;

    //Tag(LIFETIME)
    marker.lifetime = rclcpp::Duration(0, 0);

}

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);

    auto node = rclcpp::Node::make_shared("minibot_sample");

    auto sensor_qos = rclcpp::SensorDataQoS();
    auto odom_qos = rclcpp::QoS(rclcpp::KeepLast(10));
    auto marker_qos = rclcpp::QoS(rclcpp::KeepLast(1)).reliable().transient_local();

    auto imu_sub = node->create_subscription<sensor_msgs::msg::Imu>(
        "/imu_data", sensor_qos, imuCallback);

    auto odom_sub = node->create_subscription<nav_msgs::msg::Odometry>(
        "/odom", odom_qos, odomCallback);

    auto scan_sub = node->create_subscription<sensor_msgs::msg::LaserScan>(
        "/scan", sensor_qos, scanCallback);

    auto timer = node->create_wall_timer(
        100ms, callback1);

    marker_pub = node->create_publisher<visualization_msgs::msg::Marker>(
        "/visualization_marker", marker_qos);

    init_marker();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}