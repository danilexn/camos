# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QLabel, QComboBox
from camos.tasks.processing import Processing
from camos.model.inputdata import InputData

import cv2


class CAMOSImageReg(Processing):
    analysis_name = "Image Registration"
    _methods = {
        "Correlation": cv2.TM_CCOEFF,
        "Normed Correlation": cv2.TM_CCOEFF_NORMED,
        "Cross Correlation": cv2.TM_CCORR,
        "Normed Cross Correlation": cv2.TM_CCORR_NORMED,
        "Quared Difference": cv2.TM_SQDIFF,
    }

    def __init__(self, model=None, parent=None, signal=None):
        super(CAMOSImageReg, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.output = None
        self.image = None
        self.layername = "StackReg of Layer {} with Reference Layer {}"
        self.reference = "first"
        self.method = self._methods["Correlation"]
        self.finished.connect(self.image_align)

    def check8bit(self, image):
        if image.dtype == "uint16":
            image = (image / 256).astype("uint8")
        return image

    def _run(self):
        # Apply template Matching
        image = self.check8bit(self.image)
        ref = self.check8bit(self.ref)

        res = cv2.matchTemplate(ref, image, self.method)
        _, _, min_loc, max_loc = cv2.minMaxLoc(res)
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if self.method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc

        self.output = top_left

    def image_align(self):
        self.model.translate_position(self.index_img, self.output)

    def output_to_imagemodel(self):
        image = InputData(
            self.output, memoryPersist=True, name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(
            image,
            "StackReg of Layer {} with Reference Layer {}".format(
                self.index_img, self.index_ref
            ),
        )

    def initialize_UI(self):
        # TODO: Create a checkbox for GPU acceleration
        self.methodlabel = QLabel("Matching Method", self.dockUI)
        self.cbmethod = QComboBox()
        self.cbmethod.currentIndexChanged.connect(self._set_method)
        self.cbmethod.addItems(self.methods)

        self.imagelabel = QLabel("Register image", self.dockUI)
        self.cbimage = QComboBox()
        self.cbimage.currentIndexChanged.connect(self._set_image)
        self.cbimage.addItems(self.model.list_images())

        self.reflabel = QLabel("Reference image", self.dockUI)
        self.cbref = QComboBox()
        self.cbref.currentIndexChanged.connect(self._set_ref)
        self.cbref.addItems(self.model.list_images())

        self.layout.addWidget(self.methodlabel)
        self.layout.addWidget(self.cbmethod)
        self.layout.addWidget(self.imagelabel)
        self.layout.addWidget(self.cbimage)
        self.layout.addWidget(self.reflabel)
        self.layout.addWidget(self.cbref)

    def _set_image(self, index):
        self.image = self.model.images[index]._image._imgs[0]
        self.index_img = index

    def _set_ref(self, index):
        self.ref = self.model.images[index]._image._imgs[0]
        self.index_ref = index

    def _set_method(self, index):
        self.methodname = self.methods[index]
        self.method = self._methods[self.methodname]

    @property
    def methods(self):
        return list(self._methods.keys())
