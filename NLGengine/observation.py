from datetime import datetime


class Observation:
    """[summary]
    """
    def __init__(self, serie: str, prd_begin: datetime, prd_end: datetime, pattern: str, obsrv: str, rlvnc: int, m_data: dict):
        """[summary]

        Args:
            serie (str): [description]
            prd_begin (datetime): [description]
            prd_end (datetime): [description]
            pattern (str): [description]
            obsrv (str): [description]
            rlvnc (int): [description]
        """
        self.serie = serie
        self.period_begin = prd_begin
        self.period_end = prd_end
        self.pattern = pattern
        self.observation = obsrv
        # base relevance and situalional relevance
        self.relevance1 = rlvnc
        self.relevance2 = rlvnc  # 0.0
        self.meta_data = m_data

    def __str__(self):
        return self.observation
