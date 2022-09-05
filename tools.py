from difflib import SequenceMatcher
from datetime import datetime as dt, timedelta
import random
import time
import json
import os

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday']


# make booleans out of probabilities
def probability_bool_generator(probability):
    rand_prob = random.random()

    if probability > rand_prob:
        decision = True
    else:
        decision = False

    return decision


# make random waiting function
def wait_random(min_wait, max_wait):
    rand_time = random.uniform(min_wait, max_wait)

    time.sleep(rand_time)


# get the filepath of a random image
def random_image(folder):
    # get all the files in the folder
    files = [f for f in os.listdir(
        folder) if os.path.isfile(os.path.join(folder, f))]

    return random.choice(files)


# load config
def load_config(filepath='config.json'):
    with open(filepath, 'r') as config:
        information = json.loads(config.read())

    return information


# ignores case, checks if strings are similar
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# make a function to get the date from a recent weekday
def date_from_recent_weekday(weekday_str):
    # strip and convert the text to titlecase to get accepted by the string interpreter
    weekday_str = weekday_str.strip().title()

    # get today
    today = dt.today()

    # get today's weekday
    today_weekday_int = today.weekday()

    # convert the string into a weekday int
    weekday_int = DAYS_OF_WEEK.index(weekday_str)

    # get the elapsed number of days
    elapsed_days = today_weekday_int - weekday_int

    # handle for the negative case (wraparound)
    if elapsed_days < 0:
        # add 8 (works mathematically)
        elapsed_days += 7

    # subtract the number of days using a timedelta
    date = today - timedelta(days=elapsed_days)

    # return the actual date
    return date


# get the time from text strings
def string_to_unix_time(date_str=None, weekday_str=None, time_str=None):
    # make the date
    if date_str:
        date_time = dt.strptime(date_str, '%m/%d/%Y')
    elif weekday_str:
        # make a weekday with the strptime
        date_time = date_from_recent_weekday(weekday_str)
    else:
        # set the date to today
        date_time = dt.today()

    # set the time if there is a time string
    if time_str:
        stubs = time_str.split(':')

        # set the date time object piecewise
        date_time = date_time.replace(hour=int(stubs[0]), minute=int(stubs[1]))

    # once you have a datetime object, convert it to unix
    unix = time.mktime(date_time.timetuple())

    return unix


# make a standardized string for the current time
def format_time(now=None):
    if not now:
        now = dt.now()

    # create the string
    time_string = now.strftime("%m-%d-%Y---%H-%M-%S")

    return time_string
