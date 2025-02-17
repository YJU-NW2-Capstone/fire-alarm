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

        # 버튼 리스트 생성
        self.buttons = [self.pushButton, self.pushButton_2, self.pushButton_3]

        # 초기 페이지 설정 및 버튼 스타일 업데이트
        self.stackedWidget.setCurrentIndex(0)
        self.updateButtonStyles(self.pushButton)

        # 페이지 전환 버튼 연결
        self.pushButton.clicked.connect(lambda: self.changePage(0, self.pushButton))
        self.pushButton_2.clicked.connect(lambda: self.changePage(1, self.pushButton_2))
        self.pushButton_3.clicked.connect(lambda: self.changePage(2, self.pushButton_3))

    def initUI(self):
        # DateTimeLabel 생성
        self.dateTimeLabel = DateTimeLabel(self)
        # 타이머 설정: 1초마다 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)

        # 초기 날짜 및 시간 표시
        self.updateDateTime()

    def updateDateTime(self):
        # 현재 날짜와 시간 가져오기
        currentDate = QDate.currentDate().toString(Qt.DefaultLocaleLongDate)
        currentTime = QTime.currentTime().toString('hh:mm:ss')

        # 레이블에 날짜와 시간 설정
        self.dateTimeLabel.setText(f'{currentDate} {currentTime}')
        self.dateTimeLabel.adjustSize()

        # 레이블 위치 재조정
        window_width = self.width()
        window_height = self.height()

        x_position = int(window_width * 0.9) - self.dateTimeLabel.width()
        y_position = int(window_height * 0.01)

        self.dateTimeLabel.move(x_position, y_position)

        # 다시 그리기
        self.dateTimeLabel.show()

    def changePage(self, index, button):
        self.stackedWidget.setCurrentIndex(index)
        self.updateDateTime()
        self.updateButtonStyles(button)

    def updateButtonStyles(self, selectedButton):
        default_style = 'background-color: blue; color: white;'
        selected_style = 'background-color: red; color: white;'

        # 모든 버튼에 기본 스타일 적용
        for button in self.buttons:
            button.setStyleSheet(default_style)

        # 선택된 버튼에 선택된 스타일 적용
        selectedButton.setStyleSheet(selected_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = WindowClass()
    mainWindow.show()
    app.exec_()
