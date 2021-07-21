# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QFileDialog

from camos.tasks.opening import Opening
from camos.model.inputdata import InputData

import PIL


class OpenImageStack(Opening):
    analysis_name = "Open Image(s) as Stack"

    def __init__(self, *args, **kwargs):
        super(OpenImageStack, self).__init__(
            name=self.analysis_name,
            extensions="tif File (*.tif);; png File (*.png);; jpeg File (*.jpeg);; tiff File (*.tiff)",
            *args,
            **kwargs
        )

    def _run(self):
        # Added so we can load CMOS chip image
        PIL.Image.MAX_IMAGE_PIXELS = 933120000
        image = InputData(self.filename)
        image.loadImage()
        self.model.add_image(image)

    def show_filemenu(self):
        """Displays a File Dialog so the route of the file to be opened can be selected.

        Returns:
            str: route to the file
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileNames(
            self.parent, "Open Files", "", str(self.extensions), options=options,
        )

        return fileName
