# -*- coding: utf-8 -*-
# Created on Thu Jul 15 2021
# Last modified on Thu Jul 15 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5 import QtWidgets

mouse_help_text = """You can use the mouse for the following:
    1. Inside the viewport:
        Drag over the viewport: shows the values for the current
            pixel in the currently selected image layer at the 
            statusbar
        Drag over with left button pressed: moves the viewport,
            except if you are over an image (only at blank space)
        Drag over with middle button: moves the viewport, even if
            you are over an image
        Drag over with right button: same as with middle button
        Single click with left button: no action
        Drag over with left button and CTRL key: moves the clicked
            image around the viewport. Releasing the mouse will release
            the image at that specific position.
        Single click with rigth button: displays the contextual menu
            to modify visualization settings, and to export the current
            viewport
        Double click with left button: if the option 'Select Cell' is
            toggled On, creates a new image layer from the currently
            selected one, with just the pixels that have the same value
            as the pixel in which you double clicked. If 'Select Cell'
            is disabled, sends a signal to all plots, so the IDs are 
            updated to the value of the pixel
    2. Layers tab:
        Double click with left button: displays a dialog to change
            the name of the current layer
        Single click with left button: changes to the clicked layer
        Single click with right button: displays the contextual menu
            to toggle the visibility, remove the layer, and adjust
            various preferences
    3. Datasets tab:
        Single click with left button: changes the active dataset to
            the clicked one
        Double click with left button: displays the plot visualization
            for the current dataset (if available)
        Single click with right button: displays a contextual menu to
            remove the current dataset, or to display the data as a table"""


class MouseHelp(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MouseHelp, self).__init__(parent)

        self.setWindowTitle("Mouse Actions")

        box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        self.helptext = QtWidgets.QPlainTextEdit()
        self.helptext.setPlainText(mouse_help_text)
        self.helptext.setReadOnly(True)

        lay = QtWidgets.QGridLayout(self)
        lay.addWidget(self.helptext)
        lay.addWidget(box, 2, 0, 1, 2)
