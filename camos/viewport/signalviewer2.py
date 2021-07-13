# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QDockWidget, QVBoxLayout
from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QPen
from PyQt5 import QtGui, QtCore, QtOpenGL

import numpy as np
import pyqtgraph as pg


class SignalViewer2(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None):
        self.parent = parent
        self.output = signal
        self.foutput = self.output
        self.mask = []
        self.pixelsize = 1
        super(SignalViewer2, self).__init__()

    def display(self, index=0):
        self.buildUI()
        self.update_plot()
        self.show()

    def show(self):
        self.dockUI.show()

    def update_plot(self):
        self._plot()

    def buildUI(self):
        self.dockUI = QDockWidget(self.window_title, self.parent)
        self.plot_layout = QVBoxLayout()
        self.plot = pg.GraphicsLayoutWidget()
        pg.setConfigOption("useOpenGL", True)
        self.plot.setViewport(QtOpenGL.QGLWidget())
        self.plot.setViewportUpdateMode(QtGui.QGraphicsView.MinimalViewportUpdate)
        self.plot.useOpenGL(True)
        self.plot_layout.addWidget(self.plot)
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.plot_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

    def _plot(self):
        if self.foutput.dtype.names[1] == "Active":
            self.raster_plot()
        else:
            raise NotImplementedError

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

        p1 = self.plot.addPlot()
        p1.enableAutoRange(False)
        lines = MultiLine(
            self.foutput[:]["Active"].flatten(), ev_ids_norm.flatten(), p1
        )
        p1.addItem(lines)


class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, x, y, parent):
        n = len(x) if len(x) % 2 == 0 else len(x) - 1
        # Duplicating the data to connect
        x = x[0:n]
        _x = np.zeros(2 * len(x))
        _x[::2] = x
        _x[1::2] = x
        x = _x

        # Duplicating the data to connect
        y = y[0:n]
        _y = np.zeros(2 * len(y))
        _y[::2] = y - 1
        _y[1::2] = y
        y = _y

        # Creating the plot
        self.path = pg.arrayToQPath(x, y, connect="pairs")
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.setPen(QPen(QtCore.Qt.white, 1))
        self.parent = parent
        self.parent.getViewBox().setMouseMode(pg.ViewBox.RectMode)

    def shape(self):
        return pg.QtGui.QGraphicsItem.shape(self)

    def boundingRect(self):
        return self.path.boundingRect()

    def wheelEvent(self, *args):
        super(MultiLine, self).wheelEvent(*args)
        sz = self.parent.getViewBox().size().width()
        _rg = self.parent.getViewBox().state["viewRange"][0]
        rg = abs(_rg[1] - _rg[0])
        self.setPen(QPen(QtCore.Qt.white, 0.1 * sz * rg / 10 ** 6))

    def mousePressEvent(self, *args):
        super(MultiLine, self).mousePressEvent(*args)
        sz = self.parent.getViewBox().size().width()
        _rg = self.parent.getViewBox().state["viewRange"][0]
        rg = abs(_rg[1] - _rg[0])
        self.setPen(QPen(QtCore.Qt.white, 0.1 * sz * rg / 10 ** 6))

    def mouseReleaseEvent(self, *args):
        super(MultiLine, self).mousePressEvent(*args)
        sz = self.parent.getViewBox().size().width()
        _rg = self.parent.getViewBox().state["viewRange"][0]
        rg = abs(_rg[1] - _rg[0])
        self.setPen(QPen(QtCore.Qt.white, 0.1 * sz * rg / 10 ** 6))
