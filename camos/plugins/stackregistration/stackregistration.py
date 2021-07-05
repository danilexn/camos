# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from pystackreg import StackReg

from camos.tasks.processing import Processing
from camos.model.inputdata import InputData
from camos.utils.generategui import (
    ImageInput,
    CustomComboInput,
)

_reference = ["first", "previous"]


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

    def _run(
        self,
        _i_ref: CustomComboInput(_reference, "Reference Frame", 0),
        _i_img: ImageInput("Stack to register", 0),
    ):
        # Translational transformation
        def show_progress(current_iteration, end_iteration):
            self.intReady.emit(current_iteration * 100 / end_iteration)

        sr = StackReg(StackReg.RIGID_BODY)
        img = self.model.images[_i_img]._image._imgs
        self.imagename = self.model.names[_i_img]
        # register to first image
        out = sr.register_transform_stack(
            img, reference=_reference[_i_ref], progress_callback=show_progress
        )
        self.output = out

    def output_to_imagemodel(self):
        image = InputData(self.output, memoryPersist=True,)
        image.loadImage()
        self.parent.model.add_image(image, "StackReg of {}".format(self.imagename))
