# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot


class SignalViewModel(QObject):
    newdata = pyqtSignal()

    def __init__(self, data=[], parent=None):
        self.data = data
        self.parent = parent
        super(SignalViewModel, self).__init__()

    @pyqtSlot()
    def add_data(self, data):
        self.data.append(data)
        self.newdata.emit()

    def list_datasets(self):
        if len(self.data) == 0:
            return None
        return map(str, range(len(self.data)))
