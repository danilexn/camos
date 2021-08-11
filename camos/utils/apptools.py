# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

import collections
import functools
import platform
import sys
import os
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets

OS_RELEASE_PATH = "/etc/os-release"


def getCamosApp():
    """Get a reference to the `camosApp` instance.
    This is useful namely for plugins.
    """

    camosApp = None
    widgets = QtWidgets.QApplication.instance().allWidgets()
    for widget in widgets:
        if str(widget.objectName()) == "camosGUI":
            camosApp = widget.camosApp
            break

    return camosApp


def getApp():
    return getCamosApp()


def getGui():
    """Small wrapper to hide the fact that camosApp object contains gui.
    :return: main window object
    """
    try:
        return getApp().gui
    except:
        pass


def getModels():
    """Small wrapper to hide that camosApp.gui object contains dbs_tree_model.
    :return: the DBs tree model
    """
    return getGui().model, getGui().signalmodel


def getViews():
    """Small wrapper to hide that camosApp.gui object contains dbs_tree_view.
    :return: the DBs tree view
    """
    return getGui().viewport


def long_action(message=None):
    """Decorator that changes the cursor to the wait cursor.
    Used with functions that take some time finish. The provided
    message is displayed in the status bar while the function is
    running (the status bar is cleaned afterwards). If the message is
    not provided then the status bar is not updated.
    :parameter message: string to display in status bar
    """

    def _long_action(f):
        @functools.wraps(f)
        def __long_action(*args, **kwargs):
            status_bar = getGui().statusBar()
            if message is not None:
                status_bar.showMessage(message)
            QtWidgets.QApplication.setOverrideCursor(
                QtGui.QCursor(QtCore.Qt.WaitCursor)
            )
            try:
                res = f(*args, **kwargs)
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
                if message is not None:
                    status_bar.clearMessage()
            return res

        return __long_action

    return _long_action


def insertInMenu(menu, entries, uid):
    """Insert entries to the given menu before the action named uid.
    The function accept a QAction/QMenu or an iterable. The entries will
    be added before the action whose name is uid.
    :Parameters:
    - `menu`: the menu or context menu being updated
    - `entries`: QAction/Qmenu object or a list of such objects
    - `uid`: indicates the insertion position for the new entries
    :return: None
    """

    if not isinstance(entries, collections.Iterable):
        entries = [entries]

    if isinstance(entries[0], QtWidgets.QAction):
        menu.insertEntry = menu.insertAction
    elif isinstance(entries[0], QtWidgets.QMenu):
        menu.insertEntry = menu.insertMenu

    for item in menu.actions():
        if item.objectName() == uid:
            for a in entries:
                qa = menu.insertEntry(item, a)


def addToMenu(menu, entries):
    """Add entries at the end of the given menu.
    The function accept a QAction/QMenu or an iterable. Entries will be
    preceded with a separator and added at the end of the menu.
    :Parameters:
    - `menu`: the menu or context menu being updated
    - `entries`: QAction/QMenu object or a list of such objects
    :return: None
    """

    if not isinstance(entries, collections.Iterable):
        entries = [entries]

    if isinstance(entries[0], QtWidgets.QAction):
        menu.addEntry = menu.addAction
    elif isinstance(entries[0], QtWidgets.QMenu):
        menu.addEntry = menu.addMenu

    menu.addSeparator()
    for a in entries:
        menu.addEntry(a)


def addActions(target, actions, actions_dict):
    """Add a list of QActions to a menu or a toolbar.
    This is a helper function which make easier to add QActions to a
    menu or a toolbar. Separators and submenus are also handled by this
    method.
    :Parameters:
    - `target`: the menu or toolbar where actions will be added
    - `actions`: a sequence of keywords/None/QMenu used to get actions
                 from a mapping
    - `actions_dict`: a mapping of actions
    """

    for action in actions:
        if action is None:
            target.addSeparator()
        elif isinstance(action, QtWidgets.QMenu):
            target.addMenu(action)
        else:
            target.addAction(actions_dict[action])


