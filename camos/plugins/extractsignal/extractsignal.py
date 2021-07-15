# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtCore import pyqtSignal

from camos.tasks.analysis import Analysis
from camos.utils.generategui import NumericInput, ImageInput
from camos.utils.units import get_time


class ExtractSignal(Analysis):
    analysis_name = "Extract Signal"
    plotReady = pyqtSignal()
    required = ["image"]

    def __init__(self, model=None, parent=None, signal=None):
        super(ExtractSignal, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.mask = None
        self.image = None
        self.sampling = 1

    def _run(
        self,
        fps: NumericInput("Sampling Rate (Hz)", 10),
        F0_time: NumericInput("Time Window ({})".format(get_time()), 10),
        F0_perc: NumericInput("Percentile", 50),
        _i_mask: ImageInput("Mask Image", 0),
        _i_fluor: ImageInput("Fluorescence Image", 0),
    ):
        # Set the variables from the UI
        self.sampling = fps
        mask = self.model.images[_i_mask].image(0)
        image = self.model.images[_i_fluor]
        self.imagename = self.model.names[_i_fluor]

        # Get the ROIs from the mask
        ROIs = np.unique(mask)[1:]
        self.raw = np.zeros((len(ROIs), image.frames))
        total = len(ROIs)

        # Extract raw signals
        for i, r in enumerate(ROIs):
            cell = mask == r
            self.raw[i, :] = np.average(image._image._imgs[:, cell], axis=(1))
            self.intReady.emit(i * 100 / total)

        # Process raw signals to get dF/F0
        F = self.raw
        N, frames = F.shape

        # Code adapted from FluoroSNNAP
        # Determine deltaF/F by subtracting each value with the
        # mean of the lower 50% of previous 10-s values and dividing it
        # by the mean of the lower 50% of previous 10-s values.

        dF_cell = np.zeros(F.shape)

        _int_idx = np.arange(0, frames + 1, fps * F0_time)
        interval_idx = np.unique(_int_idx)

        # For the first 10-s of data, take the min value for F0
        F0 = np.min(F[:, 0 : interval_idx[1]], axis=1)

        for k in range(interval_idx[1]):
            dF_cell[:, k] = (F[:, k] - F0) / F0

        for it in range(interval_idx[1], frames):
            x = F[:, (it - F0_time) : it]
            p = np.percentile(x, F0_perc, axis=1)
            F0 = np.zeros(N)
            for n in range(N):
                F0[n] = np.mean(x[n, np.where(x[n, :] < p[n])])

            dF_cell[:, it] = (F[:, it] - F0) / F0

        self.output = dF_cell

    def output_to_signalmodel(self):
        name = self.imagename
        self.parent.signalmodel.add_data(
            self.output, "Signal from {}".format(name), self
        )

    def _plot(self):
        offset = 0
        cellID = []
        for i in range(self.foutput.shape[0]):
            t = np.arange(0, self.foutput.shape[1], 1) / self.sampling
            self.plot.axes.plot(t, self.foutput[i] + offset)
            cellID.append(str(i + 1))
            offset += 1

        self.plot.axes.set_yticks(np.arange(0, len(cellID)), minor=cellID)
        self.plot.axes.set_ylabel("ROI ID")
        self.plot.axes.set_xlabel("Time ({})".format(get_time()))
