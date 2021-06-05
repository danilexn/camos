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

translate = QtWidgets.QApplication.translate


class ErrorMessages:
    def __init__(self, message="Generic error"):
        self.error_dialog = QtWidgets.QErrorMessage()
        self.error_dialog.showMessage(message)
        self.error_dialog._exec()


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

