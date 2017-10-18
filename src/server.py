from time import time
from random import choices

from flask import Flask, request, jsonify
from flask_cors import CORS

import model
from server_utilities.exceptions import InvalidInput

app = Flask(__name__)
CORS(app)

@app.route('/predict', methods = ['POST'])
def predict():
    payload = request.get_json(force=True)

    for key, item in payload.items():
        datum = model.meta_collection.find_one({'name': key})

        # TODO: better error handling
        if datum is None:
            raise InvalidInput(data={'message': 'invalid symptom name: {}'.format(key)})
        # if datum['type'] == 'binary':
        #     raise InvalidInput(data={'message': 'invalid input'})

    return jsonify(model.predict(payload))


@app.route('/symptoms', methods = ['GET'])
def get_symptoms():
    cursor = model.meta_collection.find({})
    meta = []
    for datum in cursor:
        meta.append({'name': datum['name'], 'type': datum['type']})
    return jsonify(meta)


@app.route('/add_symptom', methods = ['POST'])
def add_symptoms():
    payload = request.get_json(force=True)
    try:
        symptom_name = payload['symptom_name']
        data_type = payload['data_type']
        if data_type not in ['binary', 'numeric']:
            raise InvalidInput()
    except KeyError:
        raise InvalidInput()

    entry = model.meta_collection.find_one({'symptom_name': symptom_name})
    if entry is not None:
        raise InvalidInput(data={'message': 'symptom already exists'})

    model.meta_collection.insert_one({
        'symptom_name': symptom_name,
        'data_type': data_type
    })


@app.route('/accuracy', methods = ['POST'])
def accuracy():
    payload = request.get_json(force=True)
    rate = model.accuracy(payload)
    return jsonify({'accuracy': rate})


@app.route('/add_knowledge', methods = ['POST'])
def add_knowledge():
    payload = request.get_json(force=True)
    try:
        symptoms = payload['symptoms']
        timestamp = time()
        result = payload['result']
        if result == 'yes':
            result = 1
        elif result == 'no':
            result = 0
        else:
            raise InvalidInput()
    except KeyError:
        raise InvalidInput()

    entry = {
        'symptoms': symptoms,
        'timestamp': timestamp,
        'result': result
    }
    if choices([True, False], [1, 5])[0]:
        model.test_collection.insert_one(entry)
    else:
        model.train_collection.insert_one(entry)

    return jsonify({})


@app.errorhandler(InvalidInput)
def handle_invalid_usage(error):
    response = jsonify(error.data)
    response.status_code = error.status_code
    return response

if __name__ == '__main__':
    app.run()
