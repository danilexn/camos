# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QPushButton,
    QWidget,
)

import numpy as np

from camos.tasks.runtask import RunTask
from camos.tasks.plotting import AnalysisPlot
from camos.tasks.processing import Processing
from camos.utils.generategui import ImageInput


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

    def _run(self, _i_img: ImageInput("Stack to Correlate", 0)):
        image = self.model.images[_i_img]._image._imgs
        self.index = _i_img
        n = image.shape[0]
        corr_a = np.corrcoef(image[0], image[int(n / 2)])[0, 1]
        corr_b = np.corrcoef(image[0], image[n - 1])[0, 1]
        if (corr_a >= 0.85) and (corr_b >= 0.85):
            print("There seems to be no motion artifact!")

        t = np.linspace(0, n - 1, self.between).astype(int)
        self.output = np.zeros((len(t), len(t)))
        for i in range(len(t)):
            self.intReady.emit(i * 100 / len(t))
            for j in range(i, len(t)):
                corr = np.corrcoef(image[t[i]], image[t[j]])
                self.output[i, j] = corr[0, 1]

        i_lower = np.tril_indices(len(t), -1)
        self.output[i_lower] = self.output.T[i_lower]

    def _plot(self):
        self.plot.axes.imshow(self.output, cmap="hot")

    def plot(self):
        self._plot()
        self.plot.draw()
        self.plotReady.emit()

    def buildUI(self):
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.main_layout = QHBoxLayout()
        self.group_settings = QGroupBox("Parameters")
        self.group_plot = QGroupBox("Plots")
        self.layout = QVBoxLayout()
        self.layout.addStretch(1)
        self.plot_layout = QVBoxLayout()
        self.plot = AnalysisPlot(self, width=5, height=4, dpi=100)
        self.plot.plottoimage.connect(self.parent.model.select_cells)
        self.toolbar = NavigationToolbar(self.plot, None)
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.plot)
        self.group_settings.setLayout(self.layout)
        self.group_plot.setLayout(self.plot_layout)
        self.main_layout.addWidget(self.group_settings, 1)
        self.main_layout.addWidget(self.group_plot, 4)
        self.params_gui = CreateGUI(self.paramDict, self.layout, self._run)
        self.params_gui.creategui()

        self.runButton = QPushButton("Run", self.parent)
        self.runButton.setToolTip("Click to run this task")
        self.handler = RunTask(self)
        self.runButton.clicked.connect(self.handler.start_progress)

        self.savePlot = QPushButton("To viewport", self.parent)
        self.savePlot.setToolTip("Click to move plot to viewport")
        self.savePlot.clicked.connect(self.export_plot_to_viewport)

        self.layout.addWidget(self.runButton)
        self.layout.addWidget(self.savePlot)

        self.dockedWidget = QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.main_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)
