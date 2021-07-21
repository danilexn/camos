# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import (
    DatasetInput,
    NumericInput,
    ImageInput,
    CustomComboInput,
)
from camos.utils.units import length
from camos.utils.units import get_time

# Import the custom heatmap plotter
from .heatmap import MFRHeatmap


class MeanFiringRate(Analysis):
    analysis_name = "Mean Firing Rate"

    def __init__(self, model=None, parent=None, signal=None):
        super(MeanFiringRate, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.plotter = MFRHeatmap(electrode_n=64)
        self.colname = "MFR"

    def _run(
        self,
        duration: NumericInput("Total Duration ({})".format(get_time()), 100),
        scale: NumericInput("Axis scale", 1),
        _i_units: CustomComboInput(list(length.keys()), "Axis units", 0),
        _i_data: DatasetInput("Source Dataset", 0),
        _i_mask: ImageInput("Mask image", 0),
    ):
        output_type = [("CellID", "int"), ("MFR", "float")]
        self.duration = duration
        self.scale = scale
        self.units = length[list(length.keys())[_i_units]]

        # data should be provided in format of peaks
        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]
        self.mask = self.model.images[_i_mask].image(0)
        if not ("Active" in data.dtype.names):
            return

        ROIs = np.unique(data[:]["CellID"])

        # Calculate mean firing rate per cell
        self.output = np.zeros(shape=(len(ROIs), 1), dtype=output_type)
        unique, counts = np.unique(data[:]["CellID"], return_counts=True)
        self.output[:]["CellID"] = unique.reshape(-1, 1)
        self.output[:]["MFR"] = counts.reshape(-1, 1)
