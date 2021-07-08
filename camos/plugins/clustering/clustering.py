# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5.QtGui import QIntValidator, QDoubleValidator

import numpy as np

from camos.tasks.analysis import Analysis


class Correlation(Analysis):
    analysis_name = "Cluster Data"

    def __init__(self, model=None, parent=None, signal=None):
        super(Correlation, self).__init__(model, parent, input, name=self.analysis_name)
        self.model = model
        self.signal = signal
        self.methods = {
            "K-means": self.k_means,
            "DBSCAN": self.dbscan,
            "Agglomerative Clustering": self.agglomerative,
            "Gaussian Mixture": self.gaussian_mixture,
        }
        self.method = None

    def _run(self):
        # Load the input data
        self._set_data()
        nclust = int(self.nclust.text())
        eps = float(self.eps.text())
        min_samples = float(self.minsamples.text())

        # Complete input data
        data = self.data

        if len(data) < 1:
            raise ValueError("Dataset is empty")

        ROIs = np.unique(data[0][:]["CellID"])

        # Define the output data
        output_type = [("CellID", "int"), ("Cluster", "int")]
        self.output = np.zeros(shape=(len(ROIs), 1), dtype=output_type)

        X = np.zeros(len(ROIs))
        # Merge all selected datasets
        for d in data:
            for n in d.dtype.names:
                if n != "CellID":
                    # Merge new column
                    X = np.vstack((X, d[n][:, 0]))

        _labels = self.method(X.T, n=nclust, eps=eps, min_samples=min_samples) + 1

        self.output[:]["CellID"] = ROIs.reshape(-1, 1)
        self.output[:]["Cluster"] = _labels.reshape(-1, 1)

        self.finished.emit()

    def k_means(self, X, n=15, **kwargs):
        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n, random_state=0).fit(X)
        return kmeans.labels_

    def dbscan(self, X, eps=0.3, min_samples=10, **kwargs):
        from sklearn.cluster import DBSCAN

        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        return db.labels_

    def agglomerative(self, X, **kwargs):
        from sklearn.cluster import AgglomerativeClustering

        clustering = AgglomerativeClustering().fit(X)
        return clustering.labels_

    def gaussian_mixture(self, X, n, **kwargs):
        from sklearn.mixture import GaussianMixture

        gm = GaussianMixture(n_components=2, random_state=0).fit_predict(X)
        return gm.labels_

    def display(self):
        if type(self.signal.list_datasets()) is type(None):
            # Handle error that there are no images
            return
        self._initialize_UI()
        self.initialize_UI()
        self._final_initialize_UI()

    def initialize_UI(self):
        self.masklabel = QLabel("Mask image", self.dockUI)
        self.cbmask = QComboBox()
        self.cbmask.currentIndexChanged.connect(self._set_mask)
        self.cbmask.addItems(self.model.list_images())

        self.datalabel = QLabel("Source datasets to cluster", self.dockUI)
        self.datalist = ThumbListWidget()
        for method in self.signal.list_datasets():
            item = QListWidgetItem(method)
            item.setCheckState(Qt.Unchecked)
            self.datalist.addItem(item)

        self.methodlabel = QLabel("Clustering method", self.dockUI)
        self.cbmethod = QComboBox()
        self.cbmethod.currentIndexChanged.connect(self._set_method)
        self.cbmethod.addItems(self.methods.keys())

        self.onlyInt = QIntValidator()
        self.nclust_label = QLabel("# of clusters", self.parent)
        self.nclust = QLineEdit()
        self.nclust.setValidator(self.onlyInt)
        self.nclust.setText("5")
        self.layout.addWidget(self.nclust_label)
        self.layout.addWidget(self.nclust)

        self.onlyFloat = QDoubleValidator()
        self.eps_label = QLabel("eps (DBSCAN only)", self.parent)
        self.eps = QLineEdit()
        self.eps.setValidator(self.onlyFloat)
        self.eps.setText("0.3")
        self.layout.addWidget(self.eps_label)
        self.layout.addWidget(self.eps)

        self.minsamples_label = QLabel("Min Samples (DBSCAN only)", self.parent)
        self.minsamples = QLineEdit()
        self.minsamples.setValidator(self.onlyInt)
        self.minsamples.setText("10")
        self.layout.addWidget(self.minsamples_label)
        self.layout.addWidget(self.minsamples)

        self.layout.addWidget(self.masklabel)
        self.layout.addWidget(self.cbmask)
        self.layout.addWidget(self.datalabel)
        self.layout.addWidget(self.datalist)
        self.layout.addWidget(self.methodlabel)
        self.layout.addWidget(self.cbmethod)

    def _set_method(self, index):
        self.methodname = list(self.methods.keys())[index]
        self.method = self.methods[self.methodname]

    def _set_mask(self, index):
        self.mask = self.model.images[index]._image

    def _set_data(self):
        self.data = []
        for i, item in self.datalist.checkedItems():
            self.data.append(self.signal.data[i])

    def _plot(self):
        mask = self.mask
        clust_dict = {}
        for i in range(1, self.foutput.shape[0]):
            clust_dict[int(self.foutput[i]["CellID"][0])] = self.foutput[i]["Cluster"][
                0
            ]

        k = np.array(list(clust_dict.keys()))
        v = np.array(list(clust_dict.values()))

        dim = max(k.max(), np.max(mask))
        mapping_ar = np.zeros(dim + 1, dtype=v.dtype)
        mapping_ar[k] = v
        clust_mask = mapping_ar[mask]

        self.outputimage = clust_mask

        im = self.plot.axes.imshow(clust_mask, cmap="inferno", origin="upper")
        self.plot.fig.colorbar(im, ax=self.plot.axes)
        self.plot.axes.set_ylabel("Y coordinate")
        self.plot.axes.set_xlabel("X coordinate")


class ThumbListWidget(QtGui.QListWidget):
    def checkedItems(self):
        for index in range(self.count()):
            item = self.item(index)
            if item.checkState() == Qt.Checked:
                yield index, item
