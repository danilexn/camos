from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from darktheme.widget_template import DarkPalette
import signal
import sys

from gui.mainwindow import MainWindow

def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    w = MainWindow()
    sys.exit(app.exec_())