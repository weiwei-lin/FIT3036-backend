"""
Mock data generator
"""

from random import choice, choices, uniform, normalvariate

def generate_random_data():
    """
    function
    """

    while True:
        yield (
            round(normalvariate(37.3, 0.7), 1), # body_temperature
            choice((0, 1)), # Cough
            choice((0, 1)), # Sore Throat
            choice((0, 1)), # Runny/Sniffy Nose
            choice((0, 1)), # Body/Muscle Ache
            choice((0, 1)), # Headaches
            choice((0, 1)), # Fatigue
            choice((0, 1))  # Chill
        )

def filter_data(random_data_generator):
    """
    filter out unrealistic data
    """

    for datum in random_data_generator:
        body_temperature, cough, sore_throat, runny_nose, body_ache, headaches, fatigue, chill = datum
        if body_temperature > uniform(37.6, 38.1) and headaches == 0:
            if uniform(0, 1) * body_temperature / 36.8 < 0.7:
                continue
        if cough != sore_throat:
            if uniform(0, 1) < 0.3:
                continue
        yield datum


def diagnose(symptoms) -> int:
    """
    diagnose symptoms
    """

    body_temperature, cough, sore_throat, runny_nose, body_ache, headaches, fatigue, chill = symptoms

    chance = 0
    if body_temperature > uniform(37.6, 38.1):
        chance += 0.3
    if cough == 1:
        chance += 0.1
    if sore_throat == 1:
        chance += 0.1
    if runny_nose == 1:
        chance += 0.2
    if body_ache == 1:
        chance += 0.05
    if headaches == 1:
        chance += 0.
    if fatigue == 1:
        chance += 0.1
    if chill == 1:
        chance += 0.1

    if cough == 1 and body_temperature > uniform(37.6, 38.1):
        chance += 0.1 * body_temperature / 38
    if cough == 1 and runny_nose == 1:
        chance += 0.2
    if fatigue == 1 and chill == 1:
        chance += 0.1

    if chance < 0.6:
        return 0
    else:
        return choices((0, 1), (0.1, chance))[0]


def generate_data():
    """
    generate data
    """

    for filtered_datum in filter_data(generate_random_data()):
        is_flu = diagnose(filtered_datum)
        yield filtered_datum, is_flu

if __name__ == '__main__':
    import csv

    with open('training.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for (features, result), _ in zip(generate_data(), range(1000)):
            writer.writerow(features + (result,))

    with open('testing.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for (features, result), _ in zip(generate_data(), range(100)):
            writer.writerow(features + (result,))
