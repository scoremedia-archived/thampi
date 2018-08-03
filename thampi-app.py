from flask import Flask, request, jsonify
from thampi.core.thampi import thampi

app = Flask(__name__)

thampi_instance = thampi(app)

global_model = thampi_instance.load_model()
global_properties = thampi_instance.load_properties()


@app.route(thampi_instance.predict_route(), methods=['POST'])
def index():
    print('^^^^ In Request ^^^')
    print(request.args)
    result = global_model.predict(request.args, thampi_instance.get_context())
    return jsonify(dict(properties=global_properties,
                        result=result))
    # return jsonify(dict(properties=properties, prediction=prediction))


# We only need this for local development.
if __name__ == '__main__':
    app.run()
