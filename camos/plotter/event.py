# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
import numpy as np

from camos.plotter.plotter import Plotter
from camos.utils.units import get_time


class Event(Plotter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.colname = "Intensity"

    def _plot(self):
        x, y = self.dataTo2DEvents()

        self.plotItem.setLabels(bottom="Time ({})".format(get_time()),)
        plot = pg.PlotDataItem(x, y, connect="pairs")
        plot.clickEvent = lambda event: self.clickEvent(event, plot)
        self.plotItem.addItem(plot)

    def dataTo2DEvents(self):
        x = self.data[:][self.colname].flatten()
        n = len(x) if len(x) % 2 == 0 else len(x) - 1

        # Duplicating the data to connect
        x = x[0:n]
        _x = np.zeros(2 * len(x))

        _x[::2] = x
        _x[1::2] = x
        x = _x

        y = np.ones(len(x))
        y[1::2] = 0

        return x, y
