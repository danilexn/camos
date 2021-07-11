# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg


class TableViewer(pg.TableWidget):
    window_title = "Signal Table Viewer {}"

    def __init__(self, model=None, index=None):
        super(TableViewer, self).__init__()
        self.data = model.data[index]
        self.name = model.names[index]
        self.setWindowTitle(self.window_title.format(self.name))

    def display(self):
        if len(self.data) > 500:
            self.setData(self.data[0:500])
        else:
            self.setData(self.data)
        self.show()
