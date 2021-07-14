# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QDockWidget, QVBoxLayout
from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QPen
from PyQt5 import QtCore, QtOpenGL

import numpy as np
import pyqtgraph as pg
import pyqtgraph.parametertree as ptree

translate = QtCore.QCoreApplication.translate

from camos.utils.units import get_time


def connectLines(l1, l2):
    l1.sigDragged.connect(lambda: l2.setValue(l1.value()))
    l2.sigDragged.connect(lambda: l1.setValue(l2.value()))


def connectRangeToPlot(r1, p1):
    pass


def addInfiniteLine(plt):
    # Add the infinite line
    timeLine = pg.InfiniteLine(0, movable=True)
    # self.timeLine.setBounds([0, 0])
    plt.addItem(timeLine)

    return timeLine


class SignalViewer2(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None, title=""):
        self.parent = parent
        self.output = signal
        self.foutput = self.output
        self.mask = []
        self.pixelsize = 1
        self.title = title
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
        self.plot.useOpenGL(True)
        self.plot_layout.addWidget(self.plot)
        self.createParameterTree(self.plot_layout)
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.plot_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

    def createParameterTree(self, layout):
        # Parameters tree
        param = ptree.Parameter.create(
            name=translate("ScatterPlot", "Parameters (disabled)"),
            type="group",
            children=[
                dict(
                    name="size",
                    title=translate("ScatterPlot", "Size:    "),
                    type="int",
                    limits=[1, None],
                    value=10,
                ),
                dict(name="pxMode", title="pxMode:    ", type="bool", value=True),
                dict(name="useCache", title="useCache:    ", type="bool", value=True),
                dict(
                    name="mode",
                    title=translate("ScatterPlot", "Mode:    "),
                    type="list",
                    values={
                        translate("ScatterPlot", "New Item"): "newItem",
                        translate("ScatterPlot", "Reuse Item"): "reuseItem",
                        translate("ScatterPlot", "Simulate Pan/Zoom"): "panZoom",
                        translate("ScatterPlot", "Simulate Hover"): "hover",
                    },
                    value="reuseItem",
                ),
            ],
        )
        for c in param.children():
            c.setDefault(c.value())

        pt = ptree.ParameterTree(showHeader=False)
        pt.setParameters(param)
        layout.addWidget(pt)

    def _plot(self):
        mask_plots = ["MFR", "ISI"]
        corr_plots = ["Cor"]
        if self.foutput.dtype.names == None:
            self.signal_plot()
        elif self.foutput.dtype.names[1] == "Burst":
            self.event_plot()
        elif self.foutput.dtype.names[1] == "Active":
            self.raster_plot()
        elif self.foutput.dtype.names[1] in mask_plots:
            self.mask_plot(self.foutput.dtype.names[1])
        elif self.foutput.dtype.names[1] in corr_plots:
            self.corr_plot()
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

        p1 = self.plot.addPlot(
            title=self.title,
            labels={"left": "Source ID", "bottom": "Time ({})".format(get_time())},
        )
        p1.enableAutoRange(False)
        lines = MultiLine(
            self.foutput[:]["Active"].flatten(), ev_ids_norm.flatten(), p1
        )
        p1.addItem(lines)

        self.timeline = addInfiniteLine(p1)
        connectLines(self.timeline, self.parent.viewport.timeLine)

    def signal_plot(self):
        nPlots = self.foutput.shape[0]
        p1 = self.plot.addPlot(
            title=self.title,
            labels={"left": "Source ID", "bottom": "Time ({})".format(get_time())},
        )
        self._signal_curves = []
        offset = 0
        for i in range(nPlots):
            t = np.arange(0, self.foutput.shape[1], 1)
            curve = pg.PlotCurveItem(
                pen=({"color": (i, nPlots * 1.3), "width": 1}), skipFiniteCheck=True
            )
            p1.addItem(curve)
            self._signal_curves.append(curve)
            curve.setData(self.foutput[i] + offset)
            offset += 1

        self.timeline = addInfiniteLine(p1)
        connectLines(self.timeline, self.parent.viewport.timeLine)

    def event_plot(self):
        x = self.foutput[:]["Burst"].flatten()
        n = len(x) if len(x) % 2 == 0 else len(x) - 1
        # Duplicating the data to connect
        x = x[0:n]
        _x = np.zeros(2 * len(x))
        _x[::2] = x
        _x[1::2] = x
        x = _x

        y = np.ones(len(x))
        y[1::2] = 0

        p1 = self.plot.addPlot(
            title=self.title, labels={"bottom": "Time ({})".format(get_time())}
        )
        plot = pg.PlotDataItem(x, y, connect="pairs")
        p1.addItem(plot)

        self.timeline = addInfiniteLine(p1)
        connectLines(self.timeline, self.parent.viewport.timeLine)

    def mask_plot(self, name):
        # Setup the mask from the data
        mask = self.mask
        mask_dict = {}
        for i in range(1, self.foutput.shape[0]):
            mask_dict[int(self.foutput[i]["CellID"][0])] = self.foutput[i][name][0]

        k = np.array(list(mask_dict.keys()))
        v = np.array(list(mask_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        mask_mask = np.nan_to_num(mapping_ar[mask])

        # Setup the display object
        p1 = self.plot.addPlot(
            title=self.title,
            labels={"left": "Y-coordinate (px)", "bottom": "X-coordinate (px)"},
        )
        p1.setAspectLocked()

        # Setup the image
        img = pg.ImageItem(image=mask_mask)
        img.setOpts(axisOrder="row-major")
        p1.addItem(img)

        # Colormap for the colorbar
        cm = pg.colormap.get("inferno", source="matplotlib")

        # What is the label for the colorbar
        cm_label = "Mean Firing Rate (Events per {})".format(get_time())
        if self.foutput.dtype.names[1] == "ISI":
            cm_label = "Interspike Interval (1/{})".format(get_time())

        # Add the colorbar
        bar = pg.ColorBarItem(
            values=(np.min(mask_mask), np.max(mask_mask)), cmap=cm, label=cm_label
        )
        bar.setImageItem(img, insert_in=p1)


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
