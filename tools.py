from difflib import SequenceMatcher
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
