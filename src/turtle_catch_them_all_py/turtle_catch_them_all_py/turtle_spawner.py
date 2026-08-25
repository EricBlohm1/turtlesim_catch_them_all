#!/usr/bin/env python3
import rclpy
import random
from functools import partial
from rclpy.node import Node
from turtlesim.srv import Kill, Spawn
from turtle_catch_them_all_interfaces.msg import Turtle, TurtleArray
from turtle_catch_them_all_interfaces.srv import CatchTurtle
 
class TurtleSpawnerNode(Node):
    def __init__(self):
        super().__init__("turtle_spawner") 
        self.alive_turtles_ = TurtleArray()
        self.turtle_counter_ = 2 # turtle1 exist from turtlesim

        self.spawn_client_ = self.create_client(Spawn, "spawn")
        self.kill_client_ = self.create_client(Kill, "kill")

        self.spawn_timer_ = self.create_timer(2.0, self.call_spawn_turtle)


        self.alive_turtles_publisher_ = self.create_publisher(
            TurtleArray, "alive_turtles", 10
        )

        self.remove_caught_turtle_server_ = self.create_service(
            CatchTurtle, "catch_turtle", self.call_remove_turtle
        )

        self.get_logger().info("Turtle Spawner node has been started.")


    def call_remove_turtle(self, request: CatchTurtle.Request, response : CatchTurtle.Response):
        turtle_name_to_remove = request.name

        while not self.kill_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Kill server")
        kill_request = Kill.Request()
        kill_request.name = turtle_name_to_remove


        future = self.kill_client_.call_async(kill_request)
        future.add_done_callback(
            partial(self.callback_call_remove_turtle, turtle_name=turtle_name_to_remove)
        )

        response.kill_requested = True
        return response

    def callback_call_remove_turtle(self,future, turtle_name):
        self.alive_turtles_.turtles = [t for t in self.alive_turtles_.turtles if t.name != turtle_name]
        self.alive_turtles_publisher_.publish(self.alive_turtles_)

    
    def call_spawn_turtle(self):
        while not self.spawn_client_.wait_for_service(1.0):
            self.get_logger().warn("Waiting for Spawn server")

        x = random.uniform(0.0, 11.0)
        y = random.uniform(0.0, 11.0)

        turtle = Turtle()
        turtle.name = "turtle" + str(self.turtle_counter_)
        turtle.x = x
        turtle.y = y

        request = Spawn.Request()
        request.x = turtle.x
        request.y = turtle.y
        request.name = turtle.name

        if(len(self.alive_turtles_.turtles)>10):
            return

        future = self.spawn_client_.call_async(request)
        future.add_done_callback(
            partial(self.callback_call_spawn_turtle, turtle=turtle)
        )

        self.turtle_counter_ +=1


    def callback_call_spawn_turtle(self, future, turtle: Turtle):
        response: Spawn.Response = future.result()
        self.get_logger().info("Got response from Spawn server: " +  response.name)

        self.alive_turtles_.turtles.append(turtle)
        self.alive_turtles_publisher_.publish(self.alive_turtles_)
        self.get_logger().info("Appended new turtle: " + turtle.name)

 
 
def main(args=None):
    rclpy.init(args=args)
    node = TurtleSpawnerNode() 
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()