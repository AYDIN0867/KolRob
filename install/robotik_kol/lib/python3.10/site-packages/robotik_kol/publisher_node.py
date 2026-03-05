import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray

class RobotikKolPublisher(Node):
    def __init__(self):
        super().__init__('robotik_kol_publisher')
        self.publisher = self.create_publisher(
            Float32MultiArray, 
            '/kol_hedef', 
            10
        )
        self.timer = self.create_timer(0.5, self.hedef_gonder)
        self.x = 5.0
        self.get_logger().info('Robotik Kol Publisher başladı!')

    def hedef_gonder(self):
        msg = Float32MultiArray()
        msg.data = [self.x, 8.0, 3.0]  # x, y, z hedef
        self.publisher.publish(msg)
        self.get_logger().info(f'Hedef gönderildi: x={self.x:.1f}')
        self.x += 0.5
        if self.x > 12.0:
            self.x = -12.0

def main():
    rclpy.init()
    node = RobotikKolPublisher()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
