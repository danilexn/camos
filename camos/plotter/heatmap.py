# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
import numpy as np

from camos.plotter.plotter import Plotter
from camos.model.inputdata import InputData


class Heatmap(Plotter):
    def __init__(self, *args, **kwargs) -> None:
        super(Heatmap, self).__init__(*args, **kwargs)
        self.electrode_n = 64
        self.exportable = True

    def _plot(self):
        mfr = np.zeros(shape=(self.electrode_n * self.electrode_n))

        for idx, i in enumerate(self.data[:]["CellID"]):
            mfr[i] = self.data[idx][self.colname]

        # reshape mfr values in shape of chip for heatmap
        mfr = np.reshape(mfr, (self.electrode_n, self.electrode_n)).T

        self.to_export = mfr
        heatmap = pg.ImageItem()
        heatmap.setImage(mfr)

        p1 = self.viewer.addPlot(
            title=self.title, labels={"left": "Electrode Y", "bottom": "Electrode X"},
        )
        p1.setAspectLocked()

        p1.invertY(True)  # orient y axis to run top-to-bottom
        p1.setDefaultPadding(0.0)  # plot without padding data range
        p1.addItem(heatmap)  # display heatmap

        # show full frame, label tick marks at top and left sides, with some extra space for labels:
        p1.showAxes(True, showValues=(True, True, False, False), size=20)
        colorMap = pg.colormap.get("inferno", source="matplotlib")

        # generate an adjustabled color bar, initially spanning -1 to 1:
        bar = pg.ColorBarItem(values=(-1, 1), cmap=colorMap)
        # link color bar and color map to correlogram, and show it in plotItem:
        bar.setImageItem(heatmap, insert_in=p1)

        return p1

    def toViewport(self, *args, **kwargs):
        try:
            image = InputData(self.to_export)
            image.loadImage()
            self.parent.model.add_image(image, "Viewport of {}".format(self.title))
        except:
            pass
