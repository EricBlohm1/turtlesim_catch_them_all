#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from turtle_catch_them_all_interfaces.msg import TurtleArray, Turtle
from turtle_catch_them_all_interfaces.srv import CatchTurtle

class TurtleControllerNode(Node): 
    def __init__(self):
        super().__init__("turtle_controller") 
        self.x_ = None
        self.y_ = None
        self.theta_ = None
        self.target_ = None

        self.kp_vel_ = 1.5
        self.kp_ang_ = 4

        self.pose_subscriber_ = self.create_subscription(
            Pose, "turtle1/pose" ,self.callback_pose, 10
        )

        self.alive_turtles_subscriber_ = self.create_subscription(
            TurtleArray , "alive_turtles" ,self.callback_alive_turtles, 10
        )

        self.velocity_publisher_ = self.create_publisher(
            Twist, "turtle1/cmd_vel", 10
        )

        self.turtle_caught_client_ = self.create_client(
            CatchTurtle, "catch_turtle"
        )

        self.control_timer_ = self.create_timer(
            0.02, self.control_loop
        )

        self.get_logger().info("Turtle controller node started.")


    def call_remove_turtle(self,turtle):
        while not self.turtle_caught_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Turtle caught server")

        request = CatchTurtle.Request()
        request.name = turtle.name

        future = self.turtle_caught_client_.call_async(request)
        future.add_done_callback(self.callback_call_remove_turtle)


    def callback_call_remove_turtle(self,future):
        response = future.result()
        if response.kill_requested:
            self.target_ = None


    def callback_alive_turtles(self, msg: TurtleArray):
        if self.target_ is not None:
            return
        
        shortest_distance = math.inf
        for turtle in msg.turtles:
            diffX = turtle.x - self.x_
            diffY = turtle.y - self.y_
            dist = math.sqrt(diffX*diffX+diffY*diffY)
            if dist < shortest_distance:
                shortest_distance = dist
                self.target_ = turtle
            
        

    def callback_pose(self, msg: Pose):
        self.x_ = msg.x
        self.y_ = msg.y
        self.theta_ = msg.theta

    def control_loop(self):
        if self.x_ is None:
            return

        if self.target_ is None:
            return
        
        ex = self.target_.x-self.x_
        ey = self.target_.y-self.y_

        dist = math.sqrt(ex*ex+ey*ey)
        if dist < 0.25:
            self.call_remove_turtle(self.target_)
            return

        u = math.sqrt(ex*ex+ey*ey)
        theta_target = math.atan2(ey,ex)
        theta_error = theta_target-self.theta_
        if theta_error > math.pi:
            theta_error -= 2 * math.pi
        elif theta_error < -math.pi:
            theta_error += 2 * math.pi

        msg = Twist()
        msg.linear.x = self.kp_vel_*u
        msg.angular.z = self.kp_ang_*theta_error

        self.velocity_publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TurtleControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()