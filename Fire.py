import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


from_class = uic.loadUiType("./Fire.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

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


app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()
