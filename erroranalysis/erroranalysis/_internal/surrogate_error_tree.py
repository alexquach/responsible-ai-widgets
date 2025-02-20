# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier, LGBMRegressor
from enum import Enum
from erroranalysis._internal.cohort_filter import filter_from_cohort
from erroranalysis._internal.constants import (PRED_Y,
                                               TRUE_Y,
                                               ROW_INDEX,
                                               DIFF,
                                               SPLIT_INDEX,
                                               SPLIT_FEATURE,
                                               LEAF_INDEX,
                                               METHOD,
                                               METHOD_EXCLUDES,
                                               METHOD_INCLUDES,
                                               ModelTask,
                                               Metrics,
                                               metric_to_display_name,
                                               error_metrics)
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, median_absolute_error,
    r2_score, f1_score, precision_score, recall_score)

MODEL = 'model'
DEFAULT_MAX_DEPTH = 3
DEFAULT_NUM_LEAVES = 31


class TreeSide(str, Enum):
    """Provide model task constants.
    Can be 'classification', 'regression', or 'unknown'.

    By default the model domain is inferred if 'unknown',
    but this can be overridden if you specify
    'classification' or 'regression'.
    """

    RIGHT_CHILD = 'right_child'
    LEFT_CHILD = 'left_child'
    UNKNOWN = 'unknown'


def compute_json_error_tree(analyzer,
                            features,
                            filters,
                            composite_filters,
                            max_depth=DEFAULT_MAX_DEPTH,
                            num_leaves=DEFAULT_NUM_LEAVES):
    # Note: this is for backcompat for older versions
    # of raiwidgets pypi package
    return compute_error_tree(analyzer,
                              features,
                              filters,
                              composite_filters,
                              max_depth,
                              num_leaves)


def compute_error_tree(analyzer,
                       features,
                       filters,
                       composite_filters,
                       max_depth=DEFAULT_MAX_DEPTH,
                       num_leaves=DEFAULT_NUM_LEAVES):
    # Fit a surrogate model on errors
    if max_depth is None:
        max_depth = DEFAULT_MAX_DEPTH
    if num_leaves is None:
        num_leaves = DEFAULT_NUM_LEAVES
    is_model_analyzer = hasattr(analyzer, MODEL)
    if is_model_analyzer:
        filtered_df = filter_from_cohort(analyzer.dataset,
                                         filters,
                                         composite_filters,
                                         analyzer.feature_names,
                                         analyzer.true_y,
                                         analyzer.categorical_features,
                                         analyzer.categories)
    else:
        filtered_df = filter_from_cohort(analyzer.dataset,
                                         filters,
                                         composite_filters,
                                         analyzer.feature_names,
                                         analyzer.true_y,
                                         analyzer.categorical_features,
                                         analyzer.categories,
                                         analyzer.pred_y)
    row_index = filtered_df[ROW_INDEX]
    true_y = filtered_df[TRUE_Y]
    dropped_cols = [TRUE_Y, ROW_INDEX]
    if not is_model_analyzer:
        pred_y = filtered_df[PRED_Y]
        dropped_cols.append(PRED_Y)
    input_data = filtered_df.drop(columns=dropped_cols)
    is_pandas = isinstance(analyzer.dataset, pd.DataFrame)
    if is_pandas:
        true_y = true_y.to_numpy()
    else:
        input_data = input_data.to_numpy()
    if is_model_analyzer:
        pred_y = analyzer.model.predict(input_data)
    if analyzer.model_task == ModelTask.CLASSIFICATION:
        diff = pred_y != true_y
    else:
        diff = pred_y - true_y
    if not isinstance(diff, np.ndarray):
        diff = np.array(diff)
    if not isinstance(pred_y, np.ndarray):
        pred_y = np.array(pred_y)
    if not isinstance(true_y, np.ndarray):
        true_y = np.array(true_y)
    indexes = []
    for feature in features:
        indexes.append(analyzer.feature_names.index(feature))
    if is_pandas:
        input_data = input_data.to_numpy()

    if analyzer.categorical_features:
        # Inplace replacement of columns
        for idx, c_i in enumerate(analyzer.categorical_indexes):
            input_data[:, c_i] = analyzer.string_indexed_data[row_index, idx]
    dataset_sub_features = input_data[:, indexes]
    dataset_sub_names = np.array(analyzer.feature_names)[np.array(indexes)]
    dataset_sub_names = list(dataset_sub_names)

    categorical_info = get_categorical_info(analyzer,
                                            dataset_sub_names)
    cat_ind_reindexed, categories_reindexed = categorical_info

    surrogate = create_surrogate_model(analyzer,
                                       dataset_sub_features,
                                       diff,
                                       max_depth,
                                       num_leaves,
                                       cat_ind_reindexed)

    filtered_indexed_df = pd.DataFrame(dataset_sub_features,
                                       columns=dataset_sub_names)
    filtered_indexed_df[DIFF] = diff
    filtered_indexed_df[TRUE_Y] = true_y
    filtered_indexed_df[PRED_Y] = pred_y
    dumped_model = surrogate._Booster.dump_model()
    tree_structure = dumped_model["tree_info"][0]['tree_structure']
    max_split_index = get_max_split_index(tree_structure) + 1
    tree = traverse(filtered_indexed_df,
                    tree_structure,
                    max_split_index,
                    (categories_reindexed,
                     cat_ind_reindexed),
                    [],
                    dataset_sub_names,
                    metric=analyzer.metric)
    return tree


