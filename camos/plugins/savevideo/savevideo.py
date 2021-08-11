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
    required = ["image"]

    def __init__(self, *args, **kwargs):
        super(SaveVideo, self).__init__(show=True, *args, **kwargs)
        self.image = None

    def _run(self, fps: NumericInput("Frames per second", 10)):
        shape = self.model.get_layer(self.model.currentlayer).shape
        size = (shape[1], shape[0])
        out = cv2.VideoWriter(
            self.filename, cv2.VideoWriter_fourcc(*"DIVX"), int(fps), size,
        )
        maxframes = self.model.frames[self.model.currentlayer]
        for i in range(maxframes):
            self.model.set_frame(i)
            from PIL import Image

            frame = Image.fromarray(
                self.model.get_layer(self.model.currentlayer)
            ).convert("RGB")
            out.write(np.array(frame))
            self.intReady.emit(i * 100 / maxframes)

        out.release()
