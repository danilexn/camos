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


class MeanFiringRate(Analysis):
    analysis_name = "Mean Firing Rate"

    def __init__(self, model=None, parent=None, signal=None):
        super(MeanFiringRate, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

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

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "MFR of {}".format(self.dataname), self, mask=self.mask
        )

    def _plot(self):
        import matplotlib.ticker as tick

        mask = self.mask.astype(int)
        MFR_dict = {}
        for i in range(1, self.foutput.shape[0]):
            MFR_dict[int(self.foutput[i]["CellID"][0])] = self.foutput[i]["MFR"][0]

        k = np.array(list(MFR_dict.keys())).astype(int)
        v = np.array(list(MFR_dict.values()))

        dim = int(max(k.max(), np.max(mask)))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        MFR_mask = mapping_ar[mask]

        self.outputimage = MFR_mask

        im = self.plot.axes.imshow(
            MFR_mask / self.duration, cmap="inferno", origin="upper"
        )
        self.plot.fig.colorbar(
            im, ax=self.plot.axes, label="Mean Firing Rate (Events/s)"
        )
        formatter = lambda x, pos: f"{(x / self.scale):.1f}"  # scale is the resolution
        self.plot.axes.xaxis.set_major_formatter(tick.FuncFormatter(formatter))
        self.plot.axes.yaxis.set_major_formatter(tick.FuncFormatter(formatter))
        self.plot.axes.set_ylabel("Y coordinate ({})".format(self.units))
        self.plot.axes.set_xlabel("X coordinate ({})".format(self.units))
