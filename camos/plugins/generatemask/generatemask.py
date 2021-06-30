# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator
from PyQt5 import QtCore

from camos.tasks.processing import Processing
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

    def _run(self):
        from cellpose import models

        _diameter = float(self.cellsize.text())
        diameter = None if _diameter == 0 else _diameter
        # Cyto model works the best in this case
        model = models.Cellpose(torch=self.torch, gpu=self.gpu, model_type=self.method)
        masks, _, _, _ = model.eval(
            self.image.image(0), diameter=diameter, channels=[[0, 0]]
        )
        self.output = masks

    def output_to_imagemodel(self):
        image = InputData(
            self.output, memoryPersist=True, name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(image, "Mask of Layer {}".format(self.index))

    def initialize_UI(self):
        self.methodlabel = QLabel("Segmentation method", self.dockUI)
        self.cbmethod = QComboBox()
        self.cbmethod.currentIndexChanged.connect(self._set_method)
        self.cbmethod.addItems(["nuclei", "cyto"])

        self.cbgpu = QCheckBox("GPU Acceleration?", self.dockUI)
        self.cbgpu.setChecked(True)
        self.cbgpu.stateChanged.connect(self._set_gpu)

        self.cbtorch = QCheckBox("Use torch?", self.dockUI)
        self.cbtorch.setChecked(True)
        self.cbtorch.stateChanged.connect(self._set_torch)

        self.onlyDouble = QDoubleValidator()
        self.cellsize_label = QLabel("Cell Diameter (0: Auto)", self.parent)
        self.cellsize = QLineEdit()
        self.cellsize.setValidator(self.onlyDouble)
        self.cellsize.setText("0")
        self.layout.addWidget(self.cellsize_label)
        self.layout.addWidget(self.cellsize)

        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.methodlabel)
        self.layout.addWidget(self.cbmethod)
        self.layout.addWidget(self.cbgpu)
        self.layout.addWidget(self.cbtorch)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, index):
        self.image = self.model.images[index]
        self.index = index

    def _set_gpu(self, state):
        self.gpu = state == QtCore.Qt.Checked

    def _set_torch(self, state):
        self.torch = state == QtCore.Qt.Checked

    def _set_method(self, index):
        self.method = ["nuclei", "cyto"][index]
