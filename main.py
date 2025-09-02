from abc import abstractmethod
from motion import core
from motion.core import logs

import main_window
import work
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import QTimer


class Widget(QWidget, work.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class MW(QMainWindow, main_window.Ui_MainWindow):

    def __init__(self):
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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_function)
        if not self.robot.connect():
            raise RuntimeError("Connect error")
        logs.add("Connect")
        self.timer.start(50)

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
        self.robot.setCartesianVelocity()
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
        self.robot.setJointVelocity()
        self.w = Widget()
        self.w.show()
        self.w.verticalSlider.actionTriggered.connect(self.update1)
        self.w.verticalSlider_2.actionTriggered.connect(self.update1)
        self.w.verticalSlider_3.actionTriggered.connect(self.update1)
        self.w.verticalSlider_4.actionTriggered.connect(self.update1)
        self.w.verticalSlider_5.actionTriggered.connect(self.update1)
        self.w.verticalSlider_6.actionTriggered.connect(self.update1)
        self.w.checkBox.clicked.connect(self.update1)

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


if __name__ == "__main__":
    app = QApplication([])
    mw = MW()
    mw.show()
    app.exec_()
