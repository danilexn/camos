# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.opening import Opening
from camos.model.inputdata import InputData


class OpenImage(Opening):
    analysis_name = "Open image"

    def __init__(self, model=None, signal=None, parent=None, file=None):
        super(OpenImage, self).__init__(
            model,
            parent,
            signal,
            name=self.analysis_name,
            extensions="tif File (*.tif)",
        )
        self.model = model

    def _run(self):
        image = InputData(self.filename, memoryPersist=True)
        image.loadImage()
        self.model.add_image(image)
