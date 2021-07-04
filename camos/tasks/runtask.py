# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread

from camos.utils.errormessages import ErrorMessages
import camos.utils.apptools as apptools


class RunTask(QWidget):
    def __init__(self, task):
        super().__init__()
        try:
            name = task.analysis_name
        except:
            name = "task"

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 500, 75)

        self.waitLabel = QLabel("Wait while {} is running".format(name))
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.setToolTip("Click to cancel this task")
        self.cancelButton.clicked.connect(self.closeEvent)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.layout.addWidget(self.waitLabel)
        self.layout.addWidget(self.cancelButton)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle("Running {}".format(name))
        self.success = False

        self.obj = task

    def _init_thread(self):
        self.thread = QThread(parent=apptools.getApp().gui)
        self.obj.intReady.connect(self.on_count_changed)
        self.obj.moveToThread(self.thread)
        self.thread.started.connect(self.obj.run)
        self.obj.finished.connect(self.finish_thread)

    def start_progress(self):
        self._init_thread()
        self.show()
        self.thread.start()

    def finish_thread(self):
        if not self.success:
            ErrorMessages("The task failed to execute")
        self.hide()

    def on_count_changed(self, value):
        self.pbar.setValue(value)

    def closeEvent(self, event):
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
