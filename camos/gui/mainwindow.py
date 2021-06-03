from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot

# TODO: this is hard coded, create a new GUI and model for managing plugins
from plugins.extractsignal import ExtractSignal
from plugins.generatemask import GenerateMask

# TODO: restructure to avoid the ..
from model.imageviewmodel import ImageViewModel
from model.signalviewmodel import SignalViewModel
from viewport.imageviewport import ImageViewPort
from viewport.signalviewport import SignalViewPort
from gui.framecontainer import FrameContainer

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Global variables of the program, models and viewports
        self.title = "CaMOS"
        self.model = ImageViewModel(parent=self)
        self.signalmodel = SignalViewModel(parent=self)
        # TODO: this is hard coded, create a new GUI and model for managing plugins
        # TODO: replace the 2d array approach by the metadata inside the specific classes
        # TODO: implement the same for analysis tasks
        self.process_plugins = [
            [ExtractSignal, "Extract Signals", "Extract signal from masked cells"],
            [GenerateMask, "Generate masks", "Generate masks from fluorescence image"],
        ]
        self.process_plugins_UI = []
        # self.viewport = ImageViewPort(self.model, self.parent, width=5, height=4, dpi=100)
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
        self.model.updatepos.connect(self._update_statusbar_pos)

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)
        self.statusBar().showMessage("Statusbar - awaiting user control")
        self.show()

    def _update_statusbar_pos(self, x, y, t):
        self.statusBar().showMessage("Position: [{}, {}]; Frame: {}".format(x, y, t))

    def create_menubar(self):
        # Main menubar
        menubar = self.menuBar()

        # High level menus
        self.fileMenu = menubar.addMenu("&File")
        self.processMenu = menubar.addMenu("&Process")

        # File menu
        # Sublevels
        # Open image
        self.openAct = QtWidgets.QAction(QIcon("open.png"), " &Open image...", self)
        self.openAct.setShortcut("Ctrl+O")
        self.openAct.setStatusTip("Open file")
        self.openAct.triggered.connect(self.on_open_image_clicked)

        self.exitAct = QtWidgets.QAction(QIcon("exit.png"), " &Exit program", self)
        self.exitAct.setShortcut("Ctrl+Q")
        self.exitAct.setStatusTip("Exit application")
        self.exitAct.triggered.connect(QtWidgets.qApp.quit)

        self.fileMenu.addAction(self.openAct)
        # self.fileMenu.addAction(self.exportAct)
        # self.fileMenu.addAction(self.settingsAct)
        self.fileMenu.addAction(self.exitAct)

        # Process menu
        # Sublevels
        # Regenerate signal from image (mask and fluorescence)
        for plugin in self.process_plugins:
            self.process_plugins_UI.append(plugin[0](self.model, parent=self))
            current_plugin_button = QtWidgets.QAction(
                QIcon("signal.png"), " {}".format(plugin[1]), self
            )
            current_plugin_button.setStatusTip(plugin[2])
            current_plugin_button.triggered.connect(self.process_plugins_UI[-1].display)

            # Parent level
            self.processMenu.addAction(current_plugin_button)

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