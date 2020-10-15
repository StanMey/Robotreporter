from articles_app.nlg_queries import find_new_observations
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from NLGengine.observation import Observation
from NLGengine.analyse import Analyse

import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Run the daily analysis of the stocks"

    def handle(self, *args, **options):
        try:
            run_analysis()
        except Exception as e:
            print(f"Something went wrong:\n{e}")


def beurs_closed():
    """Check if the beurs is closed
    """
    today_day = datetime.today().weekday()
    if today_day in [0, 1, 6]:
        # on saturday and sunday night return True
        return True
    else:
        return False


def run_analysis():

    if beurs_closed():
        print("The beurs is closed")
    else:
        print("beurs open: commencing analysis!")

        # get date today and of yesterday
        current_day = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(1)
        prev_day = current_day - timedelta(1)

        # run the analysis
        find_new_observations(prev_day, current_day, to_prompt=True)
