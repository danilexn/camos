# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from camos.tasks.processing import Processing

import numpy as np
from camos.tasks.runtask import RunTask
from camos.utils.errormessages import ErrorMessages
from camos.tasks.plotting import AnalysisPlot

class StackCorrelation(Processing):
    analysis_name = "Stack Correlation"
    plotReady = pyqtSignal()

    def __init__(self, model=None, parent=None, signal=None):
        super(StackCorrelation, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.output = None
        self.image = None
        self.between = 300
        self.finished.connect(self.plot)

    def _run(self):
        image = self.image._image._imgs
        n = image.shape[0]
        corr_a = np.corrcoef(image[0],image[int(n/2)])[0, 1]
        corr_b = np.corrcoef(image[0],image[n - 1])[0, 1]
        if (corr_a >= 0.85) and (corr_b >= 0.85):
            print("There seems to be no motion artifact!")

        t = np.linspace(0, n - 1, self.between).astype(int)
        self.output = np.zeros((len(t), len(t)))
        for i in range(len(t)):
            self.intReady.emit(i * 100 / len(t))
            for j in range(i, len(t)):
                corr = np.corrcoef(image[t[i]],image[t[j]])
                self.output[i, j] = corr[0, 1]

        i_lower = np.tril_indices(len(t), -1)
        self.output[i_lower] = self.output.T[i_lower]

    def _plot(self):
        self.plot.axes.imshow(self.output, cmap="hot")

    def plot(self):
        self._plot()
        self.plot.draw()
        self.plotReady.emit()
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

    def initialize_UI(self):
        self.imagelabel = QLabel("Stack to correlate", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, index):
        self.image = self.model.images[index]
        self.index = index