from flask import Flask, request, jsonify

from thampi.core.thampi_core import Thampi

import json

app = Flask(__name__)

thampi_instance = Thampi(app)

global_model = thampi_instance.load_model()
global_properties = thampi_instance.load_properties()


@app.route(thampi_instance.predict_route(), methods=['POST'])
def index():
    global global_model
    args = json.loads(request.data)
    if not global_model:
        global_model = thampi_instance.load_model()

    result = global_model.predict(args.get('data'), thampi_instance.get_context())
    result = jsonify(dict(properties=global_properties,
                          result=result))
    return result


# We only need this for local development.
if __name__ == '__main__':
    app.run()
