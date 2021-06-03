from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread

class RunTask(QWidget):
    def __init__(self, task):
        super().__init__()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 500, 75)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle("Running {}".format("task"))

        self.obj = task
        self.thread = QThread()
        self.obj.intReady.connect(self.on_count_changed)
        self.obj.moveToThread(self.thread)
        self.obj.finished.connect(self.thread.quit)
        self.obj.finished.connect(self.hide)
        self.thread.started.connect(self.obj.run)

    def start_progress(self):
        self.show()
        self.thread.start()

    def on_count_changed(self, value):
        self.pbar.setValue(value)

    def closeEvent(self, event):
        self.obj.finished.emit()