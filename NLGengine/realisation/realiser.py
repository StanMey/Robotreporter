from NLGengine.realisation.date_message import DateMessage


class Realiser:
    def __init__(self, observations):
        self.observs = observations
        self.is_current = False

    def realise(self):
        self.add_time_to_observs()

    def add_time_to_observs(self):

        curr_week = self.observs[0].week_number
        curr_day = self.observs[0].day_number

        count = 0
        for observ in self.observs:
            if count == 0:
                # first sentence
                observ.observation = f"Op {observ.day_number} {DateMessage.month_to_string(observ.month_number)} {observ.observation}"

            else:
                if observ.week_number == curr_week:

                    if observ.day_number == curr_day:
                        observ.observation = f"{DateMessage.day_difference_to_string(0, self.is_current)} {observ.observation}"
                    else:
                        delta = curr_day - observ.day_number
                        observ.observation = f"{DateMessage.day_difference_to_string(delta, self.is_current)} {observ.observation}"
                        curr_day = observ.day_number
                else:
                    delta = curr_week - observ.week_number
                    observ.observation = f"{DateMessage.week_difference_to_string(delta, self.is_current)} {observ.observation}"
                    curr_week = observ.week_number
            count += 1
