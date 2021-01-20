from django.core.management.base import BaseCommand
from articles_app.data_helper_functions import update_observs
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = "Runs the analysis and either finds new observations or updates current ones (default = 14 days)"

    def add_arguments(self, parser):
        # Optional argument
        parser.add_argument('-d', '--days', type=int, help='Amount of days untill now in the period')

    def handle(self, *args, **kwargs):
        days = kwargs['days']

        try:
            # get the period span
            period_end = datetime.now().replace(hour=00, minute=00, second=00, microsecond=0)

            # check for extra argument
            if days:
                period_begin = period_end - timedelta(days)
            else:
                period_begin = period_end - timedelta(14)
            # run the update observations function
            update_observs(period_begin, period_end)

        except Exception as e:
            print(e)
