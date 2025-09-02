#!/usr/bin/python3

#
#   Developer : Mikhail Filchenkov (m.filchenkov@gmail.com)
#   All rights reserved. Copyright (c) 2025 Applied Robotics.
#


from enum import Enum

class Path(Enum):
    """Path list of the robot ARM"""
    ROBOT_STATE = 'root/Logic/stateCommand'
    ROBOT_MODE = 'root/Logic/mode'
    ROBOT_MODE_SET = 'root/Logic/modeCommand'
    CURRENT_TOOL_POSE = 'root/ManipulatorControl/manipulatorToolPoseActual'
    CURRENT_JOINT_POSE_RADIANS = 'root/AxesControl/axesPositionsActual'
    HOSTIN_JOINT_VELOCITY = 'root/ManipulatorControl/hostInJointVelocity'
    HOSTIN_TOOL_VELOCITY = 'root/ManipulatorControl/hostInToolVelocity'
    ACTIVATE_MOVE_TO_START = 'root/ManipulatorControl/activateMoveToStart'
    TOOL_CMD = 'root/UserParameters/IO/gripper'
    STATE_CMD = 'root/MotionInterpreter/actualStateOut'
    MANIPULABILITY_CMD = 'root/ManipulatorControl/manipulabilityDetector/input'
    READSDO_CMD = 'root/Ethercat/Robot/read_sdo'
    ACTUAL_TEMPERATURE_CMD = ['root/Ethercat/Robot/Axis-01/SDOs/Actual Templerature',
                              'root/Ethercat/Robot/Axis-02/SDOs/Actual Templerature',
                              'root/Ethercat/Robot/Axis-03/SDOs/Actual Templerature',
                              'root/Ethercat/Robot/Axis-04/SDOs/Actual Templerature',
                              'root/Ethercat/Robot/Axis-05/SDOs/Actual Templerature',
                              'root/Ethercat/Robot/Axis-06/SDOs/Actual Templerature']
    CURRENT_JOINT_POSE_TICK = ['root/AxesControl/actuatorControlLoops/actuatorControlLoop01/motorPositionActual',
                                'root/AxesControl/actuatorControlLoops/actuatorControlLoop02/motorPositionActual',
                                'root/AxesControl/actuatorControlLoops/actuatorControlLoop03/motorPositionActual',
                                'root/AxesControl/actuatorControlLoops/actuatorControlLoop04/motorPositionActual',
                                'root/AxesControl/actuatorControlLoops/actuatorControlLoop05/motorPositionActual',
                                'root/AxesControl/actuatorControlLoops/actuatorControlLoop06/motorPositionActual']
class JoyVelicity(Enum):
    """Constraine velocity of the robot ARM"""
    MAX_JOY_VELOCITY_JOINT = 0.2
    MAX_JOY_VELOCITY_CARTESIAN = 0.2
    