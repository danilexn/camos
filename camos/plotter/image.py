# -*- coding: utf-8 -*-
# Created on Mon Jul 19 2021
# Last modified on Mon Jul 19 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
import numpy as np

from camos.plotter.plotter import Plotter
from camos.model.inputdata import InputData


class Image(Plotter):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cmap_label = "Pixel intensity value"
        self.exportable = True

    def _plot(self):
        _mask = self.replaceValuesOnMask()
        # Setup the display object
        p1 = self.viewer.addPlot(
            title=self.title,
            labels={"left": "Y-coordinate (px)", "bottom": "X-coordinate (px)"},
        )
        p1.setAspectLocked()
        p1.getViewBox().invertY(True)

        # Setup the image
        img = pg.ImageItem(image=_mask)
        img.hoverEvent = lambda event: self.hoverEvent(event, img)
        img.setOpts(axisOrder="row-major")
        p1.addItem(img)
        self.to_export = _mask

        # Colormap for the colorbar
        cm = pg.colormap.get("inferno", source="matplotlib")

        # Add the colorbar
        bar = pg.ColorBarItem(
            values=(np.min(_mask), np.max(_mask)), cmap=cm, label=self.cmap_label
        )
        bar.setImageItem(img, insert_in=p1)

        return p1

    def replaceValuesOnMask(self):
        # Setup the mask from the data
        mask = self.mask.astype(int)
        mask_dict = {}

        for i in range(1, self.data.shape[0]):
            mask_dict[int(self.data[i]["CellID"].flatten()[0])] = self.data[i][
                self.colname
            ].flatten()[0]

        k = np.array(list(mask_dict.keys())).flatten()
        v = np.array(list(mask_dict.values())).flatten()

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        return np.nan_to_num(mapping_ar[mask])

    def toViewport(self, *args, **kwargs):
        try:
            image = InputData(self.to_export)
            image.loadImage()
            self.parent.model.add_image(image, "Viewport of {}".format(self.title))
        except:
            pass
