import json


class Determinator:
    def __init__(self, last_observ, all_observs: list, history: list):
        self.last_observation = last_observ
        self.all_observations = all_observs
        self.history = history

    def load_weights(self):
        """Loads in the weights from json.
        """
        # array made with: (round(np.random.rand(7,7) * 2 - 1, 2))
        with open(r"./NLGengine/content_determination/weights.json") as f:
            self.weight_dict = json.load(f)

    def recalibrate_weights(self):
        pass

    def follow_up_weight(self, previous, new):
        """[summary]

        Args:
            previous ([type]): [description]
            new ([type]): [description]

        Returns:
            [type]: [description]
        """
        pattern_info = self.weight_dict.get("pattern")
        pattern_weight = pattern_info.get("matrix")[pattern_info.get("index").index(previous.pattern)][pattern_info.get("index").index(new.pattern)]

        week_weight = self.weight_dict.get("week").get("matrix")[int(previous.week_number == new.week_number)]
        day_weight = self.weight_dict.get("day").get("matrix")[int(previous.day_number == new.day_number)]

        return pattern_weight + week_weight + day_weight

    def reset_situational_relevance(self):
        """Reset the situational relevance of all observations before a new selection round.
        """
        for observ in self.all_observations:
            observ.relevance2 = observ.relevance1

    def calculate_new_situational_relevance(self):
        """[summary]
        """
        self.reset_situational_relevance()
        self.load_weights()
        self.apply_rules()

        for observ in self.filtered_observations:
            sit_weight = self.follow_up_weight(self.last_observation, observ)

            observ.relevance2 = observ.relevance1 + sit_weight

    def get_highest_relevance(self):
        """Gets the hightest situational relevance from the filtered observations
        and filters this observation from all observations.
        """
        # order the filtered observations
        ordered_observs = sorted(self.filtered_observations, key=lambda x: x.relevance2, reverse=True)
        # select the one with the highest situational relevance
        chosen_observ = ordered_observs.pop(0)
        # remove this observation from all observations
        self.all_observations = list(filter(lambda x: x.observ_id != chosen_observ.observ_id, self.all_observations))
        return chosen_observ

    def apply_rules(self):
        """Apply some predeterment rules to avoid certain combinations of patterns.
        """
        self.filtered_observations = self.all_observations

        current_patterns = [x.pattern for x in self.history]

        # rule 1. Individu-stijging can occur after combi-stijging, only if there is no duplication of data
        if "combi-stijging" in current_patterns:
            # get the components in the combi observation
            ob = next(i for i in self.history if i.pattern == "combi-stijging")
            comps = ob.meta_data.get("components") if ob.meta_data.get("components") is not None else [ob.serie]
            # remove all the individu-stijging observations with those series
            self.filtered_observations = list(filter(lambda x: (x.pattern != "individu-stijging") and (x.serie not in comps), self.filtered_observations))

        # rule 2. Individu-daling can occur after combi-daling, only if there is no duplication of data
        if "combi-daling" in current_patterns:
            # get the components in the combi observation
            comps = next(i for i in self.history if i.pattern == "combi-daling")
            comps = ob.meta_data.get("components") if ob.meta_data.get("components") is not None else [ob.serie]
            # remove all the individu-daling observations with those series
            self.filtered_observations = list(filter(lambda x: (x.pattern != "individu-daling") and (x.serie not in comps), self.filtered_observations))

        # # rule 3. After 2 individual increases a new pattern
        # if len(self.history) >= 2 and all(x.pattern == "individu-stijging" for x in self.history[-2:]):
        #     self.filtered_observations = list(filter(lambda x: x.pattern != "individu-stijging", self.filtered_observations))

        # # rule 4. After 2 individual decreases a new pattern
        # if len(self.history) >= 2 and all(x.pattern == "individu-daling" for x in self.history[-2:]):
        #     self.filtered_observations = list(filter(lambda x: x.pattern != "individu-daling", self.filtered_observations))

        # # rule 5. After 3 individual increases and decreases skip this pattern
        # if current_patterns.count("individu-daling") >= 3:
        #     self.filtered_observations = list(filter(lambda x: x.pattern != "individu-daling", self.filtered_observations))

        # if current_patterns.count("individu-stijging") >= 3:
        #     self.filtered_observations = list(filter(lambda x: x.pattern != "individu-stijging", self.filtered_observations))
