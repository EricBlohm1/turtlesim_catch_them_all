# #!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int64
from example_interfaces.srv import SetBool
 
class NumberCounterNode(Node): 
    def __init__(self):
        super().__init__("number_counter") 
        self.counter_ = 0
        self.subscriber_ = self.create_subscription(
            Int64, "number", self.callback_counter, 10
        )
        self.publisher_ = self.create_publisher(Int64, "number_count", 10)
        self.timer_ = self.create_timer(1, self.publish_count)


        self.server_ = self.create_service(
            SetBool, "reset_counter", self.callback_reset_counter)


        self.get_logger().info("Number Counter has started.")


    def callback_counter(self, msg: Int64):
        self.counter_ += msg.data

    def publish_count(self):
        msg = Int64()
        msg.data = self.counter_
        self.publisher_.publish(msg)

    def callback_reset_counter(self, request: SetBool.Request, response: SetBool.Response):
        if request.data: 
            self.counter_ = 0
            response.success = True
            response.message = "Counter successfully reset."
        else:
            response.success = False
            response.message = "Counter not reset."
            
        return response

 
 
def main(args=None):
    rclpy.init(args=args)
    node = NumberCounterNode() 
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()