# modified from napari source
def sys_info(as_html=False):
    from camos.utils.pluginmanager import plugins

    """Gathers relevant module versions for troubleshooting purposes.
    Parameters
    ----------
    as_html : bool
        if True, info will be returned as HTML, suitable for a QTextEdit widget
    """

    VERSION = "0.1a"

    sys_version = sys.version.replace("\n", " ")
    text = f"<b>CaMOS</b>: {VERSION}<br>" f"<b>Platform</b>: {platform.platform()}<br>"

    __sys_name = _sys_name()
    if __sys_name:
        text += f"<b>System</b>: {__sys_name}<br>"

    text += f"<b>Python</b>: {sys_version}<br>"

    try:
        from qtpy import API_NAME, PYQT_VERSION, PYSIDE_VERSION, QtCore

        if API_NAME == "PySide2":
            API_VERSION = PYSIDE_VERSION
        elif API_NAME == "PyQt5":
            API_VERSION = PYQT_VERSION
        else:
            API_VERSION = ""

        text += (
            f"<b>Qt</b>: {QtCore.__version__}<br>"
            f"<b>{API_NAME}</b>: {API_VERSION}<br>"
        )

    except Exception as e:
        text += f"<b>Qt</b>: Import failed ({e})<br>"

    modules = (
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("pyqtgraph", "PyQtGraph"),
    )

    loaded = {}
    for module, name in modules:
        try:
            loaded[module] = __import__(module)
            text += f"<b>{name}</b>: {loaded[module].__version__}<br>"
        except Exception as e:
            text += f"<b>{name}</b>: Import failed ({e})<br>"

    # Information about plugins
    loaded = {}
    text += "<br><b>Plugins</b>:<br>"
    for module in plugins:
        try:
            name = module.__name__
            loaded[name] = __import__(name)
            text += f"<b>{name}</b>: {loaded[name].__version__}<br>"
        except Exception as e:
            text += f"<b>{name}</b>: Import failed ({e})<br>"

    text += "<br><b>Screens:</b><br>"

    try:
        from qtpy.QtGui import QGuiApplication

        screen_list = QGuiApplication.screens()
        for i, screen in enumerate(screen_list, start=1):
            text += f"  - screen {i}: resolution {screen.geometry().width()}x{screen.geometry().height()}, scale {screen.devicePixelRatio()}<br>"
    except Exception as e:
        text += f"  - failed to load screen information {e}"

    if not as_html:
        text = text.replace("<br>", "\n").replace("<b>", "").replace("</b>", "")
    return text


# modified from napari source
def _linux_sys_name():
    """
    Try to discover linux system name base on /etc/os-release file or lsb_release command output
    https://www.freedesktop.org/software/systemd/man/os-release.html
    """
    if os.path.exists(OS_RELEASE_PATH):
        with open(OS_RELEASE_PATH) as f_p:
            data = {}
            for line in f_p:
                field, value = line.split("=")
                data[field.strip()] = value.strip().strip('"')
        if "PRETTY_NAME" in data:
            return data["PRETTY_NAME"]
        if "NAME" in data:
            if "VERSION" in data:
                return f'{data["NAME"]} {data["VERSION"]}'
            if "VERSION_ID" in data:
                return f'{data["NAME"]} {data["VERSION_ID"]}'
            return f'{data["NAME"]} (no version)'

    try:
        res = subprocess.run(
            ["lsb_release", "-d", "-r"], check=True, capture_output=True
        )
        text = res.stdout.decode()
        data = {}
        for line in text.split("\n"):
            key, val = line.split(":")
            data[key.strip()] = val.strip()
        version_str = data["Description"]
        if not version_str.endswith(data["Release"]):
            version_str += " " + data["Release"]
        return version_str
    except subprocess.CalledProcessError:
        pass
    return ""


# modified from napari source
def _sys_name():
    """
    Discover MacOS or Linux Human readable information. For Linux provide information about distribution.
    """
    try:
        if sys.platform == "linux":
            return _linux_sys_name()
        if sys.platform == "darwin":
            try:
                res = subprocess.run(
                    ["sw_vers", "-productVersion"], check=True, capture_output=True,
                )
                return f"MacOS {res.stdout.decode().strip()}"
            except subprocess.CalledProcessError:
                pass
    except Exception:
        pass
    return ""
