# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import numpy as np
import h5py

from camos.tasks.opening import Opening
from camos.viewport.signalviewer import SignalViewer
from camos.model.inputdata import InputData


class OpenSignal(Opening):
    analysis_name = "Open Signal"

    def __init__(self, *args, **kwargs):
        super(OpenSignal, self).__init__(extensions="hdf5 File (*.h5)", *args, **kwargs)

    def _run(self):
        h5f = h5py.File(self.filename, "r")
        for name in list(h5f.keys()):
            if hasattr(h5f[name], "keys"):
                mask = None
                keys = list(h5f[name].keys())
                if "mask" in list(h5f[name].keys()):
                    mask = self.load_mask(
                        np.array(h5f[name]["mask"]), "Mask of {}".format(name)
                    )
                    self.load_signal(np.array(h5f[name][keys[0]]), name, mask)
                else:
                    raise ValueError
            else:
                self.load_signal(np.array(h5f[name]), name)
        h5f.close()

    def load_signal(self, data, name, mask=[]):
        _sv = SignalViewer(self.parent, data)
        self.signal.add_data(data, name, _sv, mask=mask)
        _sv.mask = mask
        _sv.display()

    def load_mask(self, data, name):
        image = InputData(data, memoryPersist=True, name=name,)
        image.loadImage()
        self.model.add_image(image)

        return self.model.images[-1]._image._imgs[0]
