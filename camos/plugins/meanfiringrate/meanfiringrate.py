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
)
from camos.utils.units import length
from camos.utils.units import get_time

# Import the custom heatmap plotter
from .heatmap import MFRHeatmap


class MeanFiringRate(Analysis):
    analysis_name = "Mean Firing Rate"
    required = ["dataset"]

    def __init__(self, model=None, parent=None, signal=None):
        super(MeanFiringRate, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.plotter = MFRHeatmap
        self.colname = "MFR"

    def _run(
        self,
        duration: NumericInput("Recording duration in seconds", 600),
        electrode_x: NumericInput("Number of electrodes along one axis", 64),
        # scale: NumericInput("Axis scale", 1),
        # _i_units: CustomComboInput(list(length.keys()), "Axis units", 0),
        _i_data: DatasetInput("Source Dataset", 0),
    ):
        output_type = [("CellID", "int"), ("MFR", "float")]
        self.duration = duration
        self.plotter = MFRHeatmap(electrode_n=electrode_x)

        """
        Data format:

        First column is electrode ID
        Second column is time of event
            ('CellID', 'Active')
            [[(1520, 2.64562191e-03)]
            [(4038, 5.58520180e-03)]
            [(3245, 6.39358627e-03)]

        If electrode 1520 has 500 spike events, then there are 500 rows with ID 1520
        """

        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]

        # Calculate mean firing rate per cell
        ROIs = np.unique(data[:]["CellID"])
        self.output = np.zeros(shape=(len(ROIs), 1), dtype=output_type)

        # get the event counts and make CellID unique
        unique, counts = np.unique(data[:]["CellID"], return_counts=True)
        self.output[:]["CellID"] = unique.reshape(-1, 1)
        self.output[:]["MFR"] = counts.reshape(-1, 1)
        self.output[:]["MFR"] = self.output[:]["MFR"] / self.duration

