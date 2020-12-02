from NLGengine.observation import Observation
from NLGengine.content_determination.determinator import check_component, check_pattern, check_period

from datetime import datetime
from dateutil.parser import parse

import numpy as np
import os
import json


class MatrixTrainer:
    def __init__(self, n_estimators: int = 100, file_path: str = r"NLGengine/content_determination/test_cases.json"):
        self.n_estimators = n_estimators

        assert os.path.exists(file_path), "File does not exist"
        self.file_path = file_path

    def load_data(self):
        """[summary]
        """
        # open the file with the json data
        try:
            with open(self.file_path) as f:
                data = json.load(f)
            self.test_cases = data.get("test_cases")
            self.test_observations = self.format_observations(data.get("observations"))
        except IOError:
            print("file not accessible")

    def format_observations(self, json_obs):
        observations = {}
        for key in json_obs:
            info = json_obs.get(key)

            # format the json observation into an Observation instance
            observations[key] = Observation(info.get("serie"),
                                            parse(info.get("period_begin")),
                                            parse(info.get("period_end")),
                                            info.get("pattern"),
                                            info.get("sector"),
                                            info.get("indexx"),
                                            info.get("observation"),
                                            info.get("perc_change"),
                                            info.get("abs_change"),
                                            info.get("relevance"),
                                            info.get("meta_data"),
                                            oid=int(key))
        return observations

    def retrieve_weight(self, matrix, observ1, observ2):
        """[summary]

        Args:
            matrix ([type]): [description]
            observ1 ([type]): [description]
            observ2 ([type]): [description]

        Returns:
            [type]: [description]
        """
        pattern_index = check_pattern(observ1, observ2)
        period_index = check_period(observ1, observ2)
        comp_index = check_component(observ1, observ2)

        return matrix[pattern_index][period_index][comp_index]

    def fit(self):
        # build all the matrices
        self.matrices = [generate_matrix() for x in range(self.n_estimators)]

        # loop over all the matrices and initiate the X and y lists
        for matrix in self.matrices:
            X = list()  # a list with the predictions
            y = list()  # a list with the preferred values

            # loop over all the test cases and save both the scores
            for case in self.test_cases:
                observ1 = self.test_observations.get(str(case.get("prev_observ")))
                observ2 = self.test_observations.get(str(case.get("new_observ")))

                X.append(self.retrieve_weight(matrix, observ1, observ2))
                y.append(case.get("score"))

            # calculate the score and save the score and the corresponding matrix
            grade = score(X, y)
            self.graded_matrices.append((grade, matrix))

    def run(self):
        """[summary]
        """
        self.load_data()
        self.fit()


def generate_matrix(shape: tuple = (3, 4, 3), mean: int = 0, pos_lim: int = 2, neg_lim: int = -2):
    matrix = np.random.randint(neg_lim, pos_lim, size=shape)

    return matrix


def score(X: list, y: list):
    """Returns the mean accuracy on the given test data and labels

    Args:
        X (list): A list with all the predicted weights
        y (list): A list with all the preferred values

    Returns:
        float: Mean accuracy
    """
    assert len(X) == len(y), "The size of the two lists are not the same"

    mean = np.mean([abs(a - b) for a, b in zip(X, y)])
    return mean