def create_surrogate_model(analyzer,
                           dataset_sub_features,
                           diff,
                           max_depth,
                           num_leaves,
                           cat_ind_reindexed):
    """Creates and fits the surrogate lightgbm model.

    :param analyzer: The error analyzer containing the categorical
        features and categories for the full dataset.
    :type analyzer: BaseAnalyzer
    :param dataset_sub_features: The subset of features to train the
        surrogate model on.
    :type dataset_sub_features: numpy.array or pandas.DataFrame
    :param diff: The difference between the true and predicted labels column.
    :type diff: numpy.array
    :param max_depth: The maximum depth of the surrogate tree trained
        on errors.
    :type max_depth: int
    :param num_leaves: The number of leaves of the surrogate tree
        trained on errors.
    :type num_leaves: int
    :param cat_ind_reindexed: The list of categorical feature indexes.
    :type cat_ind_reindexed: list[int]
    :return: The trained surrogate model.
    :rtype: LGBMClassifier or LGBMRegressor
    """
    if analyzer.model_task == ModelTask.CLASSIFICATION:
        surrogate = LGBMClassifier(n_estimators=1,
                                   max_depth=max_depth,
                                   num_leaves=num_leaves)
    else:
        surrogate = LGBMRegressor(n_estimators=1,
                                  max_depth=max_depth,
                                  num_leaves=num_leaves)
    if cat_ind_reindexed:
        surrogate.fit(dataset_sub_features, diff,
                      categorical_feature=cat_ind_reindexed)
    else:
        surrogate.fit(dataset_sub_features, diff)
    return surrogate


def get_categorical_info(analyzer, dataset_sub_names):
    """Returns the categorical information for the given feature names.

    :param analyzer: The error analyzer containing the categorical
        features and categories for the full dataset.
    :type analyzer: BaseAnalyzer
    :param dataset_sub_names: The subset of feature names to get the
        categorical indexes and names for.
    :type dataset_sub_names: list[str]
    :return: The categorical indexes and categories for the subset
        of features specified.
    :rtype: tuple[list]
    """
    cat_ind_reindexed = []
    categories_reindexed = []
    if analyzer.categorical_features:
        for c_index, feature in enumerate(analyzer.categorical_features):
            try:
                index_sub = dataset_sub_names.index(feature)
            except ValueError:
                continue
            cat_ind_reindexed.append(index_sub)
            categories_reindexed.append(analyzer.categories[c_index])
    return (cat_ind_reindexed, categories_reindexed)


def get_max_split_index(tree):
    if SPLIT_INDEX in tree:
        max_index = tree[SPLIT_INDEX]
        index1 = get_max_split_index(tree[TreeSide.LEFT_CHILD])
        index2 = get_max_split_index(tree[TreeSide.RIGHT_CHILD])
        return max(max(max_index, index1), index2)
    else:
        return 0


def traverse(df,
             tree,
             max_split_index,
             categories,
             dict,
             feature_names,
             parent=None,
             side=TreeSide.UNKNOWN,
             metric=None):
    if SPLIT_INDEX in tree:
        nodeid = tree[SPLIT_INDEX]
    elif LEAF_INDEX in tree:
        nodeid = max_split_index + tree[LEAF_INDEX]
    else:
        nodeid = 0

    # write current node to a dictionary that can be saved as json
    dict, df = node_to_dict(df, tree, nodeid, categories, dict,
                            feature_names, metric, parent, side)

    # write children to a dictionary that can be saved as json
    if 'leaf_value' not in tree:
        left_child = tree[TreeSide.LEFT_CHILD]
        right_child = tree[TreeSide.RIGHT_CHILD]
        dict = traverse(df, left_child, max_split_index,
                        categories, dict, feature_names,
                        tree, TreeSide.LEFT_CHILD, metric)
        dict = traverse(df, right_child, max_split_index,
                        categories, dict, feature_names,
                        tree, TreeSide.RIGHT_CHILD, metric)
    return dict


def create_categorical_arg(parent_threshold):
    return [float(i) for i in parent_threshold.split('||')]


def create_categorical_query(method, arg, p_node_name, parent, categories):
    if method == METHOD_INCLUDES:
        operation = "=="
    else:
        operation = "!="
    categorical_values = categories[0]
    categorical_indexes = categories[1]
    thresholds = []
    catcoli = categorical_indexes.index(parent[SPLIT_FEATURE])
    catvals = categorical_values[catcoli]
    for argi in arg:
        encoded_val = catvals[int(argi)]
        if not isinstance(encoded_val, str):
            encoded_val = str(encoded_val)
        thresholds.append(encoded_val)
    threshold_str = " | ".join(thresholds)
    condition = "{} {} {}".format(p_node_name, operation, threshold_str)
    query = []
    for argi in arg:
        query.append("`" + p_node_name + "` " + operation + " " + str(argi))
    if method == METHOD_INCLUDES:
        query = " | ".join(query)
    else:
        query = " & ".join(query)
    return query, condition


