# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import sys

import numpy as np
from camos.tasks.runtask import RunTask
from camos.utils.errormessages import ErrorMessages
from camos.model.inputdata import InputData


class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        pass


class Processing(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    txtReady = pyqtSignal(str)

    def __init__(
        self, model=None, parent=None, signal=None, name="No name processing"
    ):
        super(Processing, self).__init__()
        self.model = model
        self.signal = signal
        self.layername = "Unnamed Layer {}"
        self.index = 0
        self.parent = parent
        self.output = np.zeros((1, 1))
        self.analysis_name = name
        # sys.stdout = Stream(newText=self.onUpdateOutput)

    def onUpdateOutput(self, text):
        self._onUpdateOutput(text)

    def _onUpdateOutput(self, text):
        self.txtReady.emit(text)

    def _run(self):
        pass

    @pyqtSlot()
    def run(self):
        try:
            self._run()
            self.handler.success = True
        finally:
            self.finished.emit()
        pass

    def plot(self):
        pass

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output)

    def output_to_imagemodel(self, name = None):
        image = InputData(
            self.output,
            memoryPersist=True,
            name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(image, name)

    def display(self):
        if type(self.model.list_images()) is type(None):
            # Handle error that there are no images
            ErrorMessages("There are no images loaded!")
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def initialize_UI(self):
        pass

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
