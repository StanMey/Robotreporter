from NLGengine.realisation.date_message import DateMessage
from NLGengine.article import Article
import math


class Realiser:
    """[summary]
    """
    def __init__(self, pars: list):
        """[summary]

        Args:
            pars (list): [description]
        """
        self.paragraphs = pars
        # TODO check if the most current observation is today
        self.is_current = False

    def realise(self):
        """[summary]
        """
        self.add_time_to_observs_and_paragraphs()

    def add_time_to_observs_and_paragraphs(self):
        """[summary]
        """
        # set a counter variable
        count = 0

        # loop over every paragraph
        for par in self.paragraphs:

            curr_observ = None
            count = 0

            for observ in par.observations:

                if count == 0:
                    # first sentence of the new paragraph
                    observ.observation_new = f"Op {observ.day_number} {DateMessage.month_to_string(observ.month_number)} {observ.observation}"

                else:
                    if observ.week_number == curr_observ.week_number:
                        # the observations are in the same week
                        if observ.day_number == curr_observ.day_number:
                            # the observations have the same end day
                            observ.observation_new = observ.observation
                        else:
                            # not the same end day, but in the same week
                            # calculate the day difference
                            delta = (curr_observ.period_end - observ.period_end).days
                            observ.observation_new = f"{DateMessage.day_difference_to_string(delta, self.is_current)} {observ.observation}"
                    else:
                        # calculate the difference in weeks
                        delta = math.ceil((curr_observ.period_end - observ.period_end).days / 7.0)
                        observ.observation_new = f"{DateMessage.week_difference_to_string(delta, self.is_current)} {observ.observation}"

                # set the current observation
                curr_observ = observ
                count += 1
