# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.analysis import Analysis
import networkx as nx


class Correlation(Analysis):
    analysis_name = "Calculate Correlation"

    def __init__(self, model=None, parent=None, signal=None):
        super(Correlation, self).__init__(
            model, parent, input, name=self.analysis_name
        )
        self.model = model
        self.signal = signal

    def _run(self):
        self.pos = {}
        self.events = np.array([])
        self.cells = np.array([])
        signal_output = self.data

        self.G = nx.Graph()
        self.G.add_nodes_from(list(range(1, len(signal_output))))

        # Calculate node positions in the image
        for i in range(1, len(signal_output)):
            cell = self.mask[0] == i
            p = np.average(np.where(cell > 0), axis=1)
            self.pos[i] = np.flip(p)
            self.intReady.emit(i * 100 / len(signal_output))

        # Calculate cross correlation
        for i in range(1, len(signal_output) - 1):
            for j in range(i + 1, len(signal_output)):
                cc = np.corrcoef(signal_output[i], signal_output[j])[0, 1]
                if cc >= float(self.corrthreshold.text()):
                    self.G.add_edge(i, j, weight=cc)
            self.intReady.emit(i * 100 / len(signal_output))

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
        self.masklabel = QLabel("Mask image", self.dockUI)
        self.cbmask = QComboBox()
        self.cbmask.currentIndexChanged.connect(self._set_mask)
        self.cbmask.addItems(self.model.list_images())
        self.corrthresholdlabel = QLabel("Correlation threshold", self.dockUI)
        self.corrthreshold = QLineEdit()
        self.corrthreshold.setText("0.85")

        self.layout.addWidget(self.masklabel)
        self.layout.addWidget(self.cbmask)
        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)
        self.layout.addWidget(self.corrthresholdlabel)
        self.layout.addWidget(self.corrthreshold)

    def _set_mask(self):
        index = self.cbmask.currentIndex()
        self.mask = self.model.images[index]._image

    def _set_data(self, index):
        dataset = self.signal.data[index]
        self.data = dataset

    def _plot(self):
        nx.draw(
            self.G,
            self.pos,
            edge_color="white",
            alpha=0.3,
            width=2,
            ax=self.plot.axes,
        )
        self.plot.axes.imshow(self.mask[0], cmap="gray", origin="upper")
        self.plot.axes.set_ylabel('Frame number')
        self.plot.axes.set_xlabel('Frame number')
