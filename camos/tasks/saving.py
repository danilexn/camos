#
# Created on Sat Jun 05 2021
#
# The MIT License (MIT)
# Copyright (c) 2021 Daniel León, Josua Seidel, Hani Al Hawasli
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

import numpy as np
from camos.tasks.runtask import RunTask
from camos.utils.errormessages import ErrorMessages
import camos.utils.apptools as apptools


class Saving(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(
        self,
        model=None,
        parent=None,
        input=None,
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
        self.addMenuElement()
        # self.finished.connect(self.plot)

    def _run(self):
        pass

    @pyqtSlot()
    def run(self):
        if not self.filename:
            ErrorMessages("Path was not selected!")
            return
        self._run()
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

    def addMenuElement(self):
        camosGUI = apptools.getGui()
        savingAct = QtWidgets.QAction("{}".format(self.analysis_name), camosGUI)
        savingAct.triggered.connect(self.display)
        camosGUI.saveMenu.addAction(savingAct)
