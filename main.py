from __future__ import annotations

import logging
import os
import sys
from time import time

import PRML

# Sets up the in-built logger to record key information and save it to a text file
logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w',
                    format="%(asctime)s - %(levelname)s - '%(message)s' - %(funcName)s")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))  # Outputs the loggings into screen output

# Constants
ROOT_DIR = os.path.dirname(__file__)
START_TIME = time()


def quit_program() -> None:
    """
    Closes python in a safe manner.
    :return:
        - None
    """
    logging.info("Exiting program - %s seconds -" % round(time() - START_TIME, 2))
    sys.exit(0)


def main() -> None:
    """
    Gives the user a choice between tasks or datasets.
    :return:
        - None
    """
    run = True
    while run:
        try:
            print("""
            0 - Quit
            1 - 'Fashion-MNIST'
            """)
            choice = int(input("Which question number: "))
            if choice == 0:
                return
            elif choice == 1:
                config = PRML.Config(ROOT_DIR, 'Fashion-MNIST', 'openml')
                ml = PRML.MachineLearning(config)
                ml.main()
                return
        except ValueError:
            print("Please enter a valid choice!")
        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    logging.info('Starting program')
    main()
    raise quit_program()
