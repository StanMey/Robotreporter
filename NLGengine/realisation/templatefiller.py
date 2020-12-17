import json
import os
import random as rd


class TemplateFiller:
    """[summary]
    """

    @staticmethod
    def retrieve_template_option(observation, t_source: str = r"NLGengine/realisation/templates.json"):
        """Returns one template from all the template sentences for the pattern of the given observation.

        Args:
            observation (NLGengine.observation.Observation): The observation for which the templates have to be retrieved
            t_source (str): The path to the template json file

        Returns:
            str: Returns the chosen template for the observation
        """
        assert os.path.exists(t_source), "template.json not found"  # check if templates.json exists

        with open(t_source) as f:
            data = json.load(f)

        if observation.pattern in ["combi-stijging", "combi-daling"]:
            # pattern is combi, so give templates with the right length
            templates = data.get(observation.pattern).get(str(len(observation.meta_data.get("components"))))

        elif observation.pattern in ["week", "trend"]:
            # pattern must be checked on the pos/neg of the trend
            templates = data.get(observation.pattern).get(str(observation.meta_data.get("trend")))

        elif observation.pattern == "sector":
            # check if the whole_sector or one component is chosen
            meta = observation.meta_data
            templates = data.get(observation.pattern).get(meta.get("sector_spec")).get(meta.get("trend"))

        else:
            # return the pattern
            templates = data.get(observation.pattern)

        return rd.choice(templates)

    @staticmethod
    def insert_into_template(observation, template):
        """[summary]

        Args:
            observation (NLGengine.observation.Observation): The observation to be used to fill in the template
            template_choices (str): A template string that has to be filled in

        Returns:
            str: Returns the filled in template string
        """

        if observation.pattern in ["combi-stijging", "combi-daling"]:
            # observation has multiple components and percentages
            new_sentence = template

            # get all components and percentages
            comps = observation.meta_data.get("components")
            percs = observation.meta_data.get("perc_change")

            # replace all components and percentages
            for comp, perc in zip(comps, percs):
                new_sentence = new_sentence.replace("<#comp_name#>", comp, 1)
                new_sentence = new_sentence.replace("<#perc#>", str(perc), 1)

        else:
            new_sentence = template
            # replace the comp placeholder with the actual component
            new_sentence = new_sentence.replace("<#comp_name#>", observation.serie)
            # replace the percentage placeholder
            new_sentence = new_sentence.replace("<#perc#>", str(observation.perc_change))

        if observation.pattern == "trend":
            # add the duration of the trend from the meta_data
            new_sentence = new_sentence.replace("<#trend_length#>", str(observation.meta_data.get("trend_duration")))

        if observation.pattern == "week":
            # add the week number from the meta_data
            new_sentence = new_sentence.replace("<#week#>", observation.week_number)

        if observation.pattern == "sector":
            # add the sector to the sentence
            new_sentence = new_sentence.replace("<#sector#>", observation.sector)

        return new_sentence
