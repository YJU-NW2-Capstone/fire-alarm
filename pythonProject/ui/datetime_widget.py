from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QDate, QTime, Qt, QTimer
from PyQt5.QtGui import QFont


class DateTimeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 글꼴과 크기 설정
        font = QFont('Arial', 12)
        self.setFont(font)

        # 타이머 설정: 1초마다 업데이트
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDateTime)
        self.timer.start(1000)

        # 초기 날짜와 시간 설정
        self.updateDateTime()

    def updateDateTime(self):
        # 현재 날짜와 시간 가져오기
        currentDate = QDate.currentDate().toString(Qt.DefaultLocaleLongDate)
        currentTime = QTime.currentTime().toString('hh:mm:ss')

        # 레이블에 날짜와 시간 설정
        self.setText(f'{currentDate} {currentTime}')

        # 레이블 크기 재조정
        self.adjustSize()
