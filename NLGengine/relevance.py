import numpy as np


class Relevance:
    """A class that holds static methods that help calculating the relevance.
    """

    @staticmethod
    def tanh(x):
        """Runs the tanh function over a value.

        Args:
            x (float): The value over which the tanh function has to be run

        Returns:
            float: The outcome of the function
        """
        return np.tanh(x)

    @staticmethod
    def period_single_relevance(perc, factor=0.37, multi=10.0):
        """Calculates the relevance on a period. 1.6% change, gets 5.0 points

        Args:
            perc (float): The change in percentage.
            factor (float, optional): Flattens the curve of the tanh function to control the 5.0 points value. Defaults to 0.37.
            multi (float, optional): Multiplies the outcome by a number. Defaults to 10.0.

        Returns:
            float: The outcome of the function
        """
        return min(10.0, Relevance.tanh(abs(perc) * factor) * multi)

    @staticmethod
    def period_combi_relevance(diff_perc, factor=1.09, multi=10.0):
        """Calculates the relevance on a period for a combi pattern. 0.5% mean difference change, gets 5.0 points

        Args:
            diff_perc (float): The absolute difference between two percentages.
            factor (float, optional): Flattens the curve of the tanh function to control the 5.0 points value. Defaults to 1.09.
            multi (float, optional): Multiplies the outcome by a number. Defaults to 10.0.

        Returns:
            float: The outcome of the function
        """
        return min(10.0, (1 - Relevance.tanh(abs(diff_perc) * factor)) * multi)

    @staticmethod
    def weekly_relevance(perc, factor=0.092, multi=10.0):
        """Calculates the relevance over a week. 6.0% change, gets 5.0 points

        Args:
            perc (float): The change in percentage.
            factor (float, optional): Flattens the curve of the tanh function to control the 5.0 points value. Defaults to 0.092.
            multi (float, optional): Multiplies the outcome by a number. Defaults to 10.0.

        Returns:
            float: The outcome of the function
        """
        return min(10.0, Relevance.tanh(abs(perc) * factor) * multi)

    @staticmethod
    def trend_relevance(trend, factor=5.4, multi=10.0):
        """Calculates the relevance over a trend. 3 days, gets 5.0 points

        Args:
            trend (int): The duration of the trend in days.
            factor (float, optional): Flattens the curve of the tanh function to control the 5.0 points value. Defaults to 5.4.
            multi (float, optional): Multiplies the outcome by a number. Defaults to 10.0.

        Returns:
            float: The outcome of the function
        """
        return min(10.0, Relevance.tanh(trend / factor) * multi)

    # TODO make graph for choice of factor
    @staticmethod
    def whole_sector_relevance(perc, factor=0.14, multi=10.0):
        """Calculates the relevance over all the component in the sector.

        Args:
            perc (float): The mean change in percentage off all components in the sector.
            factor (float, optional): Flattens the curve of the tanh function to control the 5.0 points value. Defaults to 0.14.
            multi (float, optional): Multiplies the outcome by a number. Defaults to 10.0.

        Returns:
            float: The outcome of the function
        """
        return min(10.0, Relevance.tanh(abs(perc) * factor) * multi)

    # TODO make graph for choice of factor
    @staticmethod
    def one_comp_sector_relevance(diff_perc, factor=0.28, multi=10.0):
        """Calculates the relevance of one component against mean of the other components in the sector. difference of 2.0, gets 5.0 points

        Args:
            diff_perc (float): The absolute change in percentage between the component and the mean of its peers.
            factor (float, optional): Flattens the curve of the tanh function to control the 5.0 points value. Defaults to 0.28.
            multi (float, optional): Multiplies the outcome by a number. Defaults to 10.0.

        Returns:
            float: The outcome of the function
        """
        return min(10.0, Relevance.tanh(abs(diff_perc) * factor) * multi)
