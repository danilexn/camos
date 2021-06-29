# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt, QSizeF, pyqtSignal

import PIL
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

from camos.tasks.opening import Opening
from camos.model.inputdata import InputData
from camos.viewport.imageviewport import ImageViewPort
from camos.model.imageviewmodel import ImageViewModel


class OpenCMOS(Opening):
    """This is the plugin to load CMOS images into CaMOS, being able to select the electrodes
    """

    finished = pyqtSignal()
    plotReady = pyqtSignal()
    gridReady = pyqtSignal(np.ndarray)
    intReady = pyqtSignal(int)
    analysis_name = "Open CMOS Chip"

    def __init__(self, parent=None, **kwargs):
        """Initialization of the object

        Args:
            model ([type], optional): [description]. Defaults to None.
            signal ([type], optional): [description]. Defaults to None.
            parent ([type], optional): [description]. Defaults to None.
            signal ([type], optional): [description]. Defaults to None.
            file ([type], optional): [description]. Defaults to None.
        """
        super(OpenCMOS, self).__init__(
            None,
            parent,
            None,
            name=self.analysis_name,
            extensions="tif File (*.tif)",
            show=True,
        )
        self.parent = parent
        self.minimodel = MiniImageViewModel(parent=self)
        self.viewport = ImageViewPort(self.minimodel)
        self.minimodel.updated.connect(self.viewport.update_viewport)
        self.minimodel.newdata.connect(self.viewport.load_image)
        self.gridReady.connect(self.minimodel.draw_grid)
        self.cardinal = []
        self.grid = None

    def _run(self):
        # We need to change this, otherwise PIL does not open the image
        PIL.Image.MAX_IMAGE_PIXELS = 933120000
        self.image = InputData(self.filename, memoryPersist=True)
        self.image.loadImage()
        self.minimodel.add_image(self.image)

    def initialize_UI(self):
        self.onlyInt = QIntValidator()
        self.xdimlabel = QLabel("Grid edge size (N)")
        self.xdim = QLineEdit()
        self.xdim.setValidator(self.onlyInt)
        self.xdim.setText("64")
        self.layout.addWidget(self.xdimlabel)
        self.layout.addWidget(self.xdim)

        self.radiuslab = QLabel("Radius")
        self.radius = QLineEdit()
        self.radius.setValidator(self.onlyInt)
        self.radius.setText("100")
        self.layout.addWidget(self.radiuslab)
        self.layout.addWidget(self.radius)

        self.scalelab = QLabel("Output Scale")
        self.scale = QLineEdit()
        self.scale.setValidator(self.onlyInt)
        self.scale.setText("10")
        self.layout.addWidget(self.scalelab)
        self.layout.addWidget(self.scale)

        self.clearButton = QPushButton("Clear Grid")
        self.clearButton.clicked.connect(self.clear_grid)
        self.layout.addWidget(self.clearButton)

        self.runButton = QPushButton("Create Grid")
        self.runButton.setToolTip("Create a grid from selected points")
        self.runButton.clicked.connect(self.calculate_grid)

        self.layout.addWidget(self.runButton)

        self.runButton = QPushButton("Import now")
        self.runButton.setToolTip("Import the chip image and the coordinates")
        self.runButton.clicked.connect(self.import_chip)

        self.layout.addWidget(self.runButton)

    def _initialize_UI(self):
        self.dockUI = QDockWidget(self.analysis_name)
        self.main_layout = QHBoxLayout()
        self.group_settings = QGroupBox("Parameters")
        self.group_plot = QGroupBox("Plots")
        self.layout = QVBoxLayout()
        self.plot_layout = QVBoxLayout()
        self.plot_layout.addWidget(self.viewport)
        self.group_settings.setLayout(self.layout)
        self.group_plot.setLayout(self.plot_layout)
        self.main_layout.addWidget(self.group_settings, 1)
        self.main_layout.addWidget(self.group_plot, 4)

    def _final_initialize_UI(self):
        self.dockedWidget = QtWidgets.QWidget()
        self.dockUI.setWidget(self.dockedWidget)
        self.dockedWidget.setLayout(self.main_layout)
        self.dockUI.setFloating(True)
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockUI)

    def projection(self, p1, p2, p3):
        l2 = np.sum((p1 - p2) ** 2)
        t = np.sum((p3 - p1) * (p2 - p1)) / l2
        t = max(0, min(1, np.sum((p3 - p1) * (p2 - p1)) / l2))
        return p1 + t * (p2 - p1)

    def createLineAndProject(self, v_x, v_y, pts_projected, dim):
        x = np.linspace(v_x[0], v_x[1], dim[0])
        y = np.linspace(v_y[0], v_y[0], dim[1])
        pts = np.array(list(zip(x, y)))
        for p in pts:
            pts_projected.append(
                self.projection(
                    np.array([v_x[0], v_y[0]]), np.array([v_x[1], v_y[1]]), p
                )
            )

    def createLineAndProjectHorizontal(self, v_x, v_y, pts_projected, dim):
        x = np.linspace(v_x[0], v_x[1], dim[0])
        y = np.linspace(v_y[0], v_y[0], dim[1])
        pts = np.array(list(zip(x, y)))
        for p in pts:
            pts_projected.append(
                np.flip(
                    self.projection(
                        np.array([v_x[0], v_y[0]]),
                        np.array([v_x[1], v_y[1]]),
                        p,
                    )
                )
            )

    @pyqtSlot()
    def calculate_grid(self):
        ps = []
        dim = (int(self.xdim.text()), int(self.xdim.text()))
        c = self.cardinal
        self.createLineAndProject(
            [c[0][0], c[1][0]], [c[0][1], c[1][1]], ps, dim
        )
        self.createLineAndProject(
            [c[2][0], c[3][0]], [c[2][1], c[3][1]], ps, dim
        )
        ps_np = np.array(ps)
        ps = []
        for i in range(dim[0]):
            self.createLineAndProjectHorizontal(
                [ps_np[i + dim[1]][1], ps_np[i][1]],
                [ps_np[i + dim[0]][0], ps_np[i][0]],
                ps,
                dim,
            )

        self.grid = np.array(ps)
        self.gridReady.emit(self.grid)

    def clear_grid(self):
        self.cardinal = []
        while len(self.viewport.view.addedItems) > 4:
            self.viewport.view.removeItem(self.viewport.view.addedItems[-1])

    def rotated_matrix_indexes(self, N):
        replacement = np.flip(np.array(np.arange(1, N*N + 1, 1)).reshape(N, N).T, axis = 1).flatten()
        return replacement

    def import_chip(self):
        scale = 1/int(self.scale.text())
        N = int(self.xdim.text())
        radius = int(int(self.radius.text())*scale)
        img_dims = self.image._image._imgs[0].shape
        grid_image = np.zeros((int(img_dims[0]*scale), int(img_dims[1]*scale)))
        replacement = self.rotated_matrix_indexes(N)
        pos = {}
        for i, c in enumerate(self.grid):
            _min_y = int(c[0]*scale) - radius if int(c[0]*scale) - radius > 0 else 0
            _max_y = int(c[0]*scale) + radius if int(c[0]*scale) - radius < img_dims[0] else img_dims[0]

            _min_x = int(c[1]*scale) - radius if int(c[1]*scale) - radius > 0 else 0
            _max_x = int(c[1]*scale) + radius if int(c[1]*scale) - radius < img_dims[1] else img_dims[1]
            pos[replacement[i]] = [np.average([_max_x, _min_x]), np.average([_max_y, _min_y])]
            grid_image[_min_x:_max_x, _min_y:_max_y] = replacement[i]

        self.grid_image = InputData(grid_image, memoryPersist=True)
        self.grid_image.loadImage()
        self.grid_image.coords = pos
        self.parent.model.add_image(self.grid_image, scale = [1/scale, 1/scale])


