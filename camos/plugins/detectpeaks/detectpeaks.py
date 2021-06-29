# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.analysis import Analysis
from . import oopsi


class DetectPeaks(Analysis):
    analysis_name = "Detect Peaks"

    def __init__(self, model=None, parent=None, signal=None):
        super(DetectPeaks, self).__init__(
            model, parent, input, name=self.analysis_name
        )
        self.model = model
        self.signal = signal
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        output_type = [('CellID', 'int'), ('Active', 'float')]
        self.output = np.zeros(shape = (1, 1), dtype = output_type)

        data = self.data
        for i in range(data.shape[0]):
            F = np.diff(data[i])
            db, Cz = oopsi.fast(F, dt=0.1, iter_max=50)
            idxs = np.where(db >= 1)[0]/self.sampling
            for idx in idxs:
                row = np.array([(i, idx)], dtype = output_type)
                self.output = np.append(self.output, row)
            self.intReady.emit(i * 100 / data.shape[0])

        self.foutput = self.output

    def display(self):
        if type(self.signal.list_datasets()) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output, "Peaks from {}".format(self.dataname), self, self.sampling)

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.signal.list_datasets())

        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

    def _set_data(self, index):
        dataset = self.signal.data[index]
        self.data = dataset
        self.dataname = self.signal.names[index]
        self.sampling = self.signal.sampling[index]

    def _update_values_plot(self, values):
        idx = np.isin(self.output[:]["CellID"], np.array(values))
        self.foutput = self.output[idx]

    def _plot(self):
        self.plot.axes.scatter(y = self.foutput[:]["CellID"], x = self.foutput[:]["Active"], s=0.5)
        self.plot.axes.set_ylabel('ROI ID')
        self.plot.axes.set_xlabel('Time (s)')
