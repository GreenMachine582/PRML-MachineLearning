from __future__ import annotations

import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas import DataFrame

import machine_learning as ml
from machine_learning import Dataset

sns.set(style='darkgrid')

# Constants
local_dir = os.path.dirname(__file__)


def preProcess(df: DataFrame) -> DataFrame:
    """
    Pre-Process the BTC dataset, by generalising feature names, correcting
    datatypes, normalising values and handling invalid instances.

    :param df: BSS dataset, should be a DataFrame
    :return: df - DataFrame
    """
    df = ml.handleMissingData(df)

    df['Date'] = pd.to_datetime(df['Date'])

    logging.info(f"Pre-Processed dataset")
    return df


def exploratoryDataAnalysis(df: DataFrame) -> None:
    """
    Performs initial investigations on data to discover patterns, to spot
    anomalies,to test hypothesis and to check assumptions with the help
    of summary statistics and graphical representations.

    :param df: BSS dataset, should be a DataFrame
    :return: None
    """
    logging.info("Exploratory Data Analysis")

    plt.figure()
    sns.heatmap(df.drop('Date', axis=1).corr(), annot=True)
    plt.title('Pre-Processed Corresponding Matrix')

    # Line Plot
    plt.figure()
    plt.plot(df.index, df['Close'])
    plt.title('BTC Demand Vs Date')
    plt.xlabel('Date')
    plt.ylabel('Close ($USD)')
    plt.show()

    plt.show()  # displays all figures


def processData(df: DataFrame) -> DataFrame:
    """
    Processes and adapts the BTC dataset to suit time series by adding a
    datetime index. Feature engineering has also been applied by adding
    historical data. It also includes some forms of feature selection,
    certain features will be dropped to reduce dimensionality and
    multi-collinearity which were identified in the previous corresponding
    matrix.

    :param df: BTC dataset, should be a DataFrame
    :return: df - DataFrame
    """
    # Adapts the dataset for time series
    df.index = df['Date']
    df.drop('Date', axis=1, inplace=True)

    # Adds historical data
    df.loc[:, 'prev'] = df.loc[:, 'Close'].shift()
    df.loc[:, 'diff'] = df.loc[:, 'prev'].diff()
    df.loc[:, 'prev-2'] = df.loc[:, 'prev'].shift()
    df.loc[:, 'diff-2'] = df.loc[:, 'prev-2'].diff()

    df = ml.handleMissingData(df)

    # Changes datatypes
    for col in ['prev', 'diff', 'prev-2', 'diff-2']:
        df[col] = df[col].astype('float64')

    logging.info("Dataset processed")
    return df


def processDataset(dataset: Dataset, overwrite: bool = False) -> Dataset:
    """
    Pre-processes the dataset if applicable, then processes the dataset.

    :param dataset: the dataset, should be a Dataset
    :param overwrite: overwrite existing file, should be a bool
    :return: dataset - Dataset
    """
    name = dataset.name
    dataset.update(name=name + '-pre-processed')

    if overwrite or not dataset.load():
        dataset.apply(preProcess)
        dataset.save()

    dataset.apply(processData)
    dataset.update(name=name + '-processed')
    return dataset


def main(dir_: str = local_dir) -> None:
    """
    Pre-processes and Processes the datasets.

    :param dir_: project's path directory, should be a str
    :return: None
    """
    name = 'BTC-USD'
    config = ml.Config(dir_, name)

    # Loads the BSS dataset
    dataset = ml.Dataset(config.dataset)
    if not dataset.load():
        return

    print(dataset.df.head())
    dataset.apply(preProcess)
    dataset.update(name=name + '-pre-processed')
    dataset.save()

    exploratoryDataAnalysis(dataset.df)

    dataset.apply(processData)
    dataset.update(name=name + '-processed')
    print(dataset.df.axes)
    print(dataset.df.head())
    print(dataset.df.dtypes)
    plt.figure()
    sns.heatmap(dataset.df.corr(), annot=True)
    plt.title('Processed Corresponding Matrix')
    plt.show()


if __name__ == '__main__':
    main()
