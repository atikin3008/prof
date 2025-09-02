#!/usr/bin/python3

import os
import random
import time
from math import *
from enum import Enum
from typing import List


# Ваш класс для логирования
class Logs:
    def __init__(self):
        self._text = []

    def add(self, string: str):
        self._text.append(string)

    def get_text(self):
        return "\n".join(self._text)


# Создаем глобальный экземпляр для логирования
logs = Logs()


# Эмуляция системных определений
class InterpreterStates(Enum):
    PROGRAM_IS_DONE = 0
    MOTION_NOT_ALLOWED_S = 1
    PROGRAM_RUNNING = 2
    PROGRAM_PAUSED = 3
    PROGRAM_STOPPED = 4


class States(Enum):
    DISENGAGED = 0
    ENGAGED = 1


class ModeCommands(Enum):
    GOTO_MANUAL_JOINT_MODE_E = 0
    GOTO_MANUAL_CART_MODE_E = 1
    SEMI_AUTO_MODE = 2


class Path(Enum):
    ROBOT_MODE = "robot_mode"
    HOSTIN_JOINT_VELOCITY = "hostin_joint_velocity"
    HOSTIN_TOOL_VELOCITY = "hostin_tool_velocity"
    ROBOT_STATE = "robot_state"
    STATE_CMD = "state_cmd"
    CURRENT_JOINT_POSE_TICK = ["joint1_tick", "joint2_tick", "joint3_tick", "joint4_tick", "joint5_tick", "joint6_tick"]
    CURRENT_TOOL_POSE = "current_tool_pose"
    CURRENT_JOINT_POSE_RADIANS = "current_joint_pose_radians"
    MANIPULABILITY_CMD = "manipulability_cmd"
    READSDO_CMD = "readsdo_cmd"
    ACTIVATE_MOVE_TO_START = "activate_move_to_start"
    TOOL_CMD = "tool_cmd"


class JoyVelicity(Enum):
    MAX_JOY_VELOCITY_JOINT = 0.5
    MAX_JOY_VELOCITY_CARTESIAN = 0.3


class Waypoint:
    def __init__(self, values):
        self.values = values


class MotionProgram:
    def __init__(self, req=None, messageTypes=None):
        self.moves = []

    def addMoveL(self, waypoint_list, velocity, acceleration,
                 rotational_velocity, rotational_acceleration,
                 ref_joint_coord_rad):
        self.moves.append({"type": "MoveL", "waypoints": waypoint_list})
        logs.add(f"Added MoveL with {len(waypoint_list)} waypoints")

    def addMoveC(self, waypoint_list, angle, velocity, acceleration,
                 rotational_velocity, rotational_acceleration,
                 ref_joint_coord_rad):
        self.moves.append({"type": "MoveC", "waypoints": waypoint_list, "angle": angle})
        logs.add(f"Added MoveC with {len(waypoint_list)} waypoints, angle: {angle}")

    def addMoveJ(self, waypoint_list, rotational_velocity, rotational_acceleration):
        self.moves.append({"type": "MoveJ", "waypoints": waypoint_list})
        logs.add(f"Added MoveJ with {len(waypoint_list)} waypoints")

    def send(self, program_name):
        logs.add(f"Program '{program_name}' sent with {len(self.moves)} moves")
        return self

    def get(self):
        return {"status": "success"}


