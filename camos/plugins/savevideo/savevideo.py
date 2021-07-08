# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
import cv2

from camos.tasks.saving import Saving
from camos.utils.generategui import NumericInput


class SaveVideo(Saving):
    analysis_name = "Save Video"

    def __init__(self, *args, **kwargs):
        super(SaveVideo, self).__init__(show=True, *args, **kwargs)
        self.image = None

    def _run(self, fps: NumericInput("Frames per second", 10)):
        height, width, layers = self.model.get_current_view(0).shape
        size = (width, height)
        out = cv2.VideoWriter(
            self.filename, cv2.VideoWriter_fourcc(*"DIVX"), int(fps), size,
        )
        for i in range(self.model.maxframe):
            self.model.frame = i
            out.write(np.uint8(self.model.get_current_view()))
            self.intReady.emit(i * 100 / self.model.maxframe)

        out.release()
