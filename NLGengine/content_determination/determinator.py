import json
import numpy as np
from datetime import datetime


class Determinator:
    """[summary]
    """
    def __init__(self, all_observs: list, history: list, sector_focus: list, sec_focus_weight: float = 0.7):
        """The init function

        Args:
            all_observs (list): All the observations that can be chosen as the next one
            history (list): A list with the already chosen observations
            sector_focus (list): A list with sectors to focus on
            sec_focus_weight (float, optional): The extra weight an observation gets when its sector is the focus sector. Defaults to 0.7
        """
        self.all_observations = all_observs
        self.history = history
        self.sector_focus = sector_focus
        self.sector_focus_weight = sec_focus_weight

    def load_weights(self):
        """Loads in the weights from json.
        """
        with open(r"./NLGengine/content_determination/weights.json") as f:
            self.weight_array = json.load(f).get("matrix")

    def follow_up_weight(self, observ, new_observ):
        """Compares two observations and retrieves the corresponding weight

        Args:
            observ (NLGengine.observation.Observation): The first observation
            new_observ (NLGengine.observation.Observation): The observation that follows the first observation

        Returns:
            float: The weight/fitness of the combination of observations
        """
        pattern_index = check_pattern(observ, new_observ)
        period_index = check_period(observ, new_observ)
        comp_index = check_component(observ, new_observ)

        return self.weight_array[pattern_index][period_index][comp_index]

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
        self.load_weights()

        # get the smoothing mean array based on the amount of selected observations
        smooth_mean = generate_smoothing_mean(len(self.history))

        for observ in self.all_observations:
            # iterate over all history observations and apply the smoothing mean to smooth out the situational relevance
            for hist_observ, sm_weight in zip(self.history, smooth_mean):

                # check if a new paragraph is started
                if new_par:
                    observ.relevance2 -= self.follow_up_weight(hist_observ, observ) * sm_weight
                else:
                    observ.relevance2 += self.follow_up_weight(hist_observ, observ) * sm_weight

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


def check_pattern(observ1, observ2):
    """Checks if the two given observations have the same/overlapping, similar or no shared patterns.

    Args:
        observ1 (NLGengine.observation.Observation): The first observation to be compared
        observ2 (NLGengine.observation.Observation): The second observation to be compared

    Returns:
        int: The corresponding index for the weights dictionary
    """
    pattern_set = set([observ1.pattern, observ2.pattern])

    if len(pattern_set) == 1:
        # the two patterns are the same
        indexx = 0
    elif ("combi-daling" in pattern_set) and ("individu-daling" in pattern_set):
        # the two patterns are similar both not the same
        indexx = 1
    elif ("combi-stijging" in pattern_set) and ("individu-stijging" in pattern_set):
        # the two patterns are similar both not the same
        indexx = 1
    else:
        # patterns neither the same nor similar
        indexx = 2

    return indexx


def check_period(observ1, observ2):
    """Checks if the two given observations have identical, overlapping, next or no shared periods.

    Args:
        observ1 (NLGengine.observation.Observation): The first observation to be compared
        observ2 (NLGengine.observation.Observation): The second observation to be compared

    Returns:
        int: The corresponding index for the weights dictionary
    """
    if (observ1.period_begin == observ2.period_begin) and (observ1.period_end == observ2.period_end):
        # the two observations are periodically identical
        indexx = 0
    elif has_overlap(observ1.period_begin, observ1.period_end, observ2.period_begin, observ2.period_end):
        # the two observations are overlapping
        indexx = 1
    elif ((np.busday_count(observ1.period_end.date(), observ2.period_begin.date()) == 1)
            or (np.busday_count(observ2.period_end.date(), observ1.period_begin.date()) == 1)):
        # the two observations are after each other (next)
        # so the start of observation 2 is 1 day after the end of observation 1 (minus the weekends) or vice versa.
        indexx = 2
    else:
        # the two observations are different
        indexx = 3

    return indexx


def check_component(observ1, observ2):
    """Checks if the two given observations have the same/overlapping, similar (same sector) or no shared components.

    Args:
        observ1 (NLGengine.observation.Observation): The first observation to be compared
        observ2 (NLGengine.observation.Observation): The second observation to be compared

    Returns:
        int: The corresponding index for the weights dictionary
    """
    if observ1.meta_data.get("components") and observ2.meta_data.get("components"):
        # observations are both combi patterns and hold multiple components
        if any(i in observ1.meta_data.get("components") for i in observ2.meta_data.get("components")):
            # both observations have one or more overlapping component(s)
            indexx = 0
        elif any(i in observ1.meta_data.get("sectors") for i in observ2.meta_data.get("sectors")):
            # both observations have one or more similar components(s)
            indexx = 1
        else:
            # both observations don't have overlapping or similar component(s)
            indexx = 2

    elif observ1.meta_data.get("components"):
        # observation 1 has multiple components
        if observ2.serie in observ1.meta_data.get("components"):
            # both observations have one or more overlapping component(s)
            indexx = 0
        elif observ2.sector in observ1.meta_data.get("sectors"):
            # both observations have one or more similar component(s)
            indexx = 1
        else:
            # both observations don't have overlapping or similar component(s)
            indexx = 2

    elif observ2.meta_data.get("components"):
        # observation 2 has multiple components
        if observ1.serie in observ2.meta_data.get("components"):
            # both observations have one or more overlapping component(s)
            indexx = 0
        elif observ1.sector in observ2.meta_data.get("sectors"):
            # both observations have one or more similar component(s)
            indexx = 1
        else:
            # both observations don't have overlapping or similar component(s)
            indexx = 2

    else:
        # neither of the observations has multiple components
        if observ1.serie == observ2.serie:
            # both observations have the same component
            indexx = 0
        elif observ1.sector == observ2.sector:
            # both observations have similar components
            indexx = 1
        else:
            # both observation share no overlapping of components
            indexx = 2

    return indexx


def has_overlap(A_start: datetime, A_end: datetime, B_start: datetime, B_end: datetime):
    """Checks if two periods have an overlap.
    https://stackoverflow.com/questions/3721249/python-date-interval-intersection

    Args:
        A_start (datetime): The period_begin datetime of the first observation
        A_end (datetime): The period_end datetime of the first observation
        B_start (datetime): The period_begin datetime of the second observation
        B_end (datetime): The period_end datetime of the second observation

    Returns:
        bool: Returns True if the two periods overlap
    """
    assert A_start <= A_end, "the start datetime is greater as the end datetime"
    assert B_start <= B_end, "the start datetime is greater as the end datetime"

    latest_start = max(A_start, B_start)
    earliest_end = min(A_end, B_end)
    return latest_start <= earliest_end


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
