# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
import os

from camos.tasks.base import BaseTask


class Analysis(BaseTask):
    def __init__(self, *args, **kwargs):
        super(Analysis, self).__init__(*args, **kwargs)
        self.foutput = np.zeros((1, 1))
        self.sampling = 1
        self.finished.connect(self.output_to_signalmodel)
        self.outputimage = np.zeros((1, 1))
        self.mask = []

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(
            self.output,
            name="{} from {}".format(self.analysis_name, self.dataname),
            sampling=self.sampling,
            mask=self.mask,
        )
