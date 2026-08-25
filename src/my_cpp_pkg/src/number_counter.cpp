#include "rclcpp/rclcpp.hpp"
#include "example_interfaces/msg/int64.hpp"
#include "example_interfaces/srv/set_bool.hpp"
using namespace std::placeholders;
using namespace std::chrono_literals;

class NumberCounterNode : public rclcpp::Node 
{
public:
    NumberCounterNode() : Node("number_counter"), counter_(0.0)
    {
        subscriber_ = this->create_subscription<example_interfaces::msg::Int64>(
            "number", 10 , std::bind(&NumberCounterNode::callbackNumberCounter, this, _1)
        );
        publisher_ = this->create_publisher<example_interfaces::msg::Int64>("number_count",10);
        timer_ = this->create_wall_timer(0.5s,std::bind(&NumberCounterNode::publishCounter,this));


        server_ = this->create_service<example_interfaces::srv::SetBool>("reset_counter", std::bind(&NumberCounterNode::callBackResetCounter,this, _1,_2));

        RCLCPP_INFO(this->get_logger(), "Number counter has been started.");
    }
 
private:
    void callbackNumberCounter(const example_interfaces::msg::Int64::SharedPtr msg){
        counter_+=msg->data; 
    }

    void publishCounter(){
        auto msg = example_interfaces::msg::Int64();
        msg.data = this->counter_;
        publisher_->publish(msg);
    }

    void callBackResetCounter(const example_interfaces::srv::SetBool::Request::SharedPtr request,
                            const example_interfaces::srv::SetBool::Response::SharedPtr response){
            if(request->data){
                this->counter_=0;
                response->success = true;
                response->message = "Counter was reset";
            }else{
                response->success = false;
                response->message = "Counter not reset";
            }

    }

    int32_t counter_; 
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Subscription<example_interfaces::msg::Int64>::SharedPtr subscriber_;
    rclcpp::Publisher<example_interfaces::msg::Int64>::SharedPtr publisher_;

    rclcpp::Service<example_interfaces::srv::SetBool>::SharedPtr server_; 

};
 
int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<NumberCounterNode>(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}