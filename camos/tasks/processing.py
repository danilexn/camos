from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np
from tasks.runtask import RunTask
from utils.errormessages import ErrorMessages

class Processing(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(self, model=None, parent=None, input=None):
        super(Processing, self).__init__()
        self.model = model
        self.input = input
        self.parent = parent
        self.output = np.zeros((1, 1))
        self.analysis_name = "Generic Processing"

    def _run(self):
        pass

    @pyqtSlot()
    def run(self):
        self._run()
        pass

    def plot(self):
        pass

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output)

    def output_to_imagemodel(self):
        self.parent.model.add_image(self.output)

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
        self.runButton = QPushButton("Run", self.parent)
        self.runButton.setToolTip("Click to run this task")
        self.handler = RunTask(self)
        self.runButton.clicked.connect(self.handler.start_progress)

        self.layout.addWidget(self.runButton)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)