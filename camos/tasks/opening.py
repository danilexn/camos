# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QDockWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from camos.tasks.base import BaseTask


class Opening(BaseTask):
    """This is the Opening class
    This handles the basic functionality that can be inherited from any other class implementing a plugin, whose purpose is opening and loading files (images or datasets) into CaMOS.
    """

    def __init__(
        self,
        show=False,
        extensions="avi File (*.avi);;mov File (*.mov)",
        *args,
        **kwargs
    ):
        """Initialize the Opening object

        Args:
            show (bool, optional): whether a dock is going to be displayed after selecting the file route (True), or the self.run method will be run just after (False). Defaults to False.
            extensions (str, optional): filter for the extensions in the QFileDialog. Defaults to "avi File (*.avi);;mov File (*.mov)".
        """
        super(Opening, self).__init__(*args, **kwargs)
        self.show = show
        self.extensions = extensions

    @pyqtSlot()
    def run(self):
        """This is the entry point when the run button is pressed, or if the plugin is called from other plugin (without UI).
        """
        if not self.filename:
            raise ValueError("Path was not selected!")
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
        else:
            self.run()

    def show_savemenu(self):
        """Displays a File Dialog so the route of the file to be opened can be selected.

        Returns:
            str: route to the file
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self.parent, "Open File", "", str(self.extensions), options=options,
        )

        return fileName
