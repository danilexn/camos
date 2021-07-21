# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QFileDialog

from camos.tasks.runtask import RunTask
from camos.tasks.base import BaseTask
from camos.utils.notifications import Notification
from camos.gui.notification import CaMOSQtNotification


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

    def display(self):
        if "image" in self.required and (type(self.model.list_images()) is type(None)):
            raise IndexError("The image model is empty")
        if "dataset" in self.required and (
            type(self.signal.list_datasets()) is type(None)
        ):
            raise IndexError("The dataset model is empty")

        self.filename = self.show_filemenu()

        if self.filename == "":
            raise ValueError("No file was selected")

        if self.show:
            self.buildUI()
            self.show()
        else:
            self.run()

        message = Notification("The file '{}' was saved".format(self.filename), "INFO")
        CaMOSQtNotification.from_notification(message)

    def show_filemenu(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(
            self.parent, "Save File", "", str(self.extensions), options=options,
        )

        return fileName
