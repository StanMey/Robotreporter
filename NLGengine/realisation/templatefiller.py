import json
import os
import random as rd


class TemplateFiller:
    """[summary]
    """

    @staticmethod
    def retrieve_template_option(observation, t_source: str = r"NLGengine/realisation/templates.json", long_version: bool = False):
        """Returns one template from all the template sentences for the pattern of the given observation.

        Args:
            observation (NLGengine.observation.Observation): The observation for which the templates have to be retrieved
            t_source (str, optional): The path to the template json file. Defaults to r"NLGengine/realisation/templates.json"
            long_version (bool, optional): [description]. Defaults to False

        Returns:
            str: Returns the chosen template for the observation
        """
        assert os.path.exists(t_source), "template.json not found"  # check if templates.json exists

        with open(t_source) as f:
            data = json.load(f)

        if observation.pattern in ["combi-stijging", "combi-daling"]:
            # pattern is combi, so give templates with the right length
            if observation.meta_data.get("only_x"):
                # special combi pattern so get the corresponding template
                info = observation.meta_data.get("only_x")
                templates = data.get(observation.pattern).get("only_x").get(str(info))
            else:
                templates = data.get(observation.pattern).get(str(len(observation.meta_data.get("components"))))

        elif observation.pattern in ["week", "trend"]:
            # pattern must be checked on the pos/neg of the trend
            templates = data.get(observation.pattern).get(str(observation.meta_data.get("trend")))

        elif observation.pattern == "sector":
            meta = observation.meta_data
            # check if the long version is chosen
            if long_version:
                # select the long version
                templates = data.get(observation.pattern).get(meta.get("sector_spec")).get("long").get(meta.get("trend"))
            else:
                # short version
                templates = data.get(observation.pattern).get(meta.get("sector_spec")).get(meta.get("trend"))

        else:
            # return the pattern
            templates = data.get(observation.pattern)

        return rd.choice(templates)

    @staticmethod
    def insert_into_template(observation, template: str, repl_comp_desc: bool, descr_file: str = r"NLGengine/realisation/companyinfo.json"):
        """Inserts the information of the observation into the chosen template.

        Args:
            observation (NLGengine.observation.Observation): The observation to be used to fill in the template
            template_choices (str): A template string that has to be filled in
            repl_comp_desc (bool): Decides whether the description of a component will be filled in before the component
            descr_file (str, optional): The path to the comp info file. Defaults to r"NLGengine/realisation/companyinfo.json"

        Returns:
            str: Returns the filled in template string
        """
        # load in the json file with company info
        with open(descr_file) as f:
            info_dict = json.load(f)

        if observation.pattern in ["combi-stijging", "combi-daling"]:
            # observation has multiple components and percentages
            new_sentence = template

            if observation.meta_data.get("only_x") and not observation.meta_data.get("components"):
                # special combi pattern so fill in apart
                # replace the comp placeholder with the actual component
                new_sentence = new_sentence.replace("<#comp_name#>", get_comp_short(info_dict, observation.serie))
                # replace the percentage placeholder and choose the abs when necessary
                new_sentence = new_sentence.replace("<#perc#>", str(observation.perc_change))

            else:
                # get all components and percentages
                comps = observation.meta_data.get("components")
                percs = observation.meta_data.get("perc_change")

                # set up the template
                new_sentence = replace_multi_comp_tag(new_sentence, len(comps))
                # insert the components into the template
                short_comps = [get_comp_short(info_dict, x) for x in comps]
                new_sentence = insert_comps_in_template(new_sentence, short_comps, percs)

            # replace the indexx tag (if it exists)
            new_sentence = new_sentence.replace("<#indexx#>", str(observation.indexx))

        else:
            new_sentence = template
            # replace the comp placeholder with the actual component
            new_sentence = new_sentence.replace("<#comp_name#>", get_comp_short(info_dict, observation.serie))
            # replace the percentage placeholder and choose the abs when necessary
            new_sentence = new_sentence.replace("<#perc#>", str(observation.perc_change))
            new_sentence = new_sentence.replace("<#abs_perc#>", str(abs(observation.perc_change)))

        if observation.pattern == "trend":
            # add the duration of the trend from the meta_data
            new_sentence = new_sentence.replace("<#trend_length#>", str(observation.meta_data.get("trend_duration")))

        if observation.pattern == "week":
            # add the week number from the meta_data
            new_sentence = new_sentence.replace("<#week#>", str(observation.week_number))

        if observation.pattern == "sector":
            # add the sector to the sentence
            new_sentence = new_sentence.replace("<#sector#>", observation.sector)

            # get all components and percentages and fill in the rest of the multi components if the long version is chosen
            comps = observation.meta_data.get("components")
            percs = observation.meta_data.get("perc_change")

            # check the amount of other components in the sector
            if len(comps[1:]) == 1:
                # only one other component in the sector
                new_sentence = new_sentence.replace("<#sec_multi_word#>", "sectorgenoot")
            else:
                # two or more other components in the sector
                new_sentence = new_sentence.replace("<#sec_multi_word#>", "sectorgenoten")

            # set up the rest of the template, by replacing the multi comp tag with the appropriate sentence
            new_sentence = replace_multi_comp_tag(new_sentence, len(comps[1:]))
            # apply all the comps
            short_comps = [get_comp_short(info_dict, x) for x in comps[1:]]
            new_sentence = insert_comps_in_template(new_sentence, short_comps, percs[1:])

        # check if component replacement should be filled in
        if repl_comp_desc:
            new_sentence = new_sentence.replace(" <#comp_desc#>", get_comp_desc(info_dict, observation.serie))
        else:
            new_sentence = new_sentence.replace(" <#comp_desc#>", "")

        return new_sentence


