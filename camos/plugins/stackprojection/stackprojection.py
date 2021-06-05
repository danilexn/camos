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


class StackProjection(Processing):
    def __init__(self, model=None, parent=None, input=None):
        super(StackProjection, self).__init__(
            model, parent, input, name="Stack Projection"
        )
        self.output = None
        self.image = None
        self._method = None
        self.axis = 0
        self.finished.connect(self.output_to_imagemodel)
        self._methods = {
            "maximum": np.max,
            "minimum": np.min,
            "stdev": np.std,
            "mean": np.mean,
            "sum": np.sum,
            "median": np.median,
        }

    def _run(self):
        self.output = self.method(self.image, axis=self.axis)

    def initialize_UI(self):
        self.projectlabel = QLabel("Projection method", self.dockUI)
        self.cbproject = QComboBox()
        self.cbproject.currentIndexChanged.connect(self._set_image)
        self.cbproject.addItems(self.methods)

        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.projectlabel)
        self.layout.addWidget(self.cbproject)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, index):
        self.image = self.model.images[index]

    def _set_proj(self, index):
        self.method = self._methods[index]

    @property
    def methods(self):
        return self._methods.keys()
