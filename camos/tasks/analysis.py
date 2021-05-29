from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

class Analysis(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(self, parent=None, data=None):
        super(Analysis, self).__init__()
        self.data = data

    def _run(self):
        pass

    @pyqtSlot()
    def run(self):
        pass

    def plot(self):
        pass

    def display(self):
        if type(self.model.list_images()) is type(None):
            # Handle error that there are no images
            ErrorMessages("There are no images loaded!")
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.layout = QVBoxLayout()

    def _final_initialize_UI(self):
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)