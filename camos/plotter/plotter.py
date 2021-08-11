# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import QObject

import pyqtgraph as pg
import numpy as np


class Plotter(QObject):
    backend = "pyqtgraph"

    def __init__(
        self,
        parent=None,
        viewer=None,
        data=None,
        hastimeline=True,
        title="",
        *args,
        **kwargs
    ):
        super(Plotter, self).__init__(*args, **kwargs)
        self.parent = parent
        self.viewer = viewer
        self.data = data
        self.hastimeline = hastimeline
        self.plotItem = None
        self.mask = []
        self._title = title
        self._axes = ["", ""]
        self._colormap = None
        self.colname = None
        self.exportable = False

        self.connect_range = True
        self._connect_time = False

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        try:
            if self.backend is "matplotlib":
                self.plotItem.axes.set_title(value)
            else:
                self.plotItem.setTitle(value)
        except Exception as e:
            print(str(e))
            pass

    @property
    def axes(self):
        return self._title

    @axes.setter
    def axes(self, x, y):
        self._axes = [x, y]
        self.plotItem.setLabels(bottom=self._axes[0], left=self._axes[1])

    @property
    def colormap(self):
        raise NotImplementedError("Colormap not available at base Plotter")

    @axes.setter
    def axes(self, x, y):
        raise NotImplementedError("Colormap not available at base Plotter")

    def addInfiniteLine(self, plt):
        # Add the infinite line
        timeLine = pg.InfiniteLine(0, movable=True, pen={"color": "y", "width": 2})
        plt.addItem(timeLine)

        return timeLine

    def connectLines(self, l1, l2):
        l1.sigDragged.connect(lambda: l2.setValue(l1.value()))
        l2.sigDragged.connect(lambda: l1.setValue(l2.value()))

    def updateRegion(self, region, p1, enable):
        if not enable:
            return
        minX, maxX = region.getRegion()
        p1.setXRange(minX, maxX)

    def _plot(self):
        raise NotImplementedError

    def plot(self):
        # The plot is not ready without parent
        # and without a viewer to attach the view
        assert self.parent is not None
        assert self.viewer is not None

        try:
            # Generate the base plot
            if self.backend is "pyqtgraph":
                self.plotItem = self.viewer.addPlot(
                    title=self.title, labels={"left": "Y axis", "bottom": "X axis"},
                )

            # Generate the specific plot
            self._plot()

            if self.backend is "matplotlib":
                self.viewer.draw()

            self.title = self._title

            if self.backend is "pyqtgraph":
                # Generate the timeline
                self.timeline = self.addInfiniteLine(self.plotItem)
                self.connectLines(self.timeline, self.parent.viewport.timeLine)
                self.timeline.hide()

                if self.connect_time:
                    self.connectRangeToPlot(self.parent.viewport.region, self.plotItem)

        except Exception as e:
            print(str(e))

    def connectRangeToPlot(self, r1, p1):
        # We could just disconnect the events
        r1.sigRegionChanged.connect(
            lambda: self.updateRegion(r1, p1, self.connect_range)
        )

    @property
    def connect_time(self):
        return self._connect_time

    @connect_time.setter
    def connect_time(self, value):
        self._connect_time = value

        if self._connect_time:
            self.timeline.show()
        else:
            self.timeline.hide()

    def toViewport(self, *args, **kwargs):
        raise NotImplementedError("Base Plotter cannot export to ViewPort")

    def clickEvent(self, event):
        if event._double:
            self.model.select_cells()

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
