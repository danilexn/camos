from PyQt5 import QtWidgets
from darktheme.widget_template import DarkPalette
import signal
import sys

signal.signal(signal.SIGINT, signal.SIG_DFL)

from gui.mainwindow import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    w = MainWindow()
    app.exec_()

# this is a test