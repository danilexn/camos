# -*- coding: utf-8 -*-
# Created on Sat Jun 05 2021
# Last modified on Mon Jun 07 2021
# Copyright (c) CaMOS Development Team. All Rights Reserved.
# Distributed under a MIT License. See LICENSE for more info.
import numpy as np

from camos.tasks.analysis import Analysis
from camos.utils.generategui import (
    NumericInput,
    DatasetList,
    CustomComboInput,
    ImageInput,
)


class Correlation(Analysis):
    analysis_name = "Cluster Data"
    required = ["dataset"]

    def __init__(self, *args, **kwargs):
        super(Correlation, self).__init__(*args, **kwargs)
        self.methods = {
            "K-means": self.k_means,
            "DBSCAN": self.dbscan,
            "Agglomerative Clustering": self.agglomerative,
            "Gaussian Mixture": self.gaussian_mixture,
        }
        self.method = None

    def _run(
        self,
        nclust: NumericInput("# of clusters", 5),
        eps: NumericInput("eps (DBSCAN only)", 0.3),
        min_samples: NumericInput("Min Samples (DBSCAN only)", 10),
        _i_data: DatasetList("Input Datasets to Cluster", 0),
        _i_mask: ImageInput("Mask", 0),
        method: CustomComboInput(
            ["K-means", "DBSCAN", "Agglomerative Clustering", "Gaussian Mixture"],
            "Clustering Method",
            0,
        ),
    ):
        data = []
        for i in _i_data:
            data.append(self.signal.data[i])

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

        method_fun = self.methods[list(self.methods.keys())[method]]
        _labels = method_fun(X.T, n=nclust, eps=eps, min_samples=min_samples) + 1

        self.output[:]["CellID"] = ROIs.reshape(-1, 1)
        self.output[:]["Cluster"] = _labels.reshape(-1, 1)
        self.mask = self.model.images[_i_mask].image(0)

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
