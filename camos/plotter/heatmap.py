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

        self.plotItem.setLabels(
            left="Electrode Y", bottom="Electrode X",
        )
        self.plotItem.setAspectLocked()

        self.plotItem.invertY(True)  # orient y axis to run top-to-bottom
        self.plotItem.setDefaultPadding(0.0)  # plot without padding data range
        self.plotItem.addItem(heatmap)  # display heatmap

        colorMap = pg.colormap.get("inferno", source="matplotlib")

        # generate an adjustabled color bar, initially spanning -1 to 1:
        self.colorbar = pg.ColorBarItem(values=(-1, 1), cmap=colorMap)
        # link color bar and color map to correlogram, and show it in plotItem:
        self.colorbar.setImageItem(heatmap, insert_in=self.plotItem)

    def toViewport(self, *args, **kwargs):
        try:
            image = InputData(self.to_export)
            image.loadImage()
            self.parent.model.add_image(image, "Viewport of {}".format(self.title))
        except:
            pass

    @property
    def colormap(self):
        return self._colormap

    @colormap.setter
    def colormap(self, value):
        self._colormap = value

        assert self.colorbar is not None
        # Colormap for the colorbar
        cmap = pg.colormap.get(self._colormap, source="matplotlib")
        self.colorbar.setCmap(cmap)
