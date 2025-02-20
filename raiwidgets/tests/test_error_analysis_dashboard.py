# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.

from sklearn.model_selection import train_test_split
import shap
import sklearn
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from raiwidgets import ErrorAnalysisDashboard
from interpret_community.common.constants import ModelTask
from interpret.ext.blackbox import MimicExplainer
from interpret.ext.glassbox import LGBMExplainableModel


class TestErrorAnalysisDashboard:
    def test_error_analysis_adult_census(self):
        X, y = shap.datasets.adult()
        y = [1 if r else 0 for r in y]

        X, y = sklearn.utils.resample(
            X, y, n_samples=1000, random_state=7, stratify=y)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=7, stratify=y)

        knn = sklearn.neighbors.KNeighborsClassifier()
        knn.fit(X_train, y_train)

        model_task = ModelTask.Classification
        explainer = MimicExplainer(knn,
                                   X_train,
                                   LGBMExplainableModel,
                                   augment_data=True,
                                   max_num_of_augmentations=10,
                                   model_task=model_task)
        global_explanation = explainer.explain_global(X_test)

        categorical_features = ['Workclass',
                                'Education-Num',
                                'Marital Status',
                                'Occupation',
                                'Relationship',
                                'Race',
                                'Sex',
                                'Country']
        ErrorAnalysisDashboard(global_explanation,
                               knn,
                               dataset=X_test,
                               true_y=y_test,
                               categorical_features=categorical_features)

    def test_error_analysis_many_rows(self):
        X, y = make_classification(n_samples=110000)

        # Split data into train and test
        X_train, X_test, y_train, y_test = train_test_split(X,
                                                            y,
                                                            test_size=0.2,
                                                            random_state=0)
        classes = np.unique(y_train).tolist()
        feature_names = ["col" + str(i) for i in list(range(X_train.shape[1]))]
        X_train = pd.DataFrame(X_train, columns=feature_names)
        X_test = pd.DataFrame(X_test, columns=feature_names)
        knn = sklearn.neighbors.KNeighborsClassifier()
        knn.fit(X_train, y_train)
        ErrorAnalysisDashboard(model=knn, dataset=X_test,
                               true_y=y_test, classes=classes)
