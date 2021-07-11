from PyQt5 import QtCore, QtGui, QtWidgets

import logging
import sys

import camos.utils.errormessages as cfgexception
import camos.utils.apptools as apptools

__docformat__ = "restructuredtext"
__version__ = "0.1a"

translate = QtWidgets.QApplication.translate


def getVersion():
    """The application version."""
    return __version__


log = logging.getLogger(__name__)


class Config(QtCore.QSettings):
    def __init__(self):
        """
        Windows, settings stored in the registry
        under HKCU\Software\camos\__version__ key
        macOS saves settings in a plist stored in a
        standard location
        """

        organization = QtWidgets.qApp.organizationName()
        product = QtWidgets.qApp.applicationName()
        version = QtWidgets.qApp.applicationVersion()

        if sys.platform.startswith("win"):
            super(Config, self).__init__(product, version)
            self.reg_path = "HKEY_CURRENT_USER\\Software\\{0}\\{1}".format(
                product, version
            )
            self.setPath(
                QtCore.QSettings.NativeFormat,
                QtCore.QSettings.UserScope,
                self.reg_path,
            )
        elif sys.platform.startswith("darwin"):
            super(Config, self).__init__(product, version)
        else:
            arg1 = organization
            arg2 = "-".join((product, version))
            super(Config, self).__init__(arg1, arg2)

        self.setFallbacksEnabled(False)

        styles = QtWidgets.QStyleFactory.keys()
        if "Fusion" in styles:
            self.default_style = "Fusion"
        else:
            self.default_style = styles[0]
        self.camosApp = apptools.getApp()
        """
        if not (self.camosApp is None):
            style_name = self.camosApp.gui.style().objectName()
            for item in styles:
                if item.lower() == style_name:
                    self.default_style = item
                    break
        """

    def readStyle(self):
        """Returns the current application style."""

        # The property key and its default value
        key = "Look/currentStyle"
        default_value = self.default_style

        # Read the entry from the configuration file/registry
        setting_value = self.value(key)

        # Check the entry format and value
        styles = QtWidgets.QStyleFactory.keys()
        if not isinstance(setting_value, str):
            return default_value
        elif setting_value not in styles:
            return default_value
        else:
            return setting_value

    def windowPosition(self):
        """
        Returns the main window geometry settings.
        Basically the main window geometry is made of the x and y coordinates
        of the top left corner, width and height. A QByteArray with all this
        information can be created via QMainWindow.saveGeometry() and stored
        in a setting with QSetting.setValue()
        """

        key = "Geometry/Position"
        default_value = None
        setting_value = self.value(key)
        if isinstance(setting_value, QtCore.QByteArray):
            return setting_value
        else:
            return default_value

    def windowLayout(self):
        """
        Returns the main window layout setting.
        This setting stores the position and size of toolbars and
        dockwidgets.
        """

        key = "Geometry/Layout"
        default_value = None
        setting_value = self.value(key)
        if isinstance(setting_value, QtCore.QByteArray):
            return setting_value
        else:
            return default_value

    def enabledPlugins(self):
        """Returns the list of enabled plugins.
        """

        key = "Plugins/Enabled"
        default_value = []
        setting_value = self.value(key)
        if isinstance(setting_value, list):
            return setting_value
        else:
            return default_value

    def viewportColor(self):
        """Returns the color of the viewport
        """

        key = "Viewport/Color"
        default_value = "Black"
        setting_value = self.value(key)
        if isinstance(setting_value, str):
            return setting_value
        else:
            return default_value

    def unitsLength(self):
        """Returns the program-wise units of length
        """

        key = "Units/Length"
        default_value = "Microns"
        setting_value = self.value(key)
        if isinstance(setting_value, str):
            return setting_value
        else:
            return default_value

    def unitsTime(self):
        """Returns the program-wise units of time
        """

        key = "Units/Time"
        default_value = "Seconds"
        setting_value = self.value(key)
        if isinstance(setting_value, str):
            return setting_value
        else:
            return default_value

    def writeValue(self, key, value):
        """
        Write an entry to the configuration file.
        :Parameters:
        - `key`: the name of the property we want to set.
        - `value`: the value we want to assign to the property
        """

        try:
            self.setValue(key, value)
            if self.status():
                raise cfgexception.ConfigFileIOException("{0}={1}".format(key, value))
        except cfgexception.ConfigFileIOException as inst:
            log.error(inst.error_message)

    def readConfiguration(self):
        """
        Get the application configuration currently stored on disk.
        Read the configuration from the stored settings. If a setting
        cannot be read (as it happens when the package is just
        installed) then its default value is returned.
        Geometry and Recent settings are returned as lists, color
        settings as QColor instances. The rest of settings are returned
        as strings or integers.
        :Returns: a dictionary with the configuration stored on disk
        """

        config = {}
        config["Geometry/Position"] = self.windowPosition()
        config["Geometry/Layout"] = self.windowLayout()
        config["Look/currentStyle"] = self.readStyle()
        config["Plugins/Enabled"] = self.enabledPlugins()
        config["Viewport/Color"] = self.viewportColor()
        config["Units/Length"] = self.unitsLength()
        config["Units/Time"] = self.unitsTime()
        return config

    def applyConfiguration(self, config, gui):
        """
        Configure the application with the given settings.
        We call `user settings` to those settings that can be setup via
        Settings dialog and `internal settings` to the rest of settings.
        At startup all settings will be loaded. At any time later the
        `users settings` can be explicitly changed via Settings dialog.
        :Parameter config: a dictionary with the settings to be (re)loaded
        """

        # Load the user settings
        self.applyUserPreferences(config)

        # Load the internal settings (if any)
        try:
            key = "Geometry/Position"
            value = config[key]
            if isinstance(value, QtCore.QByteArray):
                # Default position is provided by the underlying window manager
                gui.restoreGeometry(value)

            key = "Geometry/Layout"
            value = config[key]
            if isinstance(value, QtCore.QByteArray):
                # Default layout is provided by the underlying Qt installation
                gui.restoreState(value)

        except KeyError:
            pass

    def applyUserPreferences(self, config):
        """Apply settings that can be setup via Settings dialog.
        :Parameter config: a dictionary with the settings to be (re)loaded
        """
        key = "Look/currentStyle"
        if key in config:
            self.current_style = config[key]
            # Default style is provided by the underlying window manager
            QtWidgets.qApp.setStyle(self.current_style)

        key = "Plugins/Enabled"
        if key in config:
            self.enabled_plugins = config[key]

        key = "Viewport/Color"
        if key in config:
            self.viewport_color = config[key]

        key = "Units/Length"
        if key in config:
            self.units_length = config[key]

        key = "Units/Time"
        if key in config:
            self.units_time = config[key]

    def saveConfiguration(self):
        """
        Store current application settings on disk.
        Note that we are using ``QSettings`` for writing to the config file,
        so we **must** rely on its searching algorithms in order to find
        that file.
        """

        camosGUI = apptools.getGui()
        # Style
        # self.writeValue("Look/currentStyle", self.current_style)
        # Window geometry
        self.writeValue("Geometry/Position", camosGUI.saveGeometry())
        # The list of enabled plugins
        # self.writeValue("Plugins/Enabled", self.camosApp.plugins_mgr.enabled_plugins)
        # The current background color
        self.writeValue("Viewport/Color", self.viewport_color)
        self.writeValue("Units/Length", self.units_length)
        self.writeValue("Units/Time", self.units_time)
        self.sync()
