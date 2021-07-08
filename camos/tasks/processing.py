# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal

from camos.tasks.base import BaseTask


class Processing(BaseTask):
    txtReady = pyqtSignal(str)
    required = ["image"]

    def __init__(self, *args, **kwargs):
        super(Processing, self).__init__(*args, **kwargs)
        self.layername = "Unnamed Layer {}"
        self.index = 0

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output, "", self)
