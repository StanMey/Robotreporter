class Planner:
    def __init__(self, observs):
        self.observations = observs

    def plan(self):
        self.sort_on_date()

    def sort_on_date(self):
        self.observations = sorted(self.observations, key=lambda x: x.week_number, reverse=True)
