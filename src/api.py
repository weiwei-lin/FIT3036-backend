from flask import Flask, request, jsonify
from flask_cors import CORS

from predict import predict

app = Flask(__name__)
CORS(app)

@app.route('/')
def main():
    body_temperature = float(request.args.get('body_temperature'))
    cough = int(request.args.get('cough'))
    sore_throat = int(request.args.get('sore-throat'))
    runny_nose = int(request.args.get('runny-nose'))
    body_ache = int(request.args.get('body-ache'))
    headaches = int(request.args.get('headaches'))
    fatigue = int(request.args.get('fatigue'))
    chill = int(request.args.get('chill'))

    return jsonify(predict([body_temperature, cough, sore_throat, runny_nose, body_ache, headaches, fatigue, chill]))

if __name__ == '__main__':
    app.run()
