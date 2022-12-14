from __future__ import annotations

import logging
from copy import deepcopy

import numpy as np
from pandas import DataFrame, Series
from sklearn import ensemble, linear_model, tree
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import machine_learning as ml
from machine_learning import Config, Dataset, Model


def searchCV(model: Model, X_train: DataFrame, y_train: Series, display: bool = True, search_method: str = 'randomised',
             random_state: int | None = None) -> GridSearchCV | RandomizedSearchCV:
    """
    Search through param grids with two distinct search methods, and
    incorporates cross-validation as it searches for the highest performing
    model.

    :param model: Model to be searched and cross-validated, should be a Model
    :param X_train: Training independent features, should be a DataFrame
    :param y_train: Training dependent variables, should be a Series
    :param display: Whether to display the results, should be a bool
    :param search_method: If 'randomised', RandomizedSearchCV will be used, if 'grid',
     GridSearchCV will be used, should be a str
    :param random_state: Also known as random seed, should be an int
    :return: cv_results - GridSearchCV | RandomizedSearchCV
    """
    logging.info(f"Grid searching '{model.name}'")

    params = model.grid_params if not isinstance(model.base, Pipeline) else model.getPipelineKeys(model.grid_params)

    if search_method == "randomised":
        cv_results = RandomizedSearchCV(model.base, params, n_iter=1000, n_jobs=-1, random_state=random_state,
                                        cv=TimeSeriesSplit(10), verbose=2)
    elif search_method == "grid":
        cv_results = GridSearchCV(model.base, params, n_jobs=-1, cv=TimeSeriesSplit(10), verbose=2)
    else:
        raise ValueError("The parameter 'search_method' must be either 'randomised' or 'grid'")

    cv_results.fit(X_train, y_train)

    if display:
        print('\n\t', model.name)
        print('The best estimator:', cv_results.best_estimator_)
        print('The best score:', cv_results.best_score_)
        print('The best params:', cv_results.best_params_)
    return cv_results


def getGradientBoostingRegressor(random_state: int = None) -> dict:
    """
    Get the Gradient Boosting Regressor and appropriate attributes.

    :param random_state:
    :return: estimator - dict[str: Any]
    """
    # TODO: documentation
    grid_params = {'criterion': ['friedman_mse', 'squared_error'],
                   'learning_rate': [0.002 * (i + 1) for i in range(100)],
                   'max_depth': range(5, 101, 5),
                   'n_estimators': range(50, 801, 50),
                   'random_state': [random_state],
                   'subsample': [0.1 * (i + 1) for i in range(10)]}
    estimator = {'name': 'GBR',
                 'fullname': "Gradient Boosting Regressor",
                 'type_': 'estimator',
                 'base': ensemble.GradientBoostingRegressor(),
                 'grid_params': grid_params}
    logging.info(f"Got '{estimator['name']}' attributes")
    return estimator


def getRandomForestRegressor(random_state: int = None) -> dict:
    """
    Get the Random Forest Regressor and appropriate attributes.

    :param random_state:
    :return: estimator - dict[str: Any]
    """
    # TODO: documentation
    grid_params = {'criterion': ['squared_error', 'absolute_error', 'poisson'],
                   'max_depth': [2 * (i + 1) for i in range(40)],
                   'max_features': ['sqrt', 'log2', None, 2, 1, 0.5],
                   'min_samples_split': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1., 2, 3, 4],
                   'n_estimators': [50 * (i + 1) for i in range(20)],
                   'random_state': [random_state]}

    estimator = {'name': 'RFR',
                 'fullname': "Random Forest Regressor",
                 'type_': 'estimator',
                 'base': ensemble.RandomForestRegressor(),
                 'grid_params': grid_params}
    logging.info(f"Got '{estimator['name']}' attributes")
    return estimator


def getDecisionTreeRegressor(random_state: int = None):
    """
    Get the Decision Tree Regressor and appropriate attributes.

    :param random_state:
    :return: estimator - dict[str: Any]
    """
    # TODO: documentation
    grid_params = {'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                   'max_depth': [None, *[2 * (i + 1) for i in range(150)]],
                   'max_features': ['sqrt', 'log2', None, 2, 1, 0.5],
                   'max_leaf_nodes': [None, *[2 * (i + 1) for i in range(50)]],
                   'min_samples_split': [1 * (i + 1) for i in range(20)],
                   'min_samples_leaf': [1 * (i + 1) for i in range(5)],
                   'random_state': [random_state],
                   'splitter': ['best', 'random']}

    estimator = {'name': 'DTR',
                 'fullname': "Decision Tree Regressor",
                 'type_': 'estimator',
                 'base': tree.DecisionTreeRegressor(),
                 'grid_params': grid_params}
    logging.info(f"Got '{estimator['name']}' attributes")
    return estimator


def getRidgeClassifier(random_state: int = None):
    """
    Get the Ridge Classifier and appropriate attributes.

    :param random_state:
    :return: model - dict[str: Any]
    """
    # TODO: documentation
    grid_params = [{'alpha': [0.02 * (i + 1) for i in range(100)],
                    'class_weight': ['balanced', None],
                    'copy_X': [True, False],
                    'fit_intercept': [True, False],
                    'max_iter': [None, *[50 * (i + 1) for i in range(20)]],
                    'random_state': [random_state],
                    'solver': ['svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga']}]
    model = {'name': 'RC',
             'fullname': "Ridge Classifier",
             'type_': 'classifier',
             'base': linear_model.RidgeClassifier(),
             'grid_params': grid_params}

    logging.info(f"Got '{model['name']}' attributes")
    return model


