import math
from typing import TYPE_CHECKING
from ..flight_state import FlightState
from .handler import FlightStateHandler

if TYPE_CHECKING:
    from ..flight_test_node import FlightTestNode


class MovingToTargetHandler(FlightStateHandler):
    def handle(self, node: "FlightTestNode") -> None:
        if node.status is None or not node.status.armed:
            node.fail("Drone disarmed unexpectedly during flight")
            return

        if node.odometry is None or node.target_x is None:
            return

        current_x = node.odometry.pose.pose.position.x
        current_y = node.odometry.pose.pose.position.y

        dx = node.target_x - current_x
        dy = node.target_y - current_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance <= node.POSITION_TOLERANCE:
            node.publish_velocity(0.0, 0.0)

            node.get_logger().info(
                f"Target reached. Actual position: "
                f"x={current_x:.2f} m, y={current_y:.2f} m"
            )
            node.get_logger().info(
                f"Positioning error: {distance:.3f} m "
                f"(tolerance: {node.POSITION_TOLERANCE} m)"
            )
            node.get_logger().info("Starting landing")

            node.state = FlightState.LANDING
            return

        speed = node.MAX_SPEED * min(1.0, distance / node.SLOWDOWN_RADIUS)
        speed = max(node.MIN_SPEED, min(node.MAX_SPEED, speed))

        vx = speed * dx / distance
        vy = speed * dy / distance

        node.publish_velocity(vx, vy)
