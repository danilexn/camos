# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.tasks.opening import Opening
from camos.model.inputdata import InputData

import PIL


class OpenImage(Opening):
    analysis_name = "Open Image(s)"

    def __init__(self, *args, **kwargs):
        super(OpenImage, self).__init__(
            name=self.analysis_name,
            extensions="tif File (*.tif);; png File (*.png);; jpeg File (*.jpeg);; tiff File (*.tiff)",
            *args,
            **kwargs
        )

    def _run(self):
        # Added so we can load CMOS chip image
        PIL.Image.MAX_IMAGE_PIXELS = 933120000
        if type(self.filename) == list:
            for single in self.filename:
                image = InputData(single)
                image.loadImage()
                self.model.add_image(image)
        elif type(self.filename) == str:
            image = InputData(self.filename)
            image.loadImage()
            self.model.add_image(image)
        else:
            raise NotImplementedError("Could not understand the input path")
