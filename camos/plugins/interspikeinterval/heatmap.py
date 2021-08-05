# -*- coding: utf-8 -*-
# Created on Wed Jul 21 2021
# Last modified on Wed Jul 21 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
import numpy as np

from camos.plotter.plotter import Plotter


class ISIHeatmap(Plotter):
    def __init__(self, electrode_n=64, *args, **kwargs) -> None:
        super(ISIHeatmap, self).__init__(*args, **kwargs)
        self.electrode_n = electrode_n
        self.colname = "ISI"

    def _plot(self):
        isi = np.zeros(shape=(self.electrode_n * self.electrode_n))

        for idx, i in enumerate(self.data[:]["CellID"]):
            isi[i] = self.data[idx][self.colname]

        # reshape isi values in shape of chip for heatmap
        isi = np.reshape(isi, (self.electrode_n, self.electrode_n)).T

        heatmap = pg.ImageItem()
        heatmap.setImage(isi)

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
