from flask import Flask, request, jsonify
from flask_cors import CORS

from predict import predict

app = Flask(__name__)
CORS(app)

@app.route('/predict')
def main():
    body_temperature = float(request.args.get('body_temperature'))
    cough = int(request.args.get('cough'))
    sore_throat = int(request.args.get('sore_throat'))
    runny_nose = int(request.args.get('runny_nose'))
    body_ache = int(request.args.get('body_ache'))
    headaches = int(request.args.get('headaches'))
    fatigue = int(request.args.get('fatigue'))
    chill = int(request.args.get('chill'))

    return jsonify(predict([body_temperature, cough, sore_throat, runny_nose, body_ache, headaches, fatigue, chill]))

@app.route('/symptoms')
def get_symptoms():
    symptoms = {
        'body_temperature': {
            'name': 'Body Temperature',
            'type': 'numeric'
        },
        'cough': {
            'name': 'cough',
            'name': 'Cough',
            'type': 'binary'
        },
        'sore_throat': {
            'name': 'Sore Throat',
            'type': 'binary'
        },
        'runny_nose': {
            'name': 'Runny Nose',
            'type': 'binary'
        },
        'body_ache': {
            'name': 'Body Ache',
            'type': 'binary'
        },
        'headaches': {
            'name': 'Headaches',
            'type': 'binary'
        },
        'fatigue': {
            'name': 'Fatigue',
            'type': 'binary'
        },
        'chill': {
            'name': 'Chill',
            'type': 'binary'
        }
    }
    return jsonify(symptoms)

if __name__ == '__main__':
    app.run()
