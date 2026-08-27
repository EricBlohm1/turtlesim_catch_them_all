# Simple turtlesim application to test ROS2 nodes, services, topics, custom interfaces, and launch files. 
The application spawns turtles at a specific frequency, and a master turtle will catch the closest one. Steering is done using a simple P controller running on 50Hz. 

![Turtle-Catch-Them-All](/turtlesim_catch_them_all_.gif)

1. Clone the repo: ``git clone git@github.com:EricBlohm1/turtlesim_catch_them_all.git`` 

2. Build: ``colcon build`` 

3. Run application: ``ros2 launch turtle_catch_them_all_bringup turtle_catch_them_all.launch.xml`` 
