# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
import numpy as np

from camos.plotter.plotter import Plotter
from camos.utils.units import get_time


class Signal(Plotter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _plot(self):
        nPlots = self.data.shape[0]

        self.plotItem.setLabels(
            left="Source ID", bottom="Time ({})".format(get_time()),
        )

        self._signal_curves = []
        offset = 0
        for i in range(nPlots):
            t = np.arange(0, self.data.shape[1], 1)
            curve = pg.PlotCurveItem(
                pen=({"color": (i, nPlots * 1.3), "width": 1}), skipFiniteCheck=True
            )
            self.plotItem.addItem(curve)
            self._signal_curves.append(curve)
            curve.setData(self.data[i] + offset)
            offset += 1

        self.plotItem.clickEvent = lambda event: self.clickEvent(event, self.plotItem)
