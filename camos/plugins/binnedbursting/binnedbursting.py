# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator

import numpy as np

from camos.tasks.analysis import Analysis


class BinnedBursting(Analysis):
    analysis_name = "Binned Bursting"
    input_type = "summary"

    def __init__(self, model=None, parent=None, signal=None):
        super(BinnedBursting, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        _binsize = float(self.binsize.text())
        _threshold = float(self.threshold.text())
        output_type = [('Active', 'float')]

        # data should be provided in format summary (active events)
        data = self.data
        if not ("Active" in data.dtype.names):
            # TODO: rise an error message, not the expected data
            return

        # Calculates the bins
        active = data[:]["Active"]/_binsize
        active = np.floor(active) * _binsize

        # Calculates the number of events per bin
        unique, counts = np.unique(active, return_counts=True)

        # Conserves the events above the threshold
        active_filter = unique[np.where(counts > _threshold)]

        # Calculate mean firing rate per cell
        self.output = np.zeros(shape = (len(active_filter), 1), dtype = output_type)
        self.output[:]["Active"] = active_filter.reshape(-1, 1)

    def display(self):
        if type(self.signal.list_datasets(self.input_type)) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output, "Binned Bursting of {}".format(self.dataname), self)

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.signal.list_datasets(self.input_type))

        self.onlyDouble = QDoubleValidator()
        self.binsize_label = QLabel("Bin Size (s)", self.parent)
        self.binsize = QLineEdit()
        self.binsize.setValidator(self.onlyDouble)
        self.binsize.setText("1")
        self.layout.addWidget(self.binsize_label)
        self.layout.addWidget(self.binsize)

        self.onlyInt = QIntValidator()
        self.threshold_label = QLabel("Threshold", self.parent)
        self.threshold = QLineEdit()
        self.threshold.setValidator(self.onlyInt)
        self.threshold.setText("100")
        self.layout.addWidget(self.threshold_label)
        self.layout.addWidget(self.threshold)

        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

    def _set_data(self, index):
        dataset = self.signal.data[index]
        self.data = dataset
        self.dataname = self.signal.names[index]
        self.sampling = self.signal.sampling[index]

    def _plot(self):
        self.plot.axes.eventplot(self.foutput[:]["Active"], lineoffset = 0.5, color = "black")
        self.plot.axes.set_ylim(0, 1)
        self.plot.axes.set_xlabel('Time (s)')
