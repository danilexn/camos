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
            p_m = (
                np.min(np.where(cell), axis=1) + np.flip(maskcmos_trans)
            ) * maskcmos_scale[0]
            p_M = (
                np.max(np.where(cell), axis=1) + np.flip(maskcmos_trans)
            ) * maskcmos_scale[0]

            p = (p_m[0], p_m[1], p_M[0], p_M[1])

            idx.insert(int(i), p)

        # Retrieve the Calcium mask, find positions
        maskfl_scale = self.model.scales[fl]
        maskfl_trans = self.model.translation[fl]
        maskfl = self.model.images[fl]._image
        ROIs = np.unique(maskfl)

        for i in ROIs[1:]:  # avoid the background 0 value
            self.intReady.emit(i * 100 / len(ROIs))
            cell = maskfl[0] == i
            p_m = (
                np.min(np.where(cell), axis=1) + np.flip(maskfl_trans)
            ) * maskfl_scale[0]
            p_M = (
                np.max(np.where(cell), axis=1) + np.flip(maskfl_trans)
            ) * maskfl_scale[0]

            p = np.array((p_m[0] - dist, p_m[1] - dist, p_M[0] + dist, p_M[1] + dist))

            # Introduce checking the distance under the threshold
            nearest = list(idx.intersection(p))
            if len(nearest) == 0:
                continue

            row = np.array([(int(i), nearest[0])], dtype=output_type)
            self.output = np.append(self.output, row)

        self.mask = self.model.images[fl].image(0)
