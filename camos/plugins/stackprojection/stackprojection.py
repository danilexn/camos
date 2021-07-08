# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
from PyQt5.QtWidgets import *
from camos.tasks.processing import Processing
from camos.model.inputdata import InputData


class StackProjection(Processing):
    analysis_name = "Stack Projection"

    def __init__(self, model=None, parent=None, **kwargs):
        super(StackProjection, self).__init__(
            model, parent, input, name=self.analysis_name
        )
        self.output = None
        self.layername = "Projection of Layer {}"
        self.image = None
        self.axis = 0
        self.finished.connect(self.output_to_imagemodel)
        self.methodname = ""
        self._methods = {
            "maximum": np.max,
            "minimum": np.min,
            "stdev": np.std,
            "mean": np.mean,
            "sum": np.sum,
            "median": np.median,
        }

    def _run(self):
        self.output = self.method(self.image._image._imgs, axis=self.axis)

    def output_to_imagemodel(self, name=None):
        image = InputData(
            self.output, memoryPersist=True, name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(
            image,
            "{} projection of {}".format(
                str.capitalize(self.methodname), self.imagename
            ),
        )

    def initialize_UI(self):
        self.projectlabel = QLabel("Projection method", self.dockUI)
        self.cbproject = QComboBox()
        self.cbproject.currentIndexChanged.connect(self._set_proj)
        self.cbproject.addItems(self.methods)

        self.imagelabel = QLabel("Fluorescence image", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.projectlabel)
        self.layout.addWidget(self.cbproject)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, text):
        index = self.cbimage.currentIndex()
        self.image = self.model.images[index]
        self.imagename = self.model.names[index]

    def _set_proj(self, index):
        self.methodname = self.methods[index]
        self.method = self._methods[self.methodname]

    @property
    def methods(self):
        return list(self._methods.keys())
