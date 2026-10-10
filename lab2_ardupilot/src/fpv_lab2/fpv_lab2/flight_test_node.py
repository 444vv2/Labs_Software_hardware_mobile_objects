from rclpy.node import Node

from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger
from geometry_msgs.msg import TwistStamped

from ardupilot_msgs.msg import Status
from ardupilot_msgs.srv import ArmMotors, ModeSwitch, Takeoff

from .flight_state import FlightState
from .handlers import HANDLERS


class FlightTestNode(Node):
    GUIDED_MODE = 4
    LAND_MODE = 9

    TAKEOFF_ALTITUDE = 4.5
    HOVER_DURATION = 30.0

    DELTA_X = 7.6
    DELTA_Y = 0.8

    POSITION_TOLERANCE = 0.25
    MAX_SPEED = 1.5
    MIN_SPEED = 0.2
    SLOWDOWN_RADIUS = 3.0

    def __init__(self):
        super().__init__("flight_test")

        self.state = FlightState.WAITING_FOR_SYSTEM
        self.request_in_progress = False

        self.status = None
        self.odometry = None
        self.hover_started_at = None

        self.start_x = None
        self.start_y = None
        self.target_x = None
        self.target_y = None

        self._handlers = HANDLERS
        self.status_subscription = self.create_subscription(
            Status,
            "/ap/v1/status",
            self.status_callback,
            10,
        )
        self.odometry_subscription = self.create_subscription(
            Odometry,
            "/odometry",
            self.odometry_callback,
            10,
        )

        self.prearm_client = self.create_client(
            Trigger,
            "/ap/v1/prearm_check",
        )

        self.mode_client = self.create_client(
            ModeSwitch,
            "/ap/v1/mode_switch",
        )

        self.arm_client = self.create_client(
            ArmMotors,
            "/ap/v1/arm_motors",
        )

        self.takeoff_client = self.create_client(
            Takeoff,
            "/ap/v1/experimental/takeoff",
        )

        self.cmd_vel_publisher = self.create_publisher(
            TwistStamped,
            "/ap/v1/cmd_vel",
            10,
        )

        self.timer = self.create_timer(0.2, self.control_loop)

        self.get_logger().info("Flight test node started")
        self.get_logger().info("Waiting for ArduPilot and ROS services...")

    def status_callback(self, message):
        self.status = message

    def odometry_callback(self, message):
        self.odometry = message

        if self.start_x is None:
            self.start_x = message.pose.pose.position.x
            self.start_y = message.pose.pose.position.y
            self.target_x = self.start_x - self.DELTA_X
            self.target_y = self.start_y - self.DELTA_Y

            self.get_logger().info(
                f"Start position: x={self.start_x:.2f} m, "
                f"y={self.start_y:.2f} m"
            )
            self.get_logger().info(
                f"Target position (variant 11, "
                f"dx={self.DELTA_X}, dy={self.DELTA_Y}): "
                f"x={self.target_x:.2f} m, y={self.target_y:.2f} m"
            )

    def services_ready(self):
        return (
            self.prearm_client.service_is_ready()
            and self.mode_client.service_is_ready()
            and self.arm_client.service_is_ready()
            and self.takeoff_client.service_is_ready()
        )

    def control_loop(self):
        handler = self._handlers.get(self.state)
        if handler is not None:
            handler.handle(self)

    def call_mode_switch(self, mode, callback):
        self.request_in_progress = True

        request = ModeSwitch.Request()
        request.mode = mode

        future = self.mode_client.call_async(request)
        future.add_done_callback(callback)

        self.get_logger().info(f"Requesting flight mode {mode}")

    def publish_velocity(self, vx: float, vy: float) -> None:
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.twist.linear.x = vx
        msg.twist.linear.y = vy
        msg.twist.linear.z = 0.0
        self.cmd_vel_publisher.publish(msg)

    def fail(self, message):
        self.get_logger().error(message)
        self.state = FlightState.ERROR
