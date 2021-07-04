# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QLabel, QComboBox

import numpy as np
from collections import defaultdict

from camos.tasks.analysis import Analysis


class InterspikeInterval(Analysis):
    analysis_name = "Interspike Interval"
    input_type = "summary"

    def __init__(self, model=None, parent=None, signal=None):
        super(InterspikeInterval, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        self.pos = {}
        duration = 100
        output_type = [("CellID", "int"), ("ISI", "float")]

        # data should be provided in format of peaks
        data = self.data
        if not ("Active" in data.dtype.names):
            return

        ROIs = np.unique(data[:]["CellID"])

        # Create the output matrix
        self.output = np.zeros(shape=(len(ROIs), 1), dtype=output_type)

        # Save Cell IDs in the output matrix
        self.output[:]["CellID"] = ROIs.reshape(-1, 1)

        # Calculate a dictionary of the input, faster computation
        IDs_all = data[:]["CellID"]
        dict_events = defaultdict(list)

        # This explores all events
        # TODO: review why spikes from CMOS and Ca have different structure
        if type(IDs_all[0]) == np.ndarray:
            for i in range(len(IDs_all)):
                dict_events[IDs_all[i][0]] += [data[i]["Active"][0]]
                self.intReady.emit(i * 100 / len(IDs_all))

        else:
            for i in range(len(IDs_all)):
                dict_events[IDs_all[i]] += [data[i]["Active"]]
                self.intReady.emit(i * 100 / len(IDs_all))

        ISI = np.zeros(len(ROIs))
        for i, ROI in enumerate(ROIs):
            ISI[i] = np.average(np.diff(dict_events[ROI]))

        self.output[:]["ISI"] = ISI.reshape(-1, 1)

    def display(self):
        if type(self.signal.list_datasets(self.input_type)) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output, "ISI of {}".format(self.dataname), self, mask=self.mask
        )

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.signal.list_datasets(self.input_type))
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
        self.dataname = self.signal.names[index]

    def _set_mask(self, text):
        index = self.cbmask.currentIndex()
        self.mask = self.model.images[index]._image._imgs[0].astype(int)

    def _plot(self):
        mask = self.mask
        ISI_dict = {}
        for i in range(1, self.foutput.shape[0]):
            ISI_dict[int(self.foutput[i]["CellID"][0])] = self.foutput[i]["ISI"][0]

        k = np.array(list(ISI_dict.keys()))
        v = np.array(list(ISI_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        ISI_mask = mapping_ar[mask]

        self.outputimage = ISI_mask

        im = self.plot.axes.imshow(ISI_mask, cmap="inferno", origin="upper")
        self.plot.fig.colorbar(im, ax=self.plot.axes)
        self.plot.axes.set_ylabel("Y coordinate")
        self.plot.axes.set_xlabel("X coordinate")
