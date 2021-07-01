# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np
from camos.tasks.runtask import RunTask
from camos.utils.errormessages import ErrorMessages


class Saving(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(
        self,
        model=None,
        parent=None,
        signal=None,
        name="No name saving",
        show=False,
        extensions="avi File (*.avi);;mov File (*.mov)",
    ):
        super(Saving, self).__init__()
        self.model = model
        self.parent = parent
        self.analysis_name = name
        self.show = show
        self.extensions = extensions
        self.handler = None
        # self.finished.connect(self.plot)

    def _run(self):
        pass

    @pyqtSlot()
    def run(self):
        if not self.filename:
            ErrorMessages("Path was not selected!")
            return
        try:
            self._run()
            if self.handler != None:
                self.handler.success = True
        finally:
            self.finished.emit()
        pass

    def display(self):
        # TODO: change to signal...
        if type(self.model.list_images()) is type(None):
            # Handle error that there are no images
            ErrorMessages("There are no datasets!")
            return

        self.filename = self.show_savemenu()

        if self.show:
            self._initialize_UI()
            self.initialize_UI()
            self._final_initialize_UI()
        else:
            self.run()

    def initialize_UI(self):
        pass

    def show_savemenu(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self.parent,
            "QFileDialog.getSaveFileName()",
            "",
            str(self.extensions),
            options=options,
        )

        return fileName

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.layout = QVBoxLayout()

    def _final_initialize_UI(self):
        self.runButton = QPushButton("Run", self.parent)
        self.runButton.setToolTip("Click to run this task")
        self.handler = RunTask(self)
        self.runButton.clicked.connect(self.handler.start_progress)

        self.layout.addWidget(self.runButton)

        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)
