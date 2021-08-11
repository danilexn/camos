# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtCore import QPointF

import numpy as np

import camos.viewport.mpl_cmaps_in_ImageItem as cmaps
import camos.utils.apptools as apptools
from camos.utils.settings import Config
from camos.utils.units import get_length


class ImageViewPort(pg.ImageView):

    # constructor which inherit original
    # ImageView
    def __init__(self, model=None, parent=None, *args, **kwargs):
        self.pixelsize = 1
        pg.ImageView.__init__(self, *args, **kwargs)
        self.model = model
        self.parent = parent
        self.configuration = Config()
        self.current_configuration = self.configuration.readConfiguration()
        self.scene.sigMouseMoved.connect(self.mouse_moved)
        self.scene.sigMouseClicked.connect(self.mouse_clicked)
        self.view.sigRangeChanged.connect(self.zoom_level_changed)
        self.scale = pg.ScaleBar(size=10, suffix="{}".format(get_length()))
        self.scale.setParentItem(self.view)
        self.scale.anchor((1, 1), (1, 1), offset=(-50, -50))

        # This will hide some UI elements that will be handled by us
        # self.ui.histogram.hide()
        self.ui.histogram.setLevelMode("mono")
        self.ui.histogram.fillHistogram(False)
        self.ui.histogram.disableAutoHistogramRange()
        self.ui.menuBtn.hide()
        self.ui.roiBtn.hide()
        self.timeLine = pg.InfiniteLine(0, movable=True, pen={"color": "y", "width": 3})
        self.timeLine.setBounds([0, 0])
        self.ui.roiPlot.addItem(self.timeLine)
        self.frameTicks = pg.VTickGroup(yrange=[0.8, 1], pen=0.4)
        self.ui.roiPlot.addItem(self.frameTicks)
        self.region = pg.LinearRegionItem([0, 0])
        self.region.setBounds([0, 0])
        self.region.setZValue(-10)
        self.ui.roiPlot.addItem(self.region)
        # Hide unless more than 1 frame
        self.ui.roiPlot.hide()

        self.roi.rotatable = False

        # Connect events to update the ImageViewModel
        self.timeLine.sigPositionChanged.connect(
            lambda: self.model.set_frame(t=int(self.timeLine.value()))
        )

    def zoom_level_changed(self, event):
        x_min, x_max = event.viewRange()[0]
        new_sz = max(round((x_max - x_min) / 10), 10)
        self._update_scalebar(new_sz)
        pass

    # All functions below have similar code now, just as a placeholder
    def load_image(self, layer=-1):
        # Get the image from the model
        image = self.model.get_layer(layer=layer)

        # Setup the display object
        item = DrawingImage(image=image, model=self.model)

        # Determine if the layer is the last one, or already exists on the viewport
        if layer == -1:
            self.model.viewitems.append(item)
        else:
            self.model.viewitems[layer] = item

        op = self.model.opacities[layer]
        # Add to viewport
        self.view.addItem(self.model.viewitems[layer])
        self.view.addedItems[-1].setOpts(opacity=op / 100, axisOrder="row-major")

        # Do not update other features if the image is larger than...
        if image.shape[0] > 10000 or image.shape[1] > 10000:
            return

        # Update viewport colormap, scale and translation
        cmap = self.model.colormaps[-1]
        lut = cmaps.cmapToColormap(cmap).getLookupTable()
        self.view.addedItems[-1].setLookupTable(lut)

        scale_x, scale_y = self.model.scales[-1]
        self.view.addedItems[-1].changeScale(scale_x, scale_y)

        # Only update position if the layer has translation
        if self.model.translation[layer] != [0, 0]:
            x, y = self.model.translation[layer]
            self.model.translation[layer] = [0, 0]
            self.translate_position(layer, (x, y))

    def center_position(self, **kwargs):
        pass

    def update_viewport(self, layer=0):
        op = self.model.opacities[layer]
        sc = self.model.scales[layer]
        cmap = self.model.colormaps[layer]
        lut = cmaps.cmapToColormap(cmap).getLookupTable()
        if op / 100 != self.view.addedItems[layer + 3].opacity:
            self.view.addedItems[layer + 3].setOpts(opacity=op / 100)
        if not np.array(lut == self.view.addedItems[layer + 3].lut).all():
            self.view.addedItems[layer + 3].setOpts(lut=lut)
        if sc[0] != self.view.addedItems[layer + 3].previous_scale[0]:
            self.view.addedItems[layer + 3].changeScale(sc[0], sc[1])

    def change_background(self, color=(0, 0, 0)):
        self.view.setBackgroundColor(color)

    def toggle_visibility(self, layer=0):
        if self.view.addedItems[layer + 3].isVisible():
            self.view.addedItems[layer + 3].hide()
        else:
            self.view.addedItems[layer + 3].show()

    def _update_scalebar(self, _range=5):
        self.scale.size = _range * self.pixelsize
        self.scale.text.setText("{} {}".format(_range, get_length()))

    def update_scalebar(self, pxsize=1):
        # Check if there are layers at all
        layer = self.model.currentlayer
        if layer < 0:
            return

        self.pixelsize = pxsize
        sz = self.scale.size * self.pixelsize
        self.scale.size = sz / pxsize

        # Update histogram after scaling and changing other levels
        self.ui.histogram.setImageItem(self.view.addedItems[layer + 3])

        # Update the frame selector
        bound = [0, self.model.frames[layer] - 1]

        # Check if multiframe
        if bound[1] > 0:
            self.timeLine.setBounds(bound)
            self.timeLine.setValue(self.model.frame)
            self.region.setBounds(bound)
            self.region.setRegion(bound)
            self.ui.roiPlot.show()
        else:
            self.ui.roiPlot.hide()

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
        idx = layer + 3 if layer != -1 else -1
        x = position[0]
        y = position[1]
        x_t, y_t = self.model.translation[layer]
        self.view.addedItems[idx].translate(x - x_t, y - y_t)
        self.model.translation[layer] = [x, y]

    def toggle_roi(self):
        if self.roi.isVisible():
            self.roi.hide()
        else:
            _i_layer = self.model.currentlayer
            _layer_pos = self.model.translation[_i_layer]
            _layer_sca = self.model.scales[_i_layer]
            _layer_shape = self.model.images[_i_layer]._image._imgs[0].shape[0:2]
            self.roi.setPos(_layer_pos[0], y=_layer_pos[1])
            self.roi.setSize(
                QPointF(
                    _layer_shape[1] * _layer_sca[0], _layer_shape[0] * _layer_sca[0]
                )
            )
            self.roi.show()


