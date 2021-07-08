# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal

from camos.tasks.analysis import Analysis


class ExtractSignal(Analysis):
    analysis_name = "Extract Signal"
    plotReady = pyqtSignal()

    def __init__(self, model=None, parent=None, signal=None):
        super(ExtractSignal, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.mask = None
        self.image = None
        self.sampling = 1
        self.finished.connect(self.output_to_signalmodel)
        self.finished.connect(self.update_plot)

    def _run(self):
        # Set the sampling rate from the UI
        self.sampling = int(self.F0_fps.text())
        # Get the ROIs from the mask
        ROIs = np.unique(self.mask.image(0))[1:]
        self.raw = np.zeros((len(ROIs), self.image.frames))
        total = len(ROIs)

        # Extract raw signals
        for i, r in enumerate(ROIs):
            cell = self.mask.image(0) == r
            self.raw[i, :] = np.average(self.image._image._imgs[:, cell], axis=(1))
            self.intReady.emit(i * 100 / total)

        # Process raw signals to get dF/F0
        F = self.raw
        N, frames = F.shape
        F0_time = int(self.F0_time.text())
        F0_perc = int(self.F0_perc.text())
        fps = int(self.F0_fps.text())

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
        name = self.cbimage.currentText()
        self.parent.signalmodel.add_data(
            self.output, "Signal from {}".format(name), self
        )

    def initialize_UI(self):
        self.masklabel = QLabel("Mask image", self.dockUI)
        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbmask = QComboBox()
        self.cbmask.currentIndexChanged.connect(self._set_mask)
        self.cbmask.addItems(self.model.list_images())
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.onlyInt = QIntValidator()
        self.F0_time_label = QLabel("Time Window", self.parent)
        self.F0_time = QLineEdit()
        self.F0_time.setValidator(self.onlyInt)
        self.F0_time.setText("10")
        self.layout.addWidget(self.F0_time_label)
        self.layout.addWidget(self.F0_time)

        self.F0_perc_label = QLabel("Percentile", self.parent)
        self.F0_perc = QLineEdit()
        self.F0_perc.setValidator(self.onlyInt)
        self.F0_perc.setText("50")
        self.layout.addWidget(self.F0_perc_label)
        self.layout.addWidget(self.F0_perc)

        self.F0_fps_label = QLabel("Sampling rate (Hz)", self.parent)
        self.F0_fps = QLineEdit()
        self.F0_fps.setValidator(self.onlyInt)
        self.F0_fps.setText("10")
        self.layout.addWidget(self.F0_fps_label)
        self.layout.addWidget(self.F0_fps)

        self.layout.addWidget(self.masklabel)
        self.layout.addWidget(self.cbmask)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

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
        self.plot.axes.set_xlabel("Time (s)")

    def _set_mask(self, text):
        index = self.cbmask.currentIndex()
        self.mask = self.model.images[index]

    def _set_image(self, text):
        index = self.cbimage.currentIndex()
        self.image = self.model.images[index]
