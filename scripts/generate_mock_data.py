#!/usr/local/bin/python3

"""
Mock data generator
"""

from random import choice, choices, uniform, normalvariate
from time import time
from pymongo import MongoClient


def generate_random_data():
    while True:
        yield {
            'body_temperature': round(normalvariate(37.3, 0.7), 1),
            'cough': choice((0, 1)),
            'sore_throat': choice((0, 1)),
            'runny_nose': choice((0, 1)),
            'body_ache': choice((0, 1)),
            'headaches': choice((0, 1)),
            'fatigue': choice((0, 1)),
            'chill': choice((0, 1))
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
        if datum['body_temperature'] < 36:
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
    if symptoms['runny_nose']:
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
    if symptoms['cough'] and symptoms['runny_nose']:
        chance += 0.2
    if symptoms['fatigue'] and symptoms['chill']:
        chance += 0.2

    if chance < 0.4:
        return 0
    else:
        return choices((0, 1), (max(1 - chance, 0), chance))[0]


def generate_data():
    """
    generate data
    """

    for filtered_datum in filter_data(generate_random_data()):
        is_flu = diagnose(filtered_datum)
        yield {'symptoms': filtered_datum, 'result': is_flu, 'timestamp': time()}


def main():
    client = MongoClient('localhost', 27017)
    fit3036 = client.fit3036
    meta_collection = fit3036.meta
    train_collection = fit3036.train
    test_collection = fit3036.test
    meta_collection.delete_many({})
    train_collection.delete_many({})
    test_collection.delete_many({})

    meta_collection.insert_many([
        {
            'name': 'body_temperature',
            'type': 'numeric'
        },
        {
            'name': 'cough',
            'type': 'binary'
        },
        {
            'name': 'sore_throat',
            'type': 'binary'
        },
        {
            'name': 'runny_nose',
            'type': 'binary'
        },
        {
            'name': 'body_ache',
            'type': 'binary'
        },
        {
            'name': 'headaches',
            'type': 'binary'
        },
        {
            'name': 'fatigue',
            'type': 'binary'
        },
        {
            'name': 'chill',
            'type': 'binary'
        }
    ])

    for entry, _ in zip(generate_data(), range(1000000)):
        train_collection.insert_one(entry)

    for entry, _ in zip(generate_data(), range(200000)):
        test_collection.insert_one(entry)

if __name__ == '__main__':
    main()
