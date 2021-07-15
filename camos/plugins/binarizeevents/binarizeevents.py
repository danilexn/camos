# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, DatasetInput
from camos.utils.units import get_time


class BinarizeEvents(Analysis):
    analysis_name = "Binarize Events"
    required = ["dataset"]

    def __init__(self, model=None, parent=None, signal=None):
        super(BinarizeEvents, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None

    def _run(
        self,
        _binsize: NumericInput("Bin Size ({})".format(get_time()), 1),
        _i_data: DatasetInput("Source dataset", 0),
    ):
        output_type = [("CellID", "int"), ("Active", "float")]

        # data should be provided in format summary (active events)
        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]
        if not ("Active" in data.dtype.names):
            raise ValueError("The dataset does not have the expected shape")

        # Calculates the bins
        active = data[:]["Active"] / _binsize
        active = np.floor(active) * _binsize

        # Stores the data into the output data structure
        self.output = np.zeros(shape=(len(active), 1), dtype=output_type)
        self.output[:]["CellID"] = data[:]["CellID"].reshape(-1, 1)
        self.output[:]["Active"] = active.reshape(-1, 1)

        # This reduces the events to one per electrode in the same bin
        self.output = np.unique(self.output, axis=0)
