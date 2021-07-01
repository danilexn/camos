# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

from camos.tasks.runtask import RunTask
from camos.utils.errormessages import ErrorMessages


class Opening(QObject):
    """This is the Opening class
    This handles the basic functionality that can be inherited from any other class implementing a plugin, whose purpose is opening and loading files (images or datasets) into CaMOS.

    Args:
        QObject: inherit the basic QObject parent class
    """

    finished = pyqtSignal()
    intReady = pyqtSignal(int)

    def __init__(
        self,
        model=None,
        parent=None,
        signal=None,
        name="No name opening",
        show=False,
        extensions="avi File (*.avi);;mov File (*.mov)",
    ):
        """Initialize the Opening object

        Args:
            model (ImageViewModel, optional): the data model for images. Defaults to None.
            parent (QMainWindow, optional): the parent, main window of the GUI. Defaults to None.
            signal (SignalViewModel, optional): the data model for signals (datasets). Defaults to None.
            name (str, optional): name of the opening plugin (as will be displayed in the GUI). Defaults to "No name opening".
            show (bool, optional): whether a dock is going to be displayed after selecting the file route (True), or the self.run method will be run just after (False). Defaults to False.
            extensions (str, optional): filter for the extensions in the QFileDialog. Defaults to "avi File (*.avi);;mov File (*.mov)".
        """
        super(Opening, self).__init__()
        self.model = model
        self.parent = parent
        self.analysis_name = name
        self.show = show
        self.extensions = extensions
        # self.finished.connect(self.plot)

    def _run(self):
        """This is a placeholder for the code that will be run. This is what the programmer has to modify when implementing a plugin that inherits opening functionality.
        """
        pass

    @pyqtSlot()
    def run(self):
        """This is the entry point when the run button is pressed, or if the plugin is called from other plugin (without UI).
        """
        if not self.filename:
            ErrorMessages("Path was not selected!")
            return

        try:
            self._run()
        finally:
            self.finished.emit()
        pass

    def display(self):
        """This displays the UI for the current plugin, can be done from any other plugin, or from the menubar of the main GUI (automatically loaded at start)
        """
        self.filename = self.show_savemenu()

        if self.show:
            self._initialize_UI()
            self.initialize_UI()
            self._final_initialize_UI()
        self.run()

    def initialize_UI(self):
        """This is the main UI that will be drawn, specifically for the written plugin
        """
        pass

    def show_savemenu(self):
        """Displays a File Dialog so the route of the file to be opened can be selected.

        Returns:
            str: route to the file
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self.parent,
            "QFileDialog.getOpenFileName()",
            "",
            str(self.extensions),
            options=options,
        )

        return fileName

    def _initialize_UI(self):
        """First part of the UI, generates the dock view and the internal layout
        """
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.layout = QVBoxLayout()

    def _final_initialize_UI(self):
        """Last part of the UI, generates the button to run the task, and attaches all essential widgets to the layout
        """
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
