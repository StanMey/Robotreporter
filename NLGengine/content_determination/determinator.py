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
