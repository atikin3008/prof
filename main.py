from abc import abstractmethod

#from PIL.ImageQt import QPixmap, QImage

from motion import core
from motion.core import logs

import main_window
import work
import move
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage

from ultralytics import YOLO
import cv2

moves = [[0] * 6] * 18


class Move(QWidget, move.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class Widget(QWidget, work.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class MW(QMainWindow, main_window.Ui_MainWindow):

    def __init__(self):
        self.labelVideo = None
        self.cam = cv2.VideoCapture(0)
        self.h = None
        self.AI = False
        self.work: bool = False
        logs.add("Init")
        self.robot = core.RobotControl()
        self.mode = ""
        super().__init__()
        self.w = None
        self.setupUi(self)
        self.pushButton_4.clicked.connect(self.open_window)
        self.pushButton_5.clicked.connect(self.open_window1)
        self.pushButton_3.clicked.connect(self.emergency)
        self.pushButton.clicked.connect(self.on)
        self.pushButton_2.clicked.connect(self.off)
        self.pushButton_6.clicked.connect(self.save)
        self.pushButton_7.clicked.connect(self.open_window2)
        self.pushButton_8.clicked.connect(self.doAI)
        self.ji = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_function)
        if not self.robot.connect():
            raise RuntimeError("Connect error")
        logs.add("Connect")
        self.timer.start(50)

    def doAI(self):
        self.AI = not self.AI

    def save(self):
        with open(self.lineEdit.text(), "w") as f:
            f.write(logs.get_text())

    def emergency(self):
        self.robot.stop()
        self.work = False

    def on(self):
        self.work = True

    def off(self):
        self.work = False

    def open_window(self):
        if not self.work:
            return
        self.mode = "C"
        self.robot.manualCartMode()
        self.w = Widget()
        self.w.show()
        self.w.verticalSlider.actionTriggered.connect(self.update1)
        self.w.verticalSlider_2.actionTriggered.connect(self.update1)
        self.w.verticalSlider_3.actionTriggered.connect(self.update1)
        self.w.verticalSlider_4.actionTriggered.connect(self.update1)
        self.w.verticalSlider_5.actionTriggered.connect(self.update1)
        self.w.verticalSlider_6.actionTriggered.connect(self.update1)
        self.w.checkBox.clicked.connect(self.update1)

    def open_window1(self):
        if not self.work:
            return
        self.mode = "J"
        self.robot.manualJointMode()
        self.w = Widget()
        self.w.show()
        self.w.verticalSlider.actionTriggered.connect(self.update1)
        self.w.verticalSlider_2.actionTriggered.connect(self.update1)
        self.w.verticalSlider_3.actionTriggered.connect(self.update1)
        self.w.verticalSlider_4.actionTriggered.connect(self.update1)
        self.w.verticalSlider_5.actionTriggered.connect(self.update1)
        self.w.verticalSlider_6.actionTriggered.connect(self.update1)
        self.w.checkBox.clicked.connect(self.update1)

    def open_window2(self):
        if not self.work:
            return
        self.mode = "C"
        self.robot.manualCartMode()
        self.h = Move()
        self.h.show()
        self.h.pushButton.clicked.connect(self.play)
        self.h.pushButton_3.clicked.connect(self.add)
        self.h.pushButton_2.clicked.connect(self.play1)
        self.h.pushButton_4.clicked.connect(self.load1)
        self.h.pushButton_4.clicked.connect(self.save1)

    def save1(self):
        text2 = ""
        for i in self.ji:
            text2 += (str(" ".join(map(str, i))) + "\n")
        with open("command", "w") as f:
            f.write(text2)

    def load1(self):
        with open("command", "r") as f:
            for x in f.readlines():
                try:
                    l = list(map(int, x.split()))
                    for i in l:
                        if i < 0 or i > 100:
                            return
                    if len(l) != 7:
                        return
                    if l[-1] > 1 or l[-1] < 0:
                        return
                    self.ji.append(l)
                except:
                    pass

    def play1(self):
        if not self.work:
            return
        for i in self.ji:
            self.robot.moveToPointC(i[:-2], i[-1])
        if not self.h.checkBox.isChecked():
            self.ji.clear()
        else:
            self.play1()

    def add(self):
        try:
            l = list(map(int, self.h.lineEdit.text().split()))
            for i in l:
                if i < 0 or i > 100:
                    return
            if len(l) != 7:
                return
            if l[-1] > 1 or l[-1] < 0:
                return
            self.ji.append(l)
        except:
            pass

    def play(self):
        x1 = self.h.spinBox_2.value()
        x2 = self.h.spinBox.value()
        if x1 < 1 or x1 > 18:
            return
        if x2 < 1 or x2 > 18:
            return
        self.robot.moveToPointC(moves[x1], 0)
        self.robot.toolON()
        k = moves[x1]
        k[2] = 10
        self.robot.moveToPointC(k, 0)
        k1 = moves[x2]
        k1[2] = 10
        self.robot.moveToPointC(k1, 0)
        self.robot.moveToPointC(moves[x2], 0)
        self.robot.toolOFF()

    def update1(self):
        if not self.work:
            return
        if self.mode == 'C':
            self.robot.moveToPointC(
                [self.w.verticalSlider.value(), self.w.verticalSlider_2.value(), self.w.verticalSlider_3.value(),
                 self.w.verticalSlider_4.value(), self.w.verticalSlider_5.value(), self.w.verticalSlider_6.value()], 0)
            if self.w.verticalSlider_6.value():
                self.robot.toolON()
            else:
                self.robot.toolOFF()
        else:
            self.robot.moveToPointJ(
                [self.w.verticalSlider.value(), self.w.verticalSlider_2.value(), self.w.verticalSlider_3.value(),
                 self.w.verticalSlider_4.value(), self.w.verticalSlider_5.value(), self.w.verticalSlider_6.value()])
            if self.w.verticalSlider_6.value():
                self.robot.toolON()
            else:
                self.robot.toolOFF()

    def update_function(self):
        if not self.work:
            return
        motors_position = self.robot.getMotorPositionTick()
        text = ""
        for i in range(len(motors_position)):
            text += f"Мотор {i}: {motors_position[i]} {self.robot.getActualTemperature()}\n"
        self.label.setText(text)
        self.label_2.setText(logs.get_text())
        self.label_4.setText(f"Режим: {self.robot.getRobotMode()}")
        if self.h is not None:
            text2 = ""
            for i in self.ji:
                text2 += (str(i) + "\n")
            self.h.label.setText(text2)
        ret, cap = self.cam.read()
        if ret:
            height, width, channel = cap.shape
            qImg = QImage(cap.data, width, height, QImage.Format_RGB888)
            qImg = qImg.scaled(520, 270, Qt.KeepAspectRatio)
            if self.labelVideo is None:
                self.labelVideo = QLabel(self.frame)
                self.labelVideo.resize(480, 270)
            self.labelVideo.setPixmap(QPixmap(qImg))



if __name__ == "__main__":
    app = QApplication([])
    mw = MW()
    mw.show()
    app.exec_()
