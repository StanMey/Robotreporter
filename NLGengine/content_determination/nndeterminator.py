from NLGengine.content_determination.comparisons import check_pattern, check_period, check_component, get_recency
from keras.models import model_from_json
from datetime import datetime

import numpy as np
import os


class NNDeterminator:
    """A class for making NN based content determination decisions.
    """
    def __init__(self, model, all_observs: list, history: list, sector_focus: list, art_type: str,
                 sec_focus_weight: float = 0.5, recency_imp_weight: float = -0.6):
        """The init function

        Args:
            model (): The model to be used for determining the observations to be used
            all_observs (list): All the observations that can be chosen as the next one
            history (list): A list with the already chosen observations
            sector_focus (list): A list with sectors to focus on
            art_type (str): the type of the article to be generated
            sec_focus_weight (float, optional): The extra weight an observation gets when its sector is the focus sector. Defaults to 0.5
            recency_imp_weight (float, optional): The factor the observation gets punished for at the recency score. Defaults to -0.4
        """
        self.model = model
        self.all_observations = all_observs
        self.history = history
        self.sector_focus = sector_focus
        self.article_type = art_type
        self.sector_focus_weight = sec_focus_weight
        self.recency_importance_weight = recency_imp_weight

    def get_follow_up_weight(self, observ, new_observ):
        """Compares two observations and retrieves the corresponding weight

        Args:
            observ (NLGengine.observation.Observation): The first observation
            new_observ (NLGengine.observation.Observation): The observation that follows the first observation

        Returns:
            float: The weight/fitness of the combination of observations
        """
        # onehotencoded the both observations
        combi_encoded = one_hot_encode_input(observ, new_observ)
        # reshape the encoded array in the right form
        X = np.reshape(np.array(combi_encoded), (1, -1))
        # use the model to return the given weight and unpack it
        prediction = self.model.predict(X)[0][0]

        return prediction

    def reset_situational_relevance(self):
        """Reset the situational relevance of all observations before a new selection round.
        """
        for observ in self.all_observations:
            observ.relevance2 = observ.relevance1

    def calculate_new_situational_relevance(self, new_par: bool):
        """Reset the situational relevance and calculate the new situational relevance between the already chosen observations and the rest.

        Args:
            new_par (bool): Indicates whether a new paragraph is started
        """
        self.reset_situational_relevance()

        # get the smoothing mean array based on the amount of selected observations
        smooth_mean = generate_smoothing_mean(len(self.history))

        for observ in self.all_observations:
            # iterate over all history observations and apply the smoothing mean to smooth out the situational relevance
            for hist_observ, sm_weight in zip(self.history, smooth_mean):

                # check if a new paragraph is started
                if new_par:
                    observ.relevance2 -= self.get_follow_up_weight(hist_observ, observ) * sm_weight
                else:
                    observ.relevance2 += self.get_follow_up_weight(hist_observ, observ) * sm_weight

                # get the recency based on the article type
                recency = get_recency(self.article_type, hist_observ, observ)
                if recency > 0:
                    # punish the observation's relevance based on recency
                    observ.relevance2 += recency * - self.recency_importance_weight

            # check if sector of observation is focus
            if is_focus_sector(self.sector_focus, observ):
                observ.relevance2 += self.sector_focus_weight

    def get_highest_relevance(self):
        """Gets the hightest situational relevance from the avaiable observations
        and filters this observation from all observations.
        """
        # order the observations
        ordered_observs = sorted(self.all_observations, key=lambda x: x.relevance2, reverse=True)
        # select the one with the highest situational relevance
        chosen_observ = ordered_observs.pop(0)
        # remove this observation from all observations
        self.all_observations = list(filter(lambda x: x.observ_id != chosen_observ.observ_id, self.all_observations))
        return chosen_observ


def load_model(model_path: str = r"./NLGengine/content_determination/deter_model.json",
               weights_path: str = r"./NLGengine/content_determination/deter_model.h5"):
    """Loads in the model and the weights.

    Args:
        model_path (str, optional): The file path to the model file. Defaults to r"./NLGengine/content_determination/deter_model.json".
        weights_path (str, optional): The file path to the weights file. Defaults to r"./NLGengine/content_determination/deter_model.h5".

    Returns:
        keras.engine.sequential.Sequential: Returns the loaded model
    """

    assert os.path.exists(model_path), "Model file does not exist"
    assert os.path.exists(weights_path), "Weights file does not exist"

    # load json and create model
    with open(model_path, 'r') as json_file:
        loaded_model_json = json_file.read()

    model = model_from_json(loaded_model_json)
    # load weights into the new model
    model.load_weights(weights_path)

    return model


def one_hot_encode_input(obs1, obs2):
    """encodes the input over two observation based on the similarities.

    Args:
        obs1 (NLGengine.observation.Observation): The first Observation
        obs2 (NLGengine.observation.Observation): The second Observation

    Returns:
        np.array: A numpy array with the encoded combinations of the two observations
    """
    encoded = [0 for x in range(10)]

    # finding the similarities between the observations
    pattern_index = check_pattern(obs1, obs2)
    period_index = check_period(obs1, obs2) + 3
    comp_index = check_component(obs1, obs2) + 7

    # applying the onehotencoder
    encoded[pattern_index] = 1
    encoded[period_index] = 1
    encoded[comp_index] = 1

    return encoded


def is_focus_sector(filter_list: list, observ):
    """Returns true if the sector in the observation is in the list of sectors to focus on.

    Args:
        filter_list (list): A list with sectors to filter on
        observ (NLGengine.observation.Observation): The observation to check the sector on

    Returns:
        bool: Returns whether the observation is about a focus sector
    """
    multi_sectors = observ.meta_data.get("sectors")

    if multi_sectors:
        # "sectors" exist in the meta_data of the observation
        observ_sectors = multi_sectors
    else:
        observ_sectors = observ.sector

    if type(observ_sectors) == list:
        # multiple sectors to check for
        return any(i in filter_list for i in observ_sectors)
    else:
        # only one sector to check for
        return observ_sectors in filter_list


def generate_smoothing_mean(hist_elems):
    """Build an array with weights to use for smoothing mean.

    Args:
        hist_elems (int): The amount of elemenents already in the history

    Returns:
        numpy.ndarray: Returns an array with
    """
    return np.linspace(0.0, 1.0, num=hist_elems + 1)[1:]
