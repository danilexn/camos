# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.saving import Saving

import cv2


class SaveVideo(Saving):
    analysis_name = "Save Video"

    def __init__(self, model=None, signal=None, parent=None):
        super(SaveVideo, self).__init__(
            model, parent, signal, name=self.analysis_name, show=True
        )
        self.image = None

    def _run(self):
        height, width, layers = self.model.get_current_view(0).shape
        size = (width, height)
        out = cv2.VideoWriter(
            self.filename,
            cv2.VideoWriter_fourcc(*"DIVX"),
            int(self.fps.text()),
            size,
        )
        for i in range(self.model.maxframe):
            self.model.frame = i
            out.write(np.uint8(self.model.get_current_view()))
            self.intReady.emit(i * 100 / self.model.maxframe)

        out.release()

    def initialize_UI(self):
        self.fpslabel = QLabel("Frames per second", self.dockUI)
        self.fps = QLineEdit()

        self.layout.addWidget(self.fpslabel)
        self.layout.addWidget(self.fps)
