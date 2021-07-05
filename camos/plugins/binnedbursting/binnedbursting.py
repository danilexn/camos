# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, DatasetInput


class BinnedBursting(Analysis):
    analysis_name = "Binned Bursting"
    required = ["dataset"]

    def __init__(self, model=None, parent=None, signal=None):
        super(BinnedBursting, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(
        self,
        _binsize: NumericInput("Bin Size (s)", 1),
        _threshold: NumericInput("Threshold", 100),
        _i_data: DatasetInput("Source dataset", 0),
    ):
        _binsize = float(self.binsize.text())
        _threshold = float(self.threshold.text())
        output_type = [("Active", "float")]

        # data should be provided in format summary (active events)
        data = self.signal.data[_i_data]
        self.dataname = self.signal.names[_i_data]
        if not ("Active" in data.dtype.names):
            raise ValueError("The dataset does not have the expected shape")

        # Calculates the bins
        active = data[:]["Active"] / _binsize
        active = np.floor(active) * _binsize

        # Calculates the number of events per bin
        unique, counts = np.unique(active, return_counts=True)

        # Conserves the events above the threshold
        active_filter = unique[np.where(counts > _threshold)]

        # Calculate mean firing rate per cell
        self.output = np.zeros(shape=(len(active_filter), 1), dtype=output_type)
        self.output[:]["Active"] = active_filter.reshape(-1, 1)

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "Binned Bursting of {}".format(self.dataname), self
        )

    def _plot(self):
        self.plot.axes.eventplot(
            self.foutput[:]["Active"], lineoffset=0.5, color="black"
        )
        self.plot.axes.set_ylim(0, 1)
        self.plot.axes.set_yticklabels([])
        self.plot.axes.tick_params(axis=u"y", which=u"y", length=0)
        self.plot.axes.set_xlabel("Time (s)")
