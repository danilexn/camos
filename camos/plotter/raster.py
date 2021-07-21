# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore
from PyQt5.Qt import QPen

import pyqtgraph as pg
import numpy as np

from camos.plotter.plotter import Plotter
from camos.utils.units import get_time


class Raster(Plotter):
    def __init__(self, *args, **kwargs):
        super(Raster, self).__init__(*args, **kwargs)

    def _plot(self):
        ev_ids = self.data[:]["CellID"].flatten()
        ids = np.unique(ev_ids)
        ids = np.sort(ids)
        ids_norm = np.arange(0, len(ids), 1)

        k = np.array(list(ids))
        v = np.array(list(ids_norm))

        dim = max(k.max(), np.max(ids_norm))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        ev_ids_norm = mapping_ar[ev_ids]

        p1 = self.viewer.addPlot(
            title=self.title,
            labels={
                "left": "Normalized Source ID",
                "bottom": "Time ({})".format(get_time()),
            },
        )
        p1.enableAutoRange(False)
        lines = MultiLine(self.data[:]["Active"].flatten(), ev_ids_norm.flatten(), p1)
        lines.clickEvent = lambda event: self.clickEvent(event, lines)
        p1.addItem(lines)

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
