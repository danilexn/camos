# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from collections import defaultdict

from camos.tasks.analysis import Analysis
from camos.utils.generategui import (
    DatasetInput,
    NumericInput,
    ImageInput,
    CustomComboInput,
)
from camos.utils.units import length
from camos.plotter.image import Image


class InterspikeIntervalMask(Analysis):
    analysis_name = "Interspike Interval (on Mask)"

    def __init__(self, model=None, parent=None, signal=None):
        super(InterspikeIntervalMask, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.plotter = Image
        self.colname = "ISI"

    def _run(
        self,
        scale: NumericInput("Axis scale", 1),
        _i_units: CustomComboInput(list(length.keys()), "Axis units", 0),
        _i_data: DatasetInput("Source Dataset", 0),
        _i_mask: ImageInput("Mask image", 0),
    ):
        self.mask = self.model.images[_i_mask].image(0)
        output_type = [("CellID", "int"), ("ISI", "float")]
        self.scale = scale
        self.units = length[list(length.keys())[_i_units]]

        # data should be provided in format of peaks
        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]
        if not ("Active" in data.dtype.names):
            return

        ROIs = np.unique(data[:]["CellID"])

        # Create the output matrix
        self.output = np.zeros(shape=(len(ROIs), 1), dtype=output_type)

        # Save Cell IDs in the output matrix
        self.output[:]["CellID"] = ROIs.reshape(-1, 1)

        # Calculate a dictionary of the input, faster computation
        IDs_all = data[:]["CellID"]
        dict_events = defaultdict(list)

        # This explores all events
        if type(IDs_all[0]) == np.ndarray:
            for i in range(len(IDs_all)):
                dict_events[IDs_all[i][0]] += [data[i]["Active"][0]]
                self.intReady.emit(i * 100 / len(IDs_all))

        else:
            for i in range(len(IDs_all)):
                dict_events[IDs_all[i]] += [data[i]["Active"]]
                self.intReady.emit(i * 100 / len(IDs_all))

        ISI = np.zeros(len(ROIs))
        for i, ROI in enumerate(ROIs):
            ISI[i] = np.average(np.diff(dict_events[ROI]))

        self.output[:]["ISI"] = ISI.reshape(-1, 1)
