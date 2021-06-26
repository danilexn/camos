# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.
# ERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
from PyQt5 import QtWidgets

translate = QtWidgets.QApplication.translate


class ErrorMessages:
    def __init__(self, message="Generic error"):
        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.showMessage(message)


class ConfigFileIOException(Exception):
    """Exception class for IO errors in the configuration file.
    :Parameter key:
        the configuration file key that cannot be read/written
    """

    def __init__(self, key):
        """Setup the configuration error messages that will be shown to user.
        """

        Exception.__init__(self)
        # If key looks like /path/to/property=value a write exception is
        # raised. If not a read exception is raised
        if "=" in key:
            setting = key.split("=")[0]
            self.error_message = translate(
                "ConfigFileIOException",
                """\nConfiguration error: the application setting """
                """{0} cannot be saved.""",
                "A logger error message",
            ).format(setting)
        else:
            self.error_message = translate(
                "ConfigFileIOException",
                """\nConfiguration warning: the application setting """
                """{0} cannot be read. Its default value will be used.""",
                "A logger error message",
            ).format(key)
