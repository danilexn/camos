# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np

from camos.tasks.runtask import RunTask
from camos.model.inputdata import InputData
from camos.utils.generategui import CreateGUI
from camos.utils.notifications import notify


class BaseTask(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)
    notify = pyqtSignal(str, str)
    required = ["image", "dataset"]
    analysis_name = "Base"

    def __init__(self, model=None, parent=None, signal=None, *args, **kwargs):
        super(BaseTask, self).__init__()
        self.model = model
        self.signal = signal
        self.parent = parent
        self.output = np.zeros((1, 1))
        self.paramDict = {}
        self.handler = RunTask(self)
        self.notify.connect(self.handler.on_notify)

    def _run(self, **kwargs):
        pass

    @pyqtSlot()
    def run(self):
        try:
            self._run(**self.paramDict)
            self.handler.success = True
            self.foutput = self.output
        except Exception as e:
            raise e
        finally:
            self.finished.emit()

    def update_plot(self):
        # try:
        #     self.plot.restartFigure()
        # except:
        #     pass
        self._plot()
        self.plot.draw()
        self.plotReady.emit()

    def update_values_plot(self, values):
        self._update_values_plot(values)
        self.update_plot()

    def _update_values_plot(self, values):
        pass

    def output_to_signalmodel(self):
        self.parent.signalmodel.add_data(self.output, "", self, self.sampling)

    def output_to_imagemodel(self, name=None):
        image = InputData(
            self.output, memoryPersist=True, name=self.layername.format(self.index),
        )
        image.loadImage()
        self.parent.model.add_image(image, name)

    def show(self):
        self.dockUI.show()

    def display(self):
        if "image" in self.required and (type(self.model.list_images()) is type(None)):
            raise IndexError("The image model is empty")
        if "dataset" in self.required and (
            type(self.signal.list_datasets()) is type(None)
        ):
            raise IndexError("The dataset model is empty")

        self.buildUI()
        self.show()

    def buildUI(self):
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.layout = QVBoxLayout()
        self.params_gui = CreateGUI(self.paramDict, self.layout, self._run)
        self.params_gui.creategui()

        self.runButton = QPushButton("Run", self.parent)
        self.runButton.setToolTip("Click to run this task")
        self.runButton.clicked.connect(self.handler.start_progress)

        self.layout.addWidget(self.runButton)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)
