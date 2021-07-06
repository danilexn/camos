from PyQt5 import QtGui
from PyQt5.QtWidgets import QLabel, QComboBox
import warnings

import camos.utils.apptools as apptools
from camos.utils.settings import Config
from camos.utils.cmaps import bg_colors as colors
from camos.utils.units import length


class CAMOSPreferences(QtGui.QDialog):
    def __init__(self, parent=None):
        self.parent = parent

        if parent == None:
            self.parent = apptools.getGui()

        self.gui = apptools.getGui()
        self.configurator = Config()
        self.current_config = self.configurator.readConfiguration()

        super(CAMOSPreferences, self).__init__(parent)

        self.setWindowTitle("Program Preferences")
        layout = QtGui.QGridLayout(self)

        # Calls the functions that create individual UI components
        self.viewportBackgroundUI(layout)
        self.lengthUnitsUI(layout)

        # Creates the Accept/Cancel buttons
        box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            centerButtons=True,
        )

        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)

        # Add the buttons to the main layout
        layout.addWidget(box)
        self.show()

    def viewportBackgroundUI(self, layout):
        """Creates the UI elements for setting the viewport
        background color (options to choose from colormap)

        Args:
            layout (QtGui.QGridLayout): where the widgets should
                be attached.
        """
        try:
            # Get the current color configuration
            current_color = self.current_config["Viewport/Color"]

            # Creates the UI elements (Label and ComboBox)
            label_color = QLabel("Background Color")
            widget_color = QComboBox()
            widget_color.addItems(colors.keys())
            widget_color.setCurrentIndex(list(colors.keys()).index(current_color))
            widget_color.currentTextChanged[str].connect(self.setupViewportColor)

            # Add the widgets to the layout
            layout.addWidget(label_color)
            layout.addWidget(widget_color)
        except Exception as e:
            warnings.warn(str(e))

    def lengthUnitsUI(self, layout):
        """Creates the UI elements for setting the program-wide
        length units (options to choose from length dictionary)

        Args:
            layout (QtGui.QGridLayout): where the widgets should
                be attached.
        """
        try:
            # Get the current color configuration
            current_length = self.current_config["Units/Length"]

            # Creates the UI elements (Label and ComboBox)
            label_length = QLabel("Length units")
            widget_length = QComboBox()
            widget_length.addItems(length.keys())
            widget_length.setCurrentIndex(list(length.keys()).index(current_length))
            widget_length.currentTextChanged[str].connect(self.setupLength)

            # Add the widgets to the layout
            layout.addWidget(label_length)
            layout.addWidget(widget_length)
        except Exception as e:
            warnings.warn(str(e))

    def setupViewportColor(self, c):
        """Updates the current config variable,
        with the selected color in the ComboBox (UI)

        Args:
            c (str): string identifying the color (see keys in
                the dictionary 'colors')
        """
        self.current_config["Viewport/Color"] = c

    def setupLength(self, l):
        """Updates the current config variable,
        with the selected length unit in the ComboBox (UI)

        Args:
            c (str): string identifying the length unit (see keys in
                the dictionary 'length')
        """
        self.current_config["Units/Length"] = l

    def accept(self):
        # Sends the changes to the viewport
        self.apply_changes_viewport()

        # Update the configuration model with the local
        # copy of the configuration
        self.configurator.applyUserPreferences(self.current_config)

        # Saves the configuration model
        self.configurator.saveConfiguration()
        super().accept()

    def apply_changes_viewport(self):
        current_color = self.current_config["Viewport/Color"]
        rgb_color = colors[current_color]
        self.gui.viewport.change_background(rgb_color)
