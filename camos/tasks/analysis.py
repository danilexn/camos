# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np
from camos.tasks.runtask import RunTask
from camos.utils.errormessages import ErrorMessages
from camos.tasks.plotting import AnalysisPlot


class Analysis(QObject):
    finished = pyqtSignal()
    plotReady = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(
        self, model=None, parent=None, signal=None, name="No name processing"
    ):
        super(Analysis, self).__init__()
        self.model = model
        self.signal = signal
        self.parent = parent
        self.output = np.zeros((1, 1))
        self.analysis_name = name
        self.finished.connect(self.plot)

    def _run(self):
        pass

    def _plot(self):
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
        self._plot()
        self.plot.draw()
        self.plotReady.emit()
        pass

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output)

    def output_to_imagemodel(self):
        self.parent.model.add_image(self.output)

    def display(self):
        # TODO: change to signal...
        if type(self.model.list_images()) is type(None):
            # Handle error that there are no images
            ErrorMessages("There are no images!")
        if type(self.input.list_datasets()) is type(None):
            # Handle error that there are no images
            ErrorMessages("There are no images!")
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def initialize_UI(self):
        pass

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.main_layout = QHBoxLayout()
        self.group_settings = QGroupBox("Parameters")
        self.group_plot = QGroupBox("Plots")
        self.layout = QVBoxLayout()
        self.plot_layout = QVBoxLayout()
        self.plot = AnalysisPlot(self, width=5, height=4, dpi=100)
        self.plot_layout.addWidget(self.plot)
        self.group_settings.setLayout(self.layout)
        self.group_plot.setLayout(self.plot_layout)
        self.main_layout.addWidget(self.group_settings, 1)
        self.main_layout.addWidget(self.group_plot, 4)

    def _final_initialize_UI(self):
        self.runButton = QPushButton("Run", self.parent)
        self.runButton.setToolTip("Click to run this task")
        self.handler = RunTask(self)
        self.runButton.clicked.connect(self.handler.start_progress)

        self.layout.addWidget(self.runButton)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.main_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)
