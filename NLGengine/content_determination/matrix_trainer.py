from NLGengine.observation import Observation
from NLGengine.content_determination.determinator import check_component, check_pattern, check_period

from dateutil.parser import parse

import numpy as np
import os
import json
import itertools


class MatrixTrainer:
    """[summary]
    """
    def __init__(self, n_estimators: int = 100, subset: int = 10, combine: bool = True, overwrite: bool = False,
                 s_file: str = r"NLGengine/content_determination/test_cases.json",
                 t_file: str = r"NLGengine/content_determination/weights.json"):
        """[summary]

        Args:
            n_estimators (int, optional): The amount of matrices to be generated for the estimation. Defaults to 100.
            subset (int, optional): The subset to take when the best scoring matrices are combined. Defaults to 10.
            combine (bool, optional): If the best scoring matrices are to be combined. Defaults to True.
            overwrite (bool, optional): [description]. Defaults to False.
            s_file (str, optional): [description]. Defaults to r"NLGengine/content_determination/test_cases.json".
            t_file (str, optional): [description]. Defaults to r"NLGengine/content_determination/weights.json".
        """

        self.apply_combine = combine
        self.overwrite = overwrite

        assert n_estimators >= subset, "Subset has more elements than amount of estimators"
        self.n_estimators = n_estimators
        self.subset = subset

        assert os.path.exists(s_file), "Source file does not exist"
        self.source_file = s_file

        assert os.path.exists(t_file), "Target file does not exist"
        self.target_file = t_file

    def load_data(self):
        """[summary]
        """
        # open the file with the json data
        try:
            with open(self.source_file) as f:
                data = json.load(f)
            self.test_cases = data.get("test_cases")
            self.test_observations = self.format_observations(data.get("observations"))
        except IOError:
            print("file not accessible")

    def format_observations(self, json_obs: dict):
        """[summary]

        Args:
            json_obs (dict): [description]

        Returns:
            [type]: [description]
        """
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

    def fit(self, matrices: list):
        """[summary]

        Args:
            matrices (list): [description]

        Returns:
            [type]: [description]
        """
        # build all the matrices
        graded_matrices = list()

        # loop over all the matrices and initiate the X and y lists
        for matrix in matrices:
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
            graded_matrices.append((grade, matrix))

        return graded_matrices

    def combine_and_tweak(self, graded_matrices: list):
        """[summary]

        Args:
            graded_matrices (list): [description]

        Returns:
            [type]: [description]
        """
        # get the highest scoring x matrices.
        graded_subset = sorted(graded_matrices, key=lambda x: x[0])[:self.subset]

        # get all unique 2 combinations of these matrices
        combinations = list(itertools.combinations(graded_subset, 2))

        # calculate the mean matrix of all combinations
        combi_matrices = []
        for combi in combinations:
            combi_matrices.append((combi[0][1] + combi[1][1]) / 2.0)

        return combi_matrices

    def save_matrix(self, graded_matrix: tuple):
        """[summary]
        """
        data = {
            "score": graded_matrix[0],
            "matrix": graded_matrix[1].tolist()
        }

        with open(self.target_file, 'w') as outfile:
            json.dump(data, outfile)

    def run(self):
        """[summary]
        """
        self.load_data()

        # build all the matrices
        matrices = [generate_matrix() for x in range(self.n_estimators)]
        # fit the matrices
        self.graded_matrices = self.fit(matrices)

        # check if the function combine and tweak can be called
        if self.apply_combine:
            # call function combine_and_tweak to combine a subset of matrices in search for a better score
            combi_matrices = self.combine_and_tweak(self.graded_matrices)
            # fit the matrices
            new_graded = self.fit(combi_matrices)
            # extend list of already graded matrices with the new scores
            self.graded_matrices.extend(new_graded)

        # get the top scoring matrix
        highest = sorted(self.graded_matrices, key=lambda x: x[0])[0]
        print(highest)
        # save the matrix
        if self.overwrite:
            self.save_matrix(highest)


def generate_matrix(shape: tuple = (3, 4, 3), mean: int = 0, pos_lim: int = 2, neg_lim: int = -2):
    matrix = np.random.random(shape) * 4 - 2

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

    mean = np.mean([(a - b) ** 2 for a, b in zip(X, y)])
    return mean