def compareEstimator(estimator, dataset, config):
    # TODO: documentation
    results_dir = ml.utils.makePath(config.dir_, config.results_folder, f"{estimator.type_}_{estimator.name}")

    X_train, X_test, y_train, y_test = dataset.split(shuffle=False)

    cv_results = searchCV(estimator, X_train, y_train)

    models = [('Default', deepcopy(estimator.base)),
              ('Grid Searched', cv_results.best_estimator_)]

    logging.info("Fitting and predicting")
    y_preds = []
    for name, model in models:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_preds.append((name, np.clip(y_pred, 0, None)))

    path_, exist = ml.utils.checkPath(config.dir_, estimator.FOLDER_NAME, estimator.name, ext=estimator.EXT)
    if exist:
        models.append(('Recorded Best', estimator.load(inplace=False)))
        y_pred = models[-1][1].predict(X_test)
        y_preds.append((models[-1][0], np.clip(y_pred, 0, None)))

    ml.estimator.resultAnalysis(y_test, y_preds, dataset_name=dataset.name, results_dir=results_dir)
    ml.estimator.plotPrediction(y_train, y_test, y_preds, ylabel="Close ($USD)", dataset_name=dataset.name,
                                results_dir=results_dir)

    results = ml.estimator.biasVarianceDecomp(models, X_train, y_train, X_test, y_test, n_iter=10,
                                              dataset_name=dataset.name, results_dir=results_dir)

    index_min = np.argmin(results['loss'])
    logging.info(f"Best model is '{results['names'][index_min]}'")
    estimator.update(model=models[index_min][1])
    estimator.model.fit(X_train, y_train)
    estimator.save()


def compareClassifier(classifier, dataset, config):
    # TODO: documentation
    results_dir = ml.utils.makePath(config.dir_, config.results_folder, f"{classifier.type_}_{classifier.name}")

    dataset.df.drop('diff', axis=1, inplace=True)  # same feature as binary encoded target
    dataset.apply(ml.binaryEncode, dataset.target)

    X_train, X_test, y_train, y_test = dataset.split(shuffle=False)

    cv_results = searchCV(classifier, X_train, y_train)

    models = [('Default', deepcopy(classifier.base)),
              ('Grid Searched', cv_results.best_estimator_)]

    path_, exist = ml.utils.checkPath(config.dir_, classifier.FOLDER_NAME, classifier.name, ext=classifier.EXT)
    if exist:
        models.append(('Recorded Best', classifier.load(inplace=False)))

    logging.info("Fitting and predicting")
    y_preds = []
    for name, model in models:
        model.fit(X_train, y_train)
        y_preds.append((name, model.predict(X_test)))

    ml.classifier.resultAnalysis(y_test, y_preds, dataset_name=dataset.name, results_dir=results_dir)
    ml.classifier.plotPrediction(y_test, y_preds, dataset_name=dataset.name, results_dir=results_dir)

    results = ml.classifier.biasVarianceDecomp(models, X_train, y_train, X_test, y_test, n_iter=10,
                                               dataset_name=dataset.name, results_dir=results_dir)

    index_min = np.argmin(results['avg'])
    logging.info(f"Best model is '{results['names'][index_min]}'")
    classifier.update(model=models[index_min][1])
    classifier.model.fit(X_train, y_train)
    classifier.save()


def compareParams(dataset: Dataset, config: Config) -> None:
    """
    The user can select an ML technique to be grid-searched and cross-validated.
    A default, grid and best model will be fitted and predicted. The predictions
    be used for a result analysis and will be plotted.

    :param dataset: The loaded and processed dataset, should be a Dataset
    :param config: BSS configuration, should be a Config
    :return: None
    """
    logging.info("Comparing params")
    while True:
        print(f"""
        0 - Back
        Estimators:
            1 - Gradient Boosting Regressor
            2 - Random Forest Regressor
            3 - Decision Tree Regressor
        Classifiers:
            4 - Ridge Classifier
        """)
        choice = input("Which estimator model: ")
        try:
            choice = int(choice)
        except ValueError:
            print('\nPlease enter a valid response!')
            choice = None

        model_config = None
        if choice is not None:
            if choice == 0:
                return
            elif choice == 1:
                model_config = getGradientBoostingRegressor()
            elif choice == 2:
                model_config = getRandomForestRegressor()
            elif choice == 3:
                model_config = getDecisionTreeRegressor()
            elif choice == 4:
                model_config = getRidgeClassifier()
            else:
                print("\nPlease enter a valid choice!")

        if model_config is not None:
            model = Model(config.model, **model_config)
            model.base = Pipeline([('scaler', StandardScaler()), (model.name, model.base)])
            if model.type_ == 'estimator':
                compareEstimator(model, dataset, config)
            elif model.type_ == 'classifier':
                compareClassifier(model, deepcopy(dataset), config)
