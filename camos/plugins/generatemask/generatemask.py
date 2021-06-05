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
from camos.plugins.stackprojection import stackprojection


class GenerateMask(Processing):
    def __init__(self, model=None, parent=None, input=None):
        super(GenerateMask, self).__init__(model, parent, input, name="Generate Masks")
        self.output = None
        self.image = None
        self.finished.connect(self.output_to_imagemodel)
        self.analysis_name = "Extract Mask"
        self.gpu = False
        self.torch = False
        self.method = "nuclei"
        self.proj = "maximum"
        self.projector = stackprojection.StackProjection()

    def _run(self):
        # TODO: replace this by a simpler approach (i.e., used in FluoroSNNAP
        # WARNING: may not work in macOS if no GPU acceleration is available
        from cellpose import models

        # Nuclei model works the best in this case
        # TODO: gpu acceleration toggle, user selectable
        model = models.Cellpose(gpu=self.gpu, model_type="nuclei")
        # TODO: self.image may be the Z projection, so all cells are detected
        masks, _, _, _ = model.eval(self.image.image(0), diameter=None, channels=[0])
        self.output = masks

    def initialize_UI(self):
        # TODO: Create a checkbox for GPU acceleration
        self.cbgpu = QCheckBox("GPU Acceleration")
        self.cbgpu.setChecked(True)
        self.cbgpu.stateChanged.connect(self._set_gpu)

        self.methodlabel = QLabel("Segmentation method", self.dockUI)
        self.cbmethod = QComboBox()
        self.cbmethod.currentIndexChanged.connect(self._set_method)
        self.cbmethod.addItems(["nuclei", "cyto"])

        self.projectlabel = QLabel("Projection method", self.dockUI)
        self.cbproject = QComboBox()
        self.cbproject.currentIndexChanged.connect(self._set_image)
        self.cbproject.addItems(self.projector.methods)

        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.methodlabel)
        self.layout.addWidget(self.cbmethod)
        self.layout.addWidget(self.projectlabel)
        self.layout.addWidget(self.cbproject)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, index):
        self.image = self.model.images[index]

    def _set_gpu(self, cb):
        self.gpu = cb.isChecked()

    def _set_proj(self, index):
        self.proj = self.projector.methods[index]

    def _set_method(self, index):
        self.method = ["nuclei", "cyto"][index]