def insert_comps_in_template(template: str, comps: list, percs: list):
    """Inserts the componenents and its percentages into the template.

    Args:
        template (str): The chosen template
        comps (list): A list of all the components
        percs (list): A list of all the percentages

    Returns:
        str: The filled in template
    """
    sentence = template

    # replace all components and percentages
    for comp, perc in zip(comps, percs):
        sentence = sentence.replace("<#comp_name#>", comp, 1)
        # replace the percentage with an absolute or a normal percentage
        sentence = sentence.replace("<#perc#>", str(perc), 1)
        sentence = sentence.replace("<#abs_perc#>", str(abs(perc)), 1)

    return sentence


# TODO dynamisch opbouwen van de multi comp tags
def replace_multi_comp_tag(template: str, comp_amount: int):
    """Replaces the multi components tag with the correct amount of individual comp and perc tags.

    Args:
        template (str): The template to be filled in
        comp_amount (int): The amount of components to be filled in

    Returns:
        str: The template with the replaced tags for the multi component tag
    """
    sentence = template
    if comp_amount == 1:
        # 1 components so set the correct multi_string template into the sentence
        multi_string = "<#comp_name#> (<#perc#>%)"
        sentence = template.replace("<#multi_comp#>", multi_string)

    elif comp_amount == 2:
        # 2 components so set the correct multi_string template into the sentence
        multi_string = "<#comp_name#> (<#perc#>%) en <#comp_name#> (<#perc#>%)"
        sentence = template.replace("<#multi_comp#>", multi_string)

    elif comp_amount == 3:
        # 3 components so set the correct multi_string template into the sentence
        multi_string = "<#comp_name#> (<#perc#>%), <#comp_name#> (<#perc#>%) en <#comp_name#> (<#perc#>%)"
        sentence = template.replace("<#multi_comp#>", multi_string)

    return sentence


def get_comp_short(info_dict: dict, comp: str):
    """Tries to find the short name of the given component in the dictionary,
    if not found just returns the original component's name

    Args:
        info_dict (dict): A dictionary which holds info about the short names of the components
        comp (str): The component for which the short name has to be found

    Returns:
        str: Returns the short name of the component or the original component
    """
    short = info_dict.get(comp).get("short")
    if short:
        return short
    else:
        return comp


def get_comp_desc(info_dict: dict, comp: str):
    """Tries to find the description of the given component in the dictionary,
    if not found returns an empty String

    Args:
        info_dict (dict): A dictionary which holds info about the descriptions of the components
        comp (str): The component for which the description has to be found

    Returns:
        str: Returns either the description or an empty string
    """
    desc = info_dict.get(comp).get("comp_desc")
    if desc:
        if desc[0] == ",":
            return desc
        else:
            return f" {desc}"
    else:
        return ""
