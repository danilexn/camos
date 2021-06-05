#
# Created on Sat Jun 05 2021
#
# The MIT License (MIT)
# Copyright (c) 2021 Daniel León, Josua Seidel, Hani Al Hawasli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.analysis import Analysis
import camos.utils.apptools as apptools
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection


class InterspikeInterval(Analysis):
    def __init__(self, model=None, parent=None, input=None):
        super(InterspikeInterval, self).__init__(
            model, parent, input, name="Interspike interval"
        )
        self.data = None
        self.analysis_name = "Mean Firing Rate"

    def _run(self):
        self.output = np.zeros(len(self.data.electrodes))
        for i, electrode in enumerate(self.data.electrodes):
            electrode_event = np.argwhere(self.data.event_electrode == electrode)
            self.output[i] = np.mean(np.diff(self.data.events[electrode_event]))

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        # TODO: analyze by clusters, or analyze completely
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.model.list_datasets())

        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

    def _set_data(self, index):
        dataset = self.model.dataset[index]
        if apptools.is_cmos(dataset):
            self.data = dataset
        else:
            # TODO: include an error, the dataset is not CMOS
            pass

    def _plot(self):
        circles = [
            plt.Circle(self.input.electrodeToCoord[e]) for e in self.output.keys()
        ]
        col = PatchCollection(circles, array=self.output.values(), cmap="RdYlGn")
        self.plot.axes.add_collection(col)
        self.plot.fig.colorbar(col)
