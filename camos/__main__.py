# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import signal
import sys
import locale
import os
import traceback

from PyQt5 import QtWidgets, QtCore
from darktheme.widget_template import DarkPalette

from camos.app import camosApp
import camos.utils.settings as settings
import camos.utils.apptools
from camos.utils.errormessages import ErrorMessages
from camos.gui.notification import NapariQtNotification
from camos.utils.notifications import Notification

_I18N_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")

style = """
NapariQtNotification > QWidget {
  background: #303030;
}

NapariQtNotification::hover{
  background: {{ lighten(background, 5) }};
}

MultilineElidedLabel{
  background: none;
  color: {{ icon }};
  font-size: 12px;
}

NapariQtNotification #expand_button {
  background: none;
  padding: 0px;
  margin: 0px;
  max-width: 20px;
}

NapariQtNotification[expanded="false"] #expand_button {
  image: url(":/themes/{{ folder }}/chevron_up.svg");
}

NapariQtNotification[expanded="true"] #expand_button {
  image: url(":/themes/{{ folder }}/chevron_down.svg");
}


NapariQtNotification #close_button {
  background: none;
  image: url(":/themes/{{ folder }}/delete_shape.svg");
  padding: 0px;
  margin: 0px;
  max-width: 20px;
}

NapariQtNotification #source_label {
  color: {{ primary }};
  font-size: 11px;
}

NapariQtNotification #severity_icon {
  padding: 0;
  margin: 0 0 -3px 0;
  min-width: 20px;
  min-height: 18px;
  font-size: 15px;
  color: {{ icon }};
}
"""


def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    exit(0)


def _set_credentials(app):
    """Specify the organization's Internet domain.
    When the Internet domain is set, it is used on Mac OS X instead of
    the organization name, since Mac OS X applications conventionally
    use Internet domains to identify themselves
    """
    app.setOrganizationDomain("camos.org")
    app.setOrganizationName("camos")
    app.setApplicationName("camos")
    app.setApplicationVersion(settings.getVersion())


def _set_locale(app):
    """Set locale and load translation if available.
    Localize the application using the system locale numpy seems to
    have problems with decimal separator in some locales (catalan,
    german...) so C locale is always used for numbers.
    """
    locale.setlocale(locale.LC_ALL, "")
    locale.setlocale(locale.LC_NUMERIC, "C")

    locale_name = QtCore.QLocale.system().name()
    translator = QtCore.QTranslator()
    if translator.load("camos_" + locale_name, _I18N_PATH):
        app.installTranslator(translator)
    return translator


def excepthook(exc_type, exc_value, exc_tb):
    tb = "\n".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    # ErrorMessages(tb)
    error = Notification("\n; ".join([str(exc_value), tb]), "ERROR")
    NapariQtNotification.from_notification(error)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    sys.excepthook = excepthook
    app = QtWidgets.QApplication(sys.argv)
    _set_credentials(app)
    # translator = _set_locale(app)
    app.setStyle("Fusion")
    app.setPalette(DarkPalette())
    # setup stylesheet
    app.setStyleSheet(style)
    _app = camosApp()
    camosApp_second = camos.utils.apptools.getApp()
    sys.exit(app.exec_())
