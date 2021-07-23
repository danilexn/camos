# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QLabel, QComboBox
from camos.tasks.saving import Saving

import h5py


class SaveSignal(Saving):
    analysis_name = "Save Signals"
    required = ["dataset"]

    def __init__(self, *args, **kwargs):
        super(SaveSignal, self).__init__(extensions="hdf5 File (*.h5)", *args, **kwargs)

    def _run(self):
        h5f = h5py.File(self.filename, "w")
        for i, (name, data) in enumerate(self.signal):
            if len(self.signal.masks[i]) > 0:
                group_name = "{}".format(name)
                h5f.create_group(group_name)
                h5f[group_name].create_dataset(group_name, data=data)
                h5f[group_name].create_dataset("mask", data=self.signal.masks[i])
                h5f[group_name].create_dataset(
                    "properties", data=self.signal.properties[i]
                )
            else:
                h5f.create_dataset("{}".format(name), data=data)
        h5f.close()
