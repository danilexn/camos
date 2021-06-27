# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets, QtCore

from camos.viewport.signalviewport import SignalViewPort

class SignalViewer(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None):
        self.parent = parent
        self.signal = signal
        super(SignalViewer, self).__init__()

    def display(self, index = 0):
        self._initialize_UI()
        self._final_initialize_UI()
        self.signalviewport.add_track(index)
        self.show()

    def show(self):
        self.dockUI.show()

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.window_title, self.parent)
        self.main_layout = QHBoxLayout()
        self.group_plot = QGroupBox("Plot")
        self.layout = QVBoxLayout()
        self.plot_layout = QVBoxLayout()
        self.signalviewport = SignalViewPort(self.signal, self.parent)
        self.plot_layout.addWidget(
            self.signalviewport.scene.canvas.native
        )
        self.group_plot.setLayout(self.plot_layout)
        self.main_layout.addWidget(self.group_plot)

    def _final_initialize_UI(self):
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.main_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)
