from NLGengine.observation import Observation
from NLGengine.content_determination.comparisons import check_component, check_pattern, check_period
from NLGengine.content_determination.nndeterminator import one_hot_encode_input, load_model
from dateutil.parser import parse
from keras.models import Sequential
from keras.layers import Dense
from sklearn.model_selection import train_test_split

import keras
import numpy as np
import pandas as pd
import os
import json
import itertools


class NNMatrixTrainer:
    """A class for training the NN network for content Determination.
    """
    def __init__(self, s_file: str = r"NLGengine/content_determination/test_cases.json",
                 m_file: str = r"NLGengine/content_determination/pred_model.json"):

        assert os.path.exists(s_file), "Source file does not exist"
        self.source_file = s_file

        assert os.path.exists(m_file), "Model file does not exist"
        self.model_file = m_file

        self.model = None
        self.test_cases = None
        self.test_observations = None

    def load_data(self):
        """Loads in the data from the test file json
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
                                            info.get("perc_change"),
                                            info.get("abs_change"),
                                            info.get("observation"),
                                            info.get("relevance"),
                                            info.get("meta_data"),
                                            oid=int(key))
        return observations

    def use_network(self, model, observ1, observ2):
        """Uses the model to give back the weight between observation 1 and 2.

        Args:
            model (dict): The model for making the predictions.
            observ1 (NLGengine.observation.Observation): The first observation
            observ2 (NLGengine.observation.Observation): The second observation

        Returns:
            float: Returns the prediction made by the model
        """
        # onehotencoded the both observations
        combi_encoded = one_hot_encode_input(observ1, observ2)
        # reshape the encoded array in the right form
        X = "".join(map(str, combi_encoded))
        # use the model to return the given weight and unpack it
        prediction = model.get(X)
        return prediction

    def get_evaluations(self):
        """Uses the model on every available test case and returns the results
        """
        # initiate a list for storing all case results for displaying on the website
        cases_info = list()
        # load in the data
        self.load_data()
        # load in the current model
        model = load_model(self.model_file, self.weights_file)

        # iterate over all test cases and save the necessary information for later displaying
        for case in self.test_cases:
            # get the both observations
            observ1 = self.test_observations.get(str(case.get("prev_observ")))
            observ2 = self.test_observations.get(str(case.get("new_observ")))
            # select the indexes
            pattern_index = check_pattern(observ1, observ2)
            period_index = check_period(observ1, observ2)
            comp_index = check_component(observ1, observ2)
            # save all the info about the two combination of the two observations
            info = {
                "sentence1": observ1.observation,
                "sentence2": observ2.observation,
                "pattern": ['hetzelfde', 'vergelijkbaar', 'ongelijk'][pattern_index],
                "period": ['identiek', 'overlappend', 'opvolgend', 'anders'][period_index],
                "component": ['hetzelfde', 'vergelijkbaar', 'anders'][comp_index],
                "score": round(float(self.use_network(model, observ1, observ2)), 2),
                "expected": round(case.get("score") / 2, 2)
            }
            # append the info
            cases_info.append(info)

        data = {
            "scores": cases_info
        }

        return data
