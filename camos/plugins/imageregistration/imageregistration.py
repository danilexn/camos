# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.
import cv2

from camos.tasks.processing import Processing
from camos.model.inputdata import InputData
from camos.utils.generategui import (
    ImageInput,
    CustomComboInput,
)

_methods = {
    "Correlation": cv2.TM_CCOEFF,
    "Normed Correlation": cv2.TM_CCOEFF_NORMED,
    "Cross Correlation": cv2.TM_CCORR,
    "Normed Cross Correlation": cv2.TM_CCORR_NORMED,
    "Quared Difference": cv2.TM_SQDIFF,
}


class CAMOSImageReg(Processing):
    analysis_name = "Image Registration"

    required = ["images"]

    def __init__(self, model=None, parent=None, signal=None):
        super(CAMOSImageReg, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.output = None
        self.image = None
        self.layername = "StackReg of Layer {} with Reference Layer {}"
        self.finished.connect(self.image_align)

    def check8bit(self, image):
        if image.dtype == "uint16":
            image = (image / 256).astype("uint8")
        return image

    def _run(
        self,
        _i_img: ImageInput("Register Image", 0),
        _i_ref: ImageInput("Reference Image", 0),
        _i_method: CustomComboInput(_methods.keys(), "Matching Method", 0),
    ):
        # Apply template Matching
        self.index_img, self.index_ref = _i_img, _i_ref
        image = self.check8bit(self.model.images[_i_img].image(0))
        ref = self.check8bit(self.model.images[_i_ref].image(0))
        method = _methods[self.methods[_i_method]]

        res = cv2.matchTemplate(ref, image, method)
        _, _, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc

        self.output = top_left

    def image_align(self):
        self.model.translate_position(self.index_img, self.output)

    def output_to_imagemodel(self):
        image = InputData(self.output, memoryPersist=True)
        image.loadImage()
        self.parent.model.add_image(
            image,
            "StackReg of Layer {} with Reference Layer {}".format(
                self.index_img, self.index_ref
            ),
        )

    @property
    def methods(self):
        return list(self._methods.keys())
