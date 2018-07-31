from thampi.lib import aws
from thampi.core import helper
import os
import json


class Thampi(object):
    def __init__(self, app):
        self.app = app
        self.project_name = os.environ['PROJECT']
        self.environment = os.environ['STAGE']
        self.bucket = helper.get_bucket(self.environment)
        self.model_key = helper.model_key(self.environment, self.project_name)
        self.properties_key = helper.properties_key(self.environment, self.project_name)
        self._predict_route = f'/{self.project_name}/predict'
        self._context = ThampiContext(self.app)

    def load_model(self):
        model = aws.load_s3_object(self.bucket, self.model_key)
        model.initialize(ThampiContext(self.app))
        return model

    def load_properties(self):
        result = aws.get_s3_object(self.bucket, self.properties_key)
        return json.loads(result)

    def predict_route(self) -> str:
        return self._predict_route

    def get_context(self):
        return self._context


class ThampiContext(object):
    def __init__(self, app):
        self._app = app

    def get_app(self):
        return self._app