class RobotCommand:
    def __init__(self, req=None, messageTypes=None):
        self.engaged = False
        self.mode = ModeCommands.GOTO_MANUAL_JOINT_MODE_E
        self.state = InterpreterStates.PROGRAM_STOPPED
        self.tool_status = False

    def engage(self):
        self.engaged = True
        logs.add("Robot engaged")
        return True

    def disengage(self):
        self.engaged = False
        logs.add("Robot disengaged")
        return True

    def off(self):
        logs.add("Robot power off")
        return True

    def manualCartMode(self):
        self.mode = ModeCommands.GOTO_MANUAL_CART_MODE_E
        logs.add("Manual cartesian mode set")
        return True

    def manualJointMode(self):
        self.mode = ModeCommands.GOTO_MANUAL_JOINT_MODE_E
        logs.add("Manual joint mode set")
        return True

    def semiAutoMode(self):
        self.mode = ModeCommands.SEMI_AUTO_MODE
        logs.add("Semi-auto mode set")
        return True

    def play(self, wait_time=0):
        if self.state == InterpreterStates.PROGRAM_STOPPED:
            self.state = InterpreterStates.PROGRAM_RUNNING
        elif self.state == InterpreterStates.PROGRAM_PAUSED:
            self.state = InterpreterStates.PROGRAM_RUNNING
        logs.add(f"Play command, state: {self.state}")
        return self.state

    def pause(self):
        if self.state == InterpreterStates.PROGRAM_RUNNING:
            self.state = InterpreterStates.PROGRAM_PAUSED
        logs.add(f"Pause command, state: {self.state}")
        return self.state

    def stop(self):
        self.state = InterpreterStates.PROGRAM_STOPPED
        logs.add(f"Stop command, state: {self.state}")
        return self.state

    def reset(self):
        self.state = InterpreterStates.PROGRAM_STOPPED
        logs.add(f"Reset command, state: {self.state}")
        return self.state

    def moveToStart(self, timeout):
        logs.add(f"Move to start with timeout {timeout}")
        return True


class LedLamp(object):
    def __init__(self, ip='192.168.2.101', port=8890):
        logs.add(f"LED Lamp initialized with IP: {ip}, Port: {port}")

    def setLamp(self, status: str):
        if len(status) != 4 or not all(c in "01" for c in status):
            logs.add("ERROR: The status must be a string of four characters containing only '0' or '1'.")
            return False

        colors = []
        if status[0] == '1': colors.append("Blue")
        if status[1] == '1': colors.append("Green")
        if status[2] == '1': colors.append("Yellow")
        if status[3] == '1': colors.append("Red")

        logs.add(f"Set led lamp: {status} - Active colors: {', '.join(colors) if colors else 'None'}")
        return True