class DrawingImage(pg.ImageItem):
    accpos = [0, 0]
    previous_scale = [1, 1]
    p_co = 1
    p_br = 0
    ctrl_modif = False
    _xi, _yi = 0, 0

    def __init__(self, image, model, **kargs):
        super().__init__(image=image, **kargs)
        self.model = model

    def changeScale(self, s_x, s_y):
        p_x, p_y = self.previous_scale
        n_x, n_y = s_x / p_x, s_y / p_y
        self.scale(n_x, n_y)
        self.previous_scale = [s_x, s_y]
        self.ctrl_modif = False

    def mouseClickEvent(self, event):
        pass

    def mouseDragEvent(self, event):
        if event.isStart():
            if event.modifiers() == QtCore.Qt.ControlModifier:
                viewitems = self.model.viewitems
                idx = viewitems.index(self)
                p = event.pos()
                x, y = event.pos().x(), event.pos().y()
                self._xi, self._yi = p.x(), p.y()
                self.initial_pos = self.model.translation[idx]
                self.setBorder(pg.mkPen(cosmetic=False, width=4.5, color="r"))
                self.accpos = list(self.model.translation[idx])
                self.accpos[0] = self.accpos[0] + x - self._xi
                self.accpos[1] = self.accpos[1] + y - self._yi
                self.ctrl_modif = True
                self.model.viewitems[idx] = self

        elif event.isFinish():
            if self.ctrl_modif:
                viewitems = self.model.viewitems
                idx = viewitems.index(self)

                x, y = event.pos().x(), event.pos().y()
                self.accpos[0] = self.accpos[0] + x - self._xi
                self.accpos[1] = self.accpos[1] + y - self._yi
                self.model.set_translation(idx, self.accpos[0], self.accpos[1])

                self.setBorder(None)
                self.ctrl_modif = False
                self.model.viewitems[idx] = self

        else:
            if (event.modifiers() == QtCore.Qt.ControlModifier) or self.ctrl_modif:
                viewitems = self.model.viewitems
                idx = viewitems.index(self)
                p = event.pos()
                x, y = event.pos().x(), event.pos().y()
                self.accpos[0] = self.accpos[0] + x - self._xi
                self.accpos[1] = self.accpos[1] + y - self._yi
                self.translate(p.x() - self._xi, p.y() - self._yi)
                self.model.viewitems[idx] = self
        pass

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
