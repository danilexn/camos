#
# Created on Sat Jun 05 2021
#
# The MIT License (MIT)
# Copyright (c) 2021 Daniel León, Josua Seidel, Hani Al Hawasli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.saving import Saving

import cv2


class SaveVideo(Saving):
    def __init__(self, model=None, signal=None, parent=None, input=None):
        super(SaveVideo, self).__init__(
            model, parent, input, name="Save Video", show=True
        )
        self.image = None
        self.analysis_name = "Save Video"

    def _run(self):
        height, width, layers = self.model.get_current_view(0).shape
        size = (width, height)
        out = cv2.VideoWriter(
            self.filename, cv2.VideoWriter_fourcc(*"DIVX"), int(self.fps.text()), size
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
