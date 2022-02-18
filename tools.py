from difflib import SequenceMatcher
from datetime import datetime as dt
import random
import time
import json


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


# load config
def load_config(filepath='config.json'):
    with open(filepath, 'r') as config:
        information = json.loads(config.read())

    return information


# ignores case, checks if strings are similar
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


# get the time from two text strings
def string_to_unix_time(date_str=None, time_str=None):
    # make the date
    if date_str:
        date_time = dt.strptime(date_str, '%m/%d/%Y')
    else:
        # set the date to today
        date_time = dt.today()

    # set the time if there is a time string
    if time_str:
        stubs = time_str.split(':')

        # set the date time object piecewise
        date_time.replace(hour=int(stubs[0]), minute=int(stubs[1]))

    # once you have a datetime object, convert it to unix
    unix = time.mktime(date_time.timetuple())

    return unix
