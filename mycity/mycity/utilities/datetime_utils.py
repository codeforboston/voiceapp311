"""
Utility functions related to Date and Time

"""

import datetime

import pytz


def get_day():
    """
    Function to get day of the week
    :return: A day of the week (Monday, Tuesday, etc)
    """
    utc = datetime.datetime.now(tz=pytz.UTC)
    my_tz = pytz.timezone('America/New_York')
    return utc.astimezone(my_tz).strftime('%A')
