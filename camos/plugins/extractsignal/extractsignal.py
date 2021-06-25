# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.processing import Processing


class ExtractSignal(Processing):
    analysis_name = "Extract signal"

    def __init__(self, model=None, parent=None, signal=None):
        super(ExtractSignal, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.mask = None
        self.image = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        ROIs = np.unique(self.mask.image(0))[1:]
        self.output = np.zeros((len(ROIs), self.image.frames))
        total = len(ROIs)
        for i, r in enumerate(ROIs):
            cell = self.mask.image(0) == r
            self.output[i, :] = np.average(
                self.image._image._imgs[:, cell], axis=(1)
            )
            self.intReady.emit(i * 100 / total)

    def initialize_UI(self):
        self.masklabel = QLabel("Mask image", self.dockUI)
        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbmask = QComboBox()
        self.cbmask.currentIndexChanged.connect(self._set_mask)
        self.cbmask.addItems(self.model.list_images())
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.masklabel)
        self.layout.addWidget(self.cbmask)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_mask(self, text):
        index = self.cbmask.currentIndex()
        self.mask = self.model.images[index]

    def _set_image(self, text):
        index = self.cbimage.currentIndex()
        self.image = self.model.images[index]
