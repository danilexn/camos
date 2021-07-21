# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.tasks.saving import Saving

import pickle


class SaveView(Saving):
    analysis_name = "Save View"
    required = ["image"]

    def __init__(self, *args, **kwargs):
        super(SaveView, self).__init__(extensions="cms File (*.cms)", *args, **kwargs)

    def _run(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.model, f)
