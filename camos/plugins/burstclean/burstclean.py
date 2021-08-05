# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, DatasetInput
from camos.utils.units import get_time


class BurstClean(Analysis):
    analysis_name = "Clean Events"
    required = ["dataset"]

    def __init__(self, *args, **kwargs):
        super(BurstClean, self).__init__(*args, **kwargs)

    def _run(
        self,
        duration: NumericInput("Total Duration ({})".format(get_time()), 100),
        _filter_min: NumericInput("Minimum Events/{}".format(get_time()), 1),
        _filter_max: NumericInput("Maximum Events/{}".format(get_time()), 50),
        _i_data: DatasetInput("Source dataset", 0),
    ):
        output_type = [("CellID", "int"), ("Active", "float")]

        # data should be provided in format summary (active events)
        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]
        if not ("Active" in data.dtype.names):
            raise ValueError("The dataset does not have the expected shape")

        # Calculates the MFR, could be given as an input?
        unique, counts = np.unique(data[:]["CellID"], return_counts=True)
        active = data[:]["Active"]
        IDs = data[:]["CellID"]
        IDs_include = unique[
            np.where(
                (counts >= _filter_min * duration) & (counts <= _filter_max * duration)
            )
        ]
        idx = np.isin(IDs, IDs_include)
        active_filter = active[idx]
        IDs_filter = IDs[idx]

        # Calculate mean firing rate per cell
        self.output = np.zeros(shape=(len(active_filter), 1), dtype=output_type)
        self.output[:]["CellID"] = IDs_filter.reshape(-1, 1)
        self.output[:]["Active"] = active_filter.reshape(-1, 1)

        self.output = self.output[1:]
        self.foutput = self.output
        # self.notify(
        #     "{}: Events Before = {}; Events After = {}".format(
        #         self.analysis_name, len(data), len(self.output)
        #     ),
        #     "INFO",
        # )

    def connectComponents(self, fields):
        # Changing the input data to update the duration
        fields["_i_data"].connect(
            lambda x: fields["duration"].widget.setText(
                str(int(self.signal.properties[x]["duration"]))
            )
        )
