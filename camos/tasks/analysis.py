# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QPushButton,
    QWidget,
)
from PyQt5.QtCore import pyqtSignal
import PyQt5.QtCore as QtCore

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np

from camos.tasks.base import BaseTask
from camos.tasks.runtask import RunTask
from camos.tasks.plotting import AnalysisPlot
from camos.model.inputdata import InputData
from camos.utils.generategui import CreateGUI


class Analysis(BaseTask):
    plotReady = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Analysis, self).__init__(*args, **kwargs)
        self.foutput = np.zeros((1, 1))
        self.sampling = 1
        self.finished.connect(self.update_plot)
        self.model.imagetoplot.connect(self.update_values_plot)
        self.outputimage = np.zeros((1, 1))

    def buildUI(self):
        self.dockUI = QDockWidget(self.analysis_name, self.parent)
        self.main_layout = QHBoxLayout()
        self.group_settings = QGroupBox("Parameters")
        self.group_plot = QGroupBox("Plots")
        self.layout = QVBoxLayout()
        self.layout.addStretch(1)
        self.plot_layout = QVBoxLayout()
        self.plot = AnalysisPlot(self, width=5, height=4, dpi=100)
        self.plot.plottoimage.connect(self.parent.model.select_cells)
        self.toolbar = NavigationToolbar(self.plot, None)
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.plot)
        self.group_settings.setLayout(self.layout)
        self.group_plot.setLayout(self.plot_layout)
        self.main_layout.addWidget(self.group_settings, 1)
        self.main_layout.addWidget(self.group_plot, 4)
        self.params_gui = CreateGUI(self.paramDict, self.layout, self._run)
        self.params_gui.creategui()

        self.runButton = QPushButton("Run", self.parent)
        self.runButton.setToolTip("Click to run this task")
        self.handler = RunTask(self)
        self.runButton.clicked.connect(self.handler.start_progress)

        self.savePlot = QPushButton("To viewport", self.parent)
        self.savePlot.setToolTip("Click to move plot to viewport")
        self.savePlot.clicked.connect(self.export_plot_to_viewport)

        self.layout.addWidget(self.runButton)
        self.layout.addWidget(self.savePlot)

        self.dockedWidget = QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.main_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

    def export_plot_to_viewport(self):
        try:
            self.update_plot()
            image = InputData(self.outputimage, memoryPersist=True)
            image.loadImage()
            self.parent.model.add_image(
                image, "Viewport of {}".format(self.analysis_name)
            )
        except:
            pass
