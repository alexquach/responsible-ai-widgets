# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.

import logging
import pytest

from unittest.mock import MagicMock

from .common_utils import (create_iris_data,
                           create_cancer_data,
                           create_binary_classification_dataset,
                           create_lightgbm_classifier)

from responsibleai.modelanalysis.model_analysis import ModelAnalysis
from responsibleai.exceptions import UserConfigValidationException


class TestModelAnalysisValidations:
    def test_validate_unsupported_task_type(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_iris_data()

        model = create_lightgbm_classifier(X_train, y_train)
        X_train['target'] = y_train
        X_test['target'] = y_test

        message = ("Unsupported task type 'regre'. "
                   "Should be one of \\['classification', 'regression'\\]")
        with pytest.raises(UserConfigValidationException, match=message):
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='regre')

    def test_validate_bad_target_name(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_iris_data()

        model = create_lightgbm_classifier(X_train, y_train)
        X_train['target'] = y_train
        X_test['target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='bad_target',
                task_type='classification')
        assert "Target name bad_target not present in train/test data" in \
            str(ucve.value)

    def test_validate_categorical_features_having_target(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_iris_data()

        model = create_lightgbm_classifier(X_train, y_train)
        X_train['target'] = y_train
        X_test['target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                categorical_features=['target'])
        assert 'Found target name target in categorical feature list' in \
            str(ucve.value)

    def test_validate_categorical_features_not_having_train_features(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_iris_data()

        model = create_lightgbm_classifier(X_train, y_train)
        X_train['target'] = y_train
        X_test['target'] = y_test

        message = ("Feature names in categorical_features "
                   "do not exist in train data: \\['not_a_feature'\\]")
        with pytest.raises(UserConfigValidationException, match=message):
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                categorical_features=['not_a_feature'])

    def test_validate_serializer(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_cancer_data()
        model = create_lightgbm_classifier(X_train, y_train)

        X_train['target'] = y_train
        X_test['target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            class LoadOnlySerializer:
                def __init__(self, logger=None):
                    self._logger = logger

                def load(self):
                    pass

            serializer = LoadOnlySerializer()
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                serializer=serializer
            )
        assert 'The serializer does not implement save()' in str(ucve.value)

        with pytest.raises(UserConfigValidationException) as ucve:
            class SaveOnlySerializer:
                def __init__(self, logger=None):
                    self._logger = logger

                def save(self):
                    pass

            serializer = SaveOnlySerializer()
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                serializer=serializer
            )
        assert 'The serializer does not implement load()' in str(ucve.value)

        with pytest.raises(UserConfigValidationException) as ucve:
            class Serializer:
                def __init__(self, logger=None):
                    self._logger = logger

                def save(self):
                    pass

                def load(self):
                    pass

            serializer = Serializer(logger=logging.getLogger('some logger'))

            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                serializer=serializer
            )
        assert 'The serializer should be serializable via pickle' in \
            str(ucve.value)

    def test_model_predictions_predict(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_cancer_data()

        X_train['target'] = y_train
        X_test['target'] = y_test

        model = MagicMock()
        model.predict.side_effect = Exception()
        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification')

        assert 'The model passed cannot be used for getting predictions ' + \
            'via predict()' in str(ucve.value)

    def test_model_predictions_predict_proba(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_cancer_data()

        X_train['target'] = y_train
        X_test['target'] = y_test

        model = MagicMock()
        model.predict.return_value = [0]
        model.predict_proba.side_effect = Exception()

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification')

        assert 'The model passed cannot be used for getting predictions ' + \
            'via predict_proba()' in str(ucve.value)

    def test_mismatch_train_test_features(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_cancer_data()
        model = create_lightgbm_classifier(X_train, y_train)

        X_train['target'] = y_train
        X_test['bad_target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification')
        assert 'The features in train and test data do not match' in \
            str(ucve.value)

    def test_train_labels(self):
        X_train, X_test, y_train, y_test, _, _ = \
            create_cancer_data()
        model = create_lightgbm_classifier(X_train, y_train)

        X_train['target'] = y_train
        X_test['target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                train_labels=[0, 1, 2])
        assert 'The train labels and distinct values in ' + \
            'target (train data) do not match' in str(ucve.value)

        y_train[0] = 2
        X_train['target'] = y_train
        X_test['target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                train_labels=[0, 1])
        assert 'The train labels and distinct values in target ' + \
            '(train data) do not match' in str(ucve.value)

        y_train[0] = 0
        y_test[0] = 2
        X_train['target'] = y_train
        X_test['target'] = y_test

        with pytest.raises(UserConfigValidationException) as ucve:
            ModelAnalysis(
                model=model,
                train=X_train,
                test=X_test,
                target_column='target',
                task_type='classification',
                train_labels=[0, 1])

        assert 'The train labels and distinct values in target ' + \
            '(test data) do not match' in str(ucve.value)


class TestFeatureNameListValidations:

    def test_treatment_features_list_not_having_train_features(self):
        X_train, y_train, X_test, y_test, _ = \
            create_binary_classification_dataset()

        model = create_lightgbm_classifier(X_train, y_train)
        X_train['target'] = y_train
        X_test['target'] = y_test

        model_analysis = ModelAnalysis(
            model=model,
            train=X_train,
            test=X_test,
            target_column='target',
            task_type='classification')

        message = ("Feature names in treatment_features "
                   "do not exist in train data: \\['not_a_feature'\\]")
        with pytest.raises(UserConfigValidationException, match=message):
            model_analysis.causal.add(treatment_features=['not_a_feature'])

    def test_features_to_vary_list_not_having_train_features(self):
        X_train, y_train, X_test, y_test, _ = \
            create_binary_classification_dataset()

        model = create_lightgbm_classifier(X_train, y_train)
        X_train['target'] = y_train
        X_test['target'] = y_test

        model_analysis = ModelAnalysis(
            model=model,
            train=X_train,
            test=X_test,
            target_column='target',
            task_type='classification')

        message = ("Feature names in features_to_vary do "
                   "not exist in train data: \\['not_a_feature'\\]")
        with pytest.raises(UserConfigValidationException, match=message):
            model_analysis.counterfactual.add(
                total_CFs=10, features_to_vary=['not_a_feature'])
