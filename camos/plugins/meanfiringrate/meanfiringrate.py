# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.analysis import Analysis
import matplotlib.cm as cm

import networkx as nx
from camos.plugins.detectpeaks import oopsi


class MeanFiringRate(Analysis):
    analysis_name = "Mean Firing Rate"

    def __init__(self, model=None, parent=None, signal=None):
        super(MeanFiringRate, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None

    def _run(self):
        self.pos = {}
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

        self.G_mfr = nx.Graph()
        # Calculate the positions
        for i in range(1, len(signal_output)):
            cell = self.mask[0] == i
            p = np.average(np.where(cell > 0), axis=1)
            self.pos[i - 1] = np.flip(p)
            self.intReady.emit(i * 100 / signal_output.shape[0])

        # Calculate mean firing rate per cell
        for i in range(1, len(signal_output) - 1):
            self.G_mfr.add_node(
                i,
                weight=np.sum(np.diff(self.events[np.where(self.cells == i)])),
            )
            self.intReady.emit(i * 100 / signal_output.shape[0])

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

        self.layout.addWidget(self.masklabel)
        self.layout.addWidget(self.cbmask)
        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

    def _set_data(self, index):
        dataset = self.signal.data[index]
        self.data = dataset

    def _set_mask(self, text):
        index = self.cbmask.currentIndex()
        self.mask = self.model.images[index]._image

    def _plot(self):
        colors = [self.G_mfr.nodes[n]["weight"] for n in self.G_mfr.nodes]
        colors = [float(i) / max(colors) for i in colors]
        colors = cm.viridis(colors)
        nx.draw(
            self.G_mfr,
            self.pos,
            node_color=colors,
            alpha=0.6,
            width=2,
            ax=self.plot.axes,
        )
        self.plot.axes.imshow(self.mask[0], cmap="gray", origin="upper")
        self.plot.axes.set_ylabel('Y coordinate')
        self.plot.axes.set_xlabel('X coordinate')
