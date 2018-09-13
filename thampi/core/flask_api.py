print('Raj: Start of Thampi Flask API')
from flask import Flask, request, jsonify
print('Raj: After Flask Import')
from thampi.core.thampi_core import Thampi
print('Raj: After Thampi Core Import')
import json

app = Flask(__name__)

thampi_instance = Thampi(app)

print('Raj: Init: Before Global Model Loaded')
global_model = thampi_instance.load_model()
print('Raj: Init: After Global Model Loaded')
global_properties = thampi_instance.load_properties()
print('Raj: Init: After Global Properties loaded')


@app.route(thampi_instance.predict_route(), methods=['POST'])
def index():
    print('Raj: Start Index Method')
    global global_model
    args = json.loads(request.data)
    if not global_model:
        global_model = thampi_instance.load_model()
        print('Raj: Request: Global Properties loaded again')

    print('Raj: Before Predict')
    result = global_model.predict(args.get('data'), thampi_instance.get_context())
    print('Raj: After Predict')
    return jsonify(dict(properties=global_properties,
                        result=result))


# We only need this for local development.
if __name__ == '__main__':
    app.run()
