import abc
from typing import Dict
from thampi.core.thampi_core import ThampiContext


class Model(object):
    """
    The Abstract Model class which has to be inherited from by the model wrapper class that you create.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, context: ThampiContext) -> None:
        """
        This method is called once when AWS Lambda first loads the model. You can override this method to setup up
        global state(e.g. self.database_connection) which you can access within the `predict` method

        :param context: See documentation for Thampi Context API

        """
        pass

    @abc.abstractmethod
    def predict(self, args: Dict, context: ThampiContext) -> Dict:
        """
        This method is called when the client hits the predict endpoint.

        :param args: The `data` value sent by the client request is populated here.
        :param context: See documentation for Thampi Context API
        :return: Returns a dictionary which is automatically converted to JSON and sent back to the client.

        """
        pass
