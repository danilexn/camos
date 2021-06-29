# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *

import numpy as np
import h5py

from camos.tasks.opening import Opening
from camos.viewport.signalviewer import SignalViewer

class OpenSignal(Opening):
    analysis_name = "Open Signal"

    def __init__(self, model=None, signal=None, parent=None, file=None):
        super(OpenSignal, self).__init__(
            model,
            parent,
            signal,
            name=self.analysis_name,
            extensions="hdf5 File (*.h5)",
        )
        self.signal = signal

    def _run(self):
        h5f = h5py.File(self.filename, "r")
        for name in list(h5f.keys()):
            data = np.array(h5f[name])
            _sv = SignalViewer(self.parent, data)
            self.signal.add_data(data, name, _sv)
            _sv.display()

        h5f.close()