class RobotControl(object):
    def __init__(self, ip='192.168.2.100', port='5568:5567', login='*', password='*'):
        self.__hostname = ip
        self.__port = port
        self.__login = login
        self.__password = password
        self.__connected = False
        self.__robot = None
        self.__req = None
        self.__messageTypes = None
        self.__timeout = 0.4
        self.__joint_positions = [0.0, 0.0, radians(90), 0.0, radians(90), 0.0]
        self.__tool_position = [0.5, 0.0, 0.5, 0.0, 0.0, 0.0]

    def connect(self):
        try:
            logs.add(f"Connecting to robot at {self.__hostname}:{self.__port}")
            time.sleep(0.5)  # Имитация задержки подключения

            self.__robot = RobotCommand()
            self.__connected = True
            logs.add("Robot ARM connected successfully")
            return True
        except Exception as e:
            logs.add(f"ERROR: Connection failed: {e}")
            return False

    def engage(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            result = self.__robot.engage()
            time.sleep(self.__timeout)
            return result
        except Exception as e:
            logs.add(f"ERROR: Engage failed: {e}")
            return False

    def disengage(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            result = self.__robot.disengage()
            logs.add("Robot is Disengaged")
            return result
        except Exception as e:
            logs.add(f"ERROR: Disengage failed: {e}")
            return False

    def manualCartMode(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            result = self.__robot.manualCartMode()
            time.sleep(self.__timeout)
            return result
        except Exception as e:
            logs.add(f"ERROR: Set cartesian mode failed: {e}")
            return False

    def manualJointMode(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            result = self.__robot.manualJointMode()
            time.sleep(self.__timeout)
            return result
        except Exception as e:
            logs.add(f"ERROR: Set joint mode failed: {e}")
            return False

    def setJointVelocity(self, velocity=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            if self.__robot.mode is not ModeCommands.GOTO_MANUAL_JOINT_MODE_E:
                logs.add("INFO: Actual robot state isn't joint mode")
                return False

            if len(velocity) != 6:
                logs.add("WARNING: The number of values doesn't correspond to the number of motors")
                return False

            # Имитация обновления позиции на основе velocity
            for i in range(6):
                self.__joint_positions[i] += velocity[i] * 0.1

            logs.add(f"Set joint velocity: {velocity}")
            return True
        except Exception as e:
            logs.add(f"ERROR: Set joint velocity failed: {e}")
            return False

    def setCartesianVelocity(self, velocity=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            if self.__robot.mode is not ModeCommands.GOTO_MANUAL_CART_MODE_E:
                logs.add("INFO: Actual robot state isn't cartesian mode")
                return False

            if len(velocity) != 6:
                logs.add("WARNING: The number of values doesn't correspond to the tool")
                return False

            # Имитация обновления позиции на основе velocity
            for i in range(6):
                self.__tool_position[i] += velocity[i] * 0.1

            logs.add(f"Set cartesian velocity: {velocity}")
            return True
        except Exception as e:
            logs.add(f"ERROR: Set cartesian velocity failed: {e}")
            return False

    def moveToStart(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            self.__robot.semiAutoMode()
            motion_program = MotionProgram()
            start_point = [Waypoint([radians(0), radians(0), radians(90), radians(0), radians(90), radians(0)])]
            motion_program.addMoveJ(start_point, 0.05, 0.1)
            motion_program.send("move_to_start_point").get()

            # Имитация движения к стартовой позиции
            self.__joint_positions = [0.0, 0.0, radians(90), 0.0, radians(90), 0.0]
            self.__tool_position = [0.5, 0.0, 0.5, 0.0, 0.0, 0.0]

            logs.add('Robot is at the start position')
            return True
        except Exception as e:
            logs.add(f"ERROR: Move to start failed: {e}")
            return False

    def activateMoveToStart(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return

        try:
            logs.add("Robot move to start activated")
            # Имитация активации движения к старту
            self.moveToStart()
        except Exception as e:
            logs.add(f"ERROR: Activate move to start failed: {e}")

    def moveToPointL(self, waypoint_list, velocity=0.1, acceleration=0.2,
                     rotational_velocity=3.18, rotational_acceleration=6.37,
                     ref_joint_coord_rad=[]):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return

        try:
            self.__robot.semiAutoMode()
            motion_program = MotionProgram()
            motion_program.addMoveL(waypoint_list, velocity, acceleration,
                                    rotational_velocity, rotational_acceleration,
                                    ref_joint_coord_rad)
            motion_program.send("move_to_point_l").get()

            # Имитация обновления позиции
            if waypoint_list:
                self.__tool_position = waypoint_list[-1].values[:6]

            time.sleep(self.__timeout)
        except Exception as e:
            logs.add(f"ERROR: MoveL failed: {e}")

    def moveToPointC(self, waypoint_list, angle, velocity=0.1, acceleration=0.2,
                     rotational_velocity=3.18, rotational_acceleration=6.37,
                     ref_joint_coord_rad=[]):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return

        try:
            self.__robot.semiAutoMode()
            motion_program = MotionProgram()
            motion_program.addMoveC(waypoint_list, angle, velocity, acceleration,
                                    rotational_velocity, rotational_acceleration,
                                    ref_joint_coord_rad)
            motion_program.send("move_to_point_c").get()

            # Имитация обновления позиции
            if waypoint_list:
                self.__tool_position = waypoint_list[-1].values[:6]

            time.sleep(self.__timeout)
        except Exception as e:
            logs.add(f"ERROR: MoveC failed: {e}")

    def moveToPointJ(self, waypoint_list=[], rotational_velocity=3.18, rotational_acceleration=6.37):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return

        try:
            self.__robot.semiAutoMode()
            motion_program = MotionProgram()
            motion_program.addMoveJ(waypoint_list, rotational_velocity, rotational_acceleration)
            motion_program.send("move_to_point_j").get()

            # Имитация обновления позиции
            if waypoint_list:
                self.__joint_positions = waypoint_list[-1].values[:6]

            time.sleep(self.__timeout)
        except Exception as e:
            logs.add(f"ERROR: MoveJ failed: {e}")

    def play(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return InterpreterStates.PROGRAM_STOPPED

        try:
            logs.add("Robot program play")
            state = self.__robot.play(wait_time=0.25)
            if state == InterpreterStates.MOTION_NOT_ALLOWED_S:
                logs.add("INFO: Robot don't in start position")
            return state
        except Exception as e:
            logs.add(f"ERROR: Play failed: {e}")
            return InterpreterStates.PROGRAM_STOPPED

    def pause(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return InterpreterStates.PROGRAM_STOPPED

        try:
            logs.add("Robot program pause")
            return self.__robot.pause()
        except Exception as e:
            logs.add(f"ERROR: Pause failed: {e}")
            return InterpreterStates.PROGRAM_STOPPED

    def stop(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return InterpreterStates.PROGRAM_STOPPED

        try:
            logs.add("Robot program stop")
            return self.__robot.stop()
        except Exception as e:
            logs.add(f"ERROR: Stop failed: {e}")
            return InterpreterStates.PROGRAM_STOPPED

    def reset(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return InterpreterStates.PROGRAM_STOPPED

        try:
            logs.add("Robot program reset")
            return self.__robot.reset()
        except Exception as e:
            logs.add(f"ERROR: Reset failed: {e}")
            return InterpreterStates.PROGRAM_STOPPED

    def toolON(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            logs.add("Tool ON")
            self.__robot.tool_status = True
            return True
        except Exception as e:
            logs.add(f"ERROR: Tool ON failed: {e}")
            return False

    def toolOFF(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return False

        try:
            logs.add("Tool OFF")
            self.__robot.tool_status = False
            return True
        except Exception as e:
            logs.add(f"ERROR: Tool OFF failed: {e}")
            return False

    def getRobotMode(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return ModeCommands.GOTO_MANUAL_JOINT_MODE_E

        try:
            return self.__robot.mode
        except Exception as e:
            logs.add(f"ERROR: Get robot mode failed: {e}")
            return ModeCommands.GOTO_MANUAL_JOINT_MODE_E

    def getRobotState(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return States.DISENGAGED

        try:
            return States.ENGAGED if self.__robot.engaged else States.DISENGAGED
        except Exception as e:
            logs.add(f"ERROR: Get robot state failed: {e}")
            return States.DISENGAGED

    def getActualStateOut(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return InterpreterStates.PROGRAM_STOPPED

        try:
            return self.__robot.state
        except Exception as e:
            logs.add(f"ERROR: Get actual state failed: {e}")
            return InterpreterStates.PROGRAM_STOPPED

    def getMotorPositionTick(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return [0, 0, 0, 0, 0, 0]

        try:
            # Имитация значений энкодеров (примерные значения)
            return [int(pos * 10000) for pos in self.__joint_positions]
        except Exception as e:
            logs.add(f"ERROR: Get motor position tick failed: {e}")
            return [0, 0, 0, 0, 0, 0]

    def getToolPosition(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        try:
            return self.__tool_position
        except Exception as e:
            logs.add(f"ERROR: Get tool position failed: {e}")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def getMotorPositionRadians(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        try:
            return self.__joint_positions
        except Exception as e:
            logs.add(f"ERROR: Get motor position radians failed: {e}")
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    def getManipulability(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return 0.8

        try:
            # Возвращаем случайное значение манипулятивности в диапазоне 0.7-0.9
            return round(random.uniform(0.7, 0.9), 2)
        except Exception as e:
            logs.add(f"ERROR: Get manipulability failed: {e}")
            return 0.8

    def getActualTemperature(self):
        if not self.__connected:
            logs.add("ERROR: Not connected to robot")
            return 35.0

        try:
            # Возвращаем случайное значение температуры в диапазоне 30-45
            return round(random.uniform(30.0, 45.0), 1)
        except Exception as e:
            logs.add(f"ERROR: Get temperature failed: {e}")
            return 35.0