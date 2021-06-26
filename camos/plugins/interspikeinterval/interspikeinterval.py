# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from camos.tasks.analysis import Analysis


class InterspikeInterval(Analysis):
    analysis_name = "Interspike interval"

    def __init__(self, model=None, parent=None, signal=None):
        super(InterspikeInterval, self).__init__(
            model, parent, signal, name=self.analysis_name
        )
        self.data = None

    def _run(self):
        pass

    def initialize_UI(self):
        self.datalabel = QLabel("Source dataset", self.dockUI)
        # TODO: analyze by clusters, or analyze completely
        self.cbdata = QComboBox()
        self.cbdata.currentIndexChanged.connect(self._set_data)
        self.cbdata.addItems(self.model.list_datasets())

        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.cbdata)

    def _plot(self):
        pass
