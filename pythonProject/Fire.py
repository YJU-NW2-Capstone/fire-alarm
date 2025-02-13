# import sys
# import os
# from PyQt5.QtWidgets import *
# from PyQt5 import uic
# from PyQt5.QtCore import QDate, QTime, Qt, QTimer
# from PyQt5.QtGui import QFont
#
# sys.path.append(os.path.join(os.path.dirname(__file__), "resource"))
#
# import main_rc
#
#
# from_class = uic.loadUiType("./Fire.ui")[0]
#
#
# class WindowClass(QMainWindow, from_class):
#     def __init__(self):
#         super().__init__()
#         self.setupUi(self)
#         self.date = QDate.currentDate()
#         self.initUI()
#
#     def closeEvent(self, event):
#         msgBox = QMessageBox()
#         msgBox.setText("정말로 창을 닫으시겠습니까?")
#         msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
#         msgBox.setDefaultButton(QMessageBox.No)
#
#         ret = msgBox.exec_()
#         if ret == QMessageBox.No:
#             event.ignore()
#         else:
#             event.accept()
#
#     def initUI(self):
#         # 날짜와 시간 레이블 생성
#         self.dateTimeLabel = QLabel(self)
#
#         # 글꼴과 크기 설정
#         font = QFont('Arial', 12)
#         self.dateTimeLabel.setFont(font)
#
#         # 현재 날짜와 시간 가져오기
#         currentDate = QDate.currentDate().toString(Qt.DefaultLocaleLongDate)
#         currentTime = QTime.currentTime().toString('hh:mm:ss')
#
#         # 레이블에 날짜와 시간 설정
#         self.dateTimeLabel.setText(f'{currentDate} {currentTime}')
#
#         # 레이블 크기 조정
#         self.dateTimeLabel.adjustSize()
#
#         # 레이블 위치 설정
#         self.dateTimeLabel.move(
#             self.width() - self.dateTimeLabel.width() - 10,
#             10
#         )
#
#         # 타이머 설정: 1초마다 업데이트
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.updateDateTime)
#         self.timer.start(1000)
#
#         self.setWindowTitle('Date and Time')
#         self.show()
#
#     def updateDateTime(self):
#         # 현재 날짜와 시간 가져오기
#         currentDate = QDate.currentDate().toString(Qt.DefaultLocaleLongDate)
#         currentTime = QTime.currentTime().toString('hh:mm:ss')
#
#         # 레이블에 날짜와 시간 업데이트
#         self.dateTimeLabel.setText(f'{currentDate} {currentTime}')
#
#         # 레이블 크기 재조정
#         self.dateTimeLabel.adjustSize()
#
#         # 레이블 위치 재조정
#         self.dateTimeLabel.move(
#             self.width() - self.dateTimeLabel.width() - 10,
#             10
#         )
#
#     def resizeEvent(self, event):
#         # 레이블 위치 업데이트
#         self.dateTimeLabel.move(
#             self.width() - self.dateTimeLabel.width() - 10,
#             10
#         )
#         super().resizeEvent(event)
#
# app = QApplication(sys.argv)
# mainWindow = WindowClass()
# mainWindow.show()
# app.exec_()

# main.py

import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
# import main_rc   # 필요에 따라 임포트
from ui.datetime_widget import DateTimeLabel
from_class = uic.loadUiType("./Fire.ui")[0]


class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def closeEvent(self, event):
        msgBox = QMessageBox()
        msgBox.setText("정말로 창을 닫으시겠습니까?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)

        ret = msgBox.exec_()
        if ret == QMessageBox.No:
            event.ignore()
        else:
            event.accept()

    def initUI(self):
        # 날짜와 시간 레이블 생성
        self.dateTimeLabel = DateTimeLabel(self)

        # 레이블 위치 설정
        self.dateTimeLabel.move(
            self.width() - self.dateTimeLabel.width() - 10,
            10
        )

        self.show()

    def resizeEvent(self, event):
        # 레이블 위치 업데이트
        self.dateTimeLabel.move(
            self.width() - self.dateTimeLabel.width() - 70,
            10
        )
        super().resizeEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowClass()
    mainWindow.show()
    app.exec_()

