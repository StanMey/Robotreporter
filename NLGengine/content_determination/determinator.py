import json


class Determinator:
    def __init__(self, last_observ, all_observs: list, history: list):
        self.last_observ = last_observ
        self.all_observs = all_observs
        self.history = history

    def load_weights(self):
        # array made with: (round(np.random.rand(7,7) * 2 - 1, 2))
        with open(r"./NLGengine/content_determination/weights.json") as f:
            self.weight_dict = json.load(f)

    def recalibrate_weights(self):
        pass

    def follow_up_weight(self, feature, previous, new):
        info = self.weight_dict.get(feature)
        index1 = info.get("index").index(previous)
        index2 = info.get("index").index(new)
        return info.get("matrix")[index1][index2]

    def calculate_new_situational_relevance(self):
        self.load_weights()

        for observ in self.all_observs:
            # if observ.pattern == "combi_pattern":
            #     same_component = int(self.last_observ.serie in observ.meta_data.get("component"))
            # else:
            #     same_component = int(self.last_observ.serie == observ.serie)
            pattern_weight = self.follow_up_weight("pattern", self.last_observ.pattern, observ.pattern)

            observ.relevance2 = observ.relevance1 + pattern_weight