def node_to_dict(df, tree, nodeid, categories, json,
                 feature_names, metric, parent=None,
                 side=TreeSide.UNKNOWN):
    p_node_name = None
    condition = None
    arg = None
    method = None
    parentid = None
    if parent is not None:
        parentid = int(parent[SPLIT_INDEX])
        p_node_name = feature_names[parent[SPLIT_FEATURE]]
        parent_threshold = parent['threshold']
        parent_decision_type = parent['decision_type']
        if side == TreeSide.LEFT_CHILD:
            if parent_decision_type == '<=':
                method = "less and equal"
                arg = float(parent_threshold)
                condition = "{} <= {:.2f}".format(p_node_name,
                                                  parent_threshold)
                query = "`" + p_node_name + "` <= " + str(parent_threshold)
                df = df.query(query)
            elif parent_decision_type == '==':
                method = METHOD_INCLUDES
                arg = create_categorical_arg(parent_threshold)
                query, condition = create_categorical_query(method,
                                                            arg,
                                                            p_node_name,
                                                            parent,
                                                            categories)
                df = df.query(query)
        elif side == TreeSide.RIGHT_CHILD:
            if parent_decision_type == '<=':
                method = "greater"
                arg = float(parent_threshold)
                condition = "{} > {:.2f}".format(p_node_name,
                                                 parent_threshold)
                query = "`" + p_node_name + "` > " + str(parent_threshold)
                df = df.query(query)
            elif parent_decision_type == '==':
                method = METHOD_EXCLUDES
                arg = create_categorical_arg(parent_threshold)
                query, condition = create_categorical_query(method,
                                                            arg,
                                                            p_node_name,
                                                            parent,
                                                            categories)
                df = df.query(query)
    success = 0
    total = df.shape[0]
    if df.shape[0] == 0 and metric != Metrics.ERROR_RATE:
        metric_value = 0
        error = 0
        success = 0
    elif metric == Metrics.MEAN_ABSOLUTE_ERROR:
        pred_y, true_y, error = get_regression_metric_data(df)
        metric_value = mean_absolute_error(pred_y, true_y)
    elif metric == Metrics.MEAN_SQUARED_ERROR:
        pred_y, true_y, error = get_regression_metric_data(df)
        metric_value = mean_squared_error(pred_y, true_y)
    elif metric == Metrics.MEDIAN_ABSOLUTE_ERROR:
        pred_y, true_y, error = get_regression_metric_data(df)
        metric_value = median_absolute_error(pred_y, true_y)
    elif metric == Metrics.R2_SCORE:
        pred_y, true_y, error = get_regression_metric_data(df)
        metric_value = r2_score(pred_y, true_y)
    elif metric == Metrics.F1_SCORE:
        pred_y, true_y, error = get_classification_metric_data(df)
        metric_value = f1_score(pred_y, true_y)
        success = total - error
    elif metric == Metrics.PRECISION_SCORE:
        pred_y, true_y, error = get_classification_metric_data(df)
        metric_value = precision_score(pred_y, true_y)
        success = total - error
    elif metric == Metrics.RECALL_SCORE:
        pred_y, true_y, error = get_classification_metric_data(df)
        metric_value = recall_score(pred_y, true_y)
        success = total - error
    else:
        error = df[DIFF].values.sum()
        if total == 0:
            metric_value = 0
        else:
            metric_value = error / total
        success = total - error
    metric_name = metric_to_display_name[metric]
    is_error_metric = metric in error_metrics
    if SPLIT_FEATURE in tree:
        node_name = feature_names[tree[SPLIT_FEATURE]]
    else:
        node_name = None
    json.append({
        "arg": arg,
        "badFeaturesRowCount": 0,  # Note: remove this eventually
        "condition": condition,
        "error": float(error),
        "id": int(nodeid),
        METHOD: method,
        "nodeIndex": int(nodeid),
        "nodeName": node_name,
        "parentId": parentid,
        "parentNodeName": p_node_name,
        "pathFromRoot": "",  # Note: remove this eventually
        "size": float(total),
        "sourceRowKeyHash": "hashkey",  # Note: remove this eventually
        "success": float(success),  # Note: remove this eventually
        "metricName": metric_name,
        "metricValue": float(metric_value),
        "isErrorMetric": is_error_metric
    })
    return json, df


def get_regression_metric_data(df):
    pred_y = df[PRED_Y]
    true_y = df[TRUE_Y]
    # total abs error at the node
    error = sum(abs(pred_y - true_y))
    return pred_y, true_y, error


def get_classification_metric_data(df):
    pred_y = df[PRED_Y]
    true_y = df[TRUE_Y]
    error = df[DIFF].values.sum()
    return pred_y, true_y, error
