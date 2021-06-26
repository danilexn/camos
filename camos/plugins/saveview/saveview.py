# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.tasks.saving import Saving

import pickle


class SaveView(Saving):
    analysis_name = "Save View"

    def __init__(self, model=None, signal=None, parent=None):
        super(SaveView, self).__init__(
            model, parent, signal, name=self.analysis_name, show=False, extensions="cms File (*.cms)"
        )
        self.image = None
        self.model = model

    def _run(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.model, f)