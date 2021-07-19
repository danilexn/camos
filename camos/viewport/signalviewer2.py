# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets, QtCore
from PyQt5.Qt import QPen
from PyQt5 import QtCore, QtOpenGL

import numpy as np
import pyqtgraph as pg
import pyqtgraph.parametertree as ptree

translate = QtCore.QCoreApplication.translate

from camos.utils.units import get_time
from camos.model.inputdata import InputData


def connectLines(l1, l2):
    l1.sigDragged.connect(lambda: l2.setValue(l1.value()))
    l2.sigDragged.connect(lambda: l1.setValue(l2.value()))


def updateRegion(region, p1, enable):
    if not enable:
        return
    minX, maxX = region.getRegion()
    p1.setXRange(minX, maxX)


def addInfiniteLine(plt):
    # Add the infinite line
    timeLine = pg.InfiniteLine(0, movable=True)
    # self.timeLine.setBounds([0, 0])
    plt.addItem(timeLine)

    return timeLine


class SignalViewer2(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None, title="", mask=[]):
        self.parent = parent
        self.parent.model.imagetoplot.connect(self.update_values_plot)
        self.output = signal
        self.foutput = self.output
        self.mask = mask
        self.pixelsize = 1
        self.title = title
        self.exportable = False
        self.connect_range = False
        self.to_export = np.zeros([1, 1])
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
        # Main plot
        self.plot = pg.GraphicsLayoutWidget()
        pg.setConfigOption("useOpenGL", True)
        self.plot.setViewport(QtOpenGL.QGLWidget())
        self.plot.useOpenGL(True)
        self.plot_layout.addWidget(self.plot)

        # Bottom parameter tree
        pt = self.createParameterTree()
        self.plot_layout.addWidget(pt)
        self.dockedWidget = QtWidgets.QWidget()

        # All in a floating dock
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.plot_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

    def export_plot_to_viewport(self):
        try:
            self.update_plot()
            image = InputData(self.outputimage)
            image.loadImage()
            self.parent.model.add_image(
                image, "Viewport of {}".format(self.analysis_name)
            )
        except:
            pass

    def createParameterTree(self):
        # Parameters tree
        param = ptree.Parameter.create(
            name=translate("ScatterPlot", "Parameters"),
            type="group",
            children=[
                dict(
                    name="connectRange",
                    title="Connect X-axis to viewport:    ",
                    type="bool",
                    value=False,
                    function=self._change_range_connection,
                ),
            ],
        )
        for c in param.children():
            c.setDefault(c.value())
            c.sigValueChanged.connect(c.opts["function"])
            c.sigTreeStateChanged.connect(c.opts["function"])

        pt = ptree.ParameterTree(showHeader=False)
        pt.setParameters(param)
        return pt

    def _change_size(self, param, value):
        # TODO: this is a placeholder
        print("Value changing (not finalized): %s %s" % (param, value))

    def _change_range_connection(self, param, value):
        self.connect_range = value

    def connectRangeToPlot(self, r1, p1):
        # We could just disconnect the events
        r1.sigRegionChanged.connect(lambda: updateRegion(r1, p1, self.connect_range))

    def toViewport(self, *args, **kwargs):
        try:
            image = InputData(self.to_export)
            image.loadImage()
            self.parent.model.add_image(image, "Viewport of {}".format(self.title))
        except:
            pass

    def clickEvent(self, event):
        if event._double:
            self.model.select_cells()

    def update_values_plot(self, values):
        try:
            self.plot.removeItem(self.plotitem)
        except Exception as e:
            raise e
        finally:
            self._update_values_plot(values)
            self._plot()

    def _update_values_plot(self, values):
        try:
            idx = np.isin(self.output[:]["CellID"], np.array(values))
            self.foutput = self.output[idx]
        except Exception as e:
            raise e

    def hoverEvent(self, event, img):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            return
        pos = event.pos()
        i, j = pos.y(), pos.x()

        # Get the position, in pixel units
        ppos = img.mapToParent(pos)
        x, y = ppos.x(), ppos.y()

        # Get the value from the data
        data = img.image
        i = int(np.clip(i, 0, data.shape[0] - 1))
        j = int(np.clip(j, 0, data.shape[1] - 1))
        val = data[i, j]

        # Show the value
        print("pos: (%0.1f, %0.1f)  value: %g" % (x, y, val))

    def _plot(self):
        mask_plots = ["MFR", "ISI"]
        corr_plots = ["Cor"]
        if self.foutput.dtype.names == None:
            self.plotitem = self.signal_plot()
        elif self.foutput.dtype.names[1] == "Burst":
            self.plotitem = self.event_plot()
        elif self.foutput.dtype.names[1] == "Active":
            self.plotitem = self.raster_plot()
        elif self.foutput.dtype.names[1] in mask_plots:
            self.plotitem = self.mask_plot(self.foutput.dtype.names[1])
        elif self.foutput.dtype.names[1] in corr_plots:
            self.plotitem = self.corr_plot()
        else:
            raise NotImplementedError

        if self.exportable:
            exportButton = QPushButton("Export to Viewport")
            exportButton.setToolTip(
                "The current plot will be loaded to the viewport as an image"
            )
            exportButton.clicked.connect(self.toViewport)
            self.plot_layout.addWidget(exportButton)

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
            labels={
                "left": "Normalized Source ID",
                "bottom": "Time ({})".format(get_time()),
            },
        )
        p1.enableAutoRange(False)
        lines = MultiLine(
            self.foutput[:]["Active"].flatten(), ev_ids_norm.flatten(), p1
        )
        lines.clickEvent = lambda event: self.clickEvent(event, lines)
        p1.addItem(lines)

        self.timeline = addInfiniteLine(p1)
        connectLines(self.timeline, self.parent.viewport.timeLine)
        self.connectRangeToPlot(self.parent.viewport.region, p1)

        return p1

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

        p1.clickEvent = lambda event: self.clickEvent(event, p1)

        self.timeline = addInfiniteLine(p1)
        connectLines(self.timeline, self.parent.viewport.timeLine)
        self.connectRangeToPlot(self.parent.viewport.region, p1)

        return p1

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
        plot.clickEvent = lambda event: self.clickEvent(event, plot)
        p1.addItem(plot)

        self.timeline = addInfiniteLine(p1)
        connectLines(self.timeline, self.parent.viewport.timeLine)
        self.connectRangeToPlot(self.parent.viewport.region, p1)

        return p1

    def mask_plot(self, name):
        # Setup the mask from the data
        mask = self.mask.astype(int)
        mask_dict = {}

        self.exportable = True

        for i in range(1, self.foutput.shape[0]):
            mask_dict[int(self.foutput[i]["CellID"][0])] = self.foutput[i][name][0]

        k = np.array(list(mask_dict.keys()))
        v = np.array(list(mask_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        mask_mask = np.nan_to_num(mapping_ar[mask])
        self.to_export = mask_mask

        # Setup the display object
        p1 = self.plot.addPlot(
            title=self.title,
            labels={"left": "Y-coordinate (px)", "bottom": "X-coordinate (px)"},
        )
        p1.setAspectLocked()
        p1.getViewBox().invertY(True)

        # Setup the image
        img = pg.ImageItem(image=mask_mask)
        img.hoverEvent = lambda event: self.hoverEvent(event, img)
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

        return p1


class MultiLine(pg.QtGui.QGraphicsPathItem):
    def __init__(self, x, y, parent):
        self.parent = parent
        self.parent.getViewBox().setMouseMode(pg.ViewBox.RectMode)

        n = len(x) if len(x) % 2 == 0 else len(x) - 1
        # Duplicating the data to connect
        x = x[0:n]
        _x = np.zeros(2 * len(x))
        _x[::2] = x
        _x[1::2] = x
        self.x = _x

        # Duplicating the data to connect
        y = y[0:n]
        _y = np.zeros(2 * len(y))
        _y[::2] = y - 1
        _y[1::2] = y
        self.y = _y

        # Creating the plot
        self.path = pg.arrayToQPath(self.x, self.y, connect="pairs")
        pg.QtGui.QGraphicsPathItem.__init__(self, self.path)
        self.updatePen()

    def updatePen(self):
        sz = self.parent.getViewBox().size().width()
        _rg = self.parent.getViewBox().state["viewRange"][0]
        rg = abs(_rg[1] - _rg[0])
        width = 2 * rg / sz

        hz = self.parent.getViewBox().size().height()
        _rh = self.parent.getViewBox().state["viewRange"][1]
        rh = abs(_rh[1] - _rh[0])
        height = max(1, 2 * rh / hz)

        y = self.y
        y[::2] = self.y[1::2] - int(height)
        self.path = pg.arrayToQPath(self.x, y, connect="pairs")
        self.setPath(self.path)
        self.setPen(QPen(QtCore.Qt.white, width))

    def wheelEvent(self, *args):
        super(MultiLine, self).wheelEvent(*args)
        self.updatePen()

    def mousePressEvent(self, *args):
        super(MultiLine, self).mousePressEvent(*args)
        self.updatePen()

    def mouseReleaseEvent(self, *args):
        super(MultiLine, self).mousePressEvent(*args)
        self.updatePen()

    def dragMoveEvent(self, *args):
        super(MultiLine, self).dragMoveEvent(*args)
        self.updatePen()

