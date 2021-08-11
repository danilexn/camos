# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QFileDialog

import os

from camos.tasks.base import BaseTask
from camos.utils.notifications import notify

DEBUG = os.getenv("CAMOS_DEBUG")


class Opening(BaseTask):
    """This is the Opening class
    This handles the basic functionality that can be inherited from any other class implementing a plugin, whose purpose is opening and loading files (images or datasets) into CaMOS.
    """

    required = []

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
        self._show = show
        self.extensions = extensions
        self.filename = ""
        self.finished.connect(self.notify_opened)

    def display(self):
        if "image" in self.required and (type(self.model.list_images()) is type(None)):
            raise IndexError("The image model is empty")
        if "dataset" in self.required and (
            type(self.signal.list_datasets()) is type(None)
        ):
            # TODO: add as a warning (notification system)
            print("No file was selected")

        self.filename = self.show_filemenu()

        if self.filename == "":
            raise ValueError("No file was selected")

        if self._show:
            self.buildUI()
            self.show()
        else:
            if DEBUG is None:
                self.handler.start_progress()
            else:
                self.run()

    def notify_opened(self):
        notify("The file '{}' was opened".format(self.filename), "INFO")

    def open(self):
        """This will directly execute the run task, to support drag and drop.
        A filename must be different than the empty string!
        """
        assert self.filename != ""
        if DEBUG is None:
            self.handler.start_progress()
        else:
            self.run()

    def show_filemenu(self):
        """Displays a File Dialog so the route of the file to be opened can be selected.

        Returns:
            str: route to the file
        """
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(
            self.parent, "Open File", "", str(self.extensions), options=options,
        )

        return fileName
