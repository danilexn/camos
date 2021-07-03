# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.saving import Saving

import os
import numpy as np


class SaveCSV(Saving):
    analysis_name = "Save as CSV"

    def __init__(self, model=None, signal=None, parent=None, file=None):
        super(SaveCSV, self).__init__(
            model,
            parent,
            signal,
            name=self.analysis_name,
            extensions="csv File (*.csv)",
        )
        self.signal = signal

    def _run(self):
        s_path = os.path.splitext(self.filename)
        for i, (name, data) in enumerate(self.signal):
            name = "{}_{}{}".format(s_path[0], name, s_path[1])
            np.savetxt(
                name,
                data,
                delimiter=",",
                fmt="%s",
                header=",".join(list(data.dtype.names)),
            )

    def _set_signal(self, index):
        self.signal = self.signalmodel.data[index]
