# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from rtree import index

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, ImageInput
from camos.utils.units import get_length


class CorrelatePosition(Analysis):
    analysis_name = "Correlate Positions"
    required = ["image"]

    def __init__(self, model=None, parent=None, signal=None):
        super(CorrelatePosition, self).__init__(
            model, parent, input, name=self.analysis_name
        )
        self.model = model
        self.signal = signal
        self.finished.connect(self.output_to_signalmodel)

    def _run(
        self,
        dist: NumericInput("Maximum distance ({})".format(get_length()), 100),
        cmos: ImageInput("CMOS mask image", 0),
        fl: ImageInput("Fluorescence mask image", 0),
    ):
        # The image input returns the index of the image model
        maskcmos_scale = self.model.scales[cmos]
        maskcmos_trans = self.model.translation[cmos]
        maskcmos = self.model.images[cmos]._image

        ROIs = np.unique(maskcmos)

        # Setup the output variables
        output_type = [("CellID", "int"), ("Nearest", "int")]
        self.output = np.zeros(shape=(1, 1), dtype=output_type)

        # Create the spatial index
        idx = index.Index()
        idx_dic = {}

        # Put mask coordinates into the spatial index
        for i in ROIs[1:]:  # avoid the background 0 value
            self.intReady.emit(i * 100 / len(ROIs))
            cell = maskcmos[0] == i
            p = (
                np.average(np.where(cell), axis=1) + np.flip(maskcmos_trans)
            ) * maskcmos_scale[0]
            idx.insert(i, (p[0], p[1], p[0], p[1]))
            idx_dic[i] = p

        # Retrieve the Calcium mask, find positions
        maskfl_scale = self.model.scales[fl]
        maskfl_trans = self.model.translation[fl]
        maskfl = self.model.images[fl]._image
        ROIs = np.unique(maskfl)

        for i in ROIs[1:]:  # avoid the background 0 value
            self.intReady.emit(i * 100 / len(ROIs))
            cell = maskfl[0] == i
            p = (
                np.average(np.where(cell), axis=1) + np.flip(maskfl_trans)
            ) * maskfl_scale[0]
            # Introduce checking the distance under the threshold
            nearest = list(idx.nearest((p[0], p[1], p[0], p[1]), 1))[0]
            if np.linalg.norm(idx_dic[nearest] - p) < dist:
                row = np.array([(i, nearest)], dtype=output_type)
                self.output = np.append(self.output, row)

        self.maskimage = self.model.images[fl].image(0)
        self.finished.emit()

    def _plot(self):
        mask = self.maskimage
        map_dict = {}
        for i in range(1, self.foutput.shape[0]):
            map_dict[int(self.foutput[i]["CellID"])] = self.foutput[i]["Nearest"]

        k = np.array(list(map_dict.keys()))
        v = np.array(list(map_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        map_mask = mapping_ar[mask]

        self.outputimage = map_mask

        im = self.plot.axes.imshow(map_mask, cmap="gray", origin="upper")
        self.plot.fig.colorbar(im, ax=self.plot.axes, label="ID of the ROI")
        self.plot.axes.set_ylabel("Y coordinate")
        self.plot.axes.set_xlabel("X coordinate")
