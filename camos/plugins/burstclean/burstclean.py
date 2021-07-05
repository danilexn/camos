# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, DatasetInput


class BurstClean(Analysis):
    analysis_name = "Clean Events"
    required = ["dataset"]

    def __init__(self, *args, **kwargs):
        super(BurstClean, self).__init__(*args, **kwargs)
        self.finished.connect(self.output_to_signalmodel)

    def _run(
        self,
        _filter_min: NumericInput("Minimum Events", 1),
        _filter_max: NumericInput("Maximum Events", 10000),
        _i_data: DatasetInput("Source dataset", 0),
    ):
        self.pos = {}
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
        IDs_include = unique[np.where((counts > _filter_min) & (counts < _filter_max))]
        idx = np.isin(IDs, IDs_include)
        active_filter = active[idx]
        IDs_filter = IDs[idx]

        # Calculate mean firing rate per cell
        self.output = np.zeros(shape=(len(active_filter), 1), dtype=output_type)
        self.output[:]["CellID"] = IDs_filter.reshape(-1, 1)
        self.output[:]["Active"] = active_filter.reshape(-1, 1)

        self.output = self.output[1:]
        self.foutput = self.output

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "Clean Events of {}".format(self.dataname), self
        )

    def _plot(self):
        ev_ids = self.foutput[:]["CellID"].flatten()
        ids = np.unique(ev_ids)
        ids = np.sort(ids)
        ids_norm = np.arange(0, len(ids), 1)

        k = np.array(list(ids))
        v = np.array(list(ids_norm))

        dim = max(k.max(), np.max(ids_norm))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        ev_ids_norm = mapping_ar[ev_ids]
        self.plot.axes.scatter(y=ev_ids_norm, x=self.foutput[:]["Active"], s=0.5)
        self.plot.axes.set_ylabel("Normalized ID")
        self.plot.axes.set_xlabel("Time (s)")
