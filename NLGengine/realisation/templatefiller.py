import json
import os


class TemplateFiller:
    """[summary]
    """

    @staticmethod
    def find_template_options(observation, t_source: str = r"NLGengine/realisation/templates.json"):
        """Returns the template sentences for the pattern of the given observation.

        Args:
            observation (NLGengine.observation.Observation): The observation for which the templates have to be retrieved
            t_source (str): The path to the template json file

        Returns:
            list: Returns a list with possible templates for the given observations
        """
        assert os.path.exists(t_source), "template.json not found"  # check if templates.json exists

        with open(t_source) as f:
            data = json.load(f)

        if observation.pattern in ["combi-stijging", "combi-daling"]:
            # pattern is combi, so give templates with the right length
            templates = data.get(observation.pattern).get(str(observation.meta_data.get("components")))

        elif observation.pattern in ["week", "trend"]:
            # pattern must be checked on the pos/neg of the trend
            templates = data.get(observation.pattern).get(str(observation.meta_data.get("trend")))

        elif observation.pattern == "sector":
            # check if the whole_sector or one component is chosen
            # TODO add identifer for particular sector pattern
            pass

        else:
            # return the pattern
            templates = data.get(observation.pattern)

        return templates

    @staticmethod
    def insert_into_template(observation, template_choices):
        """[summary]

        Args:
            observation (NLGengine.observation.Observation): [description]
            template_choices ([type]): [description]

        Returns:
            [type]: [description]
        """

        return 1
