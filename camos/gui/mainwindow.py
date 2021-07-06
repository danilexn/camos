# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QHBoxLayout, QMenu, QMessageBox

from camos.model.imageviewmodel import ImageViewModel
from camos.model.signalviewmodel import SignalViewModel
from camos.viewport.imageviewport import ImageViewPort
from camos.gui.preferencespanel import CAMOSPreferences
from camos.utils.settings import Config
from camos.utils.cmaps import bg_colors
from camos.utils.units import get_length
import camos.utils.units as units

from camos.gui.framecontainer import FrameContainer


class MainWindow(QtWidgets.QMainWindow):
    """This is the main GUI entry point of the application

    Args:
        QtWidgets (QMainWindow): base class from PyQt5 to inherit basic Window functionality
    """

    def __init__(self, camosApp=None, *args, **kwargs):
        """Initialization of the class and its parent

        Args:
            camosApp (camosApp, optional): The main instance of the application. Defaults to None.
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        # Global variables of the program, models and viewports

        self.title = "CaMOS"
        self.configuration = Config()
        self.current_configuration = self.configuration.readConfiguration()
        self.setup_model(ImageViewModel(parent=self))
        self.signalmodel = SignalViewModel(parent=self)
        self.setObjectName("camosGUI")
        self.camosApp = camosApp

        # Configure the main window settings
        self.readSettings()

        # Configure the units model
        units.configuration = self.configuration

        self.viewport = ImageViewPort(self.model, self.parent)
        # Config the background color of the viewport
        self.viewport.change_background(
            bg_colors[self.current_configuration["Viewport/Color"]]
        )

        # Connect events
        self.model.newdata.connect(self.viewport.load_image)
        self.model.updated.connect(self.viewport.update_viewport)
        self.model.updatedscale.connect(self.viewport.update_scalebar)
        self.model.axes.connect(self.viewport.translate_position)
        self.model.updatedframe.connect(self.viewport.update_viewport_frame)

        # Layout of the UI
        layout = QHBoxLayout()
        self.centralwidget = QtGui.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(layout)
        self.init_UI()
        self.create_menubar()
        self.container = FrameContainer(self)
        self.setCentralWidget(self.container)
        self.model.newdata.connect(self.container._update_layer_elements)
        self.model.removedata.connect(self.viewport.remove_image)
        self.model.updatepos.connect(self._update_statusbar)

    def setup_model(self, model):
        self.model = model

    def init_UI(self):
        """Basic appearance properties; title, geometry and statusbar. Eventually, shows the window.
        """
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon("resources/icon-app.png"))
        self.setGeometry(100, 100, 800, 600)
        self.statusBar().showMessage("Statusbar - awaiting user control")

        # This fixes the tooltip, so text is visible
        self.setStyleSheet(
            """QToolTip {
                           background-color: black;
                           color: white;
                           border: black solid 1px
                           }"""
        )
        self.show()

    def _update_statusbar(self, x, y, t, v, pxs):
        """Updates the basic info about the current image being displayed in the ImageViewPort in the statusbar.

        Args:
            x (int): X-coordinate of the pixel under the mouse for the current layer
            y (int): Y-coordinate of the pixel under the mouse for the current layer
            t (int): currently selected frame of the current layer
            v (int): RGB or gray value (any bit depth) of the pixel under the mouse for the current layer
            pxs (int): pixel size for the current layer
        """
        self.statusBar().showMessage(
            "Position (px): [{:.0f}, {:.0f}]; Position ({}): [{:.0f}, {:.0f}]; Frame: {}; Value: {}".format(
                x, y, get_length(), x / pxs, y / pxs, t, v
            )
        )

    def create_menubar(self):
        """Creates the menubar itself and the menus: File, Process and Analyze.
        File contains submenus for Open, Save, Preferences and Exiting the application
        Open and Save functionality are provided through plugins
        Process and Analyze are populated with the currently available plugins for each category.
        """
        # Main menubar
        menubar = self.menuBar()

        # High level menus
        self.fileMenu = menubar.addMenu("&File")
        self.processMenu = menubar.addMenu("&Process")
        self.analysisMenu = menubar.addMenu("&Analyze")
        self.helpMenu = menubar.addMenu("&Help")

        # File menu
        # Sublevels
        # Open image
        self.openMenu = QMenu("Open", self)
        self.saveMenu = QMenu("Save", self)

        self.exitAct = QtWidgets.QAction(QIcon("exit.png"), "&Exit program", self)
        self.exitAct.setShortcut("Ctrl+Q")
        self.exitAct.setStatusTip("Exit application")
        self.exitAct.triggered.connect(lambda: self.closeEvent(QtGui.QCloseEvent()))

        self.prefsAct = QtWidgets.QAction("&Preferences", self)
        self.prefsAct.setStatusTip("Main preferences of the application")
        self.prefsAct.triggered.connect(lambda: CAMOSPreferences(self))

        self.fileMenu.addMenu(self.openMenu)
        self.fileMenu.addMenu(self.saveMenu)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.prefsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

    def closeEvent(self, event):
        """Handle for self.exitAct being triggered

        Args:
            event (QtGui.QCloseEvent)
        """
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(
            self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Save all the configuration to the file
            self.configuration.saveConfiguration()
            event.accept()
        else:
            event.ignore()

    def readSettings(self):
        self.configuration.applyConfiguration(self.current_configuration, self)
