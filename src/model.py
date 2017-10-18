from time import time
from hashlib import md5
from os.path import dirname, realpath
import json

import numpy as np
import tensorflow as tf
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
fit3036 = client.fit3036
model_collection = fit3036.model
meta_collection = fit3036.meta
train_collection = fit3036.train
test_collection = fit3036.test


def get_classifier(symptom_keys_itr):
    symptom_key_list = list(symptom_keys_itr)
    symptom_key_list.sort()
    model_name = md5(json.dumps(symptom_key_list).encode('utf-8')).hexdigest()
    model_datum = model_collection.find_one({'name': model_name})

    if model_datum is None:
        model_datum = {
            'name': model_name,
            'symptom_keys': symptom_key_list,
            'timestamp': 0,
            'accuracy': 0,
            'accuracy_timestamp': 0
        }
        model_collection.insert_one(model_datum)
    symptom_keys = model_datum['symptom_keys']

    symptom_meta = {key: meta_collection.find_one({'symptom_name': key}) for key in symptom_keys}
    # Specify that all features have real-value data
    feature_columns = [
        tf.feature_column.numeric_column(
            'x',
            shape=[len(symptom_keys)]
        )
    ]

    timestamp = time()
    train_collection_query = {
        'timestamp': {
            '$lte': timestamp,
            '$gt': model_datum['timestamp']
        }
    }
    for key in symptom_keys:
        train_collection_query['symptoms.{}'.format(key)] = {'$exists': True}
    train_data = train_collection.find(train_collection_query)

    training_x = []
    training_y = []
    for datum in train_data:
        symptoms_ref = datum['symptoms']
        training_x.append([symptoms_ref[key] for key in symptom_keys])
        training_y.append(datum['result'])

    # Build 4 layer DNN with 10, 20, 20, 10 units respectively.
    classifier = tf.estimator.DNNClassifier(
        feature_columns=feature_columns,
        hidden_units=[10, 20, 20, 10],
        n_classes=2,
        model_dir='{}/models/{}'.format(dirname(dirname(realpath(__file__))), model_name)
    )

    if len(training_x) > 0:
        # Define the training inputs
        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={'x': np.array(training_x)},
            y=np.array(training_y),
            num_epochs=1,
            shuffle=False
        )

        # Train model.
        classifier.train(input_fn=train_input_fn)

        model_collection.update_one(
            {'name': model_name},
            {'$set': {
                'timestamp': timestamp
            }}
        )

    return classifier, symptom_key_list


def predict(symptoms):
    classifier, key_list = get_classifier(tuple(symptoms.keys()))
    symptom_nums = [symptoms[key] for key in key_list]

    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'x': np.array([symptom_nums])},
        num_epochs=1,
        shuffle=False
    )
    for prediction in classifier.predict(test_input_fn):
        probabilities = prediction.get('probabilities')

        return {
            'no': float(probabilities[0]),
            'yes': float(probabilities[1])
        }


def accuracy(symptom_keys_itr) -> float:
    timestamp = time()
    key_list = list(symptom_keys_itr)
    key_list.sort()
    print(key_list)

    model_name = md5(json.dumps(key_list).encode('utf-8')).hexdigest()
    model_datum = model_collection.find_one({'name': model_name})
    print(model_datum)
    if model_datum is not None:
        print(model_datum['accuracy_timestamp'] > timestamp - 60 * 60 * 24)
    if model_datum is not None and model_datum['accuracy_timestamp'] > timestamp - 60 * 60 * 24:
        return model_datum['accuracy']

    classifier, _ = get_classifier(key_list)

    test_collection_filter = {}
    for key in key_list:
        test_collection_filter['symptoms.{}'.format(key)] = {'$exists': True}
    train_data = train_collection.aggregate([
        {'$match': test_collection_filter},
        {'$sample': {'size': 1000}}
    ])
    test_data = test_collection.find(test_collection_filter)

    testing_x = []
    testing_y = []
    for datum in test_data:
        symptoms_ref = datum['symptoms']
        testing_x.append([symptoms_ref[key] for key in key_list])
        testing_y.append(datum['result'])

    test_input_fn = tf.estimator.inputs.numpy_input_fn(
        x={'x': np.array(testing_x)},
        y=np.array(testing_y),
        num_epochs=1,
        shuffle=False
    )

    accuracy_score = float(classifier.evaluate(test_input_fn)['accuracy'])
    print(accuracy_score)

    model_collection.update_one(
        {'name': model_name},
        {'$set': {'accuracy': accuracy_score, 'accuracy_timestamp': timestamp}}
    )

    return accuracy_score
