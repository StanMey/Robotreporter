import json


class Determinator:
    def __init__(self, last_observ, all_observs: list, history: list):
        self.last_observ = last_observ
        self.all_observs = all_observs
        self.history = history

    def load_weights(self):
        with open(r"./NLGengine/content_determination/base.json") as f:
            self.weight_dict = json.load(f)

    def apply_rules(self, comp, patt, sect, period, week):
        weight = 0

        if period and not comp:
            weight += self.weight_dict.get("S_period_O_comp")
        if period and comp:
            weight += self.weight_dict.get("S_period_S_comp")
        if not period and comp:
            weight += self.weight_dict.get("O_period_S_comp")
        if week and not comp:
            weight += self.weight_dict.get("S_week_O_comp")
        if patt and week:
            weight += self.weight_dict.get("S_period_O_comp")
        if not patt and week:
            weight += self.weight_dict.get("S_pattern_S_week")
        if period and not comp:
            weight += self.weight_dict.get("O_pattern_S_week")
        if patt and period:
            weight += self.weight_dict.get("S_pattern_S_period")

        return weight

    def calculate_new_situational_relevance(self):
        self.load_weights()

        for observ in self.all_observs:
            if observ.pattern == "combi_pattern":
                same_component = int(self.last_observ.serie in observ.meta_data.get("component"))
            else:
                same_component = int(self.last_observ.serie == observ.serie)
            same_pattern = int(self.last_observ.pattern == observ.pattern)
            same_sector = 0
            same_period = int(self.last_observ.day_number == observ.day_number)
            same_week = int(self.last_observ.week_number == observ.week_number)

            alpha = self.apply_rules(same_component, same_pattern, same_sector, same_period, same_week)
            observ.relevance2 = observ.relevance1 + alpha
