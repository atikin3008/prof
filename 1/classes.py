import enum
from motion import core
from logger import Logger

logger = Logger()


class ArmMode(enum.Enum):
    EmergencyStop = -1
    Pause = 0
    Joint = 1
    Cartesian = 2


class ARM:
    def __init__(self):
        self.mode: ArmMode = ArmMode.Pause
        self.robot = core.RobotControl()
        if self.robot.connect():
            logger.log("Рука успешно подключена!")
        else:
            logger.log("Рука не подключена!")
            raise RuntimeError("Ошибка подключения к руке")
        self.robot.pause()

    def emergency(self):
        self.mode = ArmMode.EmergencyStop
        self.robot.stop()

    def set_mode(self, arm_mode: ArmMode):
        if arm_mode == ArmMode.Pause:
            self.robot.pause()
        elif arm_mode == ArmMode.Cartesian:
            self.robot.manualCartMode()
        elif arm_mode == ArmMode.Joint:
            self.robot.manualJointMode()
        self.mode = arm_mode

    def move(self, position: tuple[int | float]):
        if self.mode == ArmMode.Cartesian:
            self.robot.moveToPointC(position)
