# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.tasks.processing import Processing
from camos.model.inputdata import InputData
from camos.utils.generategui import (
    NumericInput,
    CheckboxInput,
    ImageInput,
    CustomComboInput,
)


class GenerateMask(Processing):
    analysis_name = "Extract Mask"
    required = ["image"]

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

    def _run(
        self,
        _diameter: NumericInput("Cell Diameter (0: Auto)", 0),
        torch: CheckboxInput("Use Torch?", True),
        gpu: CheckboxInput("Use GPU?", True),
        _i_img: ImageInput("Fluorescence Image", 0),
        _i_method: CustomComboInput(["nuclei", "cyto"], "Segmentation Model", 0),
    ):
        from cellpose import models

        diameter = None if _diameter == 0 else _diameter
        method = ["nuclei", "cyto"][_i_method]
        image = self.model.images[_i_img]
        self.index = _i_img

        # Cyto model works the best in this case
        model = models.Cellpose(torch=torch, gpu=gpu, model_type=method)
        masks, _, _, _ = model.eval(
            image.image(0), diameter=diameter, channels=[[0, 0]]
        )
        self.output = masks

    def output_to_imagemodel(self):
        image = InputData(
            self.output, memoryPersist=True, name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(image, "Mask of Layer {}".format(self.index))
