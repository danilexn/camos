# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator

import numpy as np

from camos.tasks.analysis import Analysis


class BurstClean(Analysis):
    analysis_name = "Clean Events"
    input_type = "summary"

    def __init__(self, model=None, parent=None, signal=None):
        super(BurstClean, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        _filter_min = float(self.minimumev.text())
        _filter_max = float(self.maximumev.text())
        self.pos = {}
        output_type = [('CellID', 'int'), ('Active', 'float')]

        # data should be provided in format summary (active events)
        data = self.data
        if not ("Active" in data.dtype.names):
            # TODO: rise an error message, not the expected data
            return

        # Calculates the MFR, could be given as an input?
        unique, counts = np.unique(data[:]["CellID"], return_counts=True)
        active = data[:]["Active"]
        IDs = data[:]["CellID"]
        IDs_include = unique[np.where((counts > _filter_min) & (counts < _filter_max))]
        idx = np.isin(IDs, IDs_include)
        active_filter = active[idx]
        IDs_filter = IDs[idx]

        # Calculate mean firing rate per cell
        self.output = np.zeros(shape = (len(active_filter), 1), dtype = output_type)
        self.output[:]["CellID"] = IDs_filter.reshape(-1, 1)
        self.output[:]["Active"] = active_filter.reshape(-1, 1)

        self.output = self.output[1:]
        self.foutput = self.output

    def display(self):
        if type(self.signal.list_datasets(self.input_type)) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output, "Clean Events of {}".format(self.dataname), self)

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.signal.list_datasets(self.input_type))

        self.onlyInt = QIntValidator()
        self.minimumev_label = QLabel("Minimum Events", self.parent)
        self.minimumev = QLineEdit()
        self.minimumev.setValidator(self.onlyInt)
        self.minimumev.setText("1")
        self.layout.addWidget(self.minimumev_label)
        self.layout.addWidget(self.minimumev)

        self.maximumev_label = QLabel("Maximum Events", self.parent)
        self.maximumev = QLineEdit()
        self.maximumev.setValidator(self.onlyInt)
        self.maximumev.setText("10000")
        self.layout.addWidget(self.maximumev_label)
        self.layout.addWidget(self.maximumev)

        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

    def _set_data(self, index):
        dataset = self.signal.data[index]
        self.data = dataset
        self.sampling = self.signal.sampling[index]
        self.dataname = self.signal.names[index]

    def _plot(self):
        self.plot.axes.scatter(y = self.foutput[:]["CellID"], x = self.foutput[:]["Active"], s=0.5)
        self.plot.axes.set_ylabel('ROI ID')
        self.plot.axes.set_xlabel('Time (s)')
