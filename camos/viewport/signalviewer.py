# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets, QtCore

import numpy as np

from camos.tasks.plotting import AnalysisPlot

from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)

class SignalViewer(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None):
        self.parent = parent
        self.output = signal
        self.foutput = self.output
        self.parent.model.imagetoplot.connect(self.update_values_plot)
        super(SignalViewer, self).__init__()

    def display(self, index = 0):
        self._initialize_UI()
        self._final_initialize_UI()
        self.update_plot()
        self.show()

    def show(self):
        self.dockUI.show()

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.window_title, self.parent)
        self.main_layout = QHBoxLayout()
        self.group_settings = QGroupBox("Parameters")
        self.group_plot = QGroupBox("Plots")
        self.layout = QVBoxLayout()
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

    def _final_initialize_UI(self):
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.main_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

    def update_plot(self):
        self._plot()
        self.plot.draw()

    def update_values_plot(self, values):
        self._update_values_plot(values)
        self.plot.axes.clear()
        self.update_plot()

    def _update_values_plot(self, values):
        idx = np.isin(self.output[:]["CellID"], np.array(values))
        self.foutput = self.output[idx]

    def _plot(self):
        mask_plots = ["MFR", "ISI"]
        corr_plots = ["Cor"]
        if self.foutput.dtype.names == None:
            self.signal_plot()
        elif self.foutput.dtype.names[1] == "Active":
            self.event_plot()
        elif self.foutput.dtype.names[1] in mask_plots:
            self.mask_plot()
        elif self.foutput.dtype.names[1] in corr_plots:
            self.corr_plot()

    def signal_plot(self):
        offset = 0
        cellID = []
        for i in range(self.foutput.shape[0]):
            t = np.arange(0, self.foutput.shape[1], 1)
            r = np.ptp(self.foutput[i])
            self.plot.axes.plot(t, self.foutput[i] + offset)
            cellID.append(str(i))
            offset += r

        self.plot.axes.set_yticks(np.arange(0, len(cellID)), cellID)
        self.plot.axes.set_ylabel('ROI ID')
        self.plot.axes.set_xlabel('Time (s)')

    def event_plot(self):
        self.plot.axes.scatter(y = self.foutput[:]["CellID"], x = self.foutput[:]["Active"], s=0.5)
        self.plot.axes.set_ylabel('ROI ID')
        self.plot.axes.set_xlabel('Time (s)')
