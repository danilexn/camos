# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
from PyQt5 import QtGui

import camos.viewport.mpl_cmaps_in_ImageItem as cmaps
import camos.utils.apptools as apptools


class ImageViewPort(pg.ImageView):

    # constructor which inherit original
    # ImageView
    def __init__(self, model=None, parent=None, *args, **kwargs):
        self.pixelsize = 1
        pg.ImageView.__init__(self, *args, **kwargs)
        self.model = model
        self.parent = parent
        self.scene.sigMouseMoved.connect(self.mouse_moved)
        self.scene.sigMouseClicked.connect(self.mouse_clicked)
        self.view.sigRangeChanged.connect(self.zoom_level_changed)
        self.scale = pg.ScaleBar(size=10, suffix="μm")
        self.scale.text.setText("10 μm")
        self.scale.setParentItem(self.view)
        self.scale.anchor((1, 1), (1, 1), offset=(-50, -50))

        # This will hide some UI elements that will be handled by us
        self.ui.histogram.hide()
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()
        self.roi.rotatable = False

    def zoom_level_changed(self, event):
        x_min, x_max = event.viewRange()[0]
        new_sz = max(round((x_max - x_min) / 10), 100)
        self._update_scalebar(new_sz)
        pass

    # All functions below have similar code now, just as a placeholder
    def load_image(self, layer=-1):
        image = self.model.get_layer(layer=layer)
        item = DrawingImage(image=image)
        if layer == -1:
            self.model.viewitems.append(item)
        else:
            self.model.viewitems[layer] = item
        self.view.addItem(self.model.viewitems[layer])
        self.view.addedItems[-1].setOpts(opacity=0.5, axisOrder="row-major")
        if image.shape[0] > 10000 or image.shape[1] > 10000:
            return
        cmap = self.model.colormaps[-1]
        lut = cmaps.cmapToColormap(cmap).getLookupTable()
        self.view.addedItems[-1].setLookupTable(lut)
        scale_x, scale_y = self.model.scales[-1]
        self.view.addedItems[-1].scale(scale_x, scale_y)
        # self.view.addedItems[-1].setLevels([0, 210])

    def center_position(self, **kwargs):
        pass

    def update_viewport(self, layer=0):
        op = self.model.opacities[layer]
        sc = self.model.scales[layer]
        cmap = self.model.colormaps[layer]
        lut = cmaps.cmapToColormap(cmap).getLookupTable()
        self.view.addedItems[layer + 3].setOpts(opacity=op / 100, lut=lut)
        self.view.addedItems[layer + 3].scale(sc[0], sc[1])
        # self.view.addedItems[layer + 3].setLevels([0, 210])

    def change_background(self, color=(0, 0, 0)):
        self.view.setBackgroundColor(color)

    def toggle_visibility(self, layer=0):
        if self.view.addedItems[layer + 3].isVisible():
            self.view.addedItems[layer + 3].hide()
        else:
            self.view.addedItems[layer + 3].show()

    def _update_scalebar(self, _range=5):
        self.scale.size = _range * self.pixelsize
        self.scale.text.setText("{} μm".format(_range))

    def update_scalebar(self, pxsize=1):
        self.pixelsize = pxsize
        sz = self.scale.size * self.pixelsize
        self.scale.size = sz / pxsize

    def update_viewport_frame(self, layer=0):
        image = self.model.get_layer(layer=layer)
        self.view.addedItems[layer + 3].setImage(image)
        self.model.viewitems[layer] = self.view.addedItems[layer + 3]

    def remove_image(self, layer=0):
        self.view.removeItem(self.view.addedItems[layer + 3])

    def mouse_moved(self, event):
        if len(self.view.addedItems) <= 3:
            return
        layer = self.model.currentlayer
        scenePos = self.view.addedItems[layer + 3].mapFromScene(event)
        row, col = int(scenePos.x()), int(scenePos.y())
        self.model.set_currpos(col, row)

    def mouse_clicked(self, event):
        if event._double:
            self.model.select_cells()

    def roiChanged(self, event):
        roi_coord = [
            [event.pos().y(), event.pos().x()],
            [event.pos().y() + event.size().y(), event.pos().x() + event.size().x(),],
        ]
        self.model.roi_coord = roi_coord

    def translate_position(self, layer, position):
        x = position[0]
        y = position[1]
        x_t, y_t = self.model.translation[layer]
        self.view.addedItems[layer + 3].translate(x - x_t, y - y_t)
        self.model.translation[layer] = [x, y]

    def toggle_roi(self):
        if self.roi.isVisible():
            self.roi.hide()
        else:
            self.roi.show()


class DrawingImage(pg.ImageItem):
    accpos = [0, 0]

    def mouseClickEvent(self, event):
        pass

    def mouseDragEvent(self, event):
        if event.isStart():
            model = apptools.getApp().gui.model
            viewitems = model.viewitems
            idx = viewitems.index(self)
            self.initial_pos = model.translation[idx]
            self.setBorder(pg.mkPen(cosmetic=False, width=4.5, color="r"))
            self.accpos = model.translation[idx]

        elif event.isFinish():
            model = apptools.getApp().gui.model
            viewitems = model.viewitems
            idx = viewitems.index(self)

            x, y = event.pos().x(), event.pos().y()
            self.accpos[0] = self.accpos[0] + x
            self.accpos[1] = self.accpos[1] + y
            apptools.getApp().gui.model.translation[idx] = [
                self.accpos[0],
                self.accpos[1],
            ]

            self.setBorder(None)

        else:
            p = event.pos()
            x, y = event.pos().x(), event.pos().y()
            self.accpos[0] = self.accpos[0] + x
            self.accpos[1] = self.accpos[1] + y
            self.translate(p.x(), p.y())

    def hoverEvent(self, event):
        if not event.isExit():
            # the mouse is hovering over the image; make sure no other items
            # will receive left click/drag events from here.
            event.acceptDrags(pg.QtCore.Qt.LeftButton)
            event.acceptClicks(pg.QtCore.Qt.LeftButton)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d
