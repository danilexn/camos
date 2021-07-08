# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.analysis import Analysis
from rtree import index


class CorrelatePosition(Analysis):
    analysis_name = "Correlate Positions"

    def __init__(self, model=None, parent=None, signal=None):
        super(CorrelatePosition, self).__init__(
            model, parent, input, name=self.analysis_name
        )
        self.model = model
        self.signal = signal
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        # Retrieve the UI parameters
        dist = float(self.distthreshold.text())
        # Retrieve the CMOS mask
        maskcmos = self.maskcmos
        ROIs = np.unique(maskcmos)

        # Setup the output variables
        output_type = [("CellID", "int"), ("Nearest", "int")]
        self.output = np.zeros(shape=(1, 1), dtype=output_type)

        # Create the spatial index
        idx = index.Index()
        idx_dic = {}

        # Put mask coordinates into the spatial index
        for i in ROIs[1:]:  # avoid the background 0 value
            self.intReady.emit(i * 100 / len(ROIs))
            cell = maskcmos[0] == i
            p = (
                np.average(np.where(cell), axis=1) + self.maskcmos_trans
            ) * self.maskcmos_scale[0]
            idx.insert(i, (p[0], p[1], p[0], p[1]))
            idx_dic[i] = p

        # Retrieve the Calcium mask, find positions
        maskfl = self.maskfl
        ROIs = np.unique(maskfl)

        for i in ROIs[1:]:  # avoid the background 0 value
            self.intReady.emit(i * 100 / len(ROIs))
            cell = maskfl[0] == i
            p = (
                np.average(np.where(cell), axis=1) + self.maskfl_trans
            ) * self.maskfl_scale[0]
            # Introduce checking the distance under the threshold
            nearest = list(idx.nearest((p[0], p[1], p[0], p[1]), 1))[0]
            if np.linalg.norm(idx_dic[nearest] - p) < dist:
                row = np.array([(i, nearest)], dtype=output_type)
                self.output = np.append(self.output, row)

        self.finished.emit()

    def display(self):
        if type(self.model.list_images()) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def initialize_UI(self):
        self.maskcmoslabel = QLabel("CMOS mask image", self.dockUI)
        self.cbmaskcmos = QComboBox()
        self.cbmaskcmos.currentIndexChanged.connect(self._set_maskcmos)
        self.cbmaskcmos.addItems(self.model.list_images())
        self.maskfllabel = QLabel("Fluorescence mask image", self.dockUI)
        self.cbmaskfl = QComboBox()
        self.cbmaskfl.currentIndexChanged.connect(self._set_maskfl)
        self.cbmaskfl.addItems(self.model.list_images())
        self.distthresholdlabel = QLabel("Maximum distance (μm)", self.dockUI)
        self.distthreshold = QLineEdit()
        self.distthreshold.setText("100")

        self.layout.addWidget(self.maskcmoslabel)
        self.layout.addWidget(self.cbmaskcmos)
        self.layout.addWidget(self.maskfllabel)
        self.layout.addWidget(self.cbmaskfl)
        self.layout.addWidget(self.distthresholdlabel)
        self.layout.addWidget(self.distthreshold)

    def _set_maskcmos(self, index):
        self.maskcmos_scale = self.model.scales[index]
        self.maskcmos_trans = self.model.translation[index]
        self.maskcmos = self.model.images[index]._image

    def _set_maskfl(self, index):
        self.maskfl_scale = self.model.scales[index]
        self.maskfl_trans = self.model.translation[index]
        self.maskfl = self.model.images[index]._image

    def _plot(self):
        mask = self.maskfl
        map_dict = {}
        for i in range(1, self.foutput.shape[0]):
            map_dict[int(self.foutput[i]["CellID"])] = self.foutput[i]["Nearest"]

        k = np.array(list(map_dict.keys()))
        v = np.array(list(map_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        map_mask = mapping_ar[mask]

        self.outputimage = map_mask

        im = self.plot.axes.imshow(map_mask, cmap="gray", origin="upper")
        self.plot.fig.colorbar(im, ax=self.plot.axes)
        self.plot.axes.set_ylabel("Y coordinate")
        self.plot.axes.set_xlabel("X coordinate")
