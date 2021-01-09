import numpy as np
from datetime import datetime


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


def get_recency(art_type: str, observ1, observ2):
    """Calculates based on the dates of the observations and based on the artikel type the difference in period.

    Args:
        art_type (str): the type of the article to be generated
        observ1 (NLGengine.observation.Observation): The first observation to be compared
        observ2 (NLGengine.observation.Observation): The second observation to be compared

    Returns:
        int: Returns the difference in period based on the artikeltype
    """
    if observ1.period_end > observ2.period_end:
        # observation 1 is more recent than observation 2
        dates = (observ2.period_end, observ1.period_end)
    else:
        # vice versa
        dates = (observ1.period_end, observ2.period_end)

    if art_type == "dagartikel":
        # get the difference in days between the two observations
        delta = dates[1] - dates[0]
        diff = delta.days

    elif art_type == "weekartikel":
        # get the difference in weeks between the two observations
        delta = dates[1] - dates[0]
        diff = np.floor(delta.days / 7)

    elif art_type == "maandartikel":
        # get the difference in months between the two observations
        start_date = dates[0]
        end_date = dates[1]
        diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    return diff
