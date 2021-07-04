# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QLabel, QComboBox
from camos.tasks.processing import Processing
from camos.model.inputdata import InputData

from pystackreg import StackReg


class CAMOSStackReg(Processing):
    analysis_name = "Stack Registration"

    def __init__(self, model=None, parent=None, signal=None):
        super(CAMOSStackReg, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.output = None
        self.image = None
        self.layername = "StackReg of Layer {}"
        self.finished.connect(self.output_to_imagemodel)
        self.gpu = True
        self.torch = True
        self.reference = "first"

    def _run(self):
        # Translational transformation
        def show_progress(current_iteration, end_iteration):
            self.intReady.emit(current_iteration * 100 / end_iteration)

        sr = StackReg(StackReg.RIGID_BODY)
        img = self.image._image._imgs
        # register to first image
        out = sr.register_transform_stack(
            img, reference=self.reference, progress_callback=show_progress
        )
        self.output = out

    def output_to_imagemodel(self):
        image = InputData(
            self.output, memoryPersist=True, name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(image, "StackReg of Layer {}".format(self.index))

    def initialize_UI(self):
        # TODO: Create a checkbox for GPU acceleration
        self.methodlabel = QLabel("Reference Frame", self.dockUI)
        self.cbmethod = QComboBox()
        self.cbmethod.currentIndexChanged.connect(self._set_method)
        self.cbmethod.addItems(["first", "previous"])

        self.imagelabel = QLabel("Stack to register", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.layout.addWidget(self.methodlabel)
        self.layout.addWidget(self.cbmethod)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)

    def _set_image(self, index):
        self.image = self.model.images[index]
        self.index = index

    def _set_method(self, index):
        self.reference = ["first", "previous"][index]
