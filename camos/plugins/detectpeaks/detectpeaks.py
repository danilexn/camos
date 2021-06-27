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

    def _run(self):
        self.events = np.array([])
        self.cells = np.array([])
        signal_output = self.data
        for i in range(signal_output.shape[0]):
            F = np.diff(signal_output[i])
            db, Cz = oopsi.fast(F, dt=0.1, iter_max=50)
            idx = np.where(db >= 1)
            self.events = np.append(self.events, idx)
            self.cells = np.append(self.cells, np.repeat(i, len(idx[0])))
            self.intReady.emit(i * 100 / signal_output.shape[0])

        self._events = self.events
        self._cells = self.cells
        self.finished.emit()

    def display(self):
        if type(self.signal.list_datasets()) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

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

    def _update_values_plot(self, values):
        idx = np.isin(self._cells, np.array(values))
        self.events = self._events[idx]
        self.cells = self._cells[idx]

    def _plot(self):
        self.plot.axes.scatter(self.events, self.cells, s=10)
        self.plot.axes.set_ylabel('ROI ID')
        self.plot.axes.set_xlabel('Time (s)')
