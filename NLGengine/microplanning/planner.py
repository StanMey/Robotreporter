class Planner:
    """[summary]
    """
    def __init__(self, pars: list):
        """[summary]

        Args:
            pars (list): [description]
        """
        self.paragraphs = pars

    def plan(self):
        """[summary]
        """
        self.sort_on_date()
        self.sort_paragraphs()

    def sort_paragraphs(self):
        """Sorts the paragraphs based on the first observation in the paragraph.
        """
        self.paragraphs.sort(key=lambda x: x.observations[0].period_end, reverse=True)

    def sort_on_date(self):
        """Sorts the observations within the paragraphs on date.
        """
        for par in self.paragraphs:
            par.observations = sorted(par.observations, key=lambda x: (x.year, x.month_number, x.week_number, x.day_number), reverse=True)
