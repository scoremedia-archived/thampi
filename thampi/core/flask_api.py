from flask import Flask, request, jsonify
from thampi.core.thampi_core import Thampi
import json

app = Flask(__name__)

thampi_instance = Thampi(app)

global_model = thampi_instance.load_model()
print('Raj: Init: Global Model loaded')
global_properties = thampi_instance.load_properties()
print('Raj: Init: Global Properties loaded')


@app.route(thampi_instance.predict_route(), methods=['POST'])
def index():
    args = json.loads(request.data)
    if not global_model:
        global_model = thampi_instance.load_model()
        print('Raj: Request: Global Properties loaded again')
    
    result = global_model.predict(args.get('data'), thampi_instance.get_context())
    return jsonify(dict(properties=global_properties,
                        result=result))


# We only need this for local development.
if __name__ == '__main__':
    app.run()
