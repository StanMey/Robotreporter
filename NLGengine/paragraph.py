class Paragraph:
    """A paragraph class that holds all observations belonging to a certain paragraph
    contains 3 to 5 observations
    """
    def __init__(self, observations: list):
        """The init function of the paragraph

        Args:
            observations (list): A list with all the observations in the paragraph
        """
        self.observations = observations
