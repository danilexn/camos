# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from camos.plotter.matplotlibwidget import MatplotlibWidget
from PyQt5.QtWidgets import QDockWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QObject
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtCore, QtOpenGL

import numpy as np
import pyqtgraph as pg
import pyqtgraph.parametertree as ptree
import inspect

from camos.utils.apptools import getApp

translate = QtCore.QCoreApplication.translate


def get_plotter_index(plotter):
    plotter_dict = getApp().plugins_mgr.loaded_plotters
    for p in plotter_dict.values():
        if type(plotter) is p:
            return p

    return type(plotter)


class SignalViewer2(QObject):
    window_title = "Signal Viewer"

    def __init__(self, parent=None, signal=None, title="", mask=[], plotter=None):
        super(SignalViewer2, self).__init__()
        self.parent = parent
        self.model = self.parent.model
        # self.parent.model.imagetoplot.connect(self.update_values_plot)
        self.output = signal
        self.foutput = self.output
        self.mask = mask
        self.pixelsize = 1
        self.title = title
        self.exportable = False
        self.connect_range = False
        self.to_export = np.zeros([1, 1])

        # Setup pyqtgraph
        self.plot = pg.GraphicsLayoutWidget()
        pg.setConfigOption("useOpenGL", True)
        self.plot.setViewport(QtOpenGL.QGLWidget())
        self.plot.useOpenGL(True)

        assert plotter is not None

        if inspect.isclass(plotter):
            self.plotter = plotter(
                self.parent, self.plot, self.foutput, title=self.title
            )
        else:
            self.plotter = plotter
            self.plotter.parent = self.parent
            self.plotter.viewer = self.plot
            self.plotter.data = self.foutput
            self.plotter.title = self.title

        # Construct the dock
        self.buildDock()

    def display(self, index=0):
        # Construct the UI for the first time
        self.buildUI()

        # Update what is inside the plot
        self.update_plot()

        # Display the dock UI
        self.show()

    def show(self):
        self.dockUI.show()

    def update_plot(self):
        self._plot()

    def buildDock(self):
        self.dockUI = QDockWidget(self.window_title, self.parent)
        self.dockUI.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

    def buildUI(self):
        # Restore the layout
        if hasattr(self, "plot_layout"):
            for i in reversed(range(self.plot_layout.count())):
                self.plot_layout.itemAt(i).widget().setParent(None)
        else:
            self.plot_layout = QVBoxLayout()

        # Setup the correct backend
        if hasattr(self.plotter, "plotItem"):
            if self.plotter.backend is "matplotlib":
                self.plot = MatplotlibWidget()

                # Update the viewer in the plotter
                self.plotter.viewer = self.plot

        # Main plot setup in UI
        self.plot_layout.addWidget(self.plot)

        # Setup the correct backend
        if hasattr(self.plotter, "plotItem"):
            if self.plotter.backend is "pyqtgraph":
                # Parameters for pyqtgraph only
                pt = self.createParameterTree()
                self.plot_layout.addWidget(pt)

        self.dockedWidget = QtWidgets.QWidget()

        # All in a floating dock
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.plot_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

        assert self.plotter is not None
        self.exportButton = QPushButton("Export to Viewport")
        self.exportButton.setToolTip(
            "The current plot will be loaded to the viewport as an image"
        )
        self.exportButton.clicked.connect(self.plotter.toViewport)
        self.plot_layout.addWidget(self.exportButton)
        self.exportButton.hide()

    def update_values_plot(self, values):
        try:
            self.plot.clear()
        finally:
            self._update_values_plot(values)
            self.plotter.data = self.foutput
            self.plotter.plot()

    def _update_values_plot(self, values):
        try:
            if self.output.dtype.names == None:
                idx = values
            else:
                idx = np.isin(self.output[:]["CellID"], np.array(values))
            self.foutput = self.output[idx]
        except Exception as e:
            print(str(e))

    def createParameterTree(self):
        # Parameters tree
        param = ptree.Parameter.create(
            name=translate("ScatterPlot", "Parameters"),
            type="group",
            children=[
                dict(
                    name="connectRange",
                    title="Connect X-axis to viewport:    ",
                    type="bool",
                    value=False,
                    function=self._change_range_connection,
                ),
                dict(
                    name="connectTime",
                    title="Add time line to X-axis:    ",
                    type="bool",
                    value=False,
                    function=self._change_time_connection,
                ),
                dict(
                    name="plotType",
                    title="Change Plot type:    ",
                    type="list",
                    values=getApp().plugins_mgr.loaded_plotters,
                    value=get_plotter_index(self.plotter),
                    function=self._change_plot_type,
                ),
                dict(
                    name="plotCmap",
                    title="Change Colormap:    ",
                    type="list",
                    values=["inferno", "viridis", "plasma", "magma", "rainbow"],
                    value="inferno",
                    function=self._change_colormap,
                ),
            ],
        )
        for c in param.children():
            c.setDefault(c.value())
            if c.type() in ["int", "list"]:
                c.sigValueChanged.connect(c.opts["function"])
            else:
                c.sigTreeStateChanged.connect(c.opts["function"])

        pt = ptree.ParameterTree(showHeader=False)
        pt.setParameters(param)
        return pt

    def _change_size(self, param, value):
        print("Value changing (not finalized): %s %s" % (param, value))

    def _change_range_connection(self, param, value):
        self.plotter.connectrange = value

    def _change_time_connection(self, param, value):
        self.plotter.connect_time = value

    def _change_plot_type(self, param, value):
        colname = self.plotter.colname
        try:
            self.plot.clear()
        except Exception as e:
            raise e
        finally:
            self.plotter = value(self.parent, self.plot, self.foutput)
            self.plotter.colname = colname
            self.update_plot()

    def _change_colormap(self, param, value):
        self.plotter.colormap = value

    def _plot(self):
        if self.plotter is not None:
            if self.mask is not []:
                self.plotter.mask = self.mask
            self.plotter.plot()

        if self.plotter.exportable:
            self.exportButton.show()
            try:
                self.exportButton.clicked.disconnect()
            finally:
                self.exportButton.clicked.connect(self.plotter.toViewport)
        else:
            self.exportButton.hide()
