# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
import matplotlib

matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class AnalysisPlot(FigureCanvasQTAgg, QObject):
    plottoimage = pyqtSignal(tuple)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(AnalysisPlot, self).__init__(self.fig)
        connection_id = self.fig.canvas.mpl_connect("button_press_event", self.onClick)

    @pyqtSlot()
    def onClick(self, event):
        if event.dblclick:
            self.plottoimage.emit((event.button, event.xdata, event.ydata))
