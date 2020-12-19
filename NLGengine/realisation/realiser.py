from NLGengine.realisation.date_message import DateMessage
from NLGengine.realisation.templatefiller import TemplateFiller
from NLGengine.article import Article
import random as rd
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
        """Runs all the steps to realise the sentences in the article.
        """
        self.find_template()
        self.add_time_to_observs_and_paragraphs()
        self.add_interpunction()

    def find_template(self):
        """Finds for every observation the template and saves it.
        """
        used_sector_long = False

        for par in self.paragraphs:
            for observ in par.observations:
                print(observ.observ_id, observ)

                # check for the 'sector' pattern if a long version already has been used
                if observ.pattern == "sector" and not used_sector_long:
                    # go for the long pattern sentence this time
                    used_sector_long = True
                    template = TemplateFiller.retrieve_template_option(observ, long_version=used_sector_long)

                else:
                    # normally retrieve the template
                    template = TemplateFiller.retrieve_template_option(observ)

                # fill in the template
                sentence = TemplateFiller.insert_into_template(observ, template)
                # set the filled in sentence as the current observation sentence
                observ.observation = sentence

    def add_interpunction(self):
        """Adds interpunction to every sentence (. at the end and capital letter at the beginning).
        """
        for par in self.paragraphs:
            for observ in par.observations:

                # add a . after each sentence
                observ.observation_new += "."

                # add a capital letter at the beginning
                first_word = observ.observation_new.split()[0]
                # check if the first word is a number
                if not represents_integer(first_word):
                    # first word is not an integer, so add capital letter
                    observ.observation_new = observ.observation_new[0].capitalize() + observ.observation_new[1:]

    def add_time_to_observs_and_paragraphs(self):
        """[summary]
        """
        # set a counter variable
        count = 0
        # same day binding words || source: https://www.nt2.nl/documenten/luisteren_op_b2/overzicht_van_signaalwoorden.pdf
        same_day = ["verder", "dezelfde dag", "daarnaast", "vervolgens"]

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
                            observ.observation_new = f"{rd.choice(same_day)} {observ.observation}"
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


def represents_integer(s):
    """Checks whether a String is an integer.
    https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except

    Args:
        s (str): The string to check

    Returns:
        bool: Returns whether the string can be written as an integer
    """
    try:
        int(s)
        return True
    except ValueError:
        return False
