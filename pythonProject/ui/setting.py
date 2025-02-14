import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QAction
from PyQt5 import uic

from Fire import from_class


class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # 설정 버튼(QToolButton) 가져오기
        self.settingsButton = self.findChild(QToolButton, 'settingsButton')

        # QMenu 생성
        self.menu = QMenu()

        # 메뉴 항목 추가
        action1 = QAction('옵션 1', self)
        action1.triggered.connect(self.option1_selected)
        self.menu.addAction(action1)

        action2 = QAction('옵션 2', self)
        action2.triggered.connect(self.option2_selected)
        self.menu.addAction(action2)

        # 메뉴를 버튼에 연결
        self.settingsButton.setMenu(self.menu)

        # popupMode 설정 (이미 디자이너에서 설정했다면 생략 가능)
        self.settingsButton.setPopupMode(QToolButton.InstantPopup)

        self.setWindowTitle('Settings Dropdown')
        self.show()

    # 옵션 선택 시 호출되는 메서드
    def option1_selected(self):
        print('옵션 1이 선택되었습니다.')
        # 여기서 옵션 1에 대한 동작을 구현하면 돼

    def option2_selected(self):
        print('옵션 2가 선택되었습니다.')
        # 옵션 2에 대한 동작 구현
app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()