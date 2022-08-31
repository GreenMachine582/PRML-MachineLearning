from __future__ import annotations

import json
import logging
import os


class Config(object):
    """
    Config stores default and important values that the MachineLearning
    class can use. The end-user can save, load and update the attributes.
    """

    def __init__(self, _dir: str, dataset_name: str):
        self.dir = _dir
        self.dataset_name = dataset_name

        self.config_dir = f'{_dir}\\configs\\{dataset_name}.json'
        self.dataset_dir = f'{_dir}\\datasets\\{dataset_name}.csv'
        self.model_dir = f'{_dir}\\models\\{dataset_name}.model'

        self.show_figs = True
        self.show_small_responses = True

        # dataset related
        self.seperator = ','
        self.target = 'target'
        self.names = None

        # training related
        self.split_ratio = 0.8
        self.random_seed = 0
        self.model_type = 'LogisticRegression'

        self.load() if os.path.isfile(self.config_dir) else self.save()

    def update(self, kwargs: dict) -> None:
        """
        Updates the class attributes with given keys and values.
        :param kwargs: dict[str: Any]
        :return:
            - None
        """
        logging.info('Updating class attributes')
        for key, value in kwargs.items():
            setattr(self, key, value)

    def load(self) -> None:
        """
        Attempts to load the config file using json, if file is not found
        a warning will be logged.
        :return:
            - None
        """
        logging.info(f'Loading config {self.config_dir}')
        try:
            with open(self.config_dir, 'r', encoding='utf-8') as f:
                self.update(json.load(f))
        except FileNotFoundError as e:
            logging.warning(e)

    def save(self) -> None:
        """
        Saves the config attributes as an indented dict in a json file,
        to allow end-users to edit and easily view the default configs.
        :return:
            - None
        """
        logging.info(f'Saving config {self.config_dir}')
        with open(self.config_dir, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=4)
