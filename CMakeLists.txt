cmake_minimum_required(VERSION 3.8)
project(hypharos_minibot)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS_DEBUG "-g -O3")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

add_executable(main src/main.cpp)
ament_target_dependencies(main
  rclcpp
  sensor_msgs
  geometry_msgs
  std_msgs
  tf2
  nav_msgs
  visualization_msgs
)

install(TARGETS
  main
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  script/base_control.py
  script/mpu6050_node.py
  script/getimu.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
