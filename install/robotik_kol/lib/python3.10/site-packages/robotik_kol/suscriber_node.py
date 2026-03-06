import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import numpy as np

# Kol uzunlukları
L1 = 10  # omuz → dirsek
L2 = 8   # dirsek → uç

class RobotikKolSubscriber(Node):
    def __init__(self):
        super().__init__('robotik_kol_subscriber')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            '/kol_hedef',
            self.hedef_alindi,
            10
        )
        self.get_logger().info('Robotik Kol Subscriber başladı, dinliyorum...')

    def inverse_kinematics(self, tx, ty):
        """Hedef konumdan eklem açılarını hesapla"""
        dist = np.sqrt(tx**2 + ty**2)
        dist = np.clip(dist, 0.1, L1 + L2 - 0.1)

        cos_t2 = (dist**2 - L1**2 - L2**2) / (2 * L1 * L2)
        cos_t2 = np.clip(cos_t2, -1, 1)
        t2 = np.arccos(cos_t2)

        k1 = L1 + L2 * np.cos(t2)
        k2 = L2 * np.sin(t2)
        t1 = np.arctan2(ty, tx) - np.arctan2(k2, k1)

        return np.degrees(t1), np.degrees(t2)

    def hedef_alindi(self, msg):
        x = msg.data[0]
        y = msg.data[1]
        z = msg.data[2]

        # IK ile açıları hesapla
        aci1, aci2 = self.inverse_kinematics(x, y)

        self.get_logger().info(
            f'Hedef → x:{x:.1f} y:{y:.1f} z:{z:.1f} | '
            f'Motor 1: {aci1:.1f}° | Motor 2: {aci2:.1f}°'
        )

def main():
    rclpy.init()
    node = RobotikKolSubscriber()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()