# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
import numpy as np

from camos.model.inputdata import InputData


class Plotter:
    def __init__(
        self, parent=None, viewer=None, data=None, hastimeline=True, *args, **kwargs
    ):
        self.parent = parent
        self.viewer = viewer
        self.data = data
        self.hastimeline = hastimeline
        self.plotItem = None
        self.mask = []
        self.title = ""
        self.colname = None

        self.connect_range = True
        self._connect_time = False

    def addInfiniteLine(self, plt):
        # Add the infinite line
        timeLine = pg.InfiniteLine(0, movable=True)
        # self.timeLine.setBounds([0, 0])
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
            self.plotItem = self._plot()

            # Generate the timeline
            self.timeline = self.addInfiniteLine(self.plotItem)
            self.connectLines(self.timeline, self.parent.viewport.timeLine)
            self.timeline.hide()

            if self.connect_time:
                self.connectRangeToPlot(self.parent.viewport.region, self.plotItem)

        except Exception as e:
            raise e

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
        try:
            image = InputData(self.to_export)
            image.loadImage()
            self.parent.model.add_image(image, "Viewport of {}".format(self.title))
        except:
            pass

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
