# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np

from camos.tasks.processing import Processing
from camos.model.inputdata import InputData
from camos.utils.generategui import (
    ImageInput,
    CustomComboInput,
)

_methods = {
    "maximum": np.max,
    "minimum": np.min,
    "stdev": np.std,
    "mean": np.mean,
    "sum": np.sum,
    "median": np.median,
}


class StackProjection(Processing):
    analysis_name = "Stack Projection"
    required = ["image"]

    def __init__(self, *args, **kwargs):
        super(StackProjection, self).__init__(*args, **kwargs)
        self.output = None
        self.layername = "Projection of Layer {}"
        self.image = None
        self.axis = 0
        self.finished.connect(self.output_to_imagemodel)
        self.methodname = ""

    def _run(
        self,
        _i_img: ImageInput("Fluorescence Image", 0),
        _i_method: CustomComboInput(_methods.keys(), "Projection method", 0),
    ):
        self.image = self.model.images[_i_img]
        self.imagename = self.model.names[_i_img]
        self.methodname = self.methods[_i_method]
        method = _methods[self.methodname]
        self.output = method(self.image._image._imgs, axis=self.axis)

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

    @property
    def methods(self):
        return list(_methods.keys())
