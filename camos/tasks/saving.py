# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSlot

from camos.tasks.runtask import RunTask
from camos.tasks.base import BaseTask


class Saving(BaseTask):
    required = ["image", "dataset"]

    def __init__(
        self,
        show=False,
        extensions="avi File (*.avi);;mov File (*.mov)",
        *args,
        **kwargs
    ):
        super(Saving, self).__init__(*args, **kwargs)
        self.show = show
        self.extensions = extensions
        self.handler = RunTask(self)

    @pyqtSlot()
    def run(self):
        if not self.filename:
            raise ValueError("Path was not selected!")
        try:
            self._run()
            if self.handler != None:
                self.handler.success = True
        finally:
            self.finished.emit()
        pass

    def display(self):
        if "image" in self.required and (type(self.model.list_images()) is type(None)):
            raise IndexError("The image model is empty")
        if "dataset" in self.required and (
            type(self.signal.list_datasets()) is type(None)
        ):
            IndexError("The dataset model is empty")

        self.filename = self.show_savemenu()

        if self.show:
            self._initialize_UI()
            self.initialize_UI()
            self._final_initialize_UI()
        else:
            self.handler.start_progress()

    def show_savemenu(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self.parent, "Save File", "", str(self.extensions), options=options,
        )

        return fileName
