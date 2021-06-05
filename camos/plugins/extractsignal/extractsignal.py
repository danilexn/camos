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
from camos.tasks.processing import Processing


class ExtractSignal(Processing):
    def __init__(self, model=None, parent=None, input=None):
        super(ExtractSignal, self).__init__(model, parent, input, name="Extract signal")
        self.mask = None
        self.image = None
        self.finished.connect(self.output_to_signalmodel)

    def _run(self):
        self.output = np.zeros((self.mask.max, self.image.frames))
        total = int(self.mask.max)
        for i in range(1, self.mask.max):
            cell = self.mask.image(0) == i
            cell = cell[np.newaxis, :, :]
            self.output[i, :] = np.sum(
                np.where(cell > 0, self.image._image._imgs, 0), axis=(1, 2)
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

    def _set_mask(self, index):
        self.mask = self.model.images[index]

    def _set_image(self, index):
        self.image = self.model.images[index]
