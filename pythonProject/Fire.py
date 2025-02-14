import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QDate, QTime, Qt

# DateTimeLabel 임포트
from ui.datetime_widget import DateTimeLabel

from_class = uic.loadUiType("./Fire.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

        # 페이지 전환 버튼 연결
        self.pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.pushButton_2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.pushButton_3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        # 페이지 전환 시마다 업데이트
        self.stackedWidget.currentChanged.connect(self.updateDateTime)

    def initUI(self):
        # DateTimeLabel 생성
        self.dateTimeLabel = DateTimeLabel(self)
        # 타이머 설정: 1초마다 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)

    def updateDateTime(self):
        # 현재 날짜와 시간 가져오기
        currentDate = QDate.currentDate().toString(Qt.DefaultLocaleLongDate)
        currentTime = QTime.currentTime().toString('hh:mm:ss')

        # 레이블에 날짜와 시간 설정
        self.dateTimeLabel.setText(f'{currentDate} {currentTime}')
        self.dateTimeLabel.adjustSize()

        # 레이블 위치 재조정
        # 윈도우 크기 가져오기
        window_width = self.width()
        window_height = self.height()

        # 퍼센트 위치 계산 (오른쪽 90%, 위쪽 5%)
        x_position = int(window_width * 0.9) - self.dateTimeLabel.width()
        y_position = int(window_height * 0.01)

        self.dateTimeLabel.move(x_position, y_position)

        # 다시 그리기
        self.dateTimeLabel.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowClass()
    mainWindow.show()
    app.exec_()
