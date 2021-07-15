# -*- coding: utf-8 -*-
# Created on Sun Jul 04 2021
# Last modified on Sun Jul 04 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from __future__ import annotations

from PyQt5.QtWidgets import (
    QLabel,
    QComboBox,
    QLineEdit,
    QListWidgetItem,
    QCheckBox,
    QListWidget,
)
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, Qt

from typing import Callable

from camos.utils.apptools import getModels

MAXNAMELEN = 20


class CreateGUI(QObject):
    def __init__(self, valueDict={}, parent=None, function: Callable | None = None):
        self.parent = parent
        self.function = function
        self.valueDict = valueDict
        self.updateEvents = []

    def creategui(self):
        # Check that everything is not None
        assert self.parent != None
        assert self.function != None

        # Add the UI elements to the indicated widget (parent)
        for a in self.function.__annotations__:
            field = self.function.__annotations__[a]
            field.var = a
            widget = field.createComponent()
            # Store the default values
            self.valueDict[a] = field.default
            # Connect the change in values to the updateValue method
            field.updatedValue.connect(lambda x, y: self.updateVar(x, y))
            # Add the widget label
            label = QLabel(field.name)
            self.parent.addWidget(label)
            # Add the widget of the field
            self.parent.addWidget(widget)

    def updateVar(self, value, a):
        self.valueDict[a] = value


class DefaultInput(QObject):
    updatedValue = pyqtSignal(object, str)

    def __init__(self, name=None, default=None, *args, **kwargs):
        super(DefaultInput, self).__init__(*args, **kwargs)
        self.name = name
        self.default = default
        self.value = False
        self.var = ""

    def createComponent(self) -> list:
        return []

    @pyqtSlot()
    def updateValue(self, value=None) -> None:
        if value == None:
            raise ValueError("No value was passed")
        self.value = value
        self.updatedValue.emit(value, self.var)


class NumericInput(DefaultInput):
    def createComponent(self):
        widget = QLineEdit()
        if self.default != None:
            widget.setText(str(self.default))
        widget.textChanged[str].connect(lambda v: self.updateValue(float(v)))
        return widget


class ImageInput(DefaultInput):
    def __init__(self, *args, **kwargs):
        self.model, _ = getModels()
        super(ImageInput, self).__init__(*args, **kwargs)

    def createComponent(self):
        widget = QComboBox()
        widget.currentIndexChanged[int].connect(lambda x: self.updateValue(x))
        images = self.model.list_images()
        if images is not None:
            for i, name in enumerate(images):
                _s_name = name if len(name) < MAXNAMELEN else name[0:MAXNAMELEN] + "..."
                widget.addItem(_s_name, name)
                widget.setItemData(i, name, Qt.ToolTipRole)

        return widget


class DatasetInput(DefaultInput):
    def __init__(self, *args, **kwargs):
        _, self.model = getModels()
        super(DatasetInput, self).__init__(*args, **kwargs)

    def createComponent(self):
        widget = QComboBox()
        widget.currentIndexChanged[int].connect(lambda x: self.updateValue(x))
        data = self.model.list_datasets()
        if data is not None:
            for i, name in enumerate(data):
                _s_name = name if len(name) < MAXNAMELEN else name[0:MAXNAMELEN] + "..."
                widget.addItem(_s_name, name)
                widget.setItemData(i, name, Qt.ToolTipRole)

        return widget


class CustomComboInput(DefaultInput):
    def __init__(self, items: list = [], *args, **kwargs):
        self.items = items
        super(CustomComboInput, self).__init__(*args, **kwargs)

    def createComponent(self):
        widget = QComboBox()
        data = self.items
        widget.currentIndexChanged[int].connect(lambda x: self.updateValue(x))
        if data is not None:
            for i, name in enumerate(data):
                _s_name = name if len(name) < MAXNAMELEN else name[0:MAXNAMELEN] + "..."
                widget.addItem(_s_name)
                widget.setItemData(i, name, Qt.ToolTipRole)

        return widget


class DatasetList(DefaultInput):
    updatedValue = pyqtSignal(object, str)

    def __init__(self, *args, **kwargs):
        _, self.model = getModels()
        super(DatasetList, self).__init__(*args, **kwargs)

    def createComponent(self):
        widget = ThumbListWidget()
        for method in self.model.list_datasets():
            item = QListWidgetItem(method)
            item.setCheckState(Qt.Unchecked)
            widget.addItem(item)
        widget.itemSelectionChanged.connect(lambda: self.updateValue(widget))

        return widget

    @pyqtSlot()
    def updateValue(self, widget) -> None:
        self.value = []
        for i, _ in widget.checkedItems():
            self.value.append(i)
        self.updatedValue.emit(self.value, self.var)


class CheckboxInput(DefaultInput):
    def createComponent(self):
        widget = QCheckBox(self.name)
        widget.stateChanged[int].connect(lambda x: self.updateValue(x))
        widget.setChecked(self.default)

        return widget


class ThumbListWidget(QListWidget):
    def checkedItems(self):
        for index in range(self.count()):
            item = self.item(index)
            if item.checkState() == Qt.Checked:
                yield index, item
