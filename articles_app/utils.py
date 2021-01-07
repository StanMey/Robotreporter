from datetime import date, datetime, timedelta


def is_view_only(user):
    """Checks if an user has view only rights

    Args:
        user (django.utils.functional.SimpleLazyObject): An user object containing information about the user that made the request

    Returns:
        Bool: Returns whether the user has view_only rights
    """
    return user.groups.filter(name='view_only').exists()


def retrieve_filterable_months(in_text):
    """Gets the names of the current month and the last 2 months before that if in_text is True,
    otherwise returns a tuple_pair (month, year) with the same info

    Args:
        in_text (bool): Decides if the months are to be displayed numerical of in text

    Returns:
        list: returns the textual form of the months if 'in_text' is True, otherwise returns a tuple pair with the month and year
    """
    # get the current month and year in a tuple (month, year)
    current = (datetime.now().month, datetime.now().year)

    # get 2 previous months
    if current[0] == 2:
        last_month = (1, current[1])
        last_last_month = (12, current[1] - 1)
    elif current[0] == 1:
        last_month = (12, current[1] - 1)
        last_last_month = (11, current[1] - 1)
    else:
        last_month = (current[0] - 1, current[1])
        last_last_month = (current[0] - 2, current[1])

    filter_months = [current, last_month, last_last_month]

    if in_text:
        numb_to_month = {
            1: "januari",
            2: "februari",
            3: "maart",
            4: "april",
            5: "mei",
            6: "juni",
            7: "juli",
            8: "augustus",
            9: "september",
            10: "oktober",
            11: "november",
            12: "december"
        }
        return [numb_to_month.get(x) for (x, _) in filter_months]
    else:
        return filter_months


def get_period_range(period_filters):
    """Gets the greatest range based on the filters.

    Args:
        filters list: The filters that has been chosen for the selection of the Observations

    Returns:
        Tuple: A tuple containing the min and max date of the period range
    """
    all_dates = []
    # get the months on which can be filtered
    text_months = retrieve_filterable_months(True)
    date_months = retrieve_filterable_months(False)
    # get the current week
    week = datetime.now().isocalendar()[:2]

    # check for each month if it has to be filtered on
    if text_months[0] in period_filters:
        # this month has to be filtered upon
        y = date_months[0][1]
        m = date_months[0][0]
        ndays = days_in_month(y, m)
        d1 = datetime(y, m, 1)
        d2 = datetime(y, m, ndays)
        all_dates.append((d1, d2))

    if text_months[1] in period_filters:
        # this month has to be filtered upon
        y = date_months[1][1]
        m = date_months[1][0]
        ndays = days_in_month(y, m)
        d1 = datetime(y, m, 1)
        d2 = datetime(y, m, ndays)
        all_dates.append((d1, d2))

    if text_months[2] in period_filters:
        # this month has to be filtered upon
        y = date_months[2][1]
        m = date_months[2][0]
        ndays = days_in_month(y, m)
        d1 = datetime(y, m, 1)
        d2 = datetime(y, m, ndays)
        all_dates.append((d1, d2))

    if "deze week" in period_filters:
        # filter on this week
        mon_date = datetime.strptime(f"{week[0]}-W{week[1]}" + '-1', '%G-W%V-%u')
        fri_date = mon_date + timedelta(4)
        all_dates.append((mon_date, fri_date))

    if "vorige week" in period_filters:
        # TODO correct for new year
        # filter on last week
        mon_date = datetime.strptime(f"{week[0]}-W{week[1] - 1}" + '-1', '%G-W%V-%u')
        fri_date = mon_date + timedelta(4)
        all_dates.append((mon_date, fri_date))

    if "vorige dag" in period_filters:
        # filter based on last day
        current_date = datetime.now().replace(hour=00, minute=00, second=00, microsecond=0)
        if current_date.weekday() == 5:
            last = current_date - timedelta(1)
        elif current_date.weekday() == 6:
            last = current_date - timedelta(2)
        else:
            last = current_date - timedelta(1)
        all_dates.append((last - timedelta(1), last))

    if "2 dagen geleden" in period_filters:
        # filter based on 2 days ago
        current_date = datetime.now().replace(hour=00, minute=00, second=00, microsecond=0)
        if current_date.weekday() == 5:
            last = current_date - timedelta(2)
        elif current_date.weekday() == 6:
            last = current_date - timedelta(3)
        else:
            last = current_date - timedelta(2)
        all_dates.append((last - timedelta(1), last))

    # get the max and min date over all dates
    max_date = max([x for (_, x) in all_dates])
    min_date = min([x for (x, _) in all_dates])
    return (min_date, max_date)


def days_in_month(year: int, month: int):
    """Calculate the amount of days in a certain month in a certain year

    Args:
        year (int): The year as integer
        month (int): The month as integer

    Returns:
        int: Returns the amount of days in the month
    """
    if month == 12:
        # use january as the next month and increase the year
        ndays = (date(year + 1, 1, 1) - date(year, 12, 1)).days
    else:
        # calculate the days between this month and the first of the next month
        ndays = (date(year, month + 1, 1) - date(year, month, 1)).days
    return ndays
