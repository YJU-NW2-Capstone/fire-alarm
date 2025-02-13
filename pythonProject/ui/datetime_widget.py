# import sys
# from PyQt5 import uic
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from PyQt5.QtCore import QTimer, QTime, QDate
#
#
# class DateTimeApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         uic.loadUi("Fire.ui", self)  # Qt Designer에서 만든 UI 불러오기
#
#         # QTimer 설정 (1초마다 업데이트)
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_datetime)
#         self.timer.start(1000)  # 1000ms = 1초
#
#     def update_datetime(self):
#         # 현재 시각과 날짜 가져오기
#         current_time = QTime.currentTime().toString("HH:mm:ss")  # 시:분:초 형식
#         current_date = QDate.currentDate().toString("yyyy-MM-dd")  # 년-월-일 형식
#
#         # QLabel에 현재 시각과 날짜 표시
#         self.timeLabel.setText(current_time)
#         self.dateLabel.setText(current_date)
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = DateTimeApp()
#     window.show()
#     sys.exit(app.exec_())
