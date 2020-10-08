from datetime import datetime
# from articles_app.models import Observations

class Observation:
    """[summary]
    """
    def __init__(self, serie: str, prd_begin: datetime, prd_end: datetime, pattern: str, obsrv: str, rlvnc: int):
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
        self.relevance = rlvnc

    def __str__(self):
        return self.observation
