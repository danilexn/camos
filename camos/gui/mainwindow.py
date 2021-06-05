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
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from camos.model.imageviewmodel import ImageViewModel
from camos.model.signalviewmodel import SignalViewModel
from camos.viewport.imageviewport import ImageViewPort
from camos.viewport.signalviewport import SignalViewPort
from camos.gui.framecontainer import FrameContainer


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, camosApp=None, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Global variables of the program, models and viewports
        self.title = "CaMOS"
        self.model = ImageViewModel(parent=self)
        self.signalmodel = SignalViewModel(parent=self)
        self.setObjectName("camosGUI")
        self.camosApp = camosApp

        self.viewport = ImageViewPort(self.model, self.parent)
        self.signalviewport = SignalViewPort(self.signalmodel, self.parent)

        # Connect events
        self.signalmodel.newdata.connect(self.signalviewport.add_last_track)
        self.model.newdata.connect(self.viewport.update_viewport)
        self.model.updated.connect(self.viewport.update_viewport)

        # Layout of the UI
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.initUI()
        self.create_menubar()
        self.container = FrameContainer(self)
        self.setCentralWidget(self.container)
        self.model.newdata.connect(self.container._update_layer_elements)
        self.model.removedata.connect(self.viewport.remove_image)
        self.model.updatepos.connect(self._update_statusbar)

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)
        self.statusBar().showMessage("Statusbar - awaiting user control")
        self.show()

    def _update_statusbar(self, x, y, t, int):
        self.statusBar().showMessage(
            "Position: [{}, {}]; Frame: {}; Value: {}".format(x, y, t, int)
        )

    def create_menubar(self):
        # Main menubar
        menubar = self.menuBar()

        # High level menus
        self.fileMenu = menubar.addMenu("&File")
        self.processMenu = menubar.addMenu("&Process")
        self.analysisMenu = menubar.addMenu("&Analyze")

        # File menu
        # Sublevels
        # Open image
        self.openAct = QtWidgets.QAction(QIcon("open.png"), " &Open image...", self)
        self.openAct.setShortcut("Ctrl+O")
        self.openAct.setStatusTip("Open file")
        self.openAct.triggered.connect(self.on_open_image_clicked)

        self.openAct = QtWidgets.QAction(QIcon("open.png"), " &Open image...", self)
        self.openAct.setShortcut("Ctrl+O")
        self.openAct.setStatusTip("Open file")
        self.openAct.triggered.connect(self.on_open_image_clicked)

        self.openMenu = QMenu("Open", self)
        self.saveMenu = QMenu("Save", self)

        self.exitAct = QtWidgets.QAction(QIcon("exit.png"), " &Exit program", self)
        self.exitAct.setShortcut("Ctrl+Q")
        self.exitAct.setStatusTip("Exit application")
        self.exitAct.triggered.connect(QtWidgets.qApp.quit)

        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addMenu(self.openMenu)
        self.fileMenu.addMenu(self.saveMenu)
        # self.fileMenu.addAction(self.exportAct)
        # self.fileMenu.addAction(self.settingsAct)
        self.fileMenu.addAction(self.exitAct)

    def on_open_image_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "QFileDialog.getOpenFileName()",
            "",
            "All Files (*);;tif Files (*.tif)",
            options=options,
        )
        if fileName:
            # handler = RunTask(ExtractSignal, self.model)
            # handler.start_progress
            # Run in background
            self.model.load_image(fileName)

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(
            self, "Message", quit_msg, QMessageBox.Yes, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
