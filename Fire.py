import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic


from_class = uic.loadUiType("./Fire.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def closeEvent(self, event):
        print("close test")
        # event.ignore()

app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
app.exec_()