# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.saving import Saving

import tifffile


class SaveImage(Saving):
    analysis_name = "Save Image"

    def __init__(self, model=None, signal=None, parent=None):
        super(SaveImage, self).__init__(
            model,
            parent,
            signal,
            name=self.analysis_name,
            show=True,
            extensions="tif File (*.tif)",
        )
        self.image = None

    def _run(self):
        currentlayer = self.model.currentlayer
        self.image = self.model.images[currentlayer]._image._imgs
        shape = self.image.shape
        if shape[0] == 1:
            tifffile.imsave(self.filename, self.image[0])
        else:
            tifffile.imsave(self.filename, self.image, metadata={"axes": "TXY"})

    def initialize_UI(self):
        self.fpslabel = QLabel("Frames per second", self.dockUI)
        self.fps = QLineEdit()

        self.layout.addWidget(self.fpslabel)
        self.layout.addWidget(self.fps)
