from datetime import datetime


class Observation:
    """An object for storing an observation.
    """
    def __init__(self, serie: str, prd_begin: datetime, prd_end: datetime, pattern: str, sector: str, indexx: str,
                 perc: float, absp: float, obsrv: str, rlvnc: int, m_data: dict, oid: int = None):
        """The init method.

        Args:
            serie (str): The name of the main component
            prd_begin (datetime): The beginning of the period of the observation
            prd_end (datetime): The end of the period of the observation
            pattern (str): The name of the pattern
            sector (str): The sector corresponding to the main component
            indexx (str): The indexx of the component
            perc (float): The percentage change of the observation
            absp (float): The absolute change of the observation
            obsrv (str): The observation string
            rlvnc (int): The original relevance score
            m_data (dict): Extra meta data
            oid (int, optional): The id of the observation in the database. Defaults to None.
        """
        self.observ_id = oid
        self.serie = serie
        self.period_begin = prd_begin
        self.period_end = prd_end

        # extra data about the period
        self.year = self.period_end.year
        self.month_number = self.period_end.month
        self.week_number = self.period_end.isocalendar()[1:2][0]
        self.day_number = self.period_end.day

        # base information
        self.pattern = pattern
        self.sector = sector
        self.indexx = indexx
        self.observation = obsrv
        self.perc_change = perc
        self.abs_change = absp

        # base relevance and situational relevance
        self.relevance1 = rlvnc
        self.relevance2 = rlvnc

        self.meta_data = m_data

    def __str__(self):
        return self.observation
