# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.opening import Opening
from camos.model.inputdata import InputData

import PIL

class OpenImage(Opening):
    analysis_name = "Open Image"

    def __init__(self, model=None, signal=None, parent=None, file=None):
        super(OpenImage, self).__init__(
            model,
            parent,
            signal,
            name=self.analysis_name,
            extensions="tif File (*.tif);; png File (*.png);; jpeg File (*.jpeg);; tiff File (*.tiff)",
        )
        self.model = model

    def _run(self):
        # Added so we can load CMOS chip image
        PIL.Image.MAX_IMAGE_PIXELS = 933120000
        image = InputData(self.filename, memoryPersist=True)
        image.loadImage()
        self.model.add_image(image)