class MiniImageViewModel(ImageViewModel):

    def __init__(self, images=[], parent=None):
        super(MiniImageViewModel, self).__init__()
        self.images = images
        self.currentlayer = 0
        self.curr_x, self.curr_y = 0, 0
        self.parent = parent

    def trigger_select_cells(self):
        pass

    def get_current_view(self, index=0):
        if len(self.images) == 0:
            import numpy as np

            return np.zeros((1, 1))
        return self.images[0]._image._imgs[0]

    def set_currpos(self, x, y):
        self.curr_x = x
        self.curr_y = y

    def draw_grid(self, coords):
        for coord in coords:
            item = Square(name="B")
            item.setPos(coord[0], coord[1])
            self.parent.viewport.view.addItem(item)

    def select_cells(self, **kwargs):
        coord = np.array([self.curr_y - 100 / 2, self.curr_x - 100 / 2])
        self.draw_grid(np.array([coord]))
        self.parent.cardinal.append(coord)

class Square(QGraphicsWidget):
    def __init__(self, size=100, *args, name=None, **kvps):
        super().__init__(*args, **kvps)
        self.radius = 5
        self.size = size
        self.name = name
        self.setAcceptHoverEvents(True)
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemIsFocusable)

    def sizeHint(self, hint, size):
        size = super().sizeHint(hint, size)
        return QSizeF(self.size, self.size)

    def paint(self, painter, options, widget):
        painter.setBrush(Qt.red)  # ink
        painter.drawEllipse(self.rect())
