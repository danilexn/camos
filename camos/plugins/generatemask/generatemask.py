# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.processing import Processing
from camos.plugins.stackprojection import stackprojection
from camos.model.inputdata import InputData


class GenerateMask(Processing):
    analysis_name = "Extract Mask"

    def __init__(self, model=None, parent=None, signal=None):
        super(GenerateMask, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.output = None
        self.image = None
        self.layername = "Mask of Layer {}"
        self.finished.connect(self.output_to_imagemodel)
        self.gpu = True
        self.torch = True
        self.method = "nuclei"
        self.proj = "maximum"
        self.projector = stackprojection.StackProjection()

    def _run(self):
        from cellpose import models

        # Nuclei model works the best in this case
        # TODO: gpu acceleration toggle, user selectable
        model = models.Cellpose(
            torch=self.torch, gpu=self.gpu, model_type=self.method
        )
        # TODO: self.image may be the Z projection, so all cells are detected
        masks, _, _, _ = model.eval(
            self.image.image(0), diameter=None, channels=[[0, 0]]
        )
        self.output = masks

    def output_to_imagemodel(self):
        image = InputData(
            self.output,
            memoryPersist=True,
            name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(image, "Mask of Layer {}".format(self.index))

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
        self.index = index

    def _set_gpu(self, cb):
        self.gpu = cb.isChecked()

    def _set_proj(self, index):
        self.proj = self.projector.methods[index]

    def _set_method(self, index):
        self.method = ["nuclei", "cyto"][index]
