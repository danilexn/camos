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

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class SignalViewer(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None):
        self.parent = parent
        self.output = signal
        self.foutput = self.output
        self.parent.model.imagetoplot.connect(self.update_values_plot)
        self.mask = []
        self.pixelsize = 1
        super(SignalViewer, self).__init__()

    def display(self, index=0):
        self._initialize_UI()
        self._final_initialize_UI()
        self.update_plot()
        self.show()

    def show(self):
        self.dockUI.show()

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.window_title, self.parent)
        self.plot_layout = QVBoxLayout()
        self.plot = AnalysisPlot(self, width=5, height=4, dpi=100)
        self.plot.plottoimage.connect(self.parent.model.select_cells)
        self.toolbar = NavigationToolbar(self.plot, None)
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.plot)

    def _final_initialize_UI(self):
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.plot_layout)
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
        elif self.foutput.dtype.names[0] == "Active":
            self.event_plot()
        elif self.foutput.dtype.names[1] == "Active":
            self.raster_plot()
        elif self.foutput.dtype.names[1] in mask_plots:
            self.mask_plot(self.foutput.dtype.names[1])
        elif self.foutput.dtype.names[1] in corr_plots:
            self.corr_plot()
        else:
            raise NotImplementedError

    def signal_plot(self):
        offset = 0
        cellID = []
        for i in range(self.foutput.shape[0]):
            t = np.arange(0, self.foutput.shape[1], 1)
            self.plot.axes.plot(t, self.foutput[i] + offset)
            cellID.append(str(i + 1))
            offset += 1

        self.plot.axes.set_yticks(np.arange(0, len(cellID)), minor=cellID)
        self.plot.axes.set_ylabel("ROI ID")
        self.plot.axes.set_xlabel("Time (s)")

    def raster_plot(self):
        ev_ids = self.foutput[:]["CellID"].flatten()
        ids = np.unique(ev_ids)
        ids = np.sort(ids)
        ids_norm = np.arange(0, len(ids), 1)

        k = np.array(list(ids))
        v = np.array(list(ids_norm))

        dim = max(k.max(), np.max(ids_norm))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        ev_ids_norm = mapping_ar[ev_ids]
        self.plot.axes.scatter(y=ev_ids_norm, x=self.foutput[:]["Active"], s=0.5)
        self.plot.axes.set_ylabel("Normalized ID")
        self.plot.axes.set_xlabel("Time (s)")

    def event_plot(self):
        self.plot.axes.eventplot(
            self.foutput[:]["Active"], lineoffset=0.5, color="black"
        )
        self.plot.axes.set_ylim(0, 1)
        self.plot.axes.set_yticklabels([])
        self.plot.axes.tick_params(axis=u"y", which=u"y", length=0)
        self.plot.axes.set_xlabel("Time (s)")

    def mask_plot(self, name):
        mask = self.mask
        mask_dict = {}
        for i in range(1, self.foutput.shape[0]):
            mask_dict[int(self.foutput[i]["CellID"][0])] = self.foutput[i][name][0]

        k = np.array(list(mask_dict.keys()))
        v = np.array(list(mask_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        mask_mask = mapping_ar[mask]

        self.plot.axes.imshow(mask_mask, cmap="inferno", origin="upper")
        self.plot.axes.set_ylabel("Y coordinate")
        self.plot.axes.set_xlabel("X coordinate")
