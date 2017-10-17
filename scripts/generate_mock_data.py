#!/usr/local/bin/python3

"""
Mock data generator
"""

from random import choice, choices, uniform, normalvariate
from pymongo import MongoClient

def generate_random_data():
    """
    function
    """

    while True:
        yield {
            'body_temperature': round(normalvariate(37.3, 0.7), 1),
            'cough': choice((False, True)),
            'sore_throat': choice((False, True)),
            'nose': choice(('normal', 'runny', 'stiffy')),
            'body_ache': choice((False, True)),
            'headaches': choice((False, True)),
            'fatigue': choice((False, True)),
            'chill': choice((False, True))
        }

def filter_data(random_data_generator):
    """
    filter out unrealistic data
    """

    for datum in random_data_generator:
        if datum['body_temperature'] > uniform(37.6, 38.1) \
            and datum['headaches']:
            if uniform(0, 1) * datum['body_temperature'] / 36.8 < 0.7:
                continue
        if datum['cough'] != datum['sore_throat']:
            if uniform(0, 1) < 0.3:
                continue
        yield datum


def diagnose(symptoms) -> int:
    """
    diagnose symptoms
    """

    chance = 0
    if symptoms['body_temperature'] > uniform(37.6, 38.1):
        chance += 0.3
    if symptoms['cough']:
        chance += 0.2
    if symptoms['sore_throat']:
        chance += 0.2
    if symptoms['nose'] != 'normal':
        chance += 0.4
    if symptoms['body_ache']:
        chance += 0.1
    if symptoms['headaches']:
        chance += 0.2
    if symptoms['fatigue']:
        chance += 0.2
    if symptoms['chill']:
        chance += 0.2

    if symptoms['cough'] and symptoms['body_temperature'] > uniform(37.6, 38):
        chance += 0.2 * symptoms['body_temperature'] / 38
    if symptoms['cough'] and symptoms['nose'] != 'normal':
        chance += 0.2
    if symptoms['fatigue'] and symptoms['chill']:
        chance += 0.2

    if chance < 0.4:
        return 0
    else:
        return choices((0, 1), (0.1, chance))[0]


def generate_data():
    """
    generate data
    """

    for filtered_datum in filter_data(generate_random_data()):
        is_flu = diagnose(filtered_datum)
        yield {'symptoms': filtered_datum, 'result': is_flu}

if __name__ == '__main__':
    client = MongoClient('localhost', 27017)
    fit3036 = client.fit3036
    meta_data = fit3036.meta_data
    flu_data_train = fit3036.flu_data_train
    flu_data_test = fit3036.flu_data_test
    meta_data.delete_many({})
    flu_data_train.delete_many({})
    flu_data_test.delete_many({})

    meta_data.insert_many([
        {
            'symptom_name': 'body_temperature',
            'data_type': 'number'
        },
        {
            'symptom_name': 'cough',
            'data_type': 'boolean'
        },
        {
            'symptom_name': 'sore_throat',
            'data_type': 'boolean'
        },
        {
            'symptom_name': 'nose',
            'data_type': 'enum',
            'enum': ['normal', 'runny', 'stiffy']
        },
        {
            'symptom_name': 'body_ache',
            'data_type': 'boolean'
        },
        {
            'symptom_name': 'headaches',
            'data_type': 'boolean'
        },
        {
            'symptom_name': 'fatigue',
            'data_type': 'boolean'
        },
        {
            'symptom_name': 'chill',
            'data_type': 'boolean'
        }
    ])

    for entry, _ in zip(generate_data(), range(1000)):
        flu_data_train.insert_one(entry)

    for entry, _ in zip(generate_data(), range(1000)):
        flu_data_test.insert_one(entry